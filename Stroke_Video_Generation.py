# 这个文件用来生成一个文字的书写视频
# 输入数据需要有：原图片，笔画顺序

# 具体思路在这里：
#       对于每一个像素点，我们将像素点看成圆心，并且以一个选定的半径画圆

import cv2
import imageio
import numpy as np
import math
import queue
import os


def get_radius_2(dir_x, dir_y, original_img, core, pre_radius):
    # 备案2 —— 按照轨迹方向确定半径
    # 这种方法较为冒险，可能会出现笔画崩溃的现象，但是它有良好的覆盖性
    """

    :param dir_x: 方向
    :param dir_y: 方向
    :param original_img: 原始图片
    :param core: 圆心
    :param pre_radius: 之前的半径
    :return: 返回半径大小
    """
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
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y += 1
    else:
        # 寻找x - y = 0 这条边
        while original_img[iter_x, iter_y] == 0:
            radius_x += 1
            iter_x -= 1
            iter_y += 1
        iter_x, iter_y = core
        while original_img[iter_x, iter_y] == 0:
            radius_y += 1
            iter_x += 1
            iter_y -= 1
    radius = min(radius_x, radius_y)
    # if dir_x * dir_y:
    #     radius = round(radius * 1.4142135623730951)
    if abs(radius - pre_radius) > 1:
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
    cnt = 0
    iter_img = template_img.copy()

    # 广度优先遍历队列
    q = queue.Queue()
    dx = [1, -1, 0, 0]
    dy = [0, 0, -1, 1]

    for item in Stroke:
        for i in range(2, len(item) - 2):
            visit_map = np.zeros_like(original_img, dtype=bool)
            # radius = get_radius_1(original_img, item[i])
            if i == 2:
                radius = get_radius_1(original_img, item[i])
            else:
                dir_x, dir_y = item[i][0] - item[i - 1][0], item[i][1] - item[i - 1][1]
                radius = get_radius_2(dir_x, dir_y, original_img, item[i], radius)
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

def Generate_Video(fps_folder, video_folder, Picture):
    """
    :param fps_folder: 保存 fps 的文件夹
    :param video_folder: 保存 视频 的文件夹
    :param Picture: 视频名字
    :return: 返回视频
    """
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
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
    imageio.mimsave(video_folder + f"/{Picture}.gif", gif, fps=50)

    # 下面是生成MP4的代码
    # 设置 帧数
    fps = 120

    # 设置生成视频的名字
    video_name = f"{Picture}"
    video_dir = os.path.join(video_folder, video_name + ".mp4")
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
    original_image = cv2.imread(Base_path + "/Cutting/" + Picture, cv2.COLOR_BGR2GRAY)
    original_image[original_image < 100] = 0
    original_image[original_image >= 100] = 255
    rows, cols = original_image.shape
    template_img = np.zeros((rows, cols, 3), dtype=np.uint8)
    template_img.fill(255)
    # 预处理Stroke
    # Stroke = Stroke.split(',')
    # print(Stroke)
    available_stroke = []
    for item in Stroke:
        process_stroke = []
        for pixel in item:
            process_stroke.append([pixel[1], pixel[0]])
        available_stroke.append(process_stroke)
    print(available_stroke)
    Save_fps_dir = Base_path + "/Generate_Video"
    Save_dir_video = Base_path + "/Video"
    generate_fps(template_img, original_image, available_stroke, Save_fps_dir)
    Generate_Video(Save_fps_dir, Save_dir_video, Picture)


