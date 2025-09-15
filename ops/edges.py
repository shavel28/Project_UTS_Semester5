# ops/edges.py
import cv2
import numpy as np

def _gray_u8(img):
    if img is None:
        return None
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def _mag_to_u8(gx32, gy32):
    mag = cv2.magnitude(gx32, gy32)
    m = float(mag.max())
    if m > 0:
        mag = (mag / m) * 255.0
    return np.clip(mag, 0, 255).astype(np.uint8)

def sobel_edge(img, ksize: int = 3):
    """Sobel magnitude; ksize: 1,3,5,7 (akan dipaksa ganjil-minimal 1)."""
    g = _gray_u8(img)
    k = int(ksize)
    if k < 1: k = 1
    if k % 2 == 0: k += 1
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=k)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=k)
    mag_u8 = _mag_to_u8(gx, gy)
    return cv2.cvtColor(mag_u8, cv2.COLOR_GRAY2BGR)

def prewitt_edge(img):
    """Prewitt magnitude (3x3)."""
    g = _gray_u8(img)
    kx = np.array([[-1, 0, 1],
                   [-1, 0, 1],
                   [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[ 1,  1,  1],
                   [ 0,  0,  0],
                   [-1, -1, -1]], dtype=np.float32)
    gx = cv2.filter2D(g, cv2.CV_32F, kx)
    gy = cv2.filter2D(g, cv2.CV_32F, ky)
    mag_u8 = _mag_to_u8(gx, gy)
    return cv2.cvtColor(mag_u8, cv2.COLOR_GRAY2BGR)
