# 这个文件用来生成一个文字的书写视频
# 输入数据需要有：原图片，笔画顺序
import shutil

# 具体思路在这里：
#       对于每一个像素点，我们将像素点看成圆心，并且以一个选定的半径画圆

import cv2
import imageio
import numpy as np
import math
import queue
import os
import Generate_full_Video

# 专门用于生成书法毛笔视频的
size = 100
# 相对位置数组
d = [(size * 0, size * 3), (size * 1, size * 3), (size * 2, size * 3), (size * 3, size * 3), (size * 4, size * 3),
     (size * 0, size * 2), (size * 1, size * 2), (size * 2, size * 2), (size * 3, size * 2), (size * 4, size * 2),
     (size * 0, size * 1), (size * 1, size * 1), (size * 2, size * 1), (size * 3, size * 1), (size * 4, size * 1),
     (size * 0, size * 0), (size * 1, size * 0), (size * 2, size * 0), (size * 3, size * 0), (size * 4, size * 0)]


def get_radius_2(dir_x, dir_y, original_img, core, pre_radius, idx, Stroke):
    # 备案2 —— 按照轨迹方向确定半径
    # 这种方法较为冒险，可能会出现笔画崩溃的现象，但是它有良好的覆盖性
    # 这里改良一下，这个算法依然无法很好地解决笔画交点的错乱现象
    # 交点往往是文字骨架的交界处，这里在判断半径之前判断一下目标点的领域内有无其他笔画的骨架，如果有的话就保持之前的半径操作
    """
    :param item: 当前点
    :param dir_x: 方向
    :param dir_y: 方向
    :param original_img: 原始图片
    :param core: 圆心
    :param pre_radius: 之前的半径
    :param idx: 当前笔画
    :param Stroke: 整个笔画码
    :return: 返回半径大小
    """
    for i in range(len(Stroke)):
        if i == idx:
            continue
        this_stroke = Stroke[i]
        for pixel in this_stroke:
            if abs(core[0] - pixel[0]) <= 2 or abs(core[1] - pixel[1]) <= 2:
                return pre_radius

    radius_x = 0
    radius_y = 0
    iter_x, iter_y = core
    # 开始计算半径
    if dir_y == 0:
        # 寻找 y = 0 这条线
        # 先找左边
        while original_img[iter_x][iter_y] == 0:
            radius_x += 1
            iter_y -= 1
        iter_x, iter_y = core
        # 再找右边
        while original_img[iter_x][iter_y] == 0:
            radius_y += 1
            iter_y += 1
    elif dir_x == 0:
        # 寻找 x = 0 这条线
        # 先找上边
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
        iter_x, iter_y = core
        # 再找下边
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
    elif dir_x * dir_y == -1:
        # 寻找 x + y = 0 这条线
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
            iter_y -= 1
        radius_x = int(radius_x * 1.5)
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y += 1
        radius_y = int(radius_y * 1.5)
    else:
        # 寻找x - y = 0 这条边
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
            iter_y += 1
        radius_x = int(radius_x * 1.5)
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y -= 1
        radius_y = int(radius_x * 1.5)
    radius = max(radius_x, radius_y)
    # if dir_x * dir_y:
    #     radius = round(radius * 1.4142135623730951)
    if radius - pre_radius >= 2:
        # 判断笔画是否出现崩溃现象
        radius = pre_radius
    return radius


def get_radius_1(original_img, core):
    """
    确定半径大小
    :param original_img: 原始图片
    :param core: 圆心坐标
    :return: 返回半径
    """
    # 备案1 —— 八个方向取最小值确定半径
    # 这种方法较为稳定，但是缺点是可能会使得一些笔画无法覆盖
    radius = 100000000
    iter_x, iter_y = core
    radius_x, radius_y = 0, 0
    tep_radius = 0
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_y -= 1
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_y += 1
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x -= 1
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x += 1
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x -= 1
        iter_y -= 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x += 1
        iter_y += 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x -= 1
        iter_y += 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    radius = min(radius, tep_radius)
    tep_radius = 0
    iter_x, iter_y = core
    while original_img[iter_x, iter_y] == 0:
        tep_radius += 1
        iter_x += 1
        iter_y -= 1
    # radius = min(radius, round(tep_radius * 1.4142135623730951))
    radius = min(radius, tep_radius)
    return radius


