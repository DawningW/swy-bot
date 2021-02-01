# coding=utf-8

import os
import sys
import time
import ctypes
import atexit
import cv2
from player import Player, PlayerADB, PlayerScrcpy, PlayerTest
from task import Phases, Results, tasks, registerTasks, getImageCache

WINDOW_NAME = "Preview Window"
FPS = 5

player = None
task = None

def main():
    registerTasks()
    setnodpi()
    settitle("欢迎使用食物语挂机脚本")
    print('''=============================================
食物语挂机脚本 V1.2 作者: WC
本脚本仅供个人代肝使用, 严禁用于商业用途
使用本脚本造成的一切法律纠纷由使用者自行承担
项目地址: https://github.com/DawningW/swy-bot
欢迎提交问题或是直接PR
=============================================''')
    while True:
        print('''>>>----------< 主 菜 单 >----------<<<
1. 原生模式(需先启动安卓虚拟机并打开食物语)
2. ADB模式(需手机连接电脑开启调试模式并打开食物语)
3. 混合模式(使用scrcpy快速获取手机截屏并用ADB实现模拟点击)
4. 调试模式(将读取程序目录下的test.png并进行图像识别)
8. 线性规划做菜计算器
9. 用默认浏览器打开食物语wiki
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
            player = PlayerScrcpy()
        elif str == "4":
            player = PlayerTest()
        elif str == "8":
            print("正在开发中")
            continue
        elif str == "9":
            os.system("start https://wiki.biligame.com/swy");
            continue
        else:
            continue
        if (player.init()):
            select()
            player.end()
        player = None
    return

def select():
    while True:
        print(">>>----------< 挂 机 菜 单 >----------<<<")
        for i in range(len(tasks)):
            print("{}. {}({})".format(i + 1, tasks[i].name, tasks[i].description))
        print("PS: 输入其他数字退出")
        try:
            num = int(input("请输入序号: "))
            global task
            task = tasks[num - 1]
            task.init()
            run()
        except (ValueError, IndexError):
            break
    return

def run():
    settitle("食物语挂机脚本运行中 - 按 Ctrl+C 退出")
    print("开始运行挂机脚本")
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, onclicked)
    times = 0
    canceled = False
    while not canceled:
        times += 1
        print("第 {} 次运行脚本: {}".format(times, task.name))
        phase = Phases.BEGIN
        while True:
            t = time.time()
            result = None
            if phase == Phases.BEGIN:
                result = task.begin(player)
            elif phase == Phases.RUNNING:
                result = task.run(player)
            elif phase == Phases.END:
                result = task.end(player)
            else:
                print("无效的阶段, 请向作者报告这个问题")
            if result is None or result == Results.FAIL:
                canceled = True
                break
            if result == Results.SUCCESS:
                value = phase.value + 1
                if value > Phases.END.value: break
                else: phase = Phases(value)
            showimage(getImageCache())
            wait = 1 / FPS - (time.time() - t)
            if wait < 0:
                print("严重滞后, 处理时间超出 {} ms, 发生了什么呢?".format(-int(wait * 1000)))
                wait = 0
            time.sleep(wait)
    cv2.destroyAllWindows()
    settitle("当前挂机脚本已运行完毕 - 准备就绪")
    print("挂机脚本已运行完毕")
    return

def onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("点击 X: {} Y: {}".format(x, y))
        player.click(x, y)
    return

def showimage(image, wait = 1):
    cv2.imshow(WINDOW_NAME, image)
    cv2.setMouseCallback(WINDOW_NAME, onclicked)
    cv2.waitKey(wait)
    return

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
