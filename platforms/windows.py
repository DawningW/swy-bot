# coding=utf-8

import os
import ctypes
import win32api, win32gui, win32ui, win32con
import numpy
import cv2

def openurl(url):
    "打开文件/文件夹/链接"
    os.system("start " + url)
    return

def isadmin():
    "检查管理员权限"
    return True # TODO Windows下似乎不需要管理员权限
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def runasadmin(executable, argument = ""):
    "以管理员身份运行"
    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, argument, None, 1)
    return

def settitle(title):
    "设置控制台窗口标题"
    ctypes.windll.kernel32.SetConsoleTitleW(title)
    return

def getdpi(hWnd):
    hDC = win32gui.GetDC(hWnd)
    dpi = (win32ui.GetDeviceCaps(hDC, win32con.LOGPIXELSX), win32ui.GetDeviceCaps(hDC, win32con.LOGPIXELSY))
    win32gui.ReleaseDC(hWnd, hDC)
    return dpi

def setnodpi():
    try: # >= windows 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # <= windows 8.0
        ctypes.windll.user32.SetProcessDPIAware()
    return

def _toscreenpos(hWnd, x, y):
    return win32gui.ClientToScreen(hWnd, (x, y))

def _findwindow(parent, classname, windowname):
    hWnd = 0
    if parent == None:
        hWnd = win32gui.FindWindow(classname, windowname)
    else:
        hWnd = win32gui.FindWindowEx(parent, 0, classname, windowname)
    return hWnd

def _getwindow(parent, x, y):
    if parent == None:
        return win32gui.WindowFromPoint((x, y))
    else:
        return win32gui.ChildWindowFromPoint(parent, (x, y))

_WINDOWS_LIST = [
    # 腾讯手游助手后台点击可用, 并且开放ADB端口5555, 然而获取截图时失败
    ("TXGuiFoundation", "腾讯手游助手【极速傲引擎-7.1】"),
    # 华为多屏协同疑似直接获取光标位置, 而非从消息里读取, 所以需要激活才行, 无法后台挂机
    ("StartupDui", "多屏协同"),
    # Scrcpy后台挂机可用(已经提供对Scrcpy的原生支持, 建议使用混合模式)
    ("SDL_app", None)
]

def selectwindow():
    print("注意: 挂机时窗口可以被遮挡, 但不能最小化!!!")
    window = 0
    child = 0
    for classname, windowname in _WINDOWS_LIST:
        window = _findwindow(None, classname, windowname)
        if window != 0:
            if classname == _WINDOWS_LIST[-1][0]:
                print("**现已提供对Scrcpy的原生支持, 无需打开Scrcpy, 详见主菜单中的混合模式**")
            break
    if window == 0:
        print("无法自动获取游戏窗口, 请手动获取(可以用VS的SPY++工具获取)")
        str = input("请输入窗口类名: ")
        classname = str if str != "" else None
        str = input("请输入窗口标题: ")
        windowname = str if str != "" else None
        window = _findwindow(None, classname, windowname)
        if window == 0:
            print("错误: 无法获取窗口句柄")
            return -1
    print("已成功获取窗口句柄: {}".format(hex(window)))
    print("请在接下来打开的截图窗口中选择一个点以获取子窗口然后按任意键退出")
    print("若通过这种方式无法选中子窗口, 请直接在截图窗口按任意键退出并手动输入子窗口句柄")
    title = "Click a point to select child window"
    hwnds = [window, child]
    width, height = getsize(window)
    buffer = screenshot(window)
    image = numpy.frombuffer(buffer, dtype = "uint8")
    image.shape = (height, width, 4)
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, _onclicked, hwnds)
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    child = hwnds[1]
    if child == 0:
        print("遍历获取子窗口尚未编写, 请直接输入子窗口类名")
        classname = input("请输入子窗口类名: ")
        if classname != '': child = _findwindow(window, classname, None)
        if child == 0:
            print("还是失败的话请直接输入句柄吧...")
            str = input("请输入子窗口句柄(16进制): ")
            if str == '': child = window
            else: child = int(str, 16)
    print("已成功获取子窗口句柄: {}".format(hex(child)))
    return child

def _onclicked(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param[1] = _getwindow(param[0], x, y)
        print("已点击 X: {} Y: {} 窗口句柄: {}".format(x, y, hex(param[1])))
    return

def getsize(hWnd):
    left, top, right, bottom = win32gui.GetClientRect(hWnd)
    return (right - left, bottom - top)

def screenshot(hWnd):
    width, height = getsize(hWnd)
    # 返回句柄窗口的设备环境，仅包括客户区
    hDC = win32gui.GetDC(hWnd)
    # 创建设备描述表
    mfcDC = win32ui.CreateDCFromHandle(hDC)
    # 创建内存设备描述表
    memDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象准备保存图片
    bitmap = win32ui.CreateBitmap()
    # 为bitmap开辟存储空间
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    # 将截图保存到bitmap中
    memDC.SelectObject(bitmap)
    # 保存bitmap到内存设备描述表
    memDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    # 释放设备环境
    # mfcDC.DeleteDC()
    # memDC.DeleteDC()
    win32gui.ReleaseDC(hWnd, hDC)
    # win32gui.DeleteObject(bitmap.GetHandle())
    # 获取位图信息
    buffer = bitmap.GetBitmapBits(True)
    # 转换为图片
    image = numpy.frombuffer(buffer, dtype = "uint8")
    image.shape = (self.height, self.width, 4)
    return image

def _getcursorpos():
    return win32api.GetCursorPos()

def _setcursorpos(x, y):
    return win32api.SetCursorPos((x, y))

_cursorpos = None

def _storecursorpos():
    global _cursorpos
    _cursorpos = _getcursorpos()
    return

def _restorecursorpos():
    _setcursorpos(_cursorpos[0], _cursorpos[1])
    return

def click(hWnd, x, y, activate = True):
    _storecursorpos()
    scrpos = _toscreenpos(hWnd, x, y)
    _setcursorpos(scrpos[0], scrpos[1])
    pos = win32api.MAKELONG(x, y)
    if activate: win32gui.SetForegroundWindow(hWnd) # 无焦点也能点击, 为啥呢
    win32api.SendMessage(hWnd, win32con.WM_MOUSEMOVE, 0, pos)
    win32api.SendMessage(hWnd, win32con.WM_MOUSEACTIVATE, hWnd, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_LBUTTONDOWN))
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, pos)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, pos)
    _restorecursorpos()
    return
