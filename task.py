# coding=utf-8

from enum import Enum, IntEnum, auto
import time
import random
import math
import numpy
import cv2
from utils import readimage, writeimage
import matching

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
        # 0:餐厅界面 1:客潮对话框 2:客潮进行中 3:客潮结束结算界面
        self.step = 0
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
            if not self.containpoint(x, y):
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
        """客潮结束"""
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

    def containpoint(self, x, y):
        for cx, cy, time in self.pointCache:
            if math.sqrt(math.pow(int(x) - int(cx), 2) + math.pow(int(y) - int(cy), 2)) < 5:
                return True
        return False

class TaskMiniGame(TaskBase):
    """活动小游戏挂机任务的基类"""

    def __init__(self):
        super().__init__()
        self.templateButton = readimage("minigame_btn")
        return

    def init(self):
        self.lastTime = 0
        # 是否点击过开始按钮了
        self.started = False
        return

    def begin(self, player, t):
        """需要玩家位于小游戏界面"""
        self.image = player.screenshot()
        if not self.started:
            points = findtemplate(self.image, self.templateButton)
            for x, y in points:
                cv2.circle(self.image, (x, y), 40, (0, 0, 255), 2)
                player.click(x, y)
                self.lastTime = t
                self.started = True
                return Results.PASS
            if t - self.lastTime > 3:
                # 没找到开始按钮且超时
                print("未找到开始按钮, 请确认您正位于小游戏界面")
                return Results.FAIL
        elif t - self.lastTime > 1:
            self.lastTime = t
            return Results.SUCCESS
        return Results.PASS

try:
    from constant import *
except:
    # **若想使用请自行修改以下数据**
    # 消除的时间间隔
    TIME_INTERVAL = 0.5
    # 游戏区域距离屏幕左方的距离
    MARGIN_LEFT = 0
    # 游戏区域距离屏幕顶部的距离
    MARGIN_TOP = 0
    # 横向方块数量
    HORIZONTAL_NUM = 10
    # 纵向方块数量
    VERTICAL_NUM = 10
    # 方块宽度
    SQUARE_WIDTH = 100
    # 方块高度
    SQUARE_HEIGHT = 100
    # 切片处理时的左上和右下坐标
    SUB_LT_X = 20
    SUB_LT_Y = 20
    SUB_RB_X = 80
    SUB_RB_Y = 80

@Task("自动小游戏-千人千面", "需自行修改代码进行配置")
class TaskQianRenQianMian(TaskMiniGame):
    """千人千面自动连连看"""

    def init(self):
        super().init()
        self.result = None
        self.pair = None
        return

    def run(self, player, t):
        """小游戏挂机中"""
        self.image = player.screenshot()
        for j in range(VERTICAL_NUM):
            for i in range(HORIZONTAL_NUM):
                x = MARGIN_LEFT + i * SQUARE_WIDTH
                y = MARGIN_TOP + j * SQUARE_HEIGHT
                cv2.rectangle(self.image, (x, y), (x + SQUARE_WIDTH, y + SQUARE_HEIGHT), (0, 255, 0), 1)
        if self.result is None:
            # 图像切片并保存在数组中
            squares = []
            for j in range(VERTICAL_NUM):
                for i in range(HORIZONTAL_NUM):
                    x = MARGIN_LEFT + i * SQUARE_WIDTH
                    y = MARGIN_TOP + j * SQUARE_HEIGHT
                    square = self.image[y : y + SQUARE_HEIGHT, x : x + SQUARE_WIDTH]
                    # 每个方块向内缩小一部分防止边缘不一致造成干扰
                    square = square[SUB_LT_Y : SUB_RB_Y, SUB_LT_X : SUB_RB_X]
                    squares.append(square)
            # 相同的方块作为一种类型放在数组中
            types = []
            for square in squares:
                if self.isbackground(square):
                    continue
                if not self.isimageexist(square, types):
                    types.append(square)
            # 将切片处理后的图片数组转换成相对应的数字矩阵
            self.result = []
            num = 0
            for j in range(VERTICAL_NUM):
                line = []
                for i in range(HORIZONTAL_NUM):
                    if self.isbackground(squares[num]):
                        line.append(0)
                    else:
                        for t in range(len(types)):
                            if isimagesame(squares[num], types[t]):
                                line.append(t + 1)
                                break
                    num += 1
                self.result.append(line)
            return Results.PASS
        # 执行自动消除
        if t - self.lastTime >= TIME_INTERVAL:
            self.lastTime = t
            # 第二次选择
            if self.pair is not None:
                player.click(self.pair[0] + SQUARE_WIDTH / 2, self.pair[1] + SQUARE_HEIGHT / 2)
                self.pair = None
                return Results.PASS
            # 定位第一个选中点
            for i in range(len(self.result)):
                for j in range(len(self.result[0])):
                    if self.result[i][j] != 0:
                        # 定位第二个选中点
                        for m in range(len(self.result)):
                            for n in range(len(self.result[0])):
                                if self.result[m][n] != 0:
                                    if matching.canConnect(i, j, m, n, self.result):
                                        # 执行消除算法并进行第一次选择
                                        self.result[i][j] = 0
                                        self.result[m][n] = 0
                                        x1 = MARGIN_LEFT + j * SQUARE_WIDTH
                                        y1 = MARGIN_TOP + i * SQUARE_HEIGHT
                                        x2 = MARGIN_LEFT + n * SQUARE_WIDTH
                                        y2 = MARGIN_TOP + m * SQUARE_HEIGHT
                                        player.click(x1 + SQUARE_WIDTH / 2, y1 + SQUARE_HEIGHT / 2)
                                        self.pair = (x2, y2)
                                        return Results.PASS
            # TODO 判断一下出现结束画面才算完毕, 否则等待一会后重新规划
            print("自动消除运行完毕")
            return Results.SUCCESS
        return Results.PASS

    def isbackground(self, img):
        # TODO 是否有更好的算法?
        # OpenCV的顺序是BGR不是RGB...
        return abs(img[:, :, 0].mean() - 54) <= 10 and abs(img[:, :, 1].mean() - 70) <= 20 and abs(img[:, :, 2].mean() - 105) <= 15

    def isimageexist(self, img, img_list):
        for existed_img in img_list:
            if isimagesame(img, existed_img):
                return True
        return False

@Task("自动小游戏", "更多自动小游戏敬请期待...")
class TaskMoreMiniGames(TaskBase):
    """算了放弃了, 毁灭吧赶紧的"""

    def begin(self, player, t):
        print("我不想做了, 如果您需要的话可以自行编写挂机任务, 然后提交pr")
        return Results.FAIL

def isimagesame(img1, img2, threshold = 0.5):
    # TODO 是否有更好的算法?
    # b = numpy.subtract(existed_img, img)
    # return not numpy.any(b)
    result = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    location = numpy.where(result >= threshold)
    for pt in zip(*location[::-1]):
        return True
    return False

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
