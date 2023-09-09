#!/usr/bin/env python

import sys
import time
import atexit
from players import players
from tasks import tasks
try:
    import profit
except ModuleNotFoundError:
    print("线性规划做菜计算器目前尚不支持Android平台")
import utils

FPS = 10
player = None

def mainmenu():
    utils.settitle("欢迎使用食物语挂机脚本")
    print('''=============================================
食物语挂机脚本 V2.2 作者: WC
本脚本仅供个人代肝使用, 严禁用于商业用途
使用本脚本造成的一切法律纠纷由使用者自行承担
项目地址: https://github.com/DawningW/swy-bot
欢迎提交问题或者直接PR
=============================================''')
    items = [
        (),
        ("执行挂机任务", taskmenu),
        ("宏命令", macromenu),
        ("线性规划做菜计算器", profit.run),
        ("打开食物语wiki", lambda: utils.openurl("https://wiki.biligame.com/swy")),
        ("打开截图文件夹", lambda: utils.openurl("saved")),
        ("退出", lambda: sys.exit(0))
    ]
    while True:
        items[0] = ("连接至设备" if player is None else "设备已连接", playermenu)
        utils.showmenu("主菜单", items)

def androidmenu():
    def _run(Task):
        return lambda: utils.reqpermission(lambda: run(Task()))
    items = []
    for Task in tasks():
        items.append((f"{Task.name}({Task.description})", _run(Task)))
    items.append(("退出", lambda: None))
    utils.showmenu("主菜单", items)

def playermenu():
    global player
    if player is not None:
        return
    items = []
    disabled = []
    for (name, desc, Player) in players():
        if Player is not None:
            items.append((f"{name}: {desc}", Player))
        else:
            disabled.append((f"{name}\n   \033[1;33m- 由于未安装\033[1;33m{desc}\033[1;33m, 该模式无法使用\033[0m",
                            lambda: utils.throw(f"未安装{desc}")))
    items.extend(disabled)
    items.append(("返回", lambda: None))
    while True:
        try:
            player = utils.showmenu("选择模式", items)
            break
        except Exception as e:
            print(f"初始化错误: {str(e)}, 请重新选择模式")

def taskmenu():
    items = []
    for Task in tasks():
        items.append((f"{Task.name}({Task.description})", Task))
    items.append(("返回", lambda: None))
    while True:
        task = utils.showmenu("挂机菜单", items)
        if task is None:
            break
        run(task)

def macromenu():
    print("宏命令录制与执行正在开发中!")
    input("按回车键返回...")

def run(task):
    def onclicked(x, y, is_preview):
        task.clicked = (x, y)
        if is_preview:
            player.click(x, y)

    if player is None:
        playermenu()
        if player is None:
            print("尚未连接至设备, 无法执行挂机任务")
            return
    utils.settitle("食物语挂机脚本运行中 - 按 Ctrl+C 退出")
    print(f"开始运行挂机任务: {task.name}")
    utils.createpreview(onclicked)
    co = task.run(player)
    while True:
        t = time.perf_counter()
        task.frame = player.screenshot()
        try:
            co.send(None)
        except StopIteration:
            break
        utils.showpreview(task.frame)
        wait = 1 / FPS - (time.perf_counter() - t)
        if wait < 0:
            print(f"严重滞后, 处理时间超出 {-int(wait * 1000)} ms, 发生了什么呢?")
            wait = 0
        time.sleep(wait)
    utils.destroypreview()
    print("挂机任务已运行完毕")
    utils.settitle("食物语挂机脚本已运行完毕 - 准备就绪")

@atexit.register
def onexit():
    if player is not None:
        player.release()
    utils.settitle("食物语挂机脚本已退出")
    print('''
=============================================
食物语挂机脚本已停止运行, 感谢您的使用, 再见!
=============================================''')

# Android
if hasattr(utils, "Build"):
    from players import NativePlayer
    player = NativePlayer()
# 入口
if __name__ == "__main__":
    if utils.isadmin():
        try:
            mainmenu()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        utils.runasadmin(sys.executable, __file__ if len(sys.argv) >= 1 else "")
