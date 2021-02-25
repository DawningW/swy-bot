# coding=utf-8

import time
import random
import math
import numpy
import cv2
import pyautogui
import windows
from ppadb.client import Client as ADBClient
from scrcpy import ScrcpyClient
from utils import readimage, writeimage

class PlayerBase(object):
    """模拟玩家操作的基类"""
    # 游戏实际的宽度
    width = 0
    # 游戏实际的高度
    height = 0
    # 预览窗口高度
    wheight = 0
    # 预览窗口高度 / 游戏实际高度
    factor = 1.0

    def __init__(self):
        return

    def init(self):
        """执行初始化操作"""
        print("正在初始化, 请稍候")
        try:
            self.wheight = int(input("请输入预览窗口的高(默认480, 0为关闭预览): "))
        except ValueError:
            self.wheight = 480
        return True

    def end(self):
        """执行释放操作"""
        cv2.destroyAllWindows()
        return

    def calcFactor(self):
        self.factor = self.wheight / self.height
        return

    def screenshotraw(self):
        """需要子类重写"""
        return

    def screenshot(self):
        image = self.screenshotraw()
        image = cv2.resize(image, None, fx = self.factor, fy = self.factor, interpolation = cv2.INTER_AREA)
        return image

    def clickraw(self, x, y):
        """需要子类重写"""
        return

    def click(self, x, y):
        self.clickraw(x / self.factor, y / self.factor)
        return

    def clickaround(self, x, y):
        self.clickcircle(x, y, 4)
        return

    def clickcircle(self, x, y, radius):
        # 虽然不均匀, 但正是我想要的
        theta = 2 * math.pi * random.random()
        rho = radius * random.random()
        dx = rho * math.cos(theta)
        dy = rho * math.sin(theta)
        self.click(x + dx, y + dy)
        return

    def clickbetween(self, x1, y1, x2, y2):
        x, y = (x1 + x2) / 2, (y1 + y2) /2
        self.clickrect(x, y, abs(x2 - x1), abs(y2 - y1))
        return

    def clicksquare(self, x, y, length):
        dl = random.randint(-length / 2, length / 2)
        self.click(x + dl, y + dl)
        return

    def clickrect(self, x, y, width, height):
        dx = random.randint(-width / 2, width / 2)
        dy = random.randint(-height / 2, height / 2)
        self.click(x + dx, y + dy)
        return

# 腾讯手游助手后台点击可用, 并且开放ADB端口5555, 然而获取截图时失败
# 华为多屏协同疑似直接获取光标位置, 而非从消息里读取, 所以需要激活才行, 无法后台挂机
# Scrcpy后台挂机可用(已经提供对Scrcpy的原生支持, 建议使用混合模式)
WINDOWS_LIST = [
    ("TXGuiFoundation", "腾讯手游助手【极速傲引擎-7.1】"),
    ("StartupDui", "多屏协同"),
    ("SDL_app", None)
]

