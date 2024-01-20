# ocr识别书法文字
# 2024/1/20 洪一芃
from paddleocr import PaddleOCR
import ast

def recognize_chinese_character(image_path):
    # 创建一个OCR模型
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    # 对图片进行OCR识别
    result = str(ocr.ocr(image_path, cls=True))

    return result

def solve(result_str):
    # 将字符串格式的结果转换回列表
    nested_result = ast.literal_eval(result_str)

    # 提取实际的结果列表
    result = nested_result[0] if nested_result and isinstance(nested_result, list) else []

    # 创建两个空字典来存储坐标和识别结果
    coordinates_dict = {}
    recognition_dict = {}

    # 遍历每个识别结果，填充字典
    for idx, line in enumerate(result):
        # 填充坐标字典
        coordinates_dict[idx] = line[0]
        # 填充识别结果字典
        recognition_dict[idx] = line[1]

    return coordinates_dict, recognition_dict

# demo
result_str = recognize_chinese_character('./Skeleton/skeleton10.jpg')
coordinates, recognition = solve(result_str)

# print("坐标字典:", coordinates)
# print("识别结果字典:", recognition)

print("坐标:", coordinates[0])
print("识别结果:", recognition[0])
