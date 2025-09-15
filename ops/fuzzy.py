import cv2

def fuzzy_he_rgb(img):
    # TODO: ganti dengan algoritma fuzzy HE beneran jika diperlukan
    return img.copy()

def fuzzy_grayscale(img):
    if img.ndim == 2:
        return img.copy()
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
