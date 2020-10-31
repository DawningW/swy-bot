# coding=utf-8

import os
import sys
import ctypes
import atexit

from player import Player, PlayerADB

player = None

def main():
    settitle("欢迎使用食物语挂机脚本")
    print('''=============================================
食物语挂机脚本 V1.0 作者: WC
本脚本仅供个人代肝使用, 严禁用于商业用途
使用本脚本造成的一切法律纠纷由使用者自行承担
项目地址: https://github.com/DawningW/swy-bot
欢迎提交问题或是直接PR
=============================================''')
    while True:
        print('''-----< 菜 单 >-----
1. 原生模式(需先启动安卓虚拟机并打开食物语)
2. ADB模式(需手机连接电脑打开调试模式并打开食物语)
0. 退出''')
        str = input("请选择: ")
        if str == "0":
            break
        if str == "1":
            player = Player()
        elif str == "2":
            player = PlayerADB()
        else:
            continue
        settitle("食物语挂机脚本运行中 - 按 Ctrl + C 退出")
        if (player.init()): player.run()
    return

@atexit.register  
def onexit():
    settitle("食物语挂机脚本已结束")
    if player != None: player.end()
    print('''
=============================================
食物语挂机脚本已停止运行, 感谢您的使用, 再见!
=============================================''')

def settitle(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def isadmin():
    "检查管理员权限"
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 入口
if __name__ == "__main__":
    # 检查权限
    # isadmin()
    if True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        if len(sys.argv) >= 2 and sys.argv[1] == "debug":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__ + " debug", None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
