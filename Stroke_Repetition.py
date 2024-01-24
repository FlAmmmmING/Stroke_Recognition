# 这个程序用于笔画复现
# 输入一个文字的骨架以及对应的笔画编码，尝试复现出这个文字的书写过程
# 骨架生成没有什么问题，关键在于对应的笔画编码的获取，这里用到了paddleocr用来识别书法文字，对于简体字而言有不错的识别效果，但是如果是繁体字则不行
# 鉴于这个项目对于文字的书写要求只停留在初步阶段，所以暂时抛弃繁体字的识别


# 具体输入数据如下：
# 骨架图片
# ocr识别出来的文字以及这个文字的笔画顺序

# 具体输出如下：
# 这个文字的笔画书写动画

# 具体思路
# 获取这个文字的骨架的两个属性：
# 1：起始点——这个点的八领域内只有一个连续的255点
# 2：交点——这个点的八领域内有三个或三个以上不连续的255点

# 交点合并算法：设置一个较小值delta，设两个交点的坐标(x1, y1), (x2, y2)，如果有max(abs(x1 - x2), abs(y1 - y2)) <= delta，
#             则这两个交点可以视作一个交点

# 2024/1/22 蒋玮杰

import cv2
import numpy as np
from OCR_for_Stroke import Recognition_Chinese_Character
from collections import defaultdict


def Point_Judgement(stroke_img, x, y):
    """
    判断交点和起始点的八领域函数
    :param stroke_img: 骨架图
    :param x: 中心点的x
    :param y: 中心点的y
    :return:
    """
    arr = [stroke_img[x - 1][y - 1], stroke_img[x - 1][y], stroke_img[x - 1][y + 1], stroke_img[x][y + 1],
           stroke_img[x + 1][y + 1], stroke_img[x + 1][y],
           stroke_img[x + 1][y - 1], stroke_img[x][y - 1]]
    cnt = 0
    if arr[0] == arr[-1] and arr[0] == 255:
        cnt -= 1
    pre = 0
    for point in arr:
        if pre == 0 and point == 255:
            cnt += 1
        pre = point
    return cnt - 2


def Repetition_Detection(stroke_img, x, y, visit_map, val=1, jud=0):
    """
    笔画遍历实现
    :param stroke_img: 这个图像
    :param x: 具体坐标x
    :param y: 具体坐标y
    :param visit_map:
    :param val: 我要给visit_map赋的值
    :param jud: 根据visit_map的有效值判断
    :return: 八领域的某一个域——方向，下一个坐标
    """
    # 注意优先级，先是 2 4 6 8， 再是 3 5 7 9
    # 这个点我已经遍历过了
    visit_map[x][y] = val
    if stroke_img[x][y - 1] == 255 and visit_map[x][y - 1] == jud:
        return '8', (x, y - 1)
    elif stroke_img[x - 1][y] == 255 and visit_map[x - 1][y] == jud:
        return '2', (x - 1, y)
    elif stroke_img[x + 1][y] == 255 and visit_map[x + 1][y] == jud:
        return '6', (x + 1, y)
    elif stroke_img[x][y + 1] == 255 and visit_map[x][y + 1] == jud:
        return '4', (x, y + 1)
    elif stroke_img[x - 1][y - 1] == 255 and visit_map[x - 1][y - 1] == jud:
        return '9', (x - 1, y - 1)
    elif stroke_img[x + 1][y - 1] == 255 and visit_map[x + 1][y - 1] == jud:
        return '7', (x + 1, y - 1)
    elif stroke_img[x + 1][y + 1] == 255 and visit_map[x + 1][y + 1] == jud:
        return '5', (x + 1, y + 1)
    elif stroke_img[x - 1][y + 1] == 255 and visit_map[x][y + 1] == jud:
        return '3', (x - 1, y + 1)


# 重置visit_map的遍历笔画操作
def Reset_Map(begin_point_x, begin_point_y, stroke_string, visit_map, val):
    """
    :param begin_point_x: 开始的x点
    :param begin_point_y: 开始的y点
    :param stroke_string: 当前笔画顺序
    :param visit_map:
    :param val: 将要给visit_map赋的值
    :return: 没有返回
    """
    now_x = begin_point_x
    now_y = begin_point_y
    for c in stroke_string:
        if c == "2":
            now_x = now_x - 1
        elif c == "3":
            now_x = now_x - 1
            now_y = now_y + 1
        elif c == "4":
            now_y = now_y + 1
        elif c == "5":
            now_x = now_x + 1
            now_y = now_y + 1
        elif c == "6":
            now_x = now_x + 1
        elif c == "7":
            now_x = now_x + 1
            now_y = now_y - 1
        elif c == "8":
            now_y = now_y - 1
        elif c == "9":
            now_x = now_x - 1
            now_y = now_y - 1
        visit_map[now_x][now_y] = val


