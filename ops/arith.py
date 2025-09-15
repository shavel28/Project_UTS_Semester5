import cv2
import numpy as np

def _to_float01(img):
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img.astype(np.float32) / 255.0

def _to_bgr(img):
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.ndim == 3 and img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

def _same_size_channels(a, b):
    if a.shape[:2] != b.shape[:2]:
        h, w = a.shape[:2]
        b = cv2.resize(b, (w, h), interpolation=cv2.INTER_AREA)
    a = _to_bgr(a)
    b = _to_bgr(b)
    return a, b

def add_images(i1, i2):
    a, b = _same_size_channels(i1, i2)
    return cv2.add(a, b)

def sub_images(i1, i2, mode="clamp"):
    a, b = _same_size_channels(i1, i2)
    if mode == "abs":
        return cv2.absdiff(a, b)
    return cv2.subtract(a, b)

def mul_images(i1, i2):
    a, b = _same_size_channels(i1, i2)
    out = (_to_float01(a) * _to_float01(b)) * 255.0
    return np.clip(out, 0, 255).astype(np.uint8)

def div_images(i1, i2, eps=1e-6):
    a, b = _same_size_channels(i1, i2)
    af, bf = _to_float01(a), _to_float01(b)
    safe = np.where(bf < eps, 1.0, bf)
    out = af / safe
    return np.clip(out * 255.0, 0, 255).astype(np.uint8)

def blend_images(i1, i2, alpha=0.5):
    a, b = _same_size_channels(i1, i2)
    alpha = float(np.clip(alpha, 0.0, 1.0))
    return cv2.addWeighted(a, alpha, b, 1.0 - alpha, 0.0)