def generate_fps(template_img, original_img, Stroke, Save_dir):
    """
    :param Save_dir: 保存的地址
    :param template_img: 空白模板
    :param original_img: 原图
    :param Stroke: 笔画
    :return:
    """
    # 用来存储图片编号的，以便接下来合成视频
    """
            这里整理一下(dir_x, dir_y)的取值对八邻域的关系
            (dir_x, dir_y) == (0, 1) 或者 (0, -1) 则半径的选取为 x = 0 这条直线
            (dir_x, dir_y) == (1, 0) 或者 (-1, 0) 则半径的选取为 y = 0 这条直线
            (dir_x, dir_y) == (1, 1) 或者 (-1, -1) 则半径的选取为 y = x 这条直线
            (dir_x, dir_y) == (1, -1) 或者 (-1, 1) 则半径的选取为 y = -x 这条直线
            半径的长度如此定义 -> 沿着直线寻找两个端点，寻找最近的一个端点距离圆心的位移距离作为这个圆的半径
    """
    if os.path.exists(Save_dir):
        shutil.rmtree(Save_dir)
    os.mkdir(Save_dir)
    cnt = 0
    iter_img = template_img.copy()

    # 广度优先遍历队列
    q = queue.Queue()
    dx = [1, -1, 0, 0]
    dy = [0, 0, -1, 1]
    radius = 0
    stroke_number = 0
    for item in Stroke:
        for i in range(len(item)):
            visit_map = np.zeros_like(original_img, dtype=bool)
            # radius = get_radius_1(original_img, item[i])
            if i == 0:
                radius = get_radius_1(original_img, item[i])
            else:
                dir_x, dir_y = item[i][0] - item[i - 1][0], item[i][1] - item[i - 1][1]
                radius = get_radius_2(dir_x, dir_y, original_img, item[i], radius, stroke_number, Stroke)
            print(f"圆心：({item[i][0]}, {item[i][1]}), 半径: {radius}")
            # 开始分帧
            cnt += 1
            # 接下来的问题是，确定了圆心和半径，如何绘制圆
            # 一种妥协的方式： 广度优先搜索， 时间复杂度较低
            q.put(item[i])
            visit_map[item[i][0], item[i][1]] = True
            while not q.empty():
                now_x, now_y = q.get()
                # distance = round(math.sqrt(pow(now_x - item[i][0], 2) + pow(now_y - item[i][1], 2)))
                # if distance > radius:
                #     continue
                iter_img[now_x, now_y] = (0, 0, 0)
                for j in range(4):
                    next_x = now_x + dx[j]
                    next_y = now_y + dy[j]
                    if original_img[next_x, next_y] == 255 or visit_map[next_x, next_y] or \
                            round(math.sqrt(pow(next_x - item[i][0], 2) + pow(next_y - item[i][1], 2))) > radius:
                        continue
                    q.put((next_x, next_y))
                    visit_map[next_x, next_y] = True
            cv2.imwrite(Save_dir + "/" + f"{cnt}.jpg", iter_img)
        stroke_number += 1



#
# def make_circle(ret_img, original_image, x, y, stroke_direction, p):
#     """
#     根据前一个坐标和当前坐标的相对关系，确定这个圆应该怎么画
#     :param ret_img: 需要返回的图片
#     :param original_image: 原始图片
#     :param x: 圆心坐标
#     :param y: 圆心坐标
#     :param stroke_direction: 笔画坐标数组
#     :param p: 当前笔画遍历到了哪个点
#     :return:
#     """
#     # 首先确定这次笔画的方向
#     (dir_x, dir_y) = stroke_direction[p] - stroke_direction[p - 1]
#     """
#         这里整理一下(dir_x, dir_y)的取值对八邻域的关系
#         (dir_x, dir_y) == (0, 1) 或者 (0, -1) 则半径的选取为 x = 0 这条直线
#         (dir_x, dir_y) == (1, 0) 或者 (-1, 0) 则半径的选取为 y = 0 这条直线
#         (dir_x, dir_y) == (1, 1) 或者 (-1, -1) 则半径的选取为 y = -x 这条直线
#         (dir_x, dir_y) == (1, -1) 或者 (-1, 1) 则半径的选取为 y = x 这条直线
#         半径的长度如此定义 -> 沿着直线寻找两个端点，寻找最近的一个端点距离圆心的位移距离作为这个圆的半径
#     """
#     cv2.circle(ret_img, (x, y), radius=5, color=(0, 255, 255))

