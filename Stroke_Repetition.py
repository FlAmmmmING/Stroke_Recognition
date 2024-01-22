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


# 判断交点和起始点的八领域函数
def Point_Judgement(img, x, y):
    arr = [img[x - 1][y - 1], img[x - 1][y], img[x - 1][y + 1], img[x][y + 1], img[x + 1][y + 1], img[x + 1][y], img[x + 1][y - 1], img[x][y - 1]]
    cnt = 0
    if arr[0] == arr[-1] and arr[0] == 255:
        cnt -= 1
    pre = 0
    for point in arr:
        if pre == 0 and point == 255:
            cnt += 1
        pre = point
    return cnt - 2


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
    original_image = cv2.imread("Skeleton/" + pn)
    ret, skeleton_image = cv2.threshold(cv2.imread("Skeleton/" + pn, cv2.IMREAD_GRAYSCALE), 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imshow("1", Skeleton_Image)
    # cv2.waitKey(0)
    # 起始点，交点的检测算法, 数组存储的是点的坐标
    start_point = []
    intersection_point = []
    rows, cols = skeleton_image.shape
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if skeleton_image[i][j] != 255:
                continue
            continuous_substring_num = Point_Judgement(skeleton_image, i, j)
            if continuous_substring_num == 1:
                intersection_point.append((i, j))
            if continuous_substring_num == -1:
                start_point.append((i, j))

    # 展示一下算法给出的交点和起始点的位置
    for (x, y) in start_point:
        original_image[x][y] = (0, 0, 255)
    for (x, y) in intersection_point:
        original_image[x][y] = (0, 255, 0)
    cv2.imwrite("Start_and_Intersection_Point.jpg", np.uint8(original_image))
    cv2.waitKey(0)


# 测试模块
if __name__ == '__main__':
    Repetition("8.jpg")
