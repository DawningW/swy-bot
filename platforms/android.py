import os
import time
import numpy
import cv2
from java.lang import Thread, InterruptedException
from kongsang.swybot import ScriptBridge

def openurl(url):
    ScriptBridge.openUrl(url)

def isadmin():
    return True

def runasadmin(executable, argument=""):
    pass

def settitle(title):
    pass

def selectwindow():
    return ScriptBridge.getService()

def getsize(service):
    return service.getScreenSize()

def getdpi(service):
    return service.getScreenDpi()

def screenshot(service):
    width, height = getsize(service)
    while True:
        if Thread.interrupted():
            raise InterruptedException()
        buffer = service.captureScreen()
        if buffer is not None:
            break
    image = numpy.array(buffer, dtype="uint8")
    image.shape = (height, width, 4)
    return image

def click(service, x, y):
    service.tap(x, y)

def reqpermission(callback):
    ScriptBridge.requestRecord(callback)

def showmenu(title, items):
    texts = [item[0] for item in items]
    ScriptBridge.showMenu(title, texts, lambda select: items[select][1]())

_onclicked = None

def _callback(x, y):
    print(f"点击 X: {x} Y: {y}")
    if _onclicked is not None:
        _onclicked(x, y, False)

def createpreview(onclicked):
    global _onclicked
    _onclicked = onclicked

def showpreview(image, wait=1):
    pass

def destroypreview():
    pass

def readimage(name):
    filepath = os.path.join(os.path.dirname(__file__), "../data/" + name + ".png")
    return cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    filepath = ScriptBridge.getStoragePath() + "/temp.png"
    if cv2.imwrite(filepath, image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3]):
        ret = ScriptBridge.saveToAlbum(filepath, name + ".png")
        os.remove(filepath)
        return ret
    return False
