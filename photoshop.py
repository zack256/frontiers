import cv2
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def simple_bw_fix(img, threshold = 750):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if sum(img[i][j]) <= threshold:
                img[i][j] = BLACK
            else:
                img[i][j] = WHITE