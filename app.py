import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import cv2

from utils import cv2_to_pil, ensure_image_loaded, show_histogram
from ui.menus import build_menubar
from ui.arith_panel import ArithPanel

# Ops Colors
from ops.colors import (
    apply_rgb_tint, to_grayscale, invert_image,
    apply_brightness_contrast, apply_gamma,
    brighter_10, brighter_25, brighter_50,
    darker_10, darker_25, darker_50,
    apply_log_brightness, reduce_bit_depth,
)

# Ops lain
from ops.histogram import hist_equalization
from ops.fuzzy import fuzzy_he_rgb, fuzzy_grayscale
from ops.arith import add_images, sub_images, mul_images, div_images, blend_images

# Filter lengkap
from ops.filters import (
    identity, edge1, edge2, edge3, canny_edge,
    sharpen, gaussian_blur, unsharp_mask, average_filter,
    low_pass, high_pass, bandstop,
)

# Edge Detection (menu terpisah)
from ops.edges import prewitt_edge, sobel_edge

# ===== Morfologi (NEW) =====
# gunakan fungsi generik agar menu bisa mengirim (op, shape, size)
# op: "erode" | "dilate" | "open" | "close" | "gradient"
# shape: "rect" | "cross"
# size: 3,5,7,9 (ganjil)
from ops.morph import morph


class ImageApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Processing App (Modular)")
        self.root.geometry("1200x650")

        # buffers
        self.input1_cv = None      # tampil di panel kiri
        self.input2_cv = None      # buffer utk arith (tidak tampil di utama)
        self.output_cv = None      # tampil di panel kanan

        # Menubar
        menubar = build_menubar(
            root=self.root,
            # File
            on_open=self.open_image1,
            on_save=self.save_output,
            on_quit=self.root.quit,
            # View
            on_hist_input=lambda: show_histogram(self.input1_cv, "Histogram Input"),
            on_hist_output=lambda: show_histogram(self.output_cv, "Histogram Output"),
            on_hist_both=lambda: (show_histogram(self.input1_cv, "Histogram Input"),
                                  show_histogram(self.output_cv, "Histogram Output")),
            # Colors
            on_rgb_tint=self.apply_rgb_tint_dialogless,
            on_gray_avg=lambda: self.rgb_to_grayscale("average"),
            on_gray_light=lambda: self.rgb_to_grayscale("lightness"),
            on_gray_lumin=lambda: self.rgb_to_grayscale("luminance"),
            on_brightness_inc_10=self.brightness_inc_10,
            on_brightness_inc_25=self.brightness_inc_25,
            on_brightness_inc_50=self.brightness_inc_50,
            on_brightness_dec_10=self.brightness_dec_10,
            on_brightness_dec_25=self.brightness_dec_25,
            on_brightness_dec_50=self.brightness_dec_50,
            on_brightness_only=self.brightness_dialog,
            on_contrast_only=self.contrast_only_dialog,
            on_brightness_contrast=self.brightness_contrast_dialog,
            on_log_brightness=self.log_brightness,
            on_invert=self.invert_colors,
            on_gamma=self.gamma_dialog,
            on_bitdepth=self.apply_bit_depth,
            # Image Processing
            on_hist_equalization=self.do_hist_equalization,
            on_fuzzy_he_rgb=self.do_fuzzy_he_rgb,
            on_fuzzy_grayscale=self.do_fuzzy_grayscale,

            # ===== Filter lengkap =====
            on_filter_identity=self.do_identity,
            on_edge1=self.do_edge1,
            on_edge2=self.do_edge2,
            on_edge3=self.do_edge3,
            on_canny=self.canny_dialog,
            on_sharpen=self.do_sharpen,
            on_gauss3=lambda: self.do_gauss(3),
            on_gauss5=lambda: self.do_gauss(5),
            on_unsharp_mask=self.do_unsharp,
            on_average=self.do_average,
            on_lowpass=self.do_lowpass,
            on_highpass=self.do_highpass,
            on_bandstop=self.do_bandstop,

            # ===== Edge Detection (menu terpisah) =====
            on_prewitt=self.do_prewitt,
            on_sobel=self.sobel_dialog,

            # ===== Morfologi (menu baru) =====
            # build_menubar akan memanggil on_morph(op, shape, size)
            on_morph=self.morph_action,

            # Aritmetical Operation
            on_open_input1=self.open_image1,
            on_open_input2=self.open_image2,
            on_arith_add=self.arith_add,
            on_arith_sub=self.arith_sub,
            on_arith_mul=self.arith_mul,
            on_arith_div=self.arith_div,
            on_arith_blend=self.arith_blend,
            on_arith_panel=self.open_arith_panel,   # popup 3 panel

            # About
            on_about=self.show_about,
        )
        self.root.config(menu=menubar)

        # ===== Layout 2 panel (Input 1 | Output) =====
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left  = tk.LabelFrame(frame, text="Input 1", width=580, height=520)
        right = tk.LabelFrame(frame, text="Output",  width=580, height=520)

        left.pack(side=tk.LEFT,  fill=tk.BOTH, expand=True, padx=5, pady=5)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.left_label  = tk.Label(left);  self.left_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.right_label = tk.Label(right); self.right_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status = tk.Label(self.root, text="Siap", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- util tampilan ----------
    def _thumb(self, pil_img, max_size=(560, 520)):
        pil = pil_img.copy()
        pil.thumbnail(max_size, Image.Resampling.LANCZOS)
        bg = Image.new("RGB", max_size, (240, 240, 240))
        x = (max_size[0] - pil.width) // 2
        y = (max_size[1] - pil.height) // 2
        bg.paste(pil, (x, y))
        return bg

    def update_display(self):
        if self.input1_cv is not None:
            self.left_photo = ImageTk.PhotoImage(self._thumb(cv2_to_pil(self.input1_cv)))
            self.left_label.config(image=self.left_photo)
        else:
            self.left_label.config(image="")

        if self.output_cv is not None:
            self.right_photo = ImageTk.PhotoImage(self._thumb(cv2_to_pil(self.output_cv)))
            self.right_label.config(image=self.right_photo)
        else:
            self.right_label.config(image="")

    # ---------- helpers ----------
    def _active(self):
        return self.output_cv if self.output_cv is not None else self.input1_cv

    def _ask_open(self, title):
        return filedialog.askopenfilename(
            title=title,
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*.*")]
        )

    # ---------- File ops ----------
    def open_image1(self):
        path = self._ask_open("Buka Input 1")
        if not path: return
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None:
            messagebox.showerror("Error", "Gagal membuka Input 1"); return
        self.input1_cv = img
        self.status.config(text=f"Input 1: {path}")
        self.update_display()

    def open_image2(self):
        path = self._ask_open("Buka Input 2")
        if not path: return
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None:
            messagebox.showerror("Error", "Gagal membuka Input 2"); return
        self.input2_cv = img
        self.status.config(text=f"Input 2 dimuat: {path}")
        # tidak memanggil update_display() — Input 2 tidak ditampilkan di utama

    def save_output(self):
        if self.output_cv is None:
            messagebox.showinfo("Info", "Output kosong"); return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")]
        )
        if not path: return
        cv2.imwrite(path, self.output_cv)
        messagebox.showinfo("Simpan", f"Output tersimpan di:\n{path}")

    # ---------- About ----------
    def show_about(self):
        messagebox.showinfo(
            "Tentang",
        "Tugas UTS Workshop Pengolahan Citra dan Vision\n"
        "Versi 1.0\n\n"
        "Creator : Shava Selvia R.S\n"
        "NIM     : E41231350\n"
        "Kelas   : B SEM 5 TIF 23\n\n"
        )

    # ---------- Colors ----------
    def apply_rgb_tint_dialogless(self, tint_tuple):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = apply_rgb_tint(self._active(), tint_tuple)
        self.update_display()

    def rgb_to_grayscale(self, method="average"):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = to_grayscale(self._active(), method=method)
        self.update_display()

    def invert_colors(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = invert_image(self._active())
        self.update_display()

    def brightness_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        offset = simpledialog.askinteger("Brightness", "-255..255", minvalue=-255, maxvalue=255, initialvalue=0)
        if offset is None: return
        base = self._active().astype(np.int16) + int(offset)
        self.output_cv = np.clip(base, 0, 255).astype(np.uint8)
        self.update_display()

    def contrast_only_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        c = simpledialog.askfloat("Contrast", "0.1..3.0", minvalue=0.01, maxvalue=5.0, initialvalue=1.0)
        if c is None: return
        img = self._active().astype(np.float32)
        img = (img - 128.0) * float(c) + 128.0
        self.output_cv = np.clip(img, 0, 255).astype(np.uint8)
        self.update_display()

    def brightness_contrast_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        b = simpledialog.askinteger("Brightness", "-255..255", minvalue=-255, maxvalue=255, initialvalue=0)
        if b is None: return
        c = simpledialog.askfloat("Contrast", "0.01..5.0", minvalue=0.01, maxvalue=5.0, initialvalue=1.0)
        if c is None: return
        self.output_cv = apply_brightness_contrast(self._active(), brightness=b, contrast=c)
        self.update_display()

    def gamma_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        g = simpledialog.askfloat("Gamma", "0.1..5.0", minvalue=0.1, maxvalue=5.0, initialvalue=1.0)
        if g is None: return
        self.output_cv = apply_gamma(self._active(), gamma=g)
        self.update_display()

    # preset brightness
    def brightness_inc_10(self): 
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = brighter_10(self._active()); self.update_display()
    def brightness_inc_25(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = brighter_25(self._active()); self.update_display()
    def brightness_inc_50(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = brighter_50(self._active()); self.update_display()
    def brightness_dec_10(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = darker_10(self._active()); self.update_display()
    def brightness_dec_25(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = darker_25(self._active()); self.update_display()
    def brightness_dec_50(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = darker_50(self._active()); self.update_display()

    def log_brightness(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = apply_log_brightness(self._active(), base="e")
        self.update_display()

    def apply_bit_depth(self, bits: int):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = reduce_bit_depth(self._active(), bits=int(bits))
        self.update_display()

    # ---------- Image Processing ----------
    def do_hist_equalization(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = hist_equalization(self._active()); self.update_display()

    def do_fuzzy_he_rgb(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = fuzzy_he_rgb(self._active()); self.update_display()

    def do_fuzzy_grayscale(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = fuzzy_grayscale(self._active()); self.update_display()

    # ---------- Filter ----------
    def do_identity(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = identity(self._active()); self.update_display()

    def do_edge1(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = edge1(self._active()); self.update_display()

    def do_edge2(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = edge2(self._active()); self.update_display()

    def do_edge3(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = edge3(self._active()); self.update_display()

    def canny_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        t1 = simpledialog.askinteger("Canny Edge", "Threshold 1 (0..255)",
                                     minvalue=0, maxvalue=255, initialvalue=100)
        if t1 is None: return
        t2 = simpledialog.askinteger("Canny Edge", "Threshold 2 (0..255)",
                                     minvalue=0, maxvalue=255, initialvalue=200)
        if t2 is None: return
        self.output_cv = canny_edge(self._active(), t1, t2)
        self.update_display()

    def do_sharpen(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = sharpen(self._active()); self.update_display()

    def do_gauss(self, k):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = gaussian_blur(self._active(), k); self.update_display()

    def do_unsharp(self):
        if not ensure_image_loaded(self.input1_cv): return
        amt = simpledialog.askfloat("Unsharp Masking", "Amount (0.1..3.0)",
                                    minvalue=0.1, maxvalue=3.0, initialvalue=1.0)
        if amt is None: return
        self.output_cv = unsharp_mask(self._active(), 5, amt); self.update_display()

    def do_average(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = average_filter(self._active(), 3); self.update_display()

    def do_lowpass(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = low_pass(self._active(), 5); self.update_display()

    def do_highpass(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = high_pass(self._active()); self.update_display()

    def do_bandstop(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = bandstop(self._active(), 3, 11, 1.0); self.update_display()

    # ---------- Edge Detection (menu terpisah) ----------
    def do_prewitt(self):
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = prewitt_edge(self._active())
        self.update_display()

    def sobel_dialog(self):
        if not ensure_image_loaded(self.input1_cv): return
        k = simpledialog.askinteger("Sobel", "Kernel size (1/3/5/7)", minvalue=1, maxvalue=7, initialvalue=3)
        if k is None: return
        if k % 2 == 0 and k != 1:
            k += 1
        self.output_cv = sobel_edge(self._active(), k)
        self.update_display()

    # ---------- Morfologi (NEW) ----------
    def morph_action(self, op: str, shape: str, size: int):
        """
        op    : 'erode' | 'dilate' | 'open' | 'close' | 'gradient'
        shape : 'rect'  | 'cross'
        size  : ganjil, contoh 3/5/7/9
        """
        if not ensure_image_loaded(self.input1_cv): return
        self.output_cv = morph(self._active(), op=op, shape=shape, k=size)
        self.update_display()

    # ---------- Aritmetical Operation ----------
    def _need_two(self):
        if self.input1_cv is None or self.input2_cv is None:
            messagebox.showinfo("Info", "Mohon buka Input 1 dan Input 2 terlebih dahulu.")
            return False
        return True

    def arith_add(self):
        if not self._need_two(): return
        self.output_cv = add_images(self.input1_cv, self.input2_cv); self.update_display()

    def arith_sub(self):
        if not self._need_two(): return
        self.output_cv = sub_images(self.input1_cv, self.input2_cv); self.update_display()

    def arith_mul(self):
        if not self._need_two(): return
        self.output_cv = mul_images(self.input1_cv, self.input2_cv); self.update_display()

    def arith_div(self):
        if not self._need_two(): return
        self.output_cv = div_images(self.input1_cv, self.input2_cv); self.update_display()

    def arith_blend(self):
        if not self._need_two(): return
        alpha = simpledialog.askfloat("Blend", "Alpha 0..1", minvalue=0.0, maxvalue=1.0, initialvalue=0.5)
        if alpha is None: return
        self.output_cv = blend_images(self.input1_cv, self.input2_cv, alpha=alpha)
        self.update_display()

    # ---------- Arithmetic Panel Popup ----------
    def open_arith_panel(self):
        ArithPanel(self.root, init_i1=self.input1_cv, init_i2=self.input2_cv, on_send=self._receive_from_panel)

    def _receive_from_panel(self, output_cv):
        self.output_cv = output_cv
        self.update_display()


def run_app():
    root = tk.Tk()
    app = ImageApp(root)
    try:
        root.mainloop()
    except Exception as e:
        print("GUI exited:", e)
