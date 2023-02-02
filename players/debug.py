import time
import numpy
from .player import Player
import utils

class DebugPlayer(Player):
    """图像识别测试"""
    path = None
    image = None

    def __init__(self):
        self.path = input("请输入要测试的数据集路径: ")
        if self.path == "":
            self.path = "test"
        print(f"已成功读取数据集 {self.path}")
        self.image = utils.readimage(self.path)
        self.height, self.width = self.image.shape[:2]
        print(f"已获得图像尺寸: {self.width} X {self.height}")
        super().__init__()

    def _screenshot(self):
        return numpy.copy(self.image)

    def _click(self, x, y):
        x, y = int(x), int(y)
        print(f"自动点击 X: {x} Y: {y}")
        time.sleep(0.01)
