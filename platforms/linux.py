import os
import pyautogui
import numpy
import cv2

def openurl(url):
    os.system("xdg-open " + url)

def isadmin():
    return True

def runasadmin(executable, argument=""):
    print("请以管理员身份运行此程序")

def settitle(title):
    os.system(rf'echo -ne "\033]0;{title}\007"')

def selectwindow():
    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            param.append((x, y))
            print(f"已选择点 {len(param)} X: {x} Y: {y}")
            if len(param) == 2:
                cv2.destroyAllWindows()
    print("注意: 挂机时窗口不能移动, 不能被遮挡也不能最小化!!!")
    print("请在接下来打开的截图窗口中选择两个点以选择窗口")
    title = "Click two points to select window"
    points = []
    image = numpy.asarray(pyautogui.screenshot())
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, callback, points)
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if len(points) < 2:
        print("错误: 未选中两个点, 无法获取窗口")
        return None
    return points

def getsize(window):
    x1, y1 = window[0]
    x2, y2 = window[1]
    return x2 - x1, y2 - y1

def getdpi(window):
    return 96

def screenshot(window):
    left, top = window[0]
    width, height = getsize(window)
    image = pyautogui.screenshot(region=(left, top, width, height))
    image = numpy.asarray(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
    return image

def click(window, x, y):
    x1, y1 = window[0]
    pyautogui.click(x1 + x, y1 + y)
