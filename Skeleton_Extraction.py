# 骨架提取代码——这里用到ZS细化算法的一个优化
# reference: 常庆贺,吴敏华,骆力明.基于改进ZS细化算法的手写体汉字骨架提取[J].计算机应用与软件,
#               2020, 37(7):8.DOI:10.3969/j.issn.1000-386x.2020.07.017.
import cv2
import numpy as np

if __name__ == '__main__':
    path = "需要处理的书法文字"