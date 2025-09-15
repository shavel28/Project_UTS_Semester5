import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2

from utils import cv2_to_pil
from ops.arith import add_images, sub_images, mul_images, div_images, blend_images


class ArithPanel(tk.Toplevel):
    """
    Popup 3 panel (Input 1, Input 2, Output) untuk operasi aritmatika.
    on_send(output_cv) dipanggil ketika user klik 'Use as Main Output'.
    """
    def __init__(self, master, init_i1=None, init_i2=None, on_send=None):
        super().__init__(master)
        self.title("Arithmetical Operation")
        self.geometry("1200x580")
        self.resizable(True, True)

        self.on_send = on_send
        self.i1 = init_i1
        self.i2 = init_i2
        self.out = None

        # ===== Layout =====
        wrap = tk.Frame(self); wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        lf1 = tk.LabelFrame(wrap, text="Input 1")
        lf2 = tk.LabelFrame(wrap, text="Input 2")
        lf3 = tk.LabelFrame(wrap, text="Output")
        for lf in (lf1, lf2, lf3):
            lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lbl1 = tk.Label(lf1); self.lbl1.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.lbl2 = tk.Label(lf2); self.lbl2.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.lbl3 = tk.Label(lf3); self.lbl3.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        ctrl = tk.Frame(self); ctrl.pack(fill=tk.X, padx=10, pady=(0,10))

        tk.Button(ctrl, text="Load Input 1", command=self.load_i1).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Load Input 2", command=self.load_i2).pack(side=tk.LEFT, padx=4)
        tk.Label(ctrl, text=" | ").pack(side=tk.LEFT)

        tk.Button(ctrl, text="Add",      command=lambda: self.run("add")).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Subtract", command=lambda: self.run("sub")).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Multiply", command=lambda: self.run("mul")).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Divide",   command=lambda: self.run("div")).pack(side=tk.LEFT, padx=4)

        tk.Label(ctrl, text="   α:").pack(side=tk.LEFT, padx=(10,0))
        self.alpha = tk.DoubleVar(value=0.5)
        tk.Scale(ctrl, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL,
                 variable=self.alpha, length=140).pack(side=tk.LEFT)
        tk.Button(ctrl, text="Blend", command=lambda: self.run("blend")).pack(side=tk.LEFT, padx=4)

        tk.Label(ctrl, text=" | ").pack(side=tk.LEFT)
        tk.Button(ctrl, text="Use as Main Output", command=self.send_to_main).pack(side=tk.LEFT, padx=8)
        tk.Button(ctrl, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=4)

        if self.i1 is not None: self._show(self.i1, self.lbl1)
        if self.i2 is not None: self._show(self.i2, self.lbl2)

    # ---------- utils ----------
    def _ask_open(self, title):
        return filedialog.askopenfilename(
            title=title,
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
        )

    def _thumb(self, pil_img, max_size=(360, 360)):
        p = pil_img.copy()
        p.thumbnail(max_size, Image.Resampling.LANCZOS)
        return p

    def _show(self, cv_img, label):
        pil = self._thumb(cv2_to_pil(cv_img))
        imgtk = ImageTk.PhotoImage(pil)
        label.configure(image=imgtk)
        label.image = imgtk

    def _need_two(self):
        if self.i1 is None or self.i2 is None:
            messagebox.showinfo("Info", "Load Input 1 dan Input 2 dulu.")
            return False
        return True

    # ---------- actions ----------
    def load_i1(self):
        p = self._ask_open("Buka Input 1")
        if not p: return
        img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None: messagebox.showerror("Error", "Gagal membuka gambar."); return
        self.i1 = img
        self._show(self.i1, self.lbl1)

    def load_i2(self):
        p = self._ask_open("Buka Input 2")
        if not p: return
        img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None: messagebox.showerror("Error", "Gagal membuka gambar."); return
        self.i2 = img
        self._show(self.i2, self.lbl2)

    def run(self, kind):
        if not self._need_two(): return
        if kind == "add":      self.out = add_images(self.i1, self.i2)
        elif kind == "sub":    self.out = sub_images(self.i1, self.i2)
        elif kind == "mul":    self.out = mul_images(self.i1, self.i2)
        elif kind == "div":    self.out = div_images(self.i1, self.i2)
        elif kind == "blend":  self.out = blend_images(self.i1, self.i2, alpha=float(self.alpha.get()))
        else: return
        self._show(self.out, self.lbl3)

    def send_to_main(self):
        if self.out is None:
            messagebox.showinfo("Info", "Belum ada Output."); return
        if callable(self.on_send):
            self.on_send(self.out.copy())
            messagebox.showinfo("OK", "Output dikirim ke jendela utama.")
