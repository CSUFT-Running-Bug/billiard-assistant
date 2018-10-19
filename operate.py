import io
import time
import device
import cv2
import numpy as np
from PIL import Image
import bfs

# 内圆半径、外圆半径
ir, r = 70, 100
# 颜色阈值
pv1, pv2 = 220, 255
border = 10

normal, maximum, edge, f_name = device.resolution()
left_top, right_bottom = normal
left_top_m, right_bottom_m = maximum
left_top_e, right_bottom_e = edge


def draw_xp(img, p):
    px, py = p
    img[px, py, 0], img[px, py, 1], img[px, py, 2] = 0, 0, 255
    img[px, py - 1, 0], img[px, py - 1, 1], img[px, py - 1, 2] = 0, 0, 255
    img[px, py + 1, 0], img[px, py + 1, 1], img[px, py + 1, 2] = 0, 0, 255


def draw_yp(img, p):
    px, py = p
    img[px, py, 0], img[px, py, 1], img[px, py, 2] = 0, 0, 255
    img[px - 1, py, 0], img[px - 1, py, 1], img[px - 1, py, 2] = 0, 0, 255
    img[px + 1, py, 0], img[px + 1, py, 1], img[px + 1, py, 2] = 0, 0, 255


def draw_ray(img, sp, ep):
    """
    画射线。台球的反射并不是镜面反射，和碰撞时的速度有关。所以这里返回axis没什么用
    :param img: 图片
    :param sp: 起点
    :param ep: 终点
    :return: 三元组，前两位代表反射点的坐标。后一位表示法线与x轴或y轴平行
    """
    x1, y1 = sp
    x2, y2 = ep
    # 0与x轴平行，1与y轴平行
    axis = 0

    if x1 != x2 and -1 < (y1 - y2) / (x1 - x2) < 1:
        k = (y1 - y2) / (x1 - x2)
        b = (x1 * y2 - x2 * y1) / (x1 - x2)
        rx, ry = x1, y1
        if x1 < x2:
            while True:
                draw_xp(img, (rx, ry))
                rx += 1
                ry = int(k * rx + b + 0.5)
                if rx >= right_bottom[1]:
                    break
                if ry <= left_top[0] or ry >= right_bottom[0]:
                    axis = 1
                    break
        else:
            while True:
                draw_xp(img, (rx, ry))
                rx -= 1
                ry = int(k * rx + b + 0.5)
                if rx <= left_top[1]:
                    break
                if ry <= left_top[0] or ry >= right_bottom[0]:
                    axis = 1
                    break
    else:
        k = (x1 - x2) / (y1 - y2)
        b = (x2 * y1 - x1 * y2) / (y1 - y2)
        rx, ry = x1, y1
        if y1 < y2:
            while True:
                draw_yp(img, (rx, ry))
                ry += 1
                rx = int(k * ry + b + 0.5)
                if ry >= right_bottom[0]:
                    axis = 1
                    break
                if rx <= left_top[1] or rx >= right_bottom[1]:
                    break
        else:
            while True:
                draw_yp(img, (rx, ry))
                ry -= 1
                rx = int(k * ry + b + 0.5)
                if ry <= left_top[0]:
                    axis = 1
                    break
                if rx <= left_top[1] or rx >= right_bottom[1]:
                    break
    return rx, ry, axis


def center_point(x_list: list, y_list: list):
    """
    多个二维点的几何中心
    :param x_list:
    :param y_list:
    :return:
    """
    sx, sy = 0, 0
    for (x, y) in zip(x_list, y_list):
        sx += x
        sy += y
    return int(sx / len(x_list) + 0.5), int(sy / len(y_list) + 0.5)


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def beside_circle(o, r1, r2, p):
    if r1 < distance(p, o) < r2:
        return True
    return False


def final_run(data):
    start = time.time()
    # 二进制文件转图片。先用PIL.Image打开，再转opencv的图像格式，这样做比直接用opencv解码更快
    im = io.BytesIO(data)
    im = Image.open(im)
    im = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    print('图片解码：' + str(time.time() - start))

    # 裁剪图片，缩小匹配范围
    crop = im[left_top_m[1] - border:right_bottom_m[1] + border, left_top_m[0] - border:right_bottom_m[0] + border]
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    stime = time.time()
    # 匹配模板
    template = cv2.imread('templates/%s.png' % f_name, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(crop, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    # 匹配到的左上角坐标
    loc = np.where(res >= threshold)
    print('匹配：' + str(time.time() - stime))

    if len(loc[0]) != 0:
        ox = loc[0][0] + left_top_m[1] - border + w // 2
        oy = loc[1][0] + left_top_m[0] - border + h // 2

        li = []

        # 找白点
        stime = time.time()
        for i in range(ox - r, ox + r):
            for j in range(oy - r, oy + r):
                if pv1 <= im[i, j, 0] <= pv2 and pv1 <= im[i, j, 1] <= pv2 and pv1 <= im[i, j, 2] <= pv2 \
                        and left_top_m[1] < i < right_bottom_m[1] and left_top_m[0] < j < right_bottom_m[0] \
                        and beside_circle((ox, oy), ir, r, (i, j)):
                    # im[i, j, 0], im[i, j, 1], im[i, j, 2] = 0, 0, 255
                    li.append((i, j))
        print('找点：' + str(time.time() - stime))

        # 画圆
        cv2.circle(im, (oy, ox), ir, (7, 249, 151), 2)
        cv2.circle(im, (oy, ox), r, (7, 249, 151), 2)

        cv2.rectangle(im, left_top, right_bottom, (7, 249, 151), 2)
        cv2.rectangle(im, left_top_m, right_bottom_m, (200, 100, 0), 2)

        stime = time.time()
        # 找集合、画线
        for br in bfs.run(li):
            xl, yl = zip(*br)
            cp = center_point(xl, yl)
            # 画射线
            draw_ray(im, (ox, oy), cp)
            # cv2.imwrite('test.jpg', im)
        print('找集合、画线：' + str(time.time() - stime))
    else:
        print('未匹配到')
    im = im[left_top_e[1]:right_bottom_e[1], left_top_e[0]:right_bottom_e[0]]
    cv2.imshow('test', im)
    cv2.waitKey(1)
    print('总时间：' + str(time.time() - start))
    print('%.2ffps' % (1 / (time.time() - start)))
