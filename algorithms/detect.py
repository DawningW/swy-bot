import numpy
import cv2

sift = cv2.SIFT_create()

def siftcompute(image, draw=False):
    # 转灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 计算关键点和描述符
    # key_points: 关键点信息, 包括位置, 尺度, 方向信息
    # descriptors: 关键点描述符, 每个关键点对应128个梯度信息的特征向量
    kp, des = sift.detectAndCompute(gray, None)
    if draw:
        cv2.drawKeypoints(image, kp, image, (0, 255, 0),
                        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return des

def siftsimilarity(img1, img2, threshold=0.7):
    # 计算两张图片的特征点
    des1 = siftcompute(img1)
    des2 = siftcompute(img2)
    # 构建 FLANN
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    # 比较两张图片的特征点
    matches = flann.knnMatch(des1, des2, k=2)
    if len(matches) == 0:
        return 0.0
    # 计算匹配点数并计算相似度
    good = [m for (m, n) in matches if m.distance < n.distance * threshold]
    return len(good) / len(matches)

def isimagesame(img1, img2):
    # return siftsimilarity(img1, img2, 0.7) > 0.8
    result = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    location = numpy.where(result >= 0.5)
    for pt in zip(*location[::-1]):
        return True
    return False

def findtemplate(image, template, threshold=0.75, outline=False):
    theight, twidth = template.shape[:2]
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    # result = cv2.normalize(result, None, 0, 1, cv2.NORM_MINMAX)
    location = numpy.where(result >= threshold)
    lx, ly = 0, 0
    points = []
    for pt in zip(*location[::-1]):
        x, y = pt[0] + int(twidth / 2), pt[1] + int(theight / 2)
        # 去掉重复点
        if x - lx < twidth or y - ly < theight:
            continue
        points.append((x, y))
        lx, ly = x, y
        if outline:
            cv2.rectangle(image, pt, (pt[0] + twidth, pt[1] + theight), (0, 255, 0), 1)
    return points

def findcircle(image, r, outline=False):
    gimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gimg = cv2.medianBlur(gimg, 5)
    result = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, int(r / 2), None, 100, 40, r - 10, r + 10)
    points = []
    if result is not None:
        result = numpy.uint16(numpy.around(result))
        for p in result[0, :]:
            points.append((p[0], p[1]))
            if outline:
                cv2.circle(image, (p[0], p[1]), p[2], (0, 255, 0), 1)
    return points
