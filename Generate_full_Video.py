# 这个程序是用来生成原始图像的完全视频
import shutil

import cv2
import imageio
import numpy as np
import math
import queue
import os


def Generate_full_Video(base_path, PictureName, x, y):
    path = base_path + "/Generate_Video"
    character_number = len(os.listdir(path))
    print(character_number)
    video_name = f"{PictureName}"
    video_dir = base_path + "/Video/" + video_name + '.mp4'
    if os.path.exists(video_dir):
        os.remove(video_dir)
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    cols = 100 * character_number
    rows = 100 * y
    fps = 60
    # gif 图片
    gif = []
    # 这里存放的是每一个文字的帧数
    sum_fps = []
    for i in range(character_number):
        sum_fps.append(len(os.listdir(path + f"/{i}")))
    VideoWriter = cv2.VideoWriter(video_dir, fourcc, fps, (cols, rows))
    # 用来拼接
    image_background = cv2.imread("static/imgs/concat/concat.jpg")
    # 根据你的字的多少生成多少长度的视频
    for i in range(character_number):
        # 开始从第一个遍历
        picture_dir = base_path + f"/Generate_Video/{i}"
        picture_number = len(os.listdir(picture_dir))
        for j in range(1, picture_number + 1):
            one_fps = cv2.imread(picture_dir + f"/{j}.jpg")
            # 这是第几张照片
            idx = i
            for k in range(idx - 1, -1, -1):
                pre_character = cv2.imread(base_path + f"/Generate_Video/{k}/{sum_fps[k]}.jpg")
                # print(pre_character.shape)
                one_fps = cv2.hconcat([pre_character, one_fps])
            for k in range(idx + 1, character_number):
                one_fps = cv2.hconcat([one_fps, image_background])
            # print(one_fps.shape)
            gif.append(one_fps)
            VideoWriter.write(one_fps)
    imageio.mimsave(base_path + f"/GIF/{video_name}.gif", gif, fps=50)
    VideoWriter.release()
    # 从左到右开始生成视频


# 将会保存在video文件夹下
def start_Full_Video(base_path, PictureName):
    Generate_full_Video(base_path, PictureName, 2, 2)

# if __name__ == '__main__':
#     Generate_full_Video("static/data/202110310195", '112')