def Generate_Video(fps_folder, video_folder, gif_folder, Picture):
    """
    :param fps_folder: 保存 fps 的文件夹
    :param video_folder: 保存 视频 的文件夹
    :param gif_folder: 保存 gif 的文件夹
    :param Picture: 视频名字
    :return: 返回视频
    """
    frames = os.listdir(fps_folder)
    frames.sort(key=lambda x: int(x.split('.')[0]))
    # 提取视频分辨率
    rows, cols = cv2.imread(fps_folder + "/1.jpg").shape[0], cv2.imread(fps_folder + "/1.jpg").shape[1]
    # 下面是生成GIF的代码
    gif = []
    for frame in frames:
        f_path = os.path.join(fps_folder, frame)
        image = cv2.imread(f_path)
        gif.append(image)
    imageio.mimsave(gif_folder + f"/{Picture}.gif", gif, fps=50)

    # 下面是生成MP4的代码
    # 设置 帧数
    fps = 40

    # 设置生成视频的名字
    video_name = f"{Picture}"
    video_dir = os.path.join(video_folder, video_name + ".mp4")
    if os.path.exists(video_dir):
        os.remove(video_dir)
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    VideoWriter = cv2.VideoWriter(video_dir, fourcc, fps, (cols, rows))

    for frame in frames:
        f_path = os.path.join(fps_folder, frame)
        image = cv2.imread(f_path)
        VideoWriter.write(image)
    VideoWriter.release()


def Stroke_Video_Generation(Base_path, Picture, Stroke):
    """

    :param Base_path: 用户临时文件夹
    :param Picture:  对应图片
    :param Stroke:  对应图片短笔画
    :return:
    """
    original_image = cv2.imread(Base_path + f"/Cutting/{Picture}.jpg", cv2.COLOR_BGR2GRAY)
    original_image[original_image < 100] = 0
    original_image[original_image >= 100] = 255
    rows, cols = original_image.shape
    template_img = np.zeros((rows, cols, 3), dtype=np.uint8)
    template_img.fill(255)
    # 预处理Stroke
    # Stroke = Stroke.split(',')
    # print(Stroke)
    printing_stroke = []
    available_stroke = []
    for item in Stroke:
        process_stroke = []
        a_printing_stroke = []
        for pixel in item:
            process_stroke.append([pixel[1], pixel[0]])
            a_printing_stroke.append([pixel[1] + d[Picture][0], pixel[0] + d[Picture][1], 0])
        available_stroke.append(process_stroke)
        printing_stroke.append(a_printing_stroke)
    print(available_stroke)
    with open(f"model/arr/{Picture}.txt", 'w') as f:
        f.write(str(printing_stroke))

    Save_fps_dir = Base_path + f"/Generate_Video/{Picture}"
    Save_dir_video = Base_path + "/Video"
    Save_dir_gif = Base_path + "/GIF"
    generate_fps(template_img, original_image, available_stroke, Save_fps_dir)
    Generate_Video(Save_fps_dir, Save_dir_video, Save_dir_gif, Picture)


def start_generate(username, PictureName, total_picture, base_path, picture_number, Stroke):
    Stroke_Video_Generation(base_path, picture_number, Stroke)
    # if picture_number == total_picture - 1:
    #     Generate_full_Video.start_Full_Video(base_path, PictureName)


# if __name__ == '__main__':
#     start_generate(202110310195, 1, 16, "static/data/202110310195", 0, [])
