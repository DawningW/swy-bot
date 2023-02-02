import cv2

def showmenu(title, items):
    print(f">>>----------< {title} >----------<<<")
    for i in range(len(items)):
        print(f"{i + 1}. {items[i][0]}")
    while True:
        select = -1
        try:
            s = input("请选择: ")
            if s == "":
                continue
            select = int(s) - 1
        except ValueError:
            pass
        if select >= 0 and select < len(items):
            return items[select][1]()
        print("输入的选项无效, 请重新输入!")

_WINDOW_NAME = "Preview Window"
_onclicked = None

def _callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"点击 X: {x} Y: {y}")
        if _onclicked is not None:
            _onclicked(x, y, True)

def createpreview(onclicked):
    global _onclicked
    _onclicked = onclicked
    cv2.namedWindow(_WINDOW_NAME)
    cv2.setMouseCallback(_WINDOW_NAME, _callback)

def showpreview(image, wait=1):
    cv2.imshow(_WINDOW_NAME, image)
    cv2.setMouseCallback(_WINDOW_NAME, _callback)
    cv2.waitKey(wait)

def destroypreview():
    global _onclicked
    cv2.destroyWindow(_WINDOW_NAME)
    _onclicked = None

def readimage(name):
    return cv2.imread("./data/" + name + ".png", cv2.IMREAD_UNCHANGED)

def writeimage(name, image):
    return cv2.imwrite("./saved/" + name + ".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