def Judge_Intersection(x, y, stroke_img, visit_intersection_point, visit_start_point, area, visit_map):
    """
    这个函数的作用是用于判断周围是否存在可以合并的交点
    :param stroke_img: 骨架图片
    :param visit_start_point: 起始点坐标映射
    :param x: 坐标
    :param y: 坐标
    :param visit_intersection_point: 骨架图
    :param dict: 交点 default dict
    :param area: 范围
    :return: 返回需要合并与否的数值(布尔类型)，合并路径，下一个可能的方向的元组，下一个交点坐标
    """
    ret_x = -1
    ret_y = -1
    # 直接遍历visit_intersection_point这个表即可
    for now_x, now_y in visit_intersection_point.keys():
        if now_x == x and now_y == y:
            continue
        if max(abs(now_x - x), abs(now_y - y)) <= area:
            # 找到了
            ret_x = now_x
            ret_y = now_y
            break
    # 没找到， 返回false
    if ret_x == -1 and ret_y == -1:
        return False, *False
    # 已知这两个点，如何能快速找到这个路径？
    # 根据交点的性质，只需要遍历一遍它的八邻域即可
    direction_detection = [((x - 1, y), "2"), ((x - 1, y + 1), "3"), ((x, y + 1), "4"), ((x + 1, y + 1), "5"),
                           ((x + 1, y), "6"), ((x + 1, y - 1), "7"), ((x, y - 1), "8"), ((x - 1, y - 1), "9")]
    # 交点先设置为-1
    visit_map[x][y] = -1
    for ((next_go_x, next_go_y), now_direction) in direction_detection:
        # 之前点是我开始遍历的中心点
        ret_String = now_direction
        dir_x, dir_y = next_go_x, next_go_y
        if stroke_img[dir_x][dir_y] == 0:
            continue
        while True:
            now_detection, (dir_x, dir_y) = Repetition_Detection(stroke_img,
                                                                 dir_x, dir_y,
                                                                 visit_map, 1)
            ret_String += now_detection
            # 如果这个点是起始点，说明这条路不是我们要找的路，换一个
            # 当然需要把之前遍历的点都重置为0
            if ((dir_x, dir_y) in visit_start_point) or (max(abs(dir_x - x), abs(dir_y - y)) > area):
                Reset_Map(x, y,
                          ret_String,
                          visit_map,
                          0)
                break
            # 如果遍历的点已经超过area了，就需要break
            # if max(abs(dir_x - x), abs(dir_y - y)) > area:
            #     Reset_Map(x, y,
            #               ret_String,
            #               visit_map)
            #     break
            # 如果这个点是交点？则是我要的点, 直接return
            # 返回需要合并与否的数值(布尔类型)，合并路径，合并后的这个交点可能走的路径
            if (dir_x, dir_y) == (ret_x, ret_y):
                # 将这个字符串赋值为-1
                Reset_Map(x, y,
                          ret_String,
                          visit_map,
                          -1)
                # 下一个交点相连的有效像素点的集合
                direction_detection_next = [((ret_x - 1, ret_y), "2"), ((ret_x - 1, ret_y + 1), "3"),
                                            ((ret_x, ret_y + 1), "4"),
                                            ((ret_x + 1, ret_y + 1), "5"),
                                            ((ret_x + 1, ret_y), "6"), ((ret_x + 1, ret_y - 1), "7"),
                                            ((ret_x, ret_y - 1), "8"),
                                            ((ret_x - 1, ret_y - 1), "9")]
                next_direction_possibilities = []
                for ((next_possible_x, next_possible_y), next_possible_direction) in direction_detection_next:
                    if ((visit_map[next_possible_x][next_possible_y] == 0) and
                            stroke_img[next_possible_x][next_possible_y] == 255):
                        next_direction_possibilities.append(
                            ((next_possible_x, next_possible_y), next_possible_direction))
                return True, ret_String, next_direction_possibilities, (ret_x, ret_y)


