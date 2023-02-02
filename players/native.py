from .player import Player
import utils

class NativePlayer(Player):
    """模拟鼠标点击窗口"""
    window = None

    def __init__(self):
        self.window = utils.selectwindow()
        assert self.window is not None
        self.width, self.height = utils.getsize(self.window)
        print(f"已获得窗口大小: {self.width} X {self.height}")
        super().__init__()

    def _screenshot(self):
        return utils.screenshot(self.window)

    def _click(self, x, y):
        utils.click(self.window, int(x), int(y))
