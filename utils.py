from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox

def cv2_to_pil(cv_img):
    if cv_img is None:
        return None
    if len(cv_img.shape) == 2:
        return Image.fromarray(cv_img)
    b, g, r = cv2.split(cv_img)
    img = cv2.merge((r, g, b))
    return Image.fromarray(img)

def pil_to_cv2(pil_img):
    arr = np.array(pil_img)
    if arr.ndim == 2:
        return arr
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def ensure_image_loaded(img, title="Image required"):
    if img is None:
        messagebox.showinfo("Info", "Tidak ada citra yang akan diolah")
        return False
    return True

def show_histogram(cv_img, title="Histogram"):
    if cv_img is None:
        messagebox.showinfo("Info", "Tidak ada citra yang akan diolah")
        return
    plt.figure(figsize=(6, 3))
    if len(cv_img.shape) == 2:
        plt.hist(cv_img.ravel(), bins=256, color="black")
        plt.title(title + " (grayscale)")
    else:
        colors = ('b', 'g', 'r')
        for i, col in enumerate(colors):
            plt.hist(cv_img[:, :, i].ravel(), bins=256, alpha=0.6, label=col, color=col)
        plt.title(title + " (BGR channels)")
        plt.legend()
    plt.tight_layout()
    plt.show()
