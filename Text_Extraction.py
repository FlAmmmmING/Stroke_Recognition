# 这个文件用来分割书法字贴的文字
import cv2
import numpy as np
from PIL import Image


def Cutting(path, save_dir, acc_percent, resize):
    """
    # 先竖着切，再横着切
    :param path: 图片原路径
    :param save_dir: 保存地点
    :param acc_percent:  分割广度百分比
    :param resize: 图片分割后的统一大小
    :return:
    """
    # 读取图像，二值化图像
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
    rows = img.shape[0]
    cols = img.shape[1]
    acc = max(rows, cols) * acc_percent * 0.01
    # print(acc)
    # print(rows)
    # print(cols)
    # 初始化一个数组，用来判断这个图片的每一列是否满足有字的特性
    judge_col = cols * [0]
    # 开始遍历
    for i in range(cols):
        for j in range(rows):
            if img[j][i] == 0:
                judge_col[i] = 1
                break
    cut_in_col = []
    p0 = 0
    while p0 < cols:
        if judge_col[p0] == 1:
            p1 = p0 + 1
            while p1 < cols:
                if judge_col[p1] == 1:
                    p1 += 1
                else:
                    break
            if p1 - p0 < 10:
                p0 = p1 + 1
                continue
            if p1 == cols:
                p1 -= 1
            cropped = img[0:rows, max(0, p0 - 1): min(cols - 1, p1 + 1)]
            p0 = p1 + 1
            cut_in_col.append(cropped)
        else:
            p0 += 1
    cut_in_col.reverse()
    # 处理分割文字，然后进行单个文字的保存
    # cnt 用来给保存的文字编号
    cnt = 0
    for data in cut_in_col:
        judge_row = rows * [0]
        rows = data.shape[0]
        cols = data.shape[1]
        for i in range(rows):
            for j in range(cols):
                if data[i][j] == 0:
                    judge_row[i] = 1
                    break
        # print(judge_row)
        p0 = 0
        while p0 < rows:
            if judge_row[p0] == 1:
                p1 = p0 + 1
                while p1 < rows:
                    if judge_row[p1] == 1 or p1 - p0 < acc:
                        p1 += 1
                    else:
                        break
                if p1 == rows:
                    p1 -= 1
                cropped = data[max(0, p0 - 1): min(rows - 1, p1 + 1), 0:cols]
                cropped = cv2.resize(cropped, (resize - 2, resize - 2), interpolation=cv2.INTER_CUBIC)
                # 边缘填充，防止笔画直接和边界触碰
                cropped = np.pad(cropped, (1, 1), 'constant', constant_values=255)
                cv2.imwrite(f"{save_dir}/{cnt}.jpg", cropped)
                cnt += 1
                p0 = p1 + 1
            else:
                p0 += 1

#
# if __name__ == '__main__':
#     path = "../writing2.jpg"  # 用来存放输入的图像
#     save_dir = "../data/202110310195/Cutting"
#     # resize 越高效果越好，但是相反的，速度也就越慢
#     Cutting(path, save_dir, 10, 100)
