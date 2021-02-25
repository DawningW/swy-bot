# coding=utf-8

import cv2

def timeToSecond(time: str) -> int:
    strs = time.split(':')
    second = int(strs[-1])
    minute = int(strs[-2]) if len(strs) > 1 else 0
    hour = int(strs[-3]) if len(strs) > 2 else 0
    return second + minute * 60 + hour * 3600

def secondToTime(second: int) -> str:
    minute = int(second / 60)
    second %= 60
    hour = int(minute / 60)
    minute %= 60
    return "%02d:%02d:%02d" % (hour, minute, second)

def readimage(name):
    return cv2.imread("./data/" + name + ".png", cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    cv2.imwrite("./saved/" + name + ".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
    return
