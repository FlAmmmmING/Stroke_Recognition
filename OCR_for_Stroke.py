# ocr识别书法文字
# 2024/1/20 洪一芃
from paddleocr import PaddleOCR
from Text_Stroke_Table import Text_Storke_Table
import ast
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class Recognition_Chinese_Character:
    def __init__(self, image_path):
        self.image_path = image_path
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        self.TextTables = Text_Storke_Table()

    def Recognize(self):
        """
        :return: 笔画顺序, 坐标, 识别结果
        """
        try:
            character = self.ocr.ocr(self.image_path, cls=True)
            character_str = str(character)
            nested_result = ast.literal_eval(character_str)
            result = nested_result[0] if nested_result and isinstance(nested_result, list) else []
            coordinates_dict = {}
            recognition_dict = {}
            # 遍历每个识别结果，填充字典
            for idx, line in enumerate(result):
                # 填充坐标字典
                coordinates_dict[idx] = line[0]
                # 填充识别结果字典
                recognition_dict[idx] = line[1]
            return self.TextTables.get_Stork(recognition_dict[0][0]), coordinates_dict[0], recognition_dict[0][0]
        except:
            print("无法识别这个文字")
            return ["ERROR"]

