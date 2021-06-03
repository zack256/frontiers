import cv2
import os

img_path = os.getcwd() + "/data/test.png"

def display_img():
    img = cv2.imread(img_path)
    cv2.imshow("hello!", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()