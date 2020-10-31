# coding=utf-8
import numpy
import cv2
import pyautogui
from ppadb.client import Client as AdbClient

import utils


class PlayerBase(object):
    """模拟玩家操作的基类"""
    def __init__(self):
        return

    def init(self):
        """执行寻找游戏等初始化操作"""
        print("正在初始化, 请稍候")
        return True

    def run(self):
        """执行挂机逻辑, 引导用户选择挂机类别并执行"""
        while True:
            print('''-----< 菜 单 >-----
1. 自动客潮(请将界面停留在餐厅)
2. 自动小游戏(尚未编写)
PS: 输入其他数字自动退出''')
            select = input("请输入序号: ")
            if (select == "1"):
                self.kechao()
            elif (select == "2"):
                pass
            else:
                break
        return

    def kechao(self):
        self.screenshot()
        return

    def end(self):
        """结束挂机"""
        cv2.destroyAllWindows()
        return

    def screenshot(self):
        return

class Player(PlayerBase):
    """模拟鼠标点击"""
    client = None

class PlayerADB(PlayerBase):
    """通过ADB控制手机"""
    device = None

    def init(self):
        super().init()
        # os.system("adb start-server")
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = []
        try:
            devices = client.devices()
        except:
            print("未检测到ADB Server, 请先启动ADB. ")
            return False
        size = len(devices)
        if size == 1:
            print("已自动选择设备: {}".format(devices[0].serial))
            self.device = devices[0]
        elif size > 1:
            for i in range():
                print("{}. {}".format(i + 1, device[i].serial))
            select = 0
            while (select < 1 or select > size):
                select = int(input("请选择设备序号: "))
            self.device = devices[select]
        else:
            print("未检测到设备, 请手动连接设备. ")
            return False
        print("已成功连接至设备 {}, 开始运行挂机脚本".format(self.device.serial))
        return True

    def screenshot(self):
        data = self.device.screencap()
        image = numpy.asarray(bytearray(data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
        cv2.imshow('img_decode',image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return
