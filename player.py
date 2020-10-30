# coding=utf-8

class PlayerBase(object):
    """模拟玩家操作的基类"""
    def init(self):
        print("正在初始化, 请稍候")
        return

    def run(self):
        return

    def end(self):
        return

class Player(PlayerBase):
    """模拟鼠标点击"""

class PlayerADB(PlayerBase):
    """通过ADB控制手机"""

