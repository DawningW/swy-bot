# coding=utf-8

import os
import ctypes
import win32api, win32gui, win32ui, win32con

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

def toscreenpos(hWnd, x, y):
    return win32gui.ClientToScreen(hWnd, (x, y))

def getcursorpos():
    return win32api.GetCursorPos()

def setcursorpos(x, y):
    return win32api.SetCursorPos((x, y))

def findwindow(parent, classname, windowname):
    hWnd = 0
    if parent == None:
        hWnd = win32gui.FindWindow(classname, windowname)
    else:
        hWnd = win32gui.FindWindowEx(parent, 0, classname, windowname)
    return hWnd

def getwindow(parent, x, y):
    if parent == None:
        return win32gui.WindowFromPoint((x, y))
    else:
        return win32gui.ChildWindowFromPoint(parent, (x, y))

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
    return bitmap.GetBitmapBits(True)

_cursorpos = None

def _storecursorpos():
    global _cursorpos
    _cursorpos = getcursorpos()
    return

def _restorecursorpos():
    setcursorpos(_cursorpos[0], _cursorpos[1])
    return

def click(hWnd, x, y, activate = True):
    _storecursorpos()
    scrpos = toscreenpos(hWnd, x, y)
    setcursorpos(scrpos[0], scrpos[1])
    pos = win32api.MAKELONG(x, y)
    if activate: win32gui.SetForegroundWindow(hWnd) # 无焦点也能点击, 为啥呢
    win32api.SendMessage(hWnd, win32con.WM_MOUSEMOVE, 0, pos)
    win32api.SendMessage(hWnd, win32con.WM_MOUSEACTIVATE, hWnd, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_LBUTTONDOWN))
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, pos)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, pos)
    _restorecursorpos()
    return
