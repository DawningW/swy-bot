# coding=utf-8

from enum import Enum, auto
import sys
import time
import ctypes
import atexit

import cv2

from player import Player, PlayerADB, PlayerTest

class Modes(Enum):
    KECHAO = auto()
    HDXYX = auto()

WINDOW_NAME = "Preview Window"
functions = {}
fps = 5
player = None

def main():
    functions[Modes.KECHAO] = kechao
    functions[Modes.HDXYX] = None
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
        else:
            continue
        if (player.init()): select()
    return

def select():
    while True:
        print('''>>>----------< 挂 机 菜 单 >----------<<<
1. 自动客潮(请将界面停留在餐厅)
2. 自动小游戏(尚未编写)
PS: 输入其他数字退出''')
        select = input("请输入序号: ")
        mode = None;
        if (select == "1"):
            mode = Modes.KECHAO
        elif (select == "2"):
            mode = Modes.HDXYX
        else:
            break
        run(mode)
    return

def run(mode):
    settitle("食物语挂机脚本运行中 - 按 Ctrl + C 退出")
    print("开始运行挂机脚本")
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, onclicked)
    times = 0
    while True:
        times = times + 1
        print("第 {} 次运行脚本 {}".format(times, mode))
        if not functions[mode](): break
    cv2.destroyAllWindows()
    settitle("当前挂机脚本已运行完毕 - 准备就绪")
    print("挂机脚本已运行完毕")
    return

# 以下是具体挂机逻辑, 每次调用函数都应被视作挂机一次, 返回True将会继续, 如果想退出请返回False
def kechao():    
    key = 0
    while key & 0xFF != 27:
        start = time.time()
        image = player.screenshot()
        image = cv2.resize(image, None, fx = player.factor, fy = player.factor, interpolation = cv2.INTER_CUBIC)
        cv2.imshow(WINDOW_NAME, image)
        wait = int((1 / fps - (time.time() - start)) * 1000)
        if wait < 0:
            print("严重滞后, 发生了什么让你的电脑变慢呢? 时间 {} ms".format(-wait))
            wait = 1
        key = cv2.waitKey(wait)
        
    return

def onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("点击 X: {} Y: {}".format(x, y))
        player.click(x / player.factor, y / player.factor)
    return

@atexit.register  
def onexit():
    settitle("食物语挂机脚本已结束")
    if player != None: player.end()
    print('''=============================================
食物语挂机脚本已停止运行, 感谢您的使用, 再见!
=============================================''')
    return

def setnodpi():
    try: # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # win 8.0 or less
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
