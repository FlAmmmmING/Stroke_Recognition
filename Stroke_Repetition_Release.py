# 笔画复现较为困难
# 这里是最终发行版，一些其他的拟实现的功能放在前端交互上了
import os
import queue

import cv2
import numpy as np

# 我需要干什么？
# 1. 判断交点，将交点删去，之后剩下的非联通区域就是短笔画
# 2. 连通域染色

# 短笔画染色
# opencv三通道颜色顺序是 B, G, R
STOKE_COLOR = [[0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 255, 0], [255, 0, 255], [0, 255, 255],
               [0, 0, 128], [0, 128, 0], [128, 0, 0], [128, 128, 0], [128, 0, 128], [0, 128, 128],
               [93, 194, 56], [75, 86, 140], [194, 144, 254], [59, 194, 93]]
# q全局变量，遍历像素点
dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]


def Intersection_point_Judgement(skeleton_image, x, y):
    """
    # 用来判断这个点是否是交点
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
    intersection_point_set = []
    rows, cols = skeleton_image.shape
    for now_x in range(1, rows - 1):
        for now_y in range(1, cols - 1):
            if Intersection_point_Judgement(skeleton_image, now_x, now_y) and skeleton_image[now_x][now_y] == 255:
                skeleton_image[now_x][now_y] = 0


def Is_Start_Point(skeleton_image, now_x, now_y, visit_map):
    cnt = 0
    for x in range(now_x - 1, now_x + 2):
        for y in range(now_y - 1, now_y + 2):
            if 0 > x or x >= 80 or 0 > y or y >= 80:
                continue
            if not visit_map[x][y] and skeleton_image[x][y] == 255:
                cnt += 1
    # 算上自己应该是2个
    return cnt


def Repetition(skeleton_path, cutting_path, save_path, picture_name):
    """

    :param skeleton_path: 骨架图路径
    :param cutting_path: 原剪切图路径
    :param save_path: 保存路径
    :param picture_name: 图片名称
    :return:
    """
    skeleton_image = cv2.imread(skeleton_path + f'/{picture_name}.jpg', cv2.IMREAD_GRAYSCALE)
    original_image = cv2.imread(cutting_path + f'/{picture_name}.jpg', cv2.IMREAD_GRAYSCALE)
    skeleton_image[skeleton_image >= 100] = 255
    skeleton_image[skeleton_image < 100] = 0
    original_image[original_image >= 100] = 255
    original_image[original_image < 100] = 0
    # cv2.imshow("Skeleton Image", skeleton_image)
    # cv2.waitKey(0)

    Looking_for_Intersection_Point(skeleton_image)
    # 返回短笔画集合
    # short_stroke = Looking_for_Short_Stroke(skeleton_image)
    # 开始绘图
    stroke_picture = np.zeros([skeleton_image.shape[0], skeleton_image.shape[1]], dtype="uint8")
    for i in range(skeleton_image.shape[0]):
        for j in range(skeleton_image.shape[1]):
            if skeleton_image[i][j] == 255:
                stroke_picture[i][j] = 255
            else:
                if original_image[i][j] == 255:
                    stroke_picture[i][j] = 128
                else:
                    stroke_picture[i][j] = 0
    # print(f"这个字的短笔画数量是{len(short_stroke)}")
    # stroke_num = 0
    # # print(short_stroke)
    # for one_short_stroke in short_stroke:
    #     for (x, y) in one_short_stroke:
    #         stroke_picture[x][y] = 255
        # stroke_num += 1

    cv2.imwrite(save_path + f'/{picture_name}.jpg', stroke_picture)
    cv2.imwrite(f'static/Temp_Skeleton/{picture_name}.jpg', stroke_picture)
    # cv2.imshow("new image", stroke_picture)
    # cv2.waitKey(0)

    # return short_stroke


def start_stroke_repetition(skeleton_path, cutting_path, save_path):
    """

    :param skeleton_path: 骨架图文件夹路径
    :param cutting_path: 原剪切图文件夹路径
    :param save_path:  保存的文件夹路径
    :return:
    """
    photo_number = len(os.listdir(cutting_path))
    for i in range(photo_number):
        Repetition(skeleton_path, cutting_path, save_path, i)

#
# if __name__ == '__main__':
#     base_path = f'../data/{202110310195}'
#     cutting_path = base_path + "/Cutting"
#     skeleton_path = base_path + "/Skeleton"
#     save_path = base_path + "/Short_Skeleton"
#     photo_number = len(os.listdir(cutting_path))
#     for i in range(photo_number):
#         Repetition(skeleton_path, cutting_path, save_path, i)
