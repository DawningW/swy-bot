# coding=utf-8

from enum import Enum, IntEnum, auto
import time
import random
import math
import numpy
import cv2
from utils import readimage

class Phases(IntEnum):
    """任务执行的阶段"""
    BEGIN = 0
    RUNNING = 1
    END = 2

class Results(Enum):
    """任务执行的结果"""
    PASS = auto()
    SUCCESS = auto()
    FAIL = auto()

tasks = []

def getTasks():
    """获取任务列表"""
    return tasks

def registerTask(task, name, desc):
    """注册任务(已弃用,请使用装饰器注册任务)"""
    task.name = name
    task.description = desc
    tasks.append(task)
    return

def Task(name, desc):
    """用于自动注册任务的装饰器"""
    def decorator(cls):
        registerTask(cls, name, desc)
        return cls
    return decorator

class TaskBase(object):
    """自动挂机任务的基类"""
    name = ""
    description = ""

    def __init__(self):
        """初始化"""
        self.image = None
        return

    def begin(self, player, t):
        """开始任务"""
        return Results.FAIL

    def run(self, player, t):
        """执行任务"""
        return Results.FAIL

    def end(self, player, t):
        """结束任务"""
        return Results.FAIL

    def getImageCache(self):
        """获取用于预览的图像,如果不想显示请返回None"""
        return self.image

@Task("自动客潮", "请将界面停留在餐厅")
class TaskKeChao(TaskBase):
    """客潮自动化"""
    def __init__(self):
        super().__init__()
        self.templateButton = readimage("kechao_btn")
        self.templateDish = readimage("kechao_dish_part")
        self.templateTitle = readimage("kechao_title_part")

        self.lastTime = 0
        self.dialog = False
        self.pointCache = []
        return

    def begin(self, player, t):
        """需要玩家位于餐厅界面"""
        self.image = player.screenshot()
        if not self.dialog:
            points = findcircle(self.image, 25)
            for x, y in points:
                if x > (self.image.shape[1] * 0.9) and y < (self.image.shape[0] * 0.2):
                    player.clickaround(x, y)
                    self.dialog = True
        else:
            points = findtemplate(self.image, self.templateButton)
            for x, y in points:
                player.clickaround(x, y)
                time.sleep(1)
                return Results.SUCCESS
        return Results.PASS

    def run(self, player, t):
        """客潮挂机中"""
        self.image = player.screenshot()
        points = findcircle(self.image, 25)
        points2 = []
        for x, y in points:
            if x > (self.image.shape[1] * 0.9): continue
            if y > (self.image.shape[0] * 0.8): return Results.SUCCESS
            cv2.circle(self.image, (x, y), 25, (0, 0, 255), 3)
            points2.append((x, y))
        if len(points2) > 0:
            x, y = random.choice(points2)
            player.clickaround(x, y)
        return Results.PASS

    def end(self, player, t):
        """结束客潮"""
        self.image = player.screenshot()
        points = findtemplate(self.image, self.templateTitle)
        for x, y in points:
            time.sleep(2)
            player.clickaround(x, y)
            time.sleep(2)
            return Results.SUCCESS
        return Results.PASS

@Task("自动小游戏", "尚未编写")
class TaskMiniGames(TaskBase):
    """活动小游戏 算了放弃了 毁灭吧赶紧的"""

def findtemplate(image, template, threshold = 0.75, outline = False):
    theight, twidth = template.shape[:2]
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    # result = cv2.normalize(result, None, 0, 1, cv2.NORM_MINMAX)
    location = numpy.where(result >= threshold)
    lx, ly = 0, 0
    points = []
    for pt in zip(*location[::-1]):
        x, y = pt[0] + int(twidth / 2), pt[1] + int(theight / 2)
        # 去掉重复点
        if x - lx < twidth or y - ly < theight: continue
        points.append((x, y))
        lx, ly = x, y
        if outline:
            cv2.rectangle(image, pt, (pt[0] + twidth, pt[1] + theight), (0, 255, 0), 1)
    return points

def findcircle(image, r, outline = False):
    gimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gimg = cv2.medianBlur(gimg, 5)
    result = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, int(r / 2), None, 100, 40, r - 10, r + 10)
    points = []
    # 寻找不到会返回None
    if result is not None:
        result = numpy.uint16(numpy.around(result))
        for p in result[0,:]:
            points.append((p[0], p[1]))
            if outline:
                cv2.circle(image, (p[0], p[1]), p[2], (0, 255, 0), 1)
    return points
