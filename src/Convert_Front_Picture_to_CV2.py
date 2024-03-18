import cv2
import numpy as np


def convert(image):
    """
    将前端调来的图片数据类型转换为支持cv2读取的数据类型
    :param image: 输入的是从前端调过来的图片
    :return: 返回一张支持cv2读取的图片
    """
    pdf_byte = image.stream.read()
    ret_image = cv2.imdecode(np.frombuffer(pdf_byte, np.uint8), cv2.IMREAD_COLOR)
    return ret_image