# 识别器
def Repetition(picture_name):
    pn = picture_name
    recognizer = Recognition_Chinese_Character("Pretreatment_Image/" + pn)
    stroke_repetition_str = recognizer.Recognize()[0]
    # 之后需要加入手动定制的模块
    if stroke_repetition_str == "ERROR":
        print("这个文字需要用户手动定制")
        return -1
    else:
        print("汉字：" + recognizer.Recognize()[2])
        print("笔画：" + recognizer.Recognize()[0])
    # original_image = cv2.imread("Skeleton/" + pn)
    ret, skeleton_image = cv2.threshold(cv2.imread("Skeleton/" + pn, cv2.IMREAD_GRAYSCALE), 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imshow("1", Skeleton_Image)
    # cv2.waitKey(0)
    # 起始点，交点的检测算法, 数组存储的是点的坐标
    start_point = []
    intersection_point = []
    # 记录一下起始点是否有被访问过，没有则是false
    visit_start_point = defaultdict()
    visit_intersection_point = defaultdict()
    rows, cols = skeleton_image.shape
    # 图8的大小(154, 170)
    # 交点合并区域阈值暂时设成5%
    area = int(max(rows, cols) * 0.05)
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if skeleton_image[i][j] != 255:
                continue
            continuous_substring_num = Point_Judgement(skeleton_image, i, j)
            if continuous_substring_num == 1:
                intersection_point.append((i, j))
                visit_intersection_point[(i, j)] = True
            if continuous_substring_num == -1:
                start_point.append((i, j))
                visit_start_point[(i, j)] = True

    # 展示一下算法给出的交点和起始点的位置
    # for (x, y) in start_point:
    #     original_image[x][y] = (0, 0, 255)
    # for (x, y) in intersection_point:
    #     original_image[x][y] = (0, 255, 0)
    # cv2.imwrite("Start_and_Intersection_Point.jpg", np.uint8(original_image))
    # cv2.waitKey(0)

    # 用于存放笔画，起始像素点-笔画-结束像素点
    get_stroke = []
    # visit_map是用来检测这个点是否已经被笔画遍历过了
    # visit_map数值说明: 当visit_map == 0 的时候，表示这个点没有被遍历到，
    #                   当visit_map == 1 的时候，这个点已经被遍历到了，而且这个点是笔画遍历点，之后不会再遍历了
    #                   当visit_map == -1的时候，这个点是两个交点之间的点，之后有可能再遍历到
    visit_map = np.zeros(skeleton_image.shape, dtype=int)
    # 这个图像用于遍历
    for (x, y) in start_point:
        if not visit_start_point[(x, y)]:
            continue
        visit_start_point[(x, y)] = False
        # 记录一下这个笔画
        stroke = ""
        (now_x, now_y) = (x, y)
        while True:
            now_detection, (now_x, now_y) = Repetition_Detection(skeleton_image, now_x, now_y, visit_map, 1)
            stroke += now_detection
            # 判断一下这个点是不是起始点，如果是这个笔画就成功了
            # 将这个笔画记录到get_stroke中，为了之后的进一步判断
            if (now_x, now_y) in visit_start_point:
                visit_start_point[(now_x, now_y)] = False
                get_stroke.append(((x, y), stroke, (now_x, now_y)))
                break
            # 如果这个点是交点？需要进一步的算法设计了
            if (now_x, now_y) in intersection_point:
                ret, merge_str, next_direction_possibilities, next_intersection_axis = (
                    Judge_Intersection(
                        now_x, now_y,
                        skeleton_image,
                        visit_intersection_point,
                        visit_start_point,
                        area,
                        visit_map))
                if ret:
                    # 交点合并之后,把交点笔画加到当前笔画上
                    stroke += merge_str
                    # 将交点转移
                    now_x, now_y = next_intersection_axis

                    # 接下来需要考虑以下算法: 笔画截至方案





                else:
                    # 如果交点周围没有别的交点的，这里建议是继续延续当前方向
                    # 如果没有找到合适的交点方向，则这里建议是将当前笔画设置为最终笔画
                    get_stroke.append(((x, y), stroke, (now_x, now_y)))
                    break


# 测试模块
if __name__ == '__main__':
    Repetition("8.jpg")
