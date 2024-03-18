# 后端代码整合
import os
from src import Convert_Front_Picture_to_CV2
import cv2


def start_project(image_Front_End, username: str, PictureName: str):
    # image 导入，开始操作
    image = Convert_Front_Picture_to_CV2.convert(image_Front_End)
    # 所有的数据都会先存进data这个临时文件夹中
    base_path = f"../data/{username}"
    # 以后这个用户的作品就存放在这里
    path_of_original_image = base_path + "/original"
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if not os.path.exists(path_of_original_image):
        os.makedirs(path_of_original_image)
    # 所有作品的原始图片都放在这里
    cv2.imwrite(path_of_original_image + f"/{PictureName}.jpg", image)
    # 先将文字分割
    # 再将文字骨架化
    # 再实现文字的短笔画集合
    # 最后实现笔画后端DIY
