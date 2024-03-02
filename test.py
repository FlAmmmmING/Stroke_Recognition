# 这个文件用来测试一些python代码的实用性\
import math
import queue

import cv2
import numpy as np


def get_radius(dir_x, dir_y, original_img, core):
    """
    确定半径大小
    :param dir_x: 方向
    :param dir_y: 方向
    :param original_img: 原始图片
    :param core: 圆心坐标
    :return: 返回半径
    """
    # 备案1 —— 八个方向取最小值确定半径
    # 这种方法较为稳定，但是缺点是可能会使得一些笔画无法覆盖
    # radius = 100000000
    # iter_x, iter_y = item[i]
    # radius_x, radius_y = 0, 0
    # tep_radius = 0
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_y -= 1
    # radius = min(radius, tep_radius)
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_y += 1
    # radius = min(radius, tep_radius)
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x -= 1
    # radius = min(radius, tep_radius)
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x += 1
    # radius = min(radius, tep_radius)
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x -= 1
    #     iter_y -= 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x += 1
    #     iter_y += 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x -= 1
    #     iter_y += 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    # tep_radius = 0
    # iter_x, iter_y = item[i]
    # while original_img[iter_x, iter_y] == 0:
    #     tep_radius += 1
    #     iter_x += 1
    #     iter_y -= 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))

    # 备案2 —— 按照轨迹方向确定半径
    # 这种方法较为冒险，可能会出现笔画崩溃的现象，但是它有良好的覆盖性
    radius_x = 0
    radius_y = 0
    iter_x, iter_y = core
    # 开始计算半径
    if dir_y == 0:
        # 寻找 y = 0 这条线
        # 先找左边
        while original_img[iter_x][iter_y] == 0:
            radius_x += 1
            iter_y -= 1
        iter_x, iter_y = core
        # 再找右边
        while original_img[iter_x][iter_y] == 0:
            radius_y += 1
            iter_y += 1
    elif dir_x == 0:
        # 寻找 x = 0 这条线
        # 先找上边
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
        iter_x, iter_y = core
        # 再找下边
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
    elif dir_x * dir_y == -1:
        # 寻找 x + y = 0 这条线
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
            iter_y -= 1
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y += 1
    else:
        # 寻找x - y = 0 这条边
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
            iter_y += 1
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y -= 1
    radius = min(radius_x, radius_y)
    if dir_x * dir_y:
        radius = round(radius * 1.4142135623730951)
    return radius


def generate_fps(template_img, original_img, Stroke, Save_dir):
    """
    :param template_img: 空白模板
    :param original_img: 原图
    :param Stroke: 笔画
    :return:
    """
    # 用来存储图片编号的，以便接下来合成视频
    """
            这里整理一下(dir_x, dir_y)的取值对八邻域的关系
            (dir_x, dir_y) == (0, 1) 或者 (0, -1) 则半径的选取为 x = 0 这条直线
            (dir_x, dir_y) == (1, 0) 或者 (-1, 0) 则半径的选取为 y = 0 这条直线
            (dir_x, dir_y) == (1, 1) 或者 (-1, -1) 则半径的选取为 y = x 这条直线
            (dir_x, dir_y) == (1, -1) 或者 (-1, 1) 则半径的选取为 y = -x 这条直线
            半径的长度如此定义 -> 沿着直线寻找两个端点，寻找最近的一个端点距离圆心的位移距离作为这个圆的半径
    """
    cnt = 0
    iter_img = template_img.copy()

    # 广度优先遍历队列
    q = queue.Queue()
    dx = [1, -1, 0, 0]
    dy = [0, 0, -1, 1]

    for item in Stroke:
        for i in range(1, len(item)):
            visit_map = np.zeros_like(original_img, dtype=bool)
            dir_x, dir_y = item[i][0] - item[i - 1][0], item[i][1] - item[i - 1][1]
            radius = get_radius(dir_x, dir_y, original_img, item[i])
            print(f"圆心：({item[i][0]}, {item[i][1]}), 半径: {radius}")
            # 开始分帧
            cnt += 1
            # 接下来的问题是，确定了圆心和半径，如何绘制圆
            # 一种妥协的方式： 广度优先搜索， 时间复杂度较低
            q.put(item[i])
            visit_map[item[i][0], item[i][1]] = True
            while not q.empty():
                now_x, now_y = q.get()
                # distance = round(math.sqrt(pow(now_x - item[i][0], 2) + pow(now_y - item[i][1], 2)))
                # if distance > radius:
                #     continue
                iter_img[now_x, now_y] = (0, 0, 0)
                for j in range(4):
                    next_x = now_x + dx[j]
                    next_y = now_y + dy[j]
                    if original_img[next_x, next_y] == 255 or visit_map[next_x, next_y] or \
                            round(math.sqrt(pow(next_x - item[i][0], 2) + pow(next_y - item[i][1], 2))) > radius:
                        continue
                    q.put((next_x, next_y))
                    visit_map[next_x, next_y] = True
            cv2.imwrite(Save_dir + "/" + f"{cnt}.jpg", iter_img)


