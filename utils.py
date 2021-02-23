# coding=utf-8

import cv2

def readimage(name):
    return cv2.imread("./data/" + name + ".png", cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    cv2.imwrite("./saved/" + name + ".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
    return
