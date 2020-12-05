# coding=utf-8

from enum import Enum, auto
import sys
import time
import ctypes
import atexit
import numpy
import cv2

import random

from player import Player, PlayerADB, PlayerTest, readimage, writeimage

WINDOW_NAME = "Preview Window"

class Modes(Enum):
    KECHAO = auto()
    HDXYX = auto()

functions = {}
descriptions = {}

def register(mode: Modes, func, desc):
    functions[mode] = func
    descriptions[mode] = desc
    return

fps = 5
threshold = 0.75
player = None

def main():
    register(Modes.KECHAO, kechao, "自动客潮(请将界面停留在餐厅)")
    register(Modes.HDXYX, None, "自动小游戏(尚未编写)")
    setnodpi()
    settitle("欢迎使用食物语挂机脚本")
    print('''=============================================
食物语挂机脚本 V1.0 作者: WC
本脚本仅供个人代肝使用, 严禁用于商业用途
使用本脚本造成的一切法律纠纷由使用者自行承担
项目地址: https://github.com/DawningW/swy-bot
欢迎提交问题或是直接PR
=============================================''')
    while True:
        print('''>>>----------< 主 菜 单 >----------<<<
1. 原生模式(需先启动安卓虚拟机并打开食物语)
2. ADB模式(需手机连接电脑打开调试模式并打开食物语)
3. 调试模式(将读取程序目录下的test.png并进行图像识别)
4. 线性规划做菜计算器
0. 退出''')
        str = input("请选择: ")
        global player
        if str == "0":
            break
        if str == "1":
            player = Player()
        elif str == "2":
            player = PlayerADB()
        elif str == "3":
            player = PlayerTest()
        elif str == "4":
            print("正在开发中")
            continue
        else:
            continue
        if (player.init()): select()
    return

def select():
    while True:
        print(">>>----------< 挂 机 菜 单 >----------<<<")
        for i in range(1, len(Modes) + 1):
            print("{}. {}".format(i, descriptions[Modes(i)]))
        print("PS: 输入其他数字退出")
        try:
            num = int(input("请输入序号: "))
            mode = Modes(num)
            run(mode)
        except ValueError:
            break
    return

def run(mode):
    settitle("食物语挂机脚本运行中 - 按 Ctrl + C 退出")
    print("开始运行挂机脚本")
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, onclicked)
    times = 0
    while True:
        times += 1
        print("第 {} 次运行脚本 {}".format(times, mode))
        if not functions[mode](): break
    cv2.destroyAllWindows()
    settitle("当前挂机脚本已运行完毕 - 准备就绪")
    print("挂机脚本已运行完毕")
    return

def execute(func, repeat = False):
    # 向execute中传的函数若单次执行则返回值无用, 若多次执行则True为继续, False为停止
    while True:
        start = time.time()
        flag = func()
        end = time.time()
        wait = 1 / fps - (end - start)
        if wait < 0:
            print("严重滞后, 处理时间超出 {} ms, 发生了什么呢?".format(-int(wait * 1000)))
            wait = 0
        if (not repeat) or (not flag): return
        time.sleep(wait)
    return

def onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("点击 X: {} Y: {}".format(x, y))
        player.click(x / player.factor, y / player.factor)
    return

def showimage(image, wait = 1):
    cv2.imshow(WINDOW_NAME, image)
    cv2.setMouseCallback(WINDOW_NAME, onclicked)
    cv2.waitKey(wait)
    return

def findtemplate(image, template, outline = False):
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

# 以下是具体挂机逻辑, 每次调用函数都应被视作挂机一次, 返回True将会继续, 如果想退出请返回False
def kechao():
    # 开始客潮
    template = readimage("kechao_btn")
    def start():

        return False
    # 客潮挂机
    def run():
        image = player.screenshot()
        image = cv2.resize(image, None, fx = player.factor, fy = player.factor, interpolation = cv2.INTER_AREA)
        points = findcircle(image, 25)
        for x, y in points:
            if x > (image.shape[1] * 0.9): continue
            cv2.circle(image, (x, y), 25, (0, 0, 255), 3)
            player.clickaround(x / player.factor, y / player.factor)
        showimage(image)
        return True
    # 结束客潮
    def end():

        return False
    # 执行
    execute(start, True)
    execute(run, True)
    execute(end, True)
    return True

@atexit.register  
def onexit():
    settitle("食物语挂机脚本已结束")
    if player != None: player.end()
    print('''
=============================================
食物语挂机脚本已停止运行, 感谢您的使用, 再见!
=============================================''')
    return

def setnodpi():
    try: # >= windows 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # <= windows 8.0
        ctypes.windll.user32.SetProcessDPIAware()
    return

def settitle(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
    return

def isadmin():
    "检查管理员权限"
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 入口
if __name__ == "__main__":
    # 检查权限
    if isadmin() or True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        if len(sys.argv) >= 2 and sys.argv[1] == "debug":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__ + " debug", None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
