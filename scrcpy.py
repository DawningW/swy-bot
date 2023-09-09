import time
import subprocess
import socket
import struct
from queue import Queue
from threading import Thread
import av

ACTION_DOWN = b'\x00'
ACTION_UP = b'\x01'
ACTION_MOVE = b'\x02'

class ScrcpyClient(object):
    '''Scrcpy的客户端'''
    is_running = False
    device_name = None
    resolution = None
    adb_sub_process = None
    video_socket = None
    control_socket = None
    decode_thread = None
    codec = None
    video_data_queue = None

    def __init__(self, bit_rate=8000000, log_level='info', queue_length=5,
                    libs_path='libs', adb_path='adb', ip='127.0.0.1', port=27199):
        '''
        初始化Scrcpy客户端

        :param bit_rate:
        :param libs_path: path to 'scrcpy-server.jar'
        :param adb_path: path to ADB
        :param ip: scrcpy server IP
        :param port: scrcpy server port
        '''
        print('Init Scrcpy client')
        self.options = {}
        self.options['log_level'] = log_level
        self.options['bit_rate'] = bit_rate
        self.options['tunnel_forward'] = 'true'
        self.libs_path = libs_path
        self.lib_name = 'scrcpy-server.jar'
        self.lib_version = '1.25'
        self.adb_path = adb_path
        self.ip = ip
        self.port = port
        self.video_data_queue = Queue(queue_length)

    def set_option(self, key, value):
        '''
        Args for the server are as follows:
        - log_level: (string) log level
        - bit_rate: (integer) bit rate
        - max_size: (integer, multiple of 8) max width
        - max_fps: (integer) max fps
        - lock_video_orientation: (integer) lock video orientation
        - tunnel_forward: (bool) tunnel forward: use 'adb forward' instead of 'adb tunnel'
        - crop: (string) crop, value is 'width:height:x:y'
        - control: (bool) control
        - display_id: (integer) display id
        - show_touches: (bool) show touches
        - stay_awake: (bool) stay awake
        - codec_options: (string) codec options
        - encoder_name: (string) encoder name
        - power_off_on_close: (bool) power off on close
        - clipboard_autosync: (bool) auto sync clipboard
        - downsize_on_error: (bool) downsize on error
        - cleanup: (bool) cleanup
        - power_on: (bool) power on
        For more options, also see: https://github.com/Genymobile/scrcpy/blob/master/app/src/server.c#L158
        '''
        self.options[key] = value

    def connect_and_forward_scrcpy(self):
        try:
            print('Upload JAR...')
            adb_push = subprocess.Popen(
                [self.adb_path, 'push', self.lib_name, '/data/local/tmp/'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.libs_path)
            adb_push_comm = ''.join([x.decode('utf-8') for x in adb_push.communicate() if x is not None])
            if 'error' in adb_push_comm:
                print('Is your device/emulator visible to ADB?')
                raise Exception(adb_push_comm)

            print('Run JAR')
            args = [
                self.adb_path, 'shell',
                'CLASSPATH=/data/local/tmp/' + self.lib_name,
                'app_process', '/', 'com.genymobile.scrcpy.Server',
                self.lib_version
            ]
            args.append('log_level=' + self.options['log_level'])
            args.append('bit_rate=' + str(self.options['bit_rate']))
            if 'max_size' in self.options:
                args.append('max_size=' + str(self.options['max_size']))
            if 'max_fps' in self.options:
                args.append('max_fps=' + str(self.options['max_fps']))
            if 'lock_video_orientation' in self.options:
                args.append('lock_video_orientation=' + str(self.options['lock_video_orientation']))
            if 'tunnel_forward' in self.options:
                args.append('tunnel_forward=' + self.options['tunnel_forward'])
            if 'crop' in self.options:
                args.append('crop=' + self.options['crop'])
            if 'control' in self.options:
                args.append('control=' + self.options['control'])
            if 'display_id' in self.options:
                args.append('display_id=' + str(self.options['display_id']))
            if 'show_touches' in self.options:
                args.append('show_touches=' + self.options['show_touches'])
            if 'stay_awake' in self.options:
                args.append('stay_awake=' + self.options['stay_awake'])
            if 'codec_options' in self.options:
                args.append('codec_options=' + self.options['codec_options'])
            if 'encoder_name' in self.options:
                args.append('encoder_name=' + self.options['encoder_name'])
            if 'power_off_on_close' in self.options:
                args.append('power_off_on_close=' + self.options['power_off_on_close'])
            if 'clipboard_autosync' in self.options:
                args.append('clipboard_autosync=' + self.options['clipboard_autosync'])
            if 'downsize_on_error' in self.options:
                args.append('downsize_on_error=' + self.options['downsize_on_error'])
            if 'cleanup' in self.options:
                args.append('cleanup=' + self.options['cleanup'])
            if 'power_on' in self.options:
                args.append('power_on=' + self.options['power_on'])
            # ADB Shell is Blocking, don't wait up for it
            self.adb_sub_process = subprocess.Popen(args, stdin=subprocess.PIPE, cwd=self.libs_path)
            time.sleep(1)

            print('Forward port')
            subprocess.call([self.adb_path, 'forward', 'tcp:%d' % self.port, 'localabstract:scrcpy'])
            time.sleep(1)
        except FileNotFoundError:
            raise FileNotFoundError('Could not find ADB at path: ' + self.adb_path)

    def disable_forward(self):
        subprocess.call([self.adb_path, 'forward', '--remove', 'tcp:%d' % self.port])

    def connect(self):
        print('Connecting to video socket')
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((self.ip, self.port))

        dummy_byte = self.video_socket.recv(1, socket.MSG_WAITALL)
        if not len(dummy_byte):
            raise ConnectionError('Did not receive Dummy Byte!')
        else:
            print('Connected successfully!')

        print('Connecting to control socket')
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.connect((self.ip, self.port))

        self.device_name = self.video_socket.recv(64, socket.MSG_WAITALL).decode('utf-8')
        if not len(self.device_name):
            raise ConnectionError('Did not receive Device Name!')
        print('Device name: ' + self.device_name)

        self.resolution = struct.unpack('>HH', self.video_socket.recv(4, socket.MSG_WAITALL))
        print('Screen resolution: %dX%d' % (self.resolution[0], self.resolution[1]))

    def start(self):
        if self.is_running: return False
        self.is_running = True
        print('Start scrcpy client')
        try:
            self.connect_and_forward_scrcpy()
            self.codec = av.codec.CodecContext.create('h264', 'r')
            self.connect()
            if self.decode_thread is None:
                self.decode_thread = Thread(target=self.loop, daemon=True)
                self.decode_thread.start()
        except Exception:
            self.stop()
            return False
        return True

    def loop(self):
        '''
        Get raw h264 video data from video socket, parse packets, decode each
        packet to frames, convert each frame to numpy array and put them in Queue.
        This method should work in separate thread since it's blocking.
        '''
        while self.is_running:
            packets = []
            try:
                # A "meta" header includes 8 bytes PTS and 4 bytes packet size
                meta = self.video_socket.recv(12, socket.MSG_WAITALL)
                if len(meta) < 12: continue
                pts, size = struct.unpack('>QI', meta)
                raw_packet = self.video_socket.recv(size, socket.MSG_WAITALL)
                if len(raw_packet) < size: continue
                packets = self.codec.parse(raw_packet)
                if not packets: continue
            except socket.error as e:
                continue
            for packet in packets:
                # packet.pts = pts
                frames = self.codec.decode(packet)
                for frame in frames:
                    if self.video_data_queue.full():
                        self.video_data_queue.get()
                    self.video_data_queue.put(frame.to_ndarray(format='bgr24'))

    def get_next_frame(self, latest_image=False):
        if self.video_data_queue and not self.video_data_queue.empty():
            image = self.video_data_queue.get()
            if latest_image:
                while not self.video_data_queue.empty():
                    image = self.video_data_queue.get()
            return image
        return None

    def build_touch_message(self, x, y, action):
        b = bytearray(b'\x02') # SC_CONTROL_MSG_TYPE_INJECT_TOUCH_EVENT
        b += action
        b += b'\xff\xff\xff\xff\xff\xff\xff\xfe' # POINTER_ID_GENERIC_FINGER
        b += struct.pack('>i', int(x))
        b += struct.pack('>i', int(y))
        b += struct.pack('>H', int(self.resolution[0]))
        b += struct.pack('>H', int(self.resolution[1]))
        b += b'\xff\xff' if action == ACTION_DOWN else b'\x00\x00' # pressure
        b += b'\x00\x00\x00\x01' # AMOTION_EVENT_BUTTON_PRIMARY
        return bytes(b)

    def tap(self, x, y):
        self.control_socket.send(self.build_touch_message(x, y, ACTION_DOWN))
        self.control_socket.send(self.build_touch_message(x, y, ACTION_UP))

    def swipe(self, start_x, start_y, end_x, end_y, move_step_length=5, move_steps_delay=0.005):
        self.control_socket.send(self.build_touch_message(start_x, start_y, ACTION_DOWN))
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
            self.control_socket.send(self.build_touch_message(next_x, next_y, ACTION_MOVE))
            if next_x == end_x and next_y == end_y:
                self.control_socket.send(self.build_touch_message(next_x, next_y, ACTION_UP))
                break
            time.sleep(move_steps_delay)

    def stop(self):
        if not self.is_running: return
        self.is_running = False
        print('Stop scrcpy client')
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