class Player(PlayerBase):
    """模拟鼠标点击窗口"""
    window = 0
    child = 0

    def init(self):
        super().init()
        for classname, windowname in WINDOWS_LIST:
            self.window = windows.findwindow(None, classname, windowname)
            if self.window != 0:
                if classname == WINDOWS_LIST[-1][0]:
                    print("**现已提供对Scrcpy的原生支持, 无需打开Scrcpy, 详见主菜单中的混合模式**")
                break
        if self.window == 0:
            print("无法自动获取游戏窗口, 请手动获取(可以用VS的SPY++工具获取)")
            classname = input("请输入窗口类名: ")
            windowname = input("请输入窗口标题: ")
            if classname == "": classname = None
            if windowname == "": windowname = None
            self.window = windows.findwindow(None, classname, windowname)
            if (self.window == 0):
                print("错误: 无法获取窗口句柄")
                return False
        print("已成功获取窗口句柄: {}".format(hex(self.window)))
        print("请在接下来打开的截图窗口中选择一个点以获取子窗口然后按任意键退出")
        print("若通过这种方式无法选中子窗口, 请直接在截图窗口按任意键退出并手动输入子窗口句柄")
        hwnds = [self.window, self.child]
        title = "Click a point to select child window"
        width, height = windows.getsize(self.window)
        buffer = windows.screenshot(self.window)
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image.shape = (height, width, 4)
        cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        cv2.namedWindow(title)
        cv2.setMouseCallback(title, onclicked, hwnds)
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        self.child = hwnds[1]
        if self.child == 0:
            print("遍历获取子窗口尚未编写, 请直接输入子窗口类名")
            classname = input("请输入子窗口类名: ")
            if classname != '': self.child = windows.findwindow(self.window, classname, None)
            if self.child == 0:
                print("还是失败的话请直接输入句柄吧...")
                str = input("请输入子窗口句柄(16进制): ")
                if str == '': self.child = self.window
                else: self.child = int(str, 16)
        print("已成功获取子窗口句柄: {}".format(hex(self.child)))
        self.width, self.height = windows.getsize(self.child)
        print("已获得模拟器窗口大小: {} X {}".format(self.width, self.height))
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        print("注意: 挂机时窗口可以被遮挡, 但不能最小化!!!")
        return True

    def calcFactor(self):
        # TODO DPI适配
        # 算了我写不出来, 那就别适配了= =
        # dpi = windows.getdpi(self.window)
        # self.width = int(self.width * dpi['x'] / 96)
        # self.height = int(self.height * dpi['y'] / 96)
        super().calcFactor()
        return
        
    def screenshotraw(self):
        buffer = windows.screenshot(self.child)
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image.shape = (self.height, self.width, 4)
        return image

    def clickraw(self, x, y):
        windows.click(self.child, int(x), int(y), True)
        return

class PlayerADB(PlayerBase):
    """通过ADB控制手机"""
    client = None
    device = None

    def init(self):
        super().init()
        # os.system("adb start-server")
        self.client = ADBClient(host="127.0.0.1", port=5037)
        devices = []
        try:
            print("正在检测设备...")
            devices = client.devices()
        except:
            print("无法连接至ADB Server, 请先启动ADB. ")
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
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        return True

    def screenshotraw(self):
        buffer = self.device.screencap()
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    def clickraw(self, x, y):
        self.device.input_tap(int(x), int(y))
        return

class PlayerScrcpy(PlayerBase):
    """使用Scrcpy获取截屏并模拟点击"""

    def init(self):
        super().init()
        self.client = ScrcpyClient(max_fps=30, queue_length=2)
        if not self.client.start():
            print("连接失败")
            return False
        print("已成功连接至设备 {}".format(self.client.device_name))
        self.width, self.height = self.client.resolution
        print("已获得设备屏幕尺寸: {} X {}".format(self.width, self.height))
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        return True

    def end(self):
        self.client.stop()
        super().end()
        return

    def screenshotraw(self):
        image = self.client.get_next_frame(True)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            self.lastimage = image
        return self.lastimage

    def clickraw(self, x, y):
        self.client.tap(x, y)
        return

class PlayerTest(PlayerBase):
    """图像识别测试"""
    path = None

    def init(self):
        super().init()
        self.path = input("请输入要测试的数据集路径: ")
        if self.path == "": self.path = "test"
        print("已成功读取数据集 {}".format(self.path))
        self.height, self.width = self.screenshot().shape[:2]
        print("已获得截图尺寸: {} X {}".format(self.width, self.height))
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        return True

    def screenshotraw(self):
        image = readimage(self.path)
        return image

    def clickraw(self, x, y):
        x, y = int(x), int(y)
        print("自动点击 X: {} Y: {}".format(x, y))
        time.sleep(0.01)
        return

def onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param[1] = windows.getwindow(param[0], x, y)
        print("已点击 X: {} Y: {} 窗口句柄: {}".format(x, y, hex(param[1])))
    return
