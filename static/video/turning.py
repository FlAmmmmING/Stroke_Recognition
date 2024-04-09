# # 用来视频转码的
# # 将白色底的视频变成米色
# import cv2
# import numpy as np
#
# # 读取视频文件
# cap = cv2.VideoCapture('jingyijiuying.mp4')
#
# # 获取视频帧数和帧率
# fps = cap.get(cv2.CAP_PROP_FPS)
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#
# fourcc = cv2.VideoWriter.fourcc(*'H264')
# out = cv2.VideoWriter('output_video.mp4', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
#
# # 定义要替换的白色和目标米色的 BGR 值
# white_color = np.array([255, 255, 255])
# white_color_min = np.array([100, 100, 100])
# target_color = np.array([220, 245, 245])  # 米色的 BGR 值
# cnt = 0
# # 逐帧处理视频
# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret:
#         # 将白色区域转换为目标米色
#         mask = cv2.inRange(frame, white_color_min, white_color)
#         frame[mask > 0] = target_color
#         cnt += 1
#         # 写入输出视频
#         out.write(frame)
#         print(cnt)
#     else:
#         break
#
# # 释放资源
# cap.release()
# out.release()
# cv2.destroyAllWindows()
