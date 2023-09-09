import time
import cv2
from .player import Player
from scrcpy import ScrcpyClient

class ScrcpyPlayer(Player):
    """使用Scrcpy获取截屏并模拟点击"""
    client = None

    def __init__(self):
        self.client = ScrcpyClient(queue_length=3)
        self.client.set_option("max_fps", 30)
        self.client.set_option("show_touches", "false")
        self.client.start()
        print(f"已成功连接至设备 {self.client.device_name}")
        self.width, self.height = self.client.resolution
        print(f"已获得设备屏幕尺寸: {self.width} X {self.height}")
        super().__init__()

    def release(self):
        self.client.stop()

    def _screenshot(self):
        while True:
            image = self.client.get_next_frame(True)
            if image is None:
                time.sleep(0.01)
                continue
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            return image

    def _click(self, x, y):
        self.client.tap(x, y)
