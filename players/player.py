import random
import math
import cv2

DESIGN_LENGTH = 480

class Player(object):
    """模拟玩家操作的基类"""

    width: int
    "游戏实际宽度"
    height: int
    "游戏实际高度"
    factor: int
    "设计宽高 / 游戏实际宽高"

    def __init__(self):
        """初始化"""
        self.factor = DESIGN_LENGTH / min(self.width, self.height)
        print(f"已计算缩放比率: {self.factor}")

    def release(self):
        """释放资源"""
        pass

    def _screenshot(self):
        """需要子类重写"""
        return None

    def screenshot(self):
        image = self._screenshot()
        image = cv2.resize(image, None, fx=self.factor, fy=self.factor, interpolation=cv2.INTER_AREA)
        return image

    def _click(self, x, y):
        """需要子类重写"""
        pass

    def click(self, x, y):
        self._click(x / self.factor, y / self.factor)

    def clickaround(self, x, y):
        self.clickcircle(x, y, 4)

    def clickcircle(self, x, y, radius):
        # 虽然不均匀, 但正是我想要的
        theta = 2 * math.pi * random.random()
        rho = radius * random.random()
        dx = rho * math.cos(theta)
        dy = rho * math.sin(theta)
        self.click(x + dx, y + dy)

    def clickbetween(self, x1, y1, x2, y2):
        x, y = (x1 + x2) / 2, (y1 + y2) / 2
        self.clickrect(x, y, abs(x2 - x1), abs(y2 - y1))

    def clicksquare(self, x, y, length):
        dl = random.randint(-length / 2, length / 2)
        self.click(x + dl, y + dl)

    def clickrect(self, x, y, width, height):
        dx = random.randint(-width / 2, width / 2)
        dy = random.randint(-height / 2, height / 2)
        self.click(x + dx, y + dy)

_players = []

def addplayer(name, desc, cls):
    """添加玩家操作模拟类"""
    _players.append((name, desc, cls))

def players():
    """获取玩家操作模拟类"""
    return _players
