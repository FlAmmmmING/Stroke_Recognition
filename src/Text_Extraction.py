# 这个文件用来分割书法字贴的文字
import cv2
from PIL import Image

# 先竖着切，再横着切
# acc 是分割广度
def Cutting(path, save_dir, acc, resize):
    # 读取图像，二值化图像
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    rows = img.shape[0]
    cols = img.shape[1]
    print(rows)
    print(cols)
    # 初始化一个数组，用来判断这个图片的每一列是否满足有字的特性
    judge_col = cols * [0]
    # 开始遍历
    for i in range(cols):
        for j in range(rows):
            if img[j][i] == 0:
                judge_col[i] = 1
                break
    # print(judge_col)
    # 存放竖着分割的图片
    cut_in_col = []
    # 快慢指针搜索judge_col连续的1串
    p0 = 0
    while p0 < cols:
        if judge_col[p0] == 1:
            p1 = p0 + 1
            while p1 < cols:
                if judge_col[p1] == 1:
                    p1 += 1
                else:
                    break
            # 全部扫描成功
            # 判断一下：p1和p0之间的差值是否满足一个字的大小
            if p1 - p0 < 10:
                p0 = p1 + 1
                continue
            if p1 == cols:
                p1 -= 1
            cropped = img[0:rows, max(0, p0 - 1): min(cols - 1, p1 + 1)]
            # print(cropped.shape)
            p0 = p1 + 1
            # cv2.imshow("img", cropped)
            # cv2.waitKey(0)
            cut_in_col.append(cropped)
        else:
            p0 += 1
    # 处理分割文字，然后进行单个文字的保存
    # cnt 用来给保存的文字编号
    cnt = 0
    for data in cut_in_col:
        cv2.imshow("c", data)
        cv2.waitKey(0)
        judge_row = rows * [0]
        rows = data.shape[0]
        cols = data.shape[1]
        print(rows)
        print(cols)
        # print(data.shape)
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
                cropped = cv2.resize(cropped, (resize, resize), interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(f"{save_dir}/{cnt}.jpg", cropped)
                cnt += 1
                p0 = p1 + 1
                cv2.imshow("c", cropped)
                cv2.waitKey(0)
            else:
                p0 += 1


if __name__ == '__main__':
    path = "../writing.jpg"  # 用来存放输入的图像
    save_dir = "../data/cutting"
    Cutting(path, save_dir, 50, 100)
    
