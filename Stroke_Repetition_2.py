# 笔画复现较为困难
# 这里试图找一个新的方法进行复现
# 把侧重点放在了短笔画提取上
# 短笔画提取难度较小
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
    visit_map = np.zeros_like(skeleton_image, dtype=bool)
    intersection_point_set = []
    rows, cols = skeleton_image.shape
    for now_x in range(1, rows - 1):
        for now_y in range(1, cols - 1):
            if Intersection_point_Judgement(skeleton_image, now_x, now_y) and skeleton_image[now_x][now_y] == 255:
                visit_map[now_x, now_y] = True
                # 为了让切割来的更顺利，这里拓展一个八邻域
                visit_map[now_x - 1: now_x + 2, now_y - 1: now_y + 2] = True
                intersection_point_set.append((now_x, now_y))
    return intersection_point_set, visit_map


def Is_Start_Point(skeleton_image, now_x, now_y, visit_map):
    cnt = 0
    for x in range(now_x - 1, now_x + 2):
        for y in range(now_y - 1, now_y + 2):
            if not visit_map[x][y] and skeleton_image[x][y] == 255:
                cnt += 1
    # 算上自己应该是2个
    return cnt == 2


def Looking_for_Start_Point(skeleton_image, now_x, now_y, visit_map):
    que = queue.Queue(0)
    que.put((now_x, now_y))
    st = np.zeros_like(skeleton_image, dtype=bool)
    st[now_x, now_y] = True
    while True:
        ret_x, ret_y = que.get()
        if Is_Start_Point(skeleton_image, ret_x, ret_y, visit_map):
            return ret_x, ret_y
        for i in range(8):
            xx = ret_x + dx[i]
            yy = ret_y + dy[i]
            if skeleton_image[xx][yy] == 255 and not st[xx][yy]:
                st[xx][yy] = True
                que.put((xx, yy))


def Looking_for_Short_Stroke(skeleton_image, visit_map):
    """
    当找到交点并且去除交点之后，将剩下的能作为起始点的点标记起来
    :param skeleton_image: 骨架图
    :param visit_map:
    :return: 返回短笔画路径, 笔画路径是一连串的像素坐标位置
    """
    short_stroke = []
    rows, cols = skeleton_image.shape
    for now_x in range(1, rows - 1):
        for now_y in range(1, cols - 1):
            if skeleton_image[now_x, now_y] == 255 and not visit_map[now_x, now_y]:
                # 寻找起始点
                start_x, start_y = Looking_for_Start_Point(skeleton_image, now_x, now_y, visit_map)
                # print(start_x, start_y)
                que = queue.Queue(0)
                que.put((start_x, start_y))
                one_short_stroke = []
                # 开始遍历短笔画
                while not que.empty():
                    lop_x, lop_y = que.get()
                    visit_map[lop_x, lop_y] = True
                    one_short_stroke.append((lop_x, lop_y))
                    for i in range(8):
                        xx, yy = lop_x + dx[i], lop_y + dy[i]
                        if skeleton_image[xx][yy] == 255 and not visit_map[xx][yy]:
                            que.put((xx, yy))
                # 太小的短笔画我不要
                if len(one_short_stroke) <= max(skeleton_image.shape) / 50:
                    continue
                short_stroke.append(one_short_stroke)
    return short_stroke


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

    intersection_point_set, visit_map = Looking_for_Intersection_Point(skeleton_image)
    # 返回短笔画集合
    short_stroke = Looking_for_Short_Stroke(skeleton_image, visit_map)
    # 开始绘图
    stroke_picture = np.zeros([skeleton_image.shape[0], skeleton_image.shape[1], 3], dtype="uint8")
    print(f"这个字的短笔画数量是{len(short_stroke)}")
    stroke_num = 0
    for one_short_stroke in short_stroke:
        for (x, y) in one_short_stroke:
            stroke_picture[x][y] = STOKE_COLOR[stroke_num]
        stroke_num += 1

    cv2.imshow("new image", stroke_picture)
    cv2.waitKey(0)


if __name__ == '__main__':
    picture_folder = "Skeleton"
    picture_name = "5.jpg"
    Repetition_2(picture_folder, picture_name)
