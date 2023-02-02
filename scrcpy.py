import time
import subprocess
import socket
import struct
from queue import Queue
from threading import Thread
import av

ACTION_UP = b'\x01'
ACTION_DOWN = b'\x00'
ACTION_MOVE = b'\x02'

class ScrcpyClient(object):
    """Scrcpy的客户端"""
    is_running = False
    device_name = None
    resolution = None
    adb_sub_process = None
    video_socket = None
    control_socket = None
    decode_thread = None
    codec = None
    video_data_queue = None

    def __init__(self, max_size=0, bit_rate=8000000, max_fps=0, crop='-',
                    libs_path='libs', adb_path=r'adb', ip='127.0.0.1', port=27199,
                    queue_length=5):
        """
        初始化Scrcpy客户端

        :param max_size: frame width that will be broadcast from android server
        :param bit_rate:
        :param max_fps: 0 means not max fps
        :param crop:
        :param libs_path: path to 'scrcpy-server.jar'
        :param adb_path: path to ADB
        :param ip: scrcpy server IP
        :param port: scrcpy server port
        """
        print("Init Scrcpy client")
        self.max_size = max_size
        self.bit_rate = bit_rate
        self.max_fps = max_fps
        self.crop = crop
        self.libs_path = libs_path
        self.adb_path = adb_path
        self.ip = ip
        self.port = port
        self.video_data_queue = Queue(queue_length)

    def connect_and_forward_scrcpy(self):
        try:
            print("Upload JAR...")
            adb_push = subprocess.Popen(
                [self.adb_path, 'push', 'scrcpy-server.jar', '/data/local/tmp/'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.libs_path)
            adb_push_comm = ''.join([x.decode("utf-8") for x in adb_push.communicate() if x is not None])
            if "error" in adb_push_comm:
                print("Is your device/emulator visible to ADB?")
                raise Exception(adb_push_comm)

            print("Run JAR")
            '''
            ADB Shell is Blocking, don't wait up for it
            Args for the server are as follows:
            Also see: https://github.com/Genymobile/scrcpy/blob/master/app/src/server.c#L256
            '''
            self.adb_sub_process = subprocess.Popen(
                [self.adb_path, 'shell',
                 'CLASSPATH=/data/local/tmp/scrcpy-server.jar',
                 'app_process', '/', 'com.genymobile.scrcpy.Server',
                 '1.17', # scrcpy version
                 'info', # log level
                 str(self.max_size), # (integer, multiple of 8) max width
                 str(self.bit_rate), # (integer) bit rate
                 str(self.max_fps), # (integer) max fps
                 '-1', # lock_video_orientation_string
                 'true', # (bool) tunnel forward: use "adb forward" instead of "adb tunnel"
                 str(self.crop), # (string) crop: "width:height:x:y"
                 'false', # (bool) send frame meta: packet boundaries + timestamp
                 'true', # control
                 '0', # display_id_string
                 'false', # show_touches
                 'true', # stay_awake
                 '-', # codec_options
                 '-' # encoder_name 
                 ], stdin=subprocess.PIPE, cwd=self.libs_path
            )
            time.sleep(1)

            print("Forward port")
            subprocess.call([self.adb_path, 'forward', 'tcp:%d' % self.port, 'localabstract:scrcpy'])
            time.sleep(1)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find ADB at path: " + self.adb_path)

    def disable_forward(self):
        subprocess.call([self.adb_path, 'forward', '--remove', 'tcp:%d' % self.port])

    def connect(self):
        print("Connecting to video socket")
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((self.ip, self.port))

        dummy_byte = self.video_socket.recv(1)
        if not len(dummy_byte):
            raise ConnectionError("Did not receive Dummy Byte!")
        else:
            print("Connected successfully!")

        print("Connecting to control socket")
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.connect((self.ip, self.port))

        self.device_name = self.video_socket.recv(64).decode("utf-8")
        if not len(self.device_name):
            raise ConnectionError("Did not receive Device Name!")
        print("Device Name: " + self.device_name)

        self.resolution = struct.unpack(">HH", self.video_socket.recv(4))
        print("Screen resolution: %dX%d" % (self.resolution[0], self.resolution[1]))

        self.video_socket.setblocking(False)

    def start(self):
        if self.is_running: return False
        self.is_running = True
        print("Start scrcpy client")
        try:
            self.connect_and_forward_scrcpy()
            self.codec = av.codec.CodecContext.create('h264', 'r')
            self.connect()
            if self.decode_thread is None:
                self.decode_thread = Thread(target=self.loop, daemon=True)
                self.decode_thread.start()
        except Exception:
            self.stop()
            raise
            return False
        return True

    def loop(self):
        """
        Get raw h264 video data from video socket, parse packets, decode each
        packet to frames, convert each frame to numpy array and put them in Queue.
        This method should work in separate thread since it's blocking.
        """
        while self.is_running:
            packets = []
            try:
                raw_h264 = self.video_socket.recv(0x10000)
                if not raw_h264: continue
                packets = self.codec.parse(raw_h264)
                if not packets: continue
            except socket.error as e:
                continue
            for packet in packets:
                frames = self.codec.decode(packet)
                for frame in frames:
                    if self.video_data_queue.full():
                        self.video_data_queue.get()
                    self.video_data_queue.put(frame.to_ndarray(format="bgr24"))

    def get_next_frame(self, latest_image=False):
        if self.video_data_queue and not self.video_data_queue.empty():
            image = self.video_data_queue.get()
            if latest_image:
                while not self.video_data_queue.empty():
                    image = self.video_data_queue.get()
            return image
        return None

    def build_touch_message(self, x, y, action):
        b = bytearray(b'\x02')
        b += action
        b += b'\xff\xff\xff\xff\xff\xff\xff\xff'
        b += struct.pack('>I', int(x))
        b += struct.pack('>I', int(y))
        b += struct.pack('>h', int(self.resolution[0]))
        b += struct.pack('>h', int(self.resolution[1]))
        b += b'\xff\xff'  # Pressure
        b += b'\x00\x00\x00\x01'  # Event button primary
        return bytes(b)

    def tap(self, x, y):
        self.control_socket.send(self.build_touch_message(x, y, ACTION_DOWN))
        self.control_socket.send(self.build_touch_message(x, y, ACTION_UP))

    def swipe(self, start_x, start_y, end_x, end_y, move_step_length=5, move_steps_delay=0.005):
        self.control_socket.send(self.build_touch_message(start_x, start_y, self.ACTION_DOWN))
        next_x = start_x
        next_y = start_y
        if end_x > self.resolution[0]:
            end_x = self.resolution[0]
        if end_y > self.resolution[1]:
            end_y = self.resolution[1]
        decrease_x = True if start_x > end_x else False
        decrease_y = True if start_y > end_y else False
        while True:
            if decrease_x:
                next_x -= move_step_length
                if next_x < end_x:
                    next_x = end_x
            else:
                next_x += move_step_length
                if next_x > end_x:
                    next_x = end_x
            if decrease_y:
                next_y -= move_step_length
                if next_y < end_y:
                    next_y = end_y
            else:
                next_y += move_step_length
                if next_y > end_y:
                    next_y = end_y
            self.control_socket.send(self.build_touch_message(next_x, next_y, self.ACTION_MOVE))
            if next_x == end_x and next_y == end_y:
                self.control_socket.send(self.build_touch_message(next_x, next_y, self.ACTION_UP))
                break
            time.sleep(move_steps_delay)

    def stop(self):
        if not self.is_running: return
        self.is_running = False
        print("Stop scrcpy client")
        if self.decode_thread is not None:
            self.decode_thread.join()
        self.video_data_queue = None
        if self.video_socket is not None:
            self.video_socket.close()
            self.video_socket = None
        if self.control_socket is not None:
            self.control_socket.close()
            self.control_socket = None
        self.disable_forward()
