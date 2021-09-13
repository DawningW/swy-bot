# coding=utf-8

from enum import Enum, IntEnum, auto
import time
import random
import math
import numpy
import cv2
from utils import readimage, writeimage

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
        return

    def init(self):
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
        return

    def init(self):
        super().init()
        self.lastTime = 0
        self.step = 0
        # 0:餐厅界面 1:客潮对话框 2:客潮进行中 3:客潮结束结算界面
        self.pointCache = []
        return

    def begin(self, player, t):
        """需要玩家位于餐厅界面"""
        self.image = player.screenshot()
        if self.step == 0:
            points = findcircle(self.image, 25)
            for x, y in points:
                if x > (self.image.shape[1] * 0.9) and y < (self.image.shape[0] * 0.2):
                    # 找到客潮按钮
                    player.clickaround(x, y)
                    self.lastTime = t
                    self.step = 1
                    return Results.PASS
            if t - self.lastTime > 3:
                # 没找到客潮按钮且超时
                print("未找到客潮按钮, 请确认您正位于餐厅界面")
                return Results.FAIL
        elif self.step == 1 or self.step == 2:
            if t - self.lastTime > 2:
                points = findtemplate(self.image, self.templateButton)
                for x, y in points:
                    # 找到开始按钮
                    if self.step == 2:
                        print("点击按钮后没有开始, 可能是客潮开启次数不足")
                        return Results.FAIL
                    player.clickaround(x, y)
                    self.lastTime = t
                    self.step = 2
                    return Results.PASS
                # 找不到开始按钮
                if self.step == 2:
                    # 点过开始按钮了, 进入客潮
                    self.lastTime = t
                    print("进入客潮")
                    return Results.SUCCESS
                # 还没点过开始按钮, 回退到第0步
                self.lastTime = t
                self.step = 0
                return Results.PASS
        return Results.PASS

    def run(self, player, t):
        """客潮挂机中"""
        self.image = player.screenshot()
        # 处理点的缓存
        self.pointCache = [(x, y, time - 1) for x, y, time in self.pointCache if time > 1]
        # 识别圆来寻找菜(旧版本用模版匹配, 效果不好)
        points = findcircle(self.image, 25)
        points2 = []
        for x, y in points:
            if x > (self.image.shape[1] * 0.9): continue
            if y > (self.image.shape[0] * 0.8):
                # 客潮结束回到餐厅
                self.lastTime = t
                self.step = 3
                print("客潮结束")
                return Results.SUCCESS
            cv2.circle(self.image, (x, y), 25, (0, 0, 255), 3)
            if not self.containPoint(x, y):
                points2.append((x, y))
        if len(points2) > 0:
            x, y = random.choice(points2)
            player.clickaround(x, y)
            self.pointCache.append((x, y, 10))
            self.lastTime = t
            return Results.PASS
        if t - self.lastTime > 15:
            # 没人点菜, 停止挂机?
            print("超过15秒钟没有客人点菜了, 停止挂机")
            return Results.FAIL
        return Results.PASS

    def end(self, player, t):
        """结束客潮"""
        self.image = player.screenshot()
        if self.step == 3:
            if t - self.lastTime > 2:
                points = findtemplate(self.image, self.templateTitle)
                for x, y in points:
                    # 正位于客潮结算界面
                    filename = "KeChao_" + time.strftime("%Y-%m-%d-%H-%M-%S")
                    writeimage(filename, self.image)
                    print("已将客潮结算界面截图保存至: saved/%s.png" % filename)
                    player.clickaround(x, y)
                    self.lastTime = t
                    return Results.PASS
                # 结算完了
                self.lastTime = t
                return Results.SUCCESS
        return Results.PASS

    def containPoint(self, x, y):
        for cx, cy, time in self.pointCache:
            if math.sqrt(math.pow(int(x) - int(cx), 2) + math.pow(int(y) - int(cy), 2)) < 5:
                return True
        return False

@Task("自动小游戏-千人千面", "需自行修改代码进行配置")
class TaskQianRenQianMian(TaskBase):
    """千人千面"""

    def __init__(self):
        super().__init__()
        self.lastTime = 0
        return

    def begin(self, player, t):
        """开始小游戏"""
        
        return Results.FAIL

@Task("自动小游戏", "更多自动小游戏敬请期待...")
class TaskMiniGames(TaskBase):
    """活动小游戏 算了放弃了 毁灭吧赶紧的"""

    def __init__(self):
        super().__init__()
        self.lastTime = 0
        return

    def begin(self, player, t):
        """开始小游戏"""
        print("我不想做了")
        return Results.FAIL

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
