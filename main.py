import cv2
import numpy as np
import time
import bfs
from PIL import ImageGrab

r = 100


def drawline(x: list, y: list):
    k = np.polyfit(x, y, 1)[0]
    b = np.polyfit(x, y, 1)[1]

    for i in range(height):
        j = int(k * i + b)
        if 0 < j - 1 and j + 1 < width:
            im[i, j + 1, 0] = 0
            im[i, j + 1, 1] = 0
            im[i, j + 1, 2] = 255
            im[i, j - 1, 0] = 0
            im[i, j - 1, 1] = 0
            im[i, j - 1, 2] = 255
            im[i, j, 0] = 0
            im[i, j, 1] = 0
            im[i, j, 2] = 255


rect = (0, 0, 1920, 1080)
while True:
    start = time.time()
    ImageGrab.grab(rect).save('screenshot.png')
    print(time.time() - start)

    im = cv2.imread('screenshot.png')
    im1 = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    width, height = im1.shape[::-1]
    template = cv2.imread('t1.png', 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(im1, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    loc = np.where(res >= threshold)
    if len(loc[0]) == 0:
        print('没有')
        continue
    print(loc)
    ww = loc[0][0] + w // 2 - r
    hh = loc[1][0] + h // 2 - r

    li = []

    for i in range(ww, ww + 2 * r):
        for j in range(hh, hh + 2 * r):
            if im[i, j, 0] == 255 and im[i, j, 1] == 255 and im[i, j, 2] == 255:
                im[i, j, 0] = 0
                im[i, j, 1] = 0
                im[i, j, 2] = 255
                li.append((i, j))
    # for pt in zip(*loc[::-1]):
    #     pt = (pt[0] + h // 2 - r, pt[1] + w // 2 - r)
    #     cv2.rectangle(im, pt, (pt[0] + 2 * r, pt[1] + 2 * r), (7, 249, 151), 2)

    for br in bfs.run(li):
        x, y = zip(*br)
        drawline(x, y)

    cv2.imshow('Detected', im)
    cv2.waitKey(1)
