import cv2
import numpy as np

def hist_equalization(img):
    if img is None:
        return None
    if img.ndim == 2:
        return cv2.equalizeHist(img)
    # Y channel equalization
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
