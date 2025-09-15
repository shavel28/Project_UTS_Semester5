import numpy as np
import cv2
from utils import cv2_to_pil

# Helpers
def _to_float01(img):
    if img.dtype == np.uint8:
        return img.astype(np.float32) / 255.0
    arr = img.astype(np.float32)
    m, M = arr.min(), arr.max()
    if M - m < 1e-6:
        return np.zeros_like(arr, dtype=np.float32)
    return (arr - m) / (M - m)

def _to_uint8(img01):
    return np.clip(img01 * 255.0, 0, 255).astype(np.uint8)

# RGB Tint
def apply_rgb_tint(input_cv, tint):
    pil = cv2_to_pil(input_cv).convert("RGB")
    arr = np.array(pil, dtype=np.float32) / 255.0
    tinted = arr * np.array(tint, dtype=np.float32).reshape((1, 1, 3))
    return cv2.cvtColor(_to_uint8(tinted), cv2.COLOR_RGB2BGR)

# Grayscale + wrapper
def to_grayscale_average(input_cv):
    rgb = cv2.cvtColor(input_cv, cv2.COLOR_BGR2RGB).astype(np.float32)
    return np.mean(rgb, axis=2).astype(np.uint8)

def to_grayscale_lightness(input_cv):
    rgb = cv2.cvtColor(input_cv, cv2.COLOR_BGR2RGB).astype(np.float32)
    return ((np.max(rgb, axis=2) + np.min(rgb, axis=2)) / 2.0).astype(np.uint8)

def to_grayscale_luminance(input_cv):
    rgb = cv2.cvtColor(input_cv, cv2.COLOR_BGR2RGB).astype(np.float32)
    gray = 0.299*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]
    return gray.astype(np.uint8)

def to_grayscale(input_cv, method="average"):
    if input_cv.ndim == 2:
        return input_cv.copy()
    m = (method or "average").lower()
    if m == "average":   return to_grayscale_average(input_cv)
    if m == "lightness": return to_grayscale_lightness(input_cv)
    if m in ("luminance", "luminosity"): return to_grayscale_luminance(input_cv)
    raise ValueError(f"Metode grayscale tidak dikenali: {method}")

# Invert
def invert_image(input_cv):
    return cv2.bitwise_not(input_cv)

# Brightness / Contrast
def apply_brightness_contrast(input_cv, brightness=0, contrast=1.0):
    img = input_cv.astype(np.float32)
    img = img * float(contrast) + float(brightness)
    return np.clip(img, 0, 255).astype(np.uint8)

def apply_gamma(input_cv, gamma=1.0):
    gamma = max(1e-6, float(gamma))
    inv = 1.0 / gamma
    table = (np.array([((i / 255.0) ** inv) * 255 for i in np.arange(256)])).astype("uint8")
    if input_cv.ndim == 2:
        return cv2.LUT(input_cv, table)
    b, g, r = cv2.split(input_cv)
    return cv2.merge((cv2.LUT(b, table), cv2.LUT(g, table), cv2.LUT(r, table)))

# Preset brightness
def brighter_10(img): return apply_brightness_contrast(img, brightness=+25, contrast=1.0)
def brighter_25(img): return apply_brightness_contrast(img, brightness=+64, contrast=1.0)
def brighter_50(img): return apply_brightness_contrast(img, brightness=+128, contrast=1.0)
def darker_10(img):   return apply_brightness_contrast(img, brightness=-25, contrast=1.0)
def darker_25(img):   return apply_brightness_contrast(img, brightness=-64, contrast=1.0)
def darker_50(img):   return apply_brightness_contrast(img, brightness=-128, contrast=1.0)

# Log Brightness
def apply_log_brightness(input_cv, base="e"):
    x = _to_float01(input_cv)
    if base == 10:
        y = np.log10(1.0 + x) / np.log10(2.0)
    else:
        y = np.log(1.0 + x) / np.log(2.0)
    return _to_uint8(np.clip(y, 0.0, 1.0))

# Bit Depth
def reduce_bit_depth(input_cv, bits=8):
    bits = int(max(1, min(8, bits)))
    levels = 2 ** bits
    step = 255.0 / (levels - 1)
    q = np.round(input_cv.astype(np.float32) / step) * step
    return np.clip(q, 0, 255).astype(np.uint8)
