import types
import cv2
from utils import Timer

class Task(object):
    """自动挂机任务的基类"""
    name: str
    description: str

    frame = None # : cv2.Mat

    async def run(self, player):
        """执行任务"""
        return True

    def timer(self, interval: float):
        """创建一个在指定秒后到期的定时器"""
        return Timer(interval)

    @types.coroutine
    def next(self):
        """等待下一帧"""
        yield

    @types.coroutine
    def wait(self, s: float):
        """等待指定秒"""
        timer = self.timer(s)
        while not timer.timeout():
            yield

    @types.coroutine
    def inputpoint(self):
        """获取点"""
        self.clicked = None
        while self.clicked is None:
            yield
        point, self.clicked = self.clicked, None
        return point

class RepeatTask(Task):
    """可重复执行的自动挂机任务"""

    async def runonce(self, player):
        """执行一次任务"""
        return True

    async def run(self, player):
        times = 0
        while True:
            times += 1
            print(f"第 {times} 次运行任务")
            if not await self.runonce(player):
                break

_tasks = []

def task(name, desc):
    """用于自动注册任务的装饰器"""
    def decorator(cls):
        cls.name = name
        cls.description = desc
        _tasks.append(cls)
        return cls
    return decorator

def tasks():
    """获取任务列表"""
    return _tasks
