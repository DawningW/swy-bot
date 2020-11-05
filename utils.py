# coding=utf-8

import win32api, win32gui, win32ui, win32con

def getdpi(hWnd):
    hDC = win32gui.GetDC(hWnd)
    dpi = (win32ui.GetDeviceCaps(hDC, win32con.LOGPIXELSX), win32ui.GetDeviceCaps(hDC, win32con.LOGPIXELSY))
    win32gui.ReleaseDC(self.window, hDC)
    return dpi

def toscreenpos(hWnd, x, y):
    return win32gui.ClientToScreen(hWnd, (x, y))

def getcursorpos():
    return win32api.GetCursorPos()

def setcursorpos(x, y):
    return win32api.SetCursorPos((x, y))

CursorPos = None

def storecursorpos():
    global CursorPos
    CursorPos = getcursorpos()
    return

def restorecursorpos():
    setcursorpos(CursorPos[0], CursorPos[1])
    return

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
    win32gui.ReleaseDC(hWnd, hDC)
    # 获取位图信息
    return bitmap.GetBitmapBits(True)

def click(hWnd, x, y, activate = False):
    storecursorpos()
    scrpos = toscreenpos(hWnd, x, y)
    setcursorpos(scrpos[0], scrpos[1])
    pos = win32api.MAKELONG(x, y)
    if activate: win32gui.SetForegroundWindow(hWnd) # 无焦点也能点击, 为啥呢
    win32api.SendMessage(hWnd, win32con.WM_MOUSEMOVE, 0, pos)
    win32api.SendMessage(hWnd, win32con.WM_MOUSEACTIVATE, hWnd, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_LBUTTONDOWN))
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, pos)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, pos)
    restorecursorpos()
    return

