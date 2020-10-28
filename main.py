# coding=utf-8

import sys
import ctypes
import cv2

def main():
    print("食物语挂机脚本 版本V1.0")
    print("请选择 1.原生模式 2.ADB模式")
    input(">> ")
    return

def isadmin():
    "检查管理员权限"
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 入口
if __name__ == "__main__":
    # 检查权限
    if isadmin():
        main()
    else:
        if len(sys.argv) >= 2 and sys.argv[1] == "debug":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__ + " debug", None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)