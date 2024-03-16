import cv2
import numpy as np


def imgbytes2cv(image):
    pdf_byte = image.stream.read()
    image = cv2.imdecode(np.frombuffer(pdf_byte, np.uint8), cv2.IMREAD_COLOR)
    cv2.imshow('image', image)
    cv2.waitKey(0)
