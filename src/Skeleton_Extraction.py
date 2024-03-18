# 骨架提取代码——这里用到ZS细化算法的一个优化
# reference: 常庆贺,吴敏华,骆力明.基于改进ZS细化算法的手写体汉字骨架提取[J].计算机应用与软件,
#               2020, 37(7):8.DOI:10.3969/j.issn.1000-386x.2020.07.017.
# 上述论文我复现了他过滤孤立点的算法，我严重怀疑论文是在胡扯
import cv2
from skimage import measure
import numpy as np


# 获取邻居
def Get_Neighbour(x, y, img):
    return [img[x - 1][y - 1] // 255, img[x - 1][y] // 255, img[x - 1][y + 1] // 255,
            img[x][y - 1] // 255, img[x][y + 1] // 255,
            img[x + 1][y - 1] // 255, img[x + 1][y] // 255, img[x + 1][y + 1] // 255]


# 获得0-1字串
def get_Len(arr):
    res = 0
    cnt = 0
    for i in range(12):
        if arr[i] == 0:
            res = max(cnt, res)
            cnt = 0
        else:
            cnt += 1
    if cnt:
        res = max(res, cnt)
    return res >= 5


def get_transitions(arr):
    res = 0
    for i in range(0, 8):
        if arr[i % 8] == 0 and arr[(i + 1) % 8] == 1:
            res += 1
    return res


# 处理空洞算法
def Cavity_Deal(img):
    res = img
    rows = img.shape[0]
    cols = img.shape[1]
    changing = [(-1, -1)]
    while changing:
        changing = []
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P9, P2, P3, P8, P4, P7, P6, P5 = Get_Neighbour(i, j, img)
                arr = [P2, P3, P4, P5, P6, P7, P8, P9, P2, P3, P4, P5]
                if res[i][j] == 0 and get_Len(arr):
                    changing.append((i, j))
        for (x, y) in changing:
            res[x][y] = 255
    return res


def Skeleton_Extraction(path, save_dir, threshold_point, photo):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    rows = img.shape[0]
    cols = img.shape[1]

    # 过滤孤立点的算法
    img_label, num = measure.label(img, background=255, return_num=True)
    props = measure.regionprops(img_label)
    resMatrix = np.zeros(img.shape).astype(np.uint8)
    for i in range(0, len(props)):
        if props[i].area > threshold_point:
            tmp = (img_label == i + 1).astype(np.uint8)
            resMatrix += tmp
    resMatrix *= 255
    # 处理空洞算法
    Pretreatment_Image = Cavity_Deal(img=resMatrix)
    cv2.imwrite(f'../data/Pretreatment_Image/{photo}.jpg', Pretreatment_Image)
    # 细化算法实现
    # ZS细化算法得到初步骨架
    changing1 = changing2 = [(-1, -1)]
    while changing1 or changing2:
        # 迭代一
        changing1 = []
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P9, P2, P3, P8, P4, P7, P6, P5 = Get_Neighbour(i, j, Pretreatment_Image)
                arr = [P2, P3, P4, P5, P6, P7, P8, P9]
                if (Pretreatment_Image[i][j] == 255 and  # 条件0
                        P4 * P6 * P8 == 0 and  # 条件3
                        P2 * P4 * P6 == 0 and  # 条件4
                        get_transitions(arr) == 1 and  # 条件2
                        2 <= (P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9) <= 6):  # 条件1
                    changing1.append((i, j))

        for (x, y) in changing1:
            Pretreatment_Image[x][y] = 0
        # 迭代二
        changing2 = []
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P9, P2, P3, P8, P4, P7, P6, P5 = Get_Neighbour(i, j, Pretreatment_Image)
                arr = [P2, P3, P4, P5, P6, P7, P8, P9]
                if (Pretreatment_Image[i][j] == 255 and  # 条件0
                        P2 * P6 * P8 == 0 and  # 条件3
                        P2 * P4 * P8 == 0 and  # 条件4
                        get_transitions(arr) == 1 and  # 条件2
                        2 <= (P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9) <= 6):  # 条件1
                    changing2.append((i, j))

        for (x, y) in changing2:
            Pretreatment_Image[x][y] = 0

    # 得到ZS骨架后细化代码
    # 再一次改进骨架：
    cnt = -1
    while cnt != 0:
        cnt = 0
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P9, P2, P3, P8, P4, P7, P6, P5 = Get_Neighbour(i, j, Pretreatment_Image)
                if (Pretreatment_Image[i][j] == 255 and
                        ((P2 * P8 == 1 and P4 + P5 + P6 + P9 == 0) or
                         (P6 * P8 == 1 and P2 + P3 + P4 + P7 == 0) or
                         (P2 * P4 == 1 and P3 + P6 + P7 + P8 == 0) or
                         (P4 * P6 == 1 and P2 + P5 + P8 + P9 == 0) or
                         (P3 + P5 + P7 + P9 == 0 and P2 + P4 + P6 + P8 == 3))):
                    Pretreatment_Image[i][j] = 0
                    cnt += 1

    # cv2.imshow("1", Pretreatment_Image)
    cv2.imwrite(save_dir, Pretreatment_Image)
    print(photo)
    # cv2.waitKey(0)


if __name__ == '__main__':
    for photo in range(0, 15):
        path = f"../data/cutting/{photo}.jpg"
        save_dir = f"../data/Skeleton/{photo}.jpg"
        # threshold_point：是过滤掉连通域大小小于threshold_point，后期设计上可以追加一个用户自适应过滤机制
        Skeleton_Extraction(path, save_dir, 16, photo)
