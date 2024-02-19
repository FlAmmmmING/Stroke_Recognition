# 笔画复现较为困难
# 这里试图找一个新的方法进行复现
# 把侧重点放在了短笔画提取上
# 短笔画提取难度较小

# 我需要干什么？
# 1. 判断交点，将交点删去，之后剩下的非联通区域就是短笔画
# 2. 连通域染色

import cv2
import numpy as np
from collections import defaultdict

# 短笔画染色
# opencv三通道颜色顺序是 B, G, R
STOKE_COLOR = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255),
               (0, 0, 128), (0, 128, 0), (128, 0, 0), (128, 128, 0), (128, 0, 128), (0, 128, 128)]

def Point_Judgement(skeleton_image, x, y):
    """
    :param skeleton_image: 骨架图
    :param x: 当前点的横坐标
    :param y: 当前点的纵坐标
    :return: 这个点是否是交点？
    """
    Neighbor = [skeleton_image[x - 1][y - 1], skeleton_image[x - 1][y],
                skeleton_image[x - 1][y + 1], skeleton_image[x][y + 1],
                skeleton_image[x + 1][y + 1], skeleton_image[x + 1][y],
                skeleton_image[x + 1][y - 1], skeleton_image[x][y - 1]]
    cnt = 0
    # 当且仅当——这个地方的point是255并且这个地方的点是未被遍历过的才算
    if Neighbor[0] == Neighbor[-1] and Neighbor[0] == 255:
        cnt -= 1
    pre = 0
    for point in Neighbor:
        if pre == 0 and point == 255:
            cnt += 1
        pre = point
    # >= 3 就是交点
    return cnt >= 3


def Looking_for_Intersection_Point(skeleton_image):
    """
    :param skeleton_image: 初始骨架图
    :return: 交点图，visit_map
    """
    visit_map = np.zeros_like(skeleton_image, dtype=bool)
    intersection_point_set = []
    rows, cols = skeleton_image.shape
    for now_x in range(1, rows - 1):
        for now_y in range(1, cols - 1):
            if Point_Judgement(skeleton_image, now_x, now_y) and skeleton_image[now_x][now_y] == 255:
                visit_map[now_x, now_y] = 0
                intersection_point_set.append((now_x, now_y))
    return intersection_point_set, visit_map

def Looking_for_Short_Storke(skeleton_image, intersection_point_set, visit_map):
    """

    :param skeleton_image: 骨架图
    :param intersection_point_set: 交点
    :param visit_map:
    :return:
    """
    # 去掉交点之后的起始遍历点坐标
    start_point_set = defaultdict()

def Repetition_2(folder, name):
    """
    Repetition 2
    :param folder: folder path
    :param name: name of image
    :return:
    """
    pn = name
    ret, skeleton_image = cv2.threshold(cv2.imread(folder + "/" + pn, cv2.IMREAD_GRAYSCALE), 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imshow("Skeleton Image", skeleton_image)
    # cv2.waitKey(0)

    # 用来存放短笔画的数据集
    short_stroke_set = []

    intersection_point_set, visit_map = Looking_for_Intersection_Point(skeleton_image)
    print(intersection_point_set)
    # 首先是要找交点
    # 寻找短笔画

if __name__ == '__main__':
    picture_folder = "Skeleton"
    picture_name = "8.jpg"
    Repetition_2(picture_folder, picture_name)
