# ops/morph.py
import cv2
import numpy as np

def _to_bgr_u8(img):
    if img is None:
        return None
    # buang alpha jika ada
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def _kernel(shape: str, k: int):
    k = max(1, int(k))
    if k % 2 == 0:
        k += 1  # wajib ganjil
    if shape == "cross":
        st = cv2.MORPH_CROSS
    else:
        st = cv2.MORPH_RECT
    return cv2.getStructuringElement(st, (k, k))

def morph(img, op: str, shape: str = "rect", k: int = 3):
    """
    op    : 'erode' | 'dilate' | 'open' | 'close' | 'gradient'
    shape : 'rect'  | 'cross'
    k     : ukuran kernel (ganjil)
    return: BGR uint8
    """
    src = _to_bgr_u8(img)
    if src is None:
        return None
    ker = _kernel(shape, k)

    op = (op or "").lower()
    if op == "erode":
        out = cv2.erode(src, ker, iterations=1)
    elif op == "dilate":
        out = cv2.dilate(src, ker, iterations=1)
    elif op == "open":
        out = cv2.morphologyEx(src, cv2.MORPH_OPEN, ker)
    elif op == "close":
        out = cv2.morphologyEx(src, cv2.MORPH_CLOSE, ker)
    elif op == "gradient":
        out = cv2.morphologyEx(src, cv2.MORPH_GRADIENT, ker)
    else:
        # fallback: tidak mengubah
        out = src.copy()

    # pastikan 3 channel (GUI kamu pakai konversi ke PIL)
    if out.ndim == 2:
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
    return out