if __name__ == '__main__':
    arr = [
        [
            [
                12,
                14
            ],
            [
                13,
                15
            ],
            [
                14,
                16
            ],
            [
                15,
                17
            ],
            [
                16,
                18
            ],
            [
                16,
                19
            ],
            [
                16,
                20
            ],
            [
                16,
                21
            ],
            [
                17,
                22
            ],
            [
                17,
                23
            ],
            [
                17,
                24
            ],
            [
                17,
                25
            ]
        ],
        [
            [
                24,
                13
            ],
            [
                25,
                14
            ],
            [
                26,
                13
            ],
            [
                27,
                13
            ],
            [
                28,
                13
            ],
            [
                29,
                13
            ],
            [
                30,
                13
            ],
            [
                31,
                13
            ],
            [
                32,
                13
            ],
            [
                33,
                12
            ],
            [
                34,
                12
            ],
            [
                35,
                11
            ],
            [
                36,
                11
            ],
            [
                37,
                12
            ],
            [
                38,
                13
            ],
            [
                39,
                13
            ],
            [
                40,
                14
            ],
            [
                39,
                15
            ],
            [
                38,
                15
            ],
            [
                37,
                15
            ],
            [
                36,
                16
            ],
            [
                35,
                16
            ],
            [
                34,
                16
            ],
            [
                33,
                17
            ],
            [
                33,
                18
            ],
            [
                33,
                19
            ],
            [
                33,
                20
            ],
            [
                33,
                21
            ],
            [
                32,
                22
            ],
            [
                32,
                23
            ]
        ],
        [
            [
                18,
                29
            ],
            [
                18,
                28
            ],
            [
                18,
                27
            ],
            [
                19,
                26
            ],
            [
                20,
                26
            ],
            [
                21,
                26
            ],
            [
                22,
                26
            ],
            [
                23,
                26
            ],
            [
                24,
                26
            ],
            [
                25,
                26
            ],
            [
                26,
                25
            ],
            [
                27,
                25
            ],
            [
                28,
                25
            ],
            [
                29,
                25
            ],
            [
                30,
                24
            ]
        ],
        [
            [
                23,
                35
            ],
            [
                24,
                36
            ],
            [
                24,
                37
            ],
            [
                24,
                38
            ],
            [
                24,
                39
            ],
            [
                24,
                40
            ],
            [
                24,
                41
            ],
            [
                24,
                42
            ],
            [
                24,
                43
            ],
            [
                24,
                44
            ],
            [
                24,
                45
            ],
            [
                24,
                46
            ],
            [
                23,
                47
            ],
            [
                23,
                48
            ],
            [
                23,
                49
            ],
            [
                23,
                50
            ],
            [
                23,
                51
            ],
            [
                23,
                52
            ],
            [
                23,
                53
            ],
            [
                23,
                54
            ],
            [
                23,
                55
            ],
            [
                23,
                56
            ]
        ],
        [
            [
                27,
                43
            ],
            [
                28,
                43
            ],
            [
                29,
                43
            ],
            [
                30,
                43
            ],
            [
                31,
                43
            ],
            [
                32,
                43
            ],
            [
                33,
                43
            ],
            [
                34,
                43
            ]
        ],
        [
            [
                12,
                47
            ],
            [
                12,
                48
            ],
            [
                12,
                49
            ],
            [
                12,
                50
            ],
            [
                11,
                51
            ],
            [
                11,
                52
            ],
            [
                11,
                53
            ],
            [
                11,
                54
            ],
            [
                12,
                55
            ],
            [
                12,
                56
            ],
            [
                11,
                57
            ],
            [
                11,
                58
            ],
            [
                11,
                59
            ],
            [
                11,
                60
            ],
            [
                11,
                61
            ]
        ],
        [
            [
                6,
                66
            ],
            [
                7,
                66
            ],
            [
                8,
                65
            ],
            [
                9,
                65
            ],
            [
                10,
                65
            ],
            [
                11,
                65
            ],
            [
                12,
                64
            ],
            [
                13,
                63
            ],
            [
                14,
                63
            ],
            [
                15,
                63
            ],
            [
                16,
                62
            ],
            [
                17,
                62
            ],
            [
                18,
                62
            ],
            [
                19,
                62
            ],
            [
                20,
                61
            ],
            [
                21,
                60
            ],
            [
                22,
                60
            ],
            [
                23,
                60
            ],
            [
                24,
                60
            ],
            [
                25,
                59
            ],
            [
                26,
                58
            ],
            [
                27,
                58
            ],
            [
                28,
                58
            ],
            [
                29,
                57
            ],
            [
                30,
                57
            ],
            [
                31,
                57
            ],
            [
                32,
                57
            ]
        ],
        [
            [
                64,
                8
            ],
            [
                64,
                9
            ],
            [
                64,
                10
            ],
            [
                64,
                11
            ],
            [
                64,
                12
            ],
            [
                64,
                13
            ],
            [
                64,
                14
            ],
            [
                64,
                15
            ],
            [
                64,
                16
            ]
        ],
        [
            [
                51,
                19
            ],
            [
                50,
                19
            ],
            [
                49,
                20
            ],
            [
                49,
                21
            ],
            [
                49,
                22
            ],
            [
                48,
                23
            ],
            [
                48,
                24
            ],
            [
                47,
                25
            ],
            [
                47,
                26
            ],
            [
                47,
                27
            ],
            [
                47,
                28
            ],
            [
                46,
                29
            ],
            [
                46,
                30
            ],
            [
                46,
                31
            ],
            [
                45,
                32
            ],
            [
                44,
                33
            ]
        ],
        [
            [
                54,
                21
            ],
            [
                55,
                21
            ],
            [
                56,
                21
            ],
            [
                57,
                21
            ],
            [
                58,
                21
            ],
            [
                59,
                21
            ],
            [
                60,
                21
            ],
            [
                61,
                21
            ],
            [
                62,
                21
            ],
            [
                63,
                20
            ],
            [
                64,
                19
            ],
            [
                65,
                19
            ],
            [
                66,
                19
            ],
            [
                67,
                19
            ],
            [
                68,
                19
            ],
            [
                69,
                19
            ],
            [
                70,
                19
            ],
            [
                71,
                19
            ],
            [
                72,
                19
            ],
            [
                73,
                18
            ],
            [
                74,
                18
            ],
            [
                75,
                17
            ],
            [
                76,
                17
            ],
            [
                77,
                17
            ],
            [
                78,
                17
            ],
            [
                79,
                18
            ],
            [
                80,
                18
            ],
            [
                81,
                18
            ],
            [
                82,
                18
            ],
            [
                83,
                18
            ],
            [
                84,
                18
            ],
            [
                85,
                18
            ],
            [
                86,
                19
            ],
            [
                87,
                19
            ],
            [
                88,
                19
            ],
            [
                89,
                19
            ],
            [
                90,
                19
            ],
            [
                91,
                19
            ],
            [
                92,
                19
            ],
            [
                93,
                20
            ],
            [
                94,
                21
            ],
            [
                93,
                22
            ],
            [
                92,
                22
            ],
            [
                91,
                22
            ],
            [
                90,
                23
            ],
            [
                89,
                23
            ],
            [
                88,
                23
            ],
            [
                87,
                23
            ],
            [
                86,
                23
            ],
            [
                85,
                23
            ],
            [
                84,
                24
            ],
            [
                83,
                25
            ],
            [
                82,
                26
            ],
            [
                81,
                27
            ],
            [
                80,
                27
            ],
            [
                79,
                28
            ],
            [
                78,
                29
            ]
        ],
        [
            [
                56,
                37
            ],
            [
                57,
                37
            ],
            [
                58,
                37
            ],
            [
                59,
                37
            ],
            [
                60,
                37
            ],
            [
                61,
                37
            ],
            [
                62,
                37
            ],
            [
                63,
                37
            ],
            [
                64,
                37
            ],
            [
                65,
                37
            ],
            [
                66,
                37
            ],
            [
                67,
                36
            ],
            [
                68,
                35
            ],
            [
                69,
                35
            ],
            [
                70,
                35
            ]
        ],
        [
            [
                43,
                52
            ],
            [
                44,
                52
            ],
            [
                45,
                52
            ],
            [
                46,
                51
            ],
            [
                47,
                51
            ],
            [
                48,
                51
            ],
            [
                49,
                51
            ],
            [
                50,
                51
            ],
            [
                51,
                51
            ],
            [
                52,
                50
            ],
            [
                53,
                50
            ],
            [
                54,
                50
            ],
            [
                55,
                50
            ],
            [
                56,
                50
            ],
            [
                57,
                50
            ],
            [
                58,
                49
            ],
            [
                59,
                49
            ],
            [
                60,
                49
            ],
            [
                61,
                49
            ],
            [
                62,
                49
            ],
            [
                63,
                49
            ],
            [
                64,
                49
            ],
            [
                65,
                49
            ],
            [
                66,
                49
            ],
            [
                67,
                49
            ],
            [
                68,
                48
            ],
            [
                69,
                47
            ],
            [
                70,
                47
            ],
            [
                71,
                47
            ],
            [
                72,
                47
            ],
            [
                73,
                47
            ],
            [
                74,
                47
            ],
            [
                75,
                47
            ],
            [
                76,
                47
            ],
            [
                77,
                47
            ],
            [
                78,
                47
            ],
            [
                79,
                47
            ],
            [
                80,
                46
            ],
            [
                81,
                47
            ]
        ],
        [
            [
                65,
                52
            ],
            [
                65,
                53
            ],
            [
                65,
                54
            ],
            [
                65,
                55
            ],
            [
                65,
                56
            ],
            [
                65,
                57
            ],
            [
                65,
                58
            ],
            [
                65,
                59
            ],
            [
                65,
                60
            ],
            [
                65,
                61
            ],
            [
                65,
                62
            ],
            [
                65,
                63
            ],
            [
                65,
                64
            ],
            [
                65,
                65
            ],
            [
                65,
                66
            ],
            [
                65,
                67
            ],
            [
                65,
                68
            ],
            [
                64,
                69
            ],
            [
                64,
                70
            ],
            [
                64,
                71
            ],
            [
                64,
                72
            ],
            [
                64,
                73
            ],
            [
                64,
                74
            ],
            [
                64,
                75
            ],
            [
                64,
                76
            ],
            [
                63,
                77
            ],
            [
                62,
                78
            ],
            [
                62,
                79
            ],
            [
                62,
                80
            ],
            [
                61,
                81
            ],
            [
                60,
                80
            ],
            [
                59,
                79
            ],
            [
                59,
                78
            ],
            [
                58,
                77
            ],
            [
                58,
                76
            ],
            [
                57,
                75
            ],
            [
                57,
                74
            ],
            [
                56,
                73
            ]
        ],
        [
            [
                47,
                60
            ],
            [
                46,
                61
            ],
            [
                46,
                62
            ],
            [
                46,
                63
            ],
            [
                46,
                64
            ],
            [
                45,
                65
            ],
            [
                45,
                66
            ],
            [
                44,
                67
            ],
            [
                44,
                68
            ],
            [
                44,
                69
            ],
            [
                43,
                70
            ],
            [
                44,
                71
            ]
        ],
        [
            [
                78,
                58
            ],
            [
                79,
                57
            ],
            [
                80,
                57
            ],
            [
                81,
                58
            ],
            [
                82,
                58
            ],
            [
                83,
                58
            ],
            [
                84,
                59
            ],
            [
                85,
                59
            ],
            [
                86,
                60
            ],
            [
                87,
                60
            ],
            [
                88,
                61
            ],
            [
                89,
                62
            ],
            [
                90,
                63
            ],
            [
                91,
                63
            ],
            [
                92,
                64
            ]
        ]
    ]
    picture = '1.jpg'
    Base_path = 'static/data/202110310195'
    Stroke_Video_Generation(Base_path, picture, arr)

