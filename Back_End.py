# 后端代码整合
import os
import Convert_Front_Picture_to_CV2, Create_Folder_and_DataSet
import cv2


def start_project(image_Front_End, username, PictureName):
    """

    :param image_Front_End: 前端图片
    :param username: 用户名
    :param PictureName: 图片名
    :return: 返回一个批量图片的像素值矩阵
    """
    # image 导入，开始操作
    image = Convert_Front_Picture_to_CV2.convert(image_Front_End)
    # 初始化用户的临时存储文件夹
    # 实现分割，细化，骨架提取，短笔画生成操作
    Create_Folder_and_DataSet.start_creating(username, PictureName, image)


