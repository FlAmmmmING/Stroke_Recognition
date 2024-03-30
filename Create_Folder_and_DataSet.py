import os
import cv2
import shutil
import Text_Extraction, Skeleton_Extraction, Stroke_Repetition_Release


# 所有的数据都会先存进data这个临时文件夹中
def start_creating(username, PictureName, Picture):
    """
    Function to create the folder
    :param username: 用户名
    :param PictureName: 图片名称
    :param Picture: 可以通过cv2访问的图片
    :return:
    """
    print(PictureName)
    # 以后这个用户的作品就存放在这里
    base_path = f'static/data/{username}'
    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    os.mkdir(base_path)
    # 作品的原始图片都放在这里
    os.mkdir(base_path + "/Original")
    # 作品的文字切片在这里
    os.mkdir(base_path + "/Cutting")
    # 作品的骨架生成图片放在这里
    os.mkdir(base_path + "/Skeleton")
    # 作品的短笔画生产图都放在这里了
    os.mkdir(base_path + "/Short_Skeleton")
    # 制作视频的生成帧放在这里
    os.mkdir(base_path + "/Generate_Video")
    # 视频放在这里
    os.mkdir(base_path + "/Video")
    # gif放这里
    os.mkdir(base_path + "/GIF")
    # 将图片插入进去
    cv2.imwrite(base_path + f"/Original/{PictureName}.jpg", Picture)

    # 先将文字分割
    Text_Extraction.Cutting(base_path + f"/Original/{PictureName}.jpg", base_path + "/Cutting", 10, 100)

    # 细化算法实现
    Skeleton_Extraction.start_thinning(base_path + "/Cutting", base_path + "/Skeleton")

    # 短笔画生成图实现，这里是预处理的最后一个需要处理的地方，然后将短笔画反馈给前端，让用户自己DIY
    Stroke_Repetition_Release.start_stroke_repetition(base_path + "/Skeleton", base_path + "/Cutting", base_path + "/Short_Skeleton")

# if __name__ == '__main__':
#     T("1111", "6")