# COLOR = [93, 194, 56]  # 染色
# cols, rows = skeleton_image.shape
# for A_Stroke in Stroke:
#     for (x, y) in A_Stroke:
#         original_image[x][y] = COLOR
# cv2.imwrite("showing.jpg", original_image)
# cv2.imshow("Original Image", original_image)
# cv2.waitKey(0)

#
# if __name__ == '__main__':
#     Cutting_Folder = "../cutting"
#     Picture = "8.jpg"
#
#     Stroke = [
#         # [(53, 57), (53, 58), (53, 59), (53, 60), (53, 61), (53, 62), (53, 63), (52, 64), (52, 65), (53, 66), (53, 67),
#         #  (53, 68), (53, 69), (53, 70), (52, 71), (52, 72), (52, 73), (52, 74), (51, 75), (51, 76), (51, 77), (51, 78),
#         #  (51, 79), (51, 80), (51, 81), (51, 82), (51, 83), (50, 84), (50, 85), (50, 86)],
#         # [(44, 93), (44, 94), (45, 95), (45, 96), (45, 97), (45, 98), (45, 99), (45, 100), (45, 101), (45, 102),
#         #  (45, 103), (45, 104), (45, 105), (45, 106), (44, 107), (44, 108), (44, 109), (45, 110), (45, 111), (45, 112),
#         #  (45, 113), (45, 114)],
#         [(53, 57), (53, 58), (53, 59), (53, 60), (52, 61), (52, 62), (52, 63), (52, 64), (52, 65), (52, 66), (52, 67),
#          (51, 68), (51, 69), (51, 70), (51, 71), (51, 72), (51, 73), (51, 74), (50, 75), (50, 76), (50, 77), (50, 78),
#          (50, 79), (50, 80), (50, 81), (49, 82), (49, 83), (49, 84), (49, 85), (49, 86), (49, 87), (49, 88), (49, 89),
#          (48, 90), (48, 91), (48, 92), (48, 93), (48, 94), (48, 95), (48, 96), (47, 97), (47, 98), (47, 99), (47, 100),
#          (47, 101), (47, 102), (47, 103), (46, 104), (46, 105), (46, 106), (46, 107), (46, 108), (46, 109), (46, 110),
#          (45, 111), (45, 112), (45, 113), (45, 114)],
#         [(3, 77), (4, 78), (5, 79), (6, 80), (6, 81), (7, 82), (8, 83), (9, 84), (10, 85), (11, 86), (12, 87), (13, 88),
#          (14, 88), (15, 89), (16, 89), (17, 90), (18, 90), (19, 90), (20, 90), (21, 90), (22, 90), (23, 90), (24, 90),
#          (25, 90), (26, 90), (27, 90), (28, 90), (29, 90), (30, 90), (31, 90), (32, 90), (33, 90), (34, 90), (35, 90),
#          (36, 90), (37, 90), (38, 90), (39, 90), (40, 90), (41, 90)],
#         [(52, 89), (53, 89), (54, 89), (55, 89), (56, 89), (57, 89), (58, 89), (59, 89), (60, 89), (61, 89), (62, 89),
#          (63, 89), (64, 89), (65, 89), (66, 89), (67, 89), (68, 89), (69, 89), (70, 89), (71, 89), (72, 89), (73, 89),
#          (74, 89), (75, 89), (76, 89), (77, 89), (78, 89), (79, 89), (80, 89), (81, 89), (82, 89)],
#         [(96, 14), (97, 15), (97, 16), (98, 17), (98, 18), (98, 19), (99, 20), (99, 21), (99, 22), (99, 23), (98, 24),
#          (98, 25), (98, 26), (98, 27), (98, 28), (97, 29), (97, 30), (96, 31), (96, 32), (96, 33), (96, 34), (95, 35),
#          (95, 36), (95, 37), (95, 38), (95, 39), (94, 40), (94, 41), (94, 42), (94, 43), (93, 44), (93, 45), (93, 46),
#          (93, 47), (92, 48), (92, 49), (92, 50), (91, 51), (91, 52), (91, 53), (90, 54), (90, 55), (90, 56), (90, 57),
#          (90, 58), (90, 59), (89, 60), (89, 61), (89, 62), (89, 63), (89, 64), (89, 65), (89, 66), (89, 67), (88, 68),
#          (88, 69), (88, 70), (88, 71), (88, 72), (88, 73), (88, 74), (88, 75), (88, 76), (88, 77), (88, 78), (87, 79),
#          (87, 80), (87, 81), (87, 82)],
#         [(84, 91), (84, 92), (84, 93), (84, 94), (84, 95), (84, 96), (84, 97), (84, 98), (84, 99), (84, 100), (84, 101),
#          (84, 102), (84, 103), (84, 104), (84, 105), (84, 106), (84, 107), (84, 108), (84, 109), (83, 110), (83, 111),
#          (83, 112), (83, 113), (83, 114), (83, 115), (83, 116), (83, 117), (83, 118), (83, 119), (83, 120), (83, 121),
#          (83, 122), (83, 123), (82, 124), (82, 125), (82, 126), (82, 127), (82, 128), (82, 129), (81, 130), (81, 131),
#          (81, 132), (81, 133), (81, 134), (81, 135), (81, 136), (81, 137), (81, 138), (81, 139), (81, 140), (81, 141),
#          (81, 142), (81, 143), (81, 144), (81, 145), (81, 146), (81, 147), (81, 148), (82, 149), (82, 150), (83, 151),
#          (84, 152), (84, 153), (84, 154)],
#         [(90, 84), (91, 84), (92, 84), (93, 84), (94, 84), (95, 84), (96, 84), (97, 84), (98, 84), (99, 84), (100, 84),
#          (101, 84), (102, 84), (103, 84), (104, 84), (105, 83), (106, 82), (106, 81), (106, 80), (107, 79), (108, 78),
#          (109, 77), (110, 76), (111, 75), (112, 74), (113, 73), (114, 72), (115, 71), (116, 70), (117, 69), (118, 68),
#          (119, 68), (120, 67), (121, 66), (122, 65), (123, 65), (124, 65), (125, 65), (126, 64), (127, 64), (128, 63),
#          (129, 63), (130, 63), (131, 63), (132, 63), (133, 63)],
#         [(138, 49), (139, 50), (139, 51), (139, 52), (139, 53), (139, 54), (140, 55), (140, 56), (140, 57), (140, 58),
#          (140, 59), (140, 60), (139, 61), (138, 62), (137, 63)],
#         [(135, 66), (135, 67), (134, 68), (134, 69), (134, 70), (134, 71), (134, 72), (133, 73), (133, 74), (133, 75),
#          (133, 76), (133, 77), (132, 78), (132, 79), (131, 80), (131, 81), (131, 82), (130, 83), (130, 84), (130, 85),
#          (130, 86), (129, 87), (129, 88), (129, 89), (129, 90), (128, 91), (128, 92), (128, 93), (127, 94), (127, 95),
#          (127, 96), (126, 97), (126, 98), (126, 99), (125, 100), (125, 101), (125, 102), (125, 103), (125, 104),
#          (125, 105), (125, 106), (124, 107), (124, 108), (123, 109), (123, 110), (123, 111), (123, 112), (123, 113),
#          (123, 114), (122, 115)],
#         [(108, 109), (109, 110), (110, 111), (111, 112), (112, 113), (113, 114), (114, 114), (115, 115), (116, 115),
#          (117, 116), (118, 116)],
#         [(121, 119), (122, 120), (123, 121), (124, 122), (125, 123), (126, 124), (127, 125), (128, 126), (129, 127),
#          (130, 127), (131, 127), (132, 128), (133, 128), (134, 129), (135, 129), (136, 130), (137, 130), (138, 130)]]
#
#     Stroke_Video_Generation(Cutting_Folder, Picture, Stroke)
#