def generate_video(picture_folder, ret_folder):
    """

    :param picture_folder: 图片保存的文件夹
    :param ret_folder: 视频保存点
    :return: 返回视频
    """
    video_size = cv2.imread(picture_folder + "/1.jpg", cv2.COLOR_BGR2GRAY).shape
    # 视频帧数
    fps = 30
    video = cv2.VideoWriter(ret_folder + "\\video.avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
                            video_size)
    for item in picture_folder:
        img = cv2.imread(item)
        video.write(img)

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    Stroke = [
        [(3, 77), (4, 78), (5, 79), (6, 80), (6, 81), (7, 82), (8, 83), (9, 84), (10, 85), (11, 86), (12, 87), (13, 88),
         (14, 88), (15, 89), (16, 89), (17, 90), (18, 90), (19, 90), (20, 90), (21, 90), (22, 90), (23, 90), (24, 90),
         (25, 90), (26, 90), (27, 90), (28, 90), (29, 90), (30, 90), (31, 90), (32, 90), (33, 90), (34, 90), (35, 90),
         (36, 90), (37, 90), (38, 90), (39, 90), (40, 90), (41, 90)],
        [(44, 93), (44, 94), (45, 95), (45, 96), (45, 97), (45, 98), (45, 99), (45, 100), (45, 101), (45, 102),
         (45, 103), (45, 104), (45, 105), (45, 106), (44, 107), (44, 108), (44, 109), (45, 110), (45, 111), (45, 112),
         (45, 113), (45, 114)],
        [(50, 86), (50, 85), (50, 84), (51, 83), (51, 82), (51, 81), (51, 80), (51, 79), (51, 78), (51, 77), (51, 76),
         (51, 75), (52, 74), (52, 73), (52, 72), (52, 71), (53, 70), (53, 69), (53, 68), (53, 67), (53, 66), (52, 65),
         (52, 64), (53, 63), (53, 62), (53, 61), (53, 60), (53, 59), (53, 58), (53, 57)],
        [(52, 89), (53, 89), (54, 89), (55, 89), (56, 89), (57, 89), (58, 89), (59, 89), (60, 89), (61, 89), (62, 89),
         (63, 89), (64, 89), (65, 89), (66, 89), (67, 89), (68, 89), (69, 89), (70, 89), (71, 89), (72, 89), (73, 89),
         (74, 89), (75, 89), (76, 89), (77, 89), (78, 89), (79, 89), (80, 89), (81, 89), (82, 89)],
        [(84, 154), (84, 153), (84, 152), (83, 151), (82, 150), (82, 149), (81, 148), (81, 147), (81, 146), (81, 145),
         (81, 144), (81, 143), (81, 142), (81, 141), (81, 140), (81, 139), (81, 138), (81, 137), (81, 136), (81, 135),
         (81, 134), (81, 133), (81, 132), (81, 131), (81, 130), (82, 129), (82, 128), (82, 127), (82, 126), (82, 125),
         (82, 124), (83, 123), (83, 122), (83, 121), (83, 120), (83, 119), (83, 118), (83, 117), (83, 116), (83, 115),
         (83, 114), (83, 113), (83, 112), (83, 111), (83, 110), (84, 109), (84, 108), (84, 107), (84, 106), (84, 105),
         (84, 104), (84, 103), (84, 102), (84, 101), (84, 100), (84, 99), (84, 98), (84, 97), (84, 96), (84, 95),
         (84, 94), (84, 93), (84, 92), (84, 91)],
        [(87, 82), (87, 81), (87, 80), (87, 79), (88, 78), (88, 77), (88, 76), (88, 75), (88, 74), (88, 73), (88, 72),
         (88, 71), (88, 70), (88, 69), (88, 68), (89, 67), (89, 66), (89, 65), (89, 64), (89, 63), (89, 62), (89, 61),
         (89, 60), (90, 59), (90, 58), (90, 57), (90, 56), (90, 55), (90, 54), (91, 53), (91, 52), (91, 51), (92, 50),
         (92, 49), (92, 48), (93, 47), (93, 46), (93, 45), (93, 44), (94, 43), (94, 42), (94, 41), (94, 40), (95, 39),
         (95, 38), (95, 37), (95, 36), (95, 35), (96, 34), (96, 33), (96, 32), (96, 31), (97, 30), (97, 29), (98, 28),
         (98, 27), (98, 26), (98, 25), (98, 24), (99, 23), (99, 22), (99, 21), (99, 20), (98, 19), (98, 18), (98, 17),
         (97, 16), (97, 15), (96, 14)],
        [(90, 84), (91, 84), (92, 84), (93, 84), (94, 84), (95, 84), (96, 84), (97, 84), (98, 84), (99, 84), (100, 84),
         (101, 84), (102, 84), (103, 84), (104, 84), (105, 83), (106, 82), (106, 81), (106, 80), (107, 79), (108, 78),
         (109, 77), (110, 76), (111, 75), (112, 74), (113, 73), (114, 72), (115, 71), (116, 70), (117, 69), (118, 68),
         (119, 68), (120, 67), (121, 66), (122, 65), (123, 65), (124, 65), (125, 65), (126, 64), (127, 64), (128, 63),
         (129, 63), (130, 63), (131, 63), (132, 63), (133, 63)],
        [(108, 109), (109, 110), (110, 111), (111, 112), (112, 113), (113, 114), (114, 114), (115, 115), (116, 115),
         (117, 116), (118, 116)],
        [(121, 119), (122, 120), (123, 121), (124, 122), (125, 123), (126, 124), (127, 125), (128, 126), (129, 127),
         (130, 127), (131, 127), (132, 128), (133, 128), (134, 129), (135, 129), (136, 130), (137, 130), (138, 130)],
        [(122, 115), (123, 114), (123, 113), (123, 112), (123, 111), (123, 110), (123, 109), (124, 108), (124, 107),
         (125, 106), (125, 105), (125, 104), (125, 103), (125, 102), (125, 101), (125, 100), (126, 99), (126, 98),
         (126, 97), (127, 96), (127, 95), (127, 94), (128, 93), (128, 92), (128, 91), (129, 90), (129, 89), (129, 88),
         (129, 87), (130, 86), (130, 85), (130, 84), (130, 83), (131, 82), (131, 81), (131, 80), (132, 79), (132, 78),
         (133, 77), (133, 76), (133, 75), (133, 74), (133, 73), (134, 72), (134, 71), (134, 70), (134, 69), (134, 68),
         (135, 67), (135, 66)],
        [(137, 63), (138, 62), (139, 61), (140, 60), (140, 59), (140, 58), (140, 57), (140, 56), (140, 55), (139, 54),
         (139, 53), (139, 52), (139, 51), (139, 50), (138, 49)]]
    One_Stroke_for_test = [[(3, 77), (4, 78), (5, 79), (6, 80), (6, 81), (7, 82), (8, 83), (9, 84), (10, 85), (11, 86), (12, 87), (13, 88),
         (14, 88), (15, 89), (16, 89), (17, 90), (18, 90), (19, 90), (20, 90), (21, 90), (22, 90), (23, 90), (24, 90),
         (25, 90), (26, 90), (27, 90), (28, 90), (29, 90), (30, 90), (31, 90), (32, 90), (33, 90), (34, 90), (35, 90),
         (36, 90), (37, 90), (38, 90), (39, 90), (40, 90), (41, 90)]]
    img = cv2.imread('cutting/8.jpg', cv2.COLOR_BGR2GRAY)
    img[img < 100] = 0
    img[img >= 100] = 255
    rows, cols = img.shape
    ret_img = np.zeros((rows, cols, 3), dtype=np.uint8)
    ret_img.fill(255)
    for item in Stroke:
        for (x, y) in item:
            ret_img[x][y] = [93, 194, 56]
    Save_dir = "folder_for_testing"
    Save_dir_video = "folder_for_video"
    generate_fps(ret_img, img, One_Stroke_for_test, Save_dir)
    # generate_video(Save_dir, Save_dir_video)
    # cv2.imwrite("test.jpg", ret_img)
    # cv2.imshow('img', ret_img)
    # cv2.waitKey(0)
