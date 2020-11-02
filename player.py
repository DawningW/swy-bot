# coding=utf-8
import time
import numpy
import cv2
import pyautogui
from ppadb.client import Client as AdbClient

import utils

WINDOW_NAME = "Preview Window"

class PlayerBase(object):
    # 游戏实际的宽度
    width = 0
    # 游戏实际的高度
    height = 0
    # 预览窗口高度
    wheight = 0
    # 预览窗口高度 / 游戏实际高度
    radio = 1.0

    """模拟玩家操作的基类"""
    def __init__(self):
        return

    def init(self):
        """执行寻找游戏等初始化操作"""
        print("正在初始化, 请稍候")
        self.wheight = input("请输入预览窗口的高(0为关闭预览): ")
        # 考虑默认480?
        return True

    def run(self):
        """执行挂机逻辑, 引导用户选择挂机类别并执行"""
        while True:
            print('''-----< 菜 单 >-----
1. 自动客潮(请将界面停留在餐厅)
2. 自动小游戏(尚未编写)
PS: 输入其他数字退出''')
            select = input("请输入序号: ")
            if (select == "1"):
                self.kechao()
            elif (select == "2"):
                pass
            else:
                break
        return

    def kechao(self):
        image = self.screenshot()
        image = cv2.resize(image, None, fx = 0.5, fy = 0.5, interpolation = cv2.INTER_CUBIC)
        cv2.imshow(WINDOW_NAME, image)
        cv2.waitKey(0)
        #time.sleep(1)
        cv2.destroyAllWindows()

        # 模拟点击测试
        while True:
            x = input("X: ")
            y = input("Y: ")
            self.click(x, y)
        
        return

    def end(self):
        """结束挂机"""
        cv2.destroyAllWindows()
        return

    def calcFactor(self, length):

        return

    def screenshot(self):
        return

    def click(self, x, y):
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
            for i in range(size):
                print("{}. {}".format(i + 1, device[i].serial))
            select = 0
            while (select < 1 or select > size):
                select = int(input("请选择设备序号: "))
            self.device = devices[select - 1]
        else:
            print("未检测到设备, 请手动连接设备. ")
            return False
        print("已成功连接至设备 {}".format(self.device.serial))
        self.height, self.width = self.device.wm_size()
        print("已获得设备屏幕尺寸: {} X {}".format(self.width, self.height))
        print('''=============================================
开始运行挂机脚本''')
        return True

    def screenshot(self):
        buffer = self.device.screencap()
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    def click(self, x, y):
        self.device.input_tap(x, y)
        return

class PlayerTest(PlayerBase):
    """测试图像识别"""
    path = None

    def screenshot(self):
        image = readimage("test")
        return image

def readimage(name):
    return cv2.imread("./data/" + name + ".png", cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    cv2.imwrite("./data/screenshots/" + name + ".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
