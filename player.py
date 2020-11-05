# coding=utf-8
import numpy
import cv2
import pyautogui
from ppadb.client import Client as ADBClient
import utils

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
        """结束挂机"""
        cv2.destroyAllWindows()
        return

    def calcFactor(self):
        self.factor = self.wheight / self.height
        return

    def screenshot(self):
        return

    def click(self, x, y):
        return

class Player(PlayerBase):
    """模拟鼠标点击窗口"""
    window = 0
    child = 0

    def init(self):
        super().init()
        windows = [("TXGuiFoundation", "腾讯手游助手【极速傲引擎-7.1】"), ("StartupDui", "多屏协同")]# 
        for (classname, windowname) in windows:
             self.window = utils.findwindow(None, classname, windowname)
             if self.window != 0: break
        if self.window == 0:
            print("无法自动获取游戏窗口, 请手动获取(可以用VS的SPY++工具获取)")
            classname = input("请输入窗口类名: ")
            windowname = input("请输入窗口标题: ")
            if classname == "": classname = None
            if windowname == "": windowname = None
            self.window = utils.findwindow(None, classname, windowname)
            if (self.window == 0):
                print("错误: 无法获取窗口句柄")
                return False
        print("已成功获取窗口句柄: {}".format(hex(self.window)))
        print("请在接下来打开的截图窗口中选择一个点以获取子窗口然后按任意键退出")
        print("若通过这种方式无法选中子窗口, 请直接在截图窗口按任意键退出并手动输入子窗口句柄")
        title = "Click a point to select child window"
        width, height = utils.getsize(self.window)
        buffer = utils.screenshot(self.window)
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image.shape = (height, width, 4)
        cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        cv2.namedWindow(title)
        cv2.setMouseCallback(title, onclicked, [self.window])
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        self.child = Temp
        if self.child == 0:
            print("遍历获取子窗口尚未编写, 请直接输入子窗口类名")
            classname = input("请输入子窗口类名: ")
            if classname != '': self.child = utils.findwindow(self.window, classname, None)
            if self.child == 0:
                print("还是失败的话请直接输入句柄吧...")
                str = input("请输入子窗口句柄(16进制): ")
                if str == '': self.child = self.window
                else: self.child = int(str, 16)
        print("已成功获取子窗口句柄: {}".format(hex(self.child)))
        self.width, self.height = utils.getsize(self.child)
        print("已获得模拟器窗口大小: {} X {}".format(self.width, self.height))
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        print("注意: 挂机时窗口可以被遮挡, 但不能最小化!!!")
        return True

    def calcFactor(self):
        # TODO DPI适配
        # 算了我写不出来, 那就别适配了= =
        # dpi = utils.getdpi(self.window)
        # self.width = int(self.width * dpi['x'] / 96)
        # self.height = int(self.height * dpi['y'] / 96)
        super().calcFactor()
        return
        
    def screenshot(self):
        buffer = utils.screenshot(self.child)
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image.shape = (self.height, self.width, 4)
        cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        return image

    def click(self, x, y):
        utils.click(self.child, int(x), int(y))
        return

class PlayerADB(PlayerBase):
    """通过ADB控制手机"""
    server = None
    device = None

    def init(self):
        super().init()
        # os.system("adb start-server")
        client = ADBClient(host="127.0.0.1", port=5037)
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

    def screenshot(self):
        buffer = self.device.screencap()
        image = numpy.frombuffer(buffer, dtype = "uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    def click(self, x, y):
        self.device.input_tap(int(x), int(y))
        return

class PlayerTest(PlayerBase):
    """测试图像识别"""
    path = None

    def init(self):
        super().init()
        self.path = input("请输入要测试的数据集路径: ")
        if self.path == "": self.path = "test"
        print("已成功读取数据集 {}".format(self.path))
        self.height, self.width = self.screenshot().shape
        print("已获得截图尺寸: {} X {}".format(self.width, self.height))
        self.calcFactor()
        print("已计算缩放因子: {}".format(self.factor))
        return True

    def screenshot(self):
        image = readimage(self.path)
        return image

def readimage(name):
    return cv2.imread("./data/" + name + ".png", cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    cv2.imwrite("./data/screenshots/" + name + ".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
    return

Temp = 0
def onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global Temp
        Temp = utils.getwindow(param[0], x, y)
        print("已点击 X: {} Y: {} 窗口句柄: {}".format(x, y, hex(Temp)))
    return
