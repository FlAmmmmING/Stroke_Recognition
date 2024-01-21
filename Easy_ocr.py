# 测试了一下，认为easyocr在书法识别上的准确性不及paddleocr
# 2024/1/21 蒋玮杰
import easyocr

img_path = "cutting/0.jpg"
reader = easyocr.Reader(['ch_sim'], gpu=True)
result = reader.readtext(img_path)
print(result)
