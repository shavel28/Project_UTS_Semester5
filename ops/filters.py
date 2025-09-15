# ops/filters.py
import cv2
import numpy as np

def _ensure_u8(img):
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def _apply_kernel(img, kernel):
    img = _ensure_u8(img)
    if img.ndim == 2:
        return cv2.filter2D(img, -1, kernel)
    # proses per-channel agar BGRA/ BGR aman
    if img.ndim == 3 and img.shape[2] in (3, 4):
        chs = cv2.split(img[:, :, :3])
        out = [cv2.filter2D(c, -1, kernel) for c in chs]
        merged = cv2.merge(out)
        if img.shape[2] == 4:  # kembalikan alpha jika ada
            return np.dstack([merged, img[:, :, 3]])
        return merged
    return img

# ===== dasar =====
def identity(img):
    k = np.array([[0,0,0],[0,1,0],[0,0,0]], np.float32)
    return _apply_kernel(img, k)

def sharpen(img):
    k = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]], np.float32)
    return _apply_kernel(img, k)

def gaussian_blur(img, ksize=3, sigma=0):
    img = _ensure_u8(img)
    k = int(ksize) if int(ksize) % 2 == 1 else int(ksize)+1
    return cv2.GaussianBlur(img, (k, k), sigma)

def average_filter(img, ksize=3):
    img = _ensure_u8(img)
    k = int(ksize) if int(ksize) % 2 == 1 else int(ksize)+1
    return cv2.blur(img, (k, k))

# ===== edge detection =====
def edge1(img):
    # Laplacian 8-neighbour
    k = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]], np.float32)
    return _apply_kernel(img, k)

def edge2(img):
    # Laplacian 4-neighbour
    k = np.array([[0,1,0],[1,-4,1],[0,1,0]], np.float32)
    return _apply_kernel(img, k)

def edge3(img):
    # Roberts-like diagonal emphasis
    k = np.array([[1,0,-1],[0,0,0],[-1,0,1]], np.float32)
    return _apply_kernel(img, k)

def canny_edge(img, t1=100, t2=200):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if (img.ndim==3 and img.shape[2]>=3) else img
    g = _ensure_u8(g)
    edges = cv2.Canny(g, int(t1), int(t2))
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

# ===== lain-lain =====
def unsharp_mask(img, ksize=5, amount=1.0):
    """USM = original + amount*(original - blur)"""
    blur = gaussian_blur(img, ksize)
    high = cv2.subtract(img, blur)
    out  = cv2.addWeighted(img, 1.0, high, float(amount), 0.0)
    return out

def low_pass(img, ksize=5):
    return gaussian_blur(img, ksize)

def high_pass(img):
    # high-boost kernel sederhana
    k = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]], np.float32)
    return _apply_kernel(img, k)

def bandstop(img, ksmall=3, klarge=9, strength=1.0):
    """Bandstop = original - bandpass(DoG)."""
    g1 = gaussian_blur(img, ksmall)
    g2 = gaussian_blur(img, klarge)
    bandpass = cv2.subtract(g1, g2)  # DoG ≈ bandpass
    out = cv2.addWeighted(img, 1.0, bandpass, -float(strength), 0.0)
    return np.clip(out, 0, 255).astype(np.uint8)
