import tkinter as tk

_TINTS = [
    ("Kuning", (1.0, 1.0, 0.0)),
    ("Orange", (1.0, 0.6, 0.0)),
    ("Cyan",   (0.0, 1.0, 1.0)),
    ("Purple", (0.6, 0.0, 1.0)),
    ("Grey",   (0.6, 0.6, 0.6)),
    ("Coklat", (0.6, 0.3, 0.0)),
    ("Merah",  (1.0, 0.0, 0.0)),
]

def build_menubar(
    root,
    # File
    on_open, on_save, on_quit,
    # View
    on_hist_input, on_hist_output, on_hist_both,
    # Colors
    on_rgb_tint,
    on_gray_avg, on_gray_light, on_gray_lumin,
    on_brightness_inc_10, on_brightness_inc_25, on_brightness_inc_50,
    on_brightness_dec_10, on_brightness_dec_25, on_brightness_dec_50,
    on_brightness_only, on_contrast_only,
    on_brightness_contrast, on_log_brightness,
    on_invert, on_gamma,
    on_bitdepth,
    # Image Processing
    on_hist_equalization, on_fuzzy_he_rgb, on_fuzzy_grayscale,
    # Filter (lengkap)
    on_filter_identity,
    on_edge1, on_edge2, on_edge3, on_canny,
    on_sharpen,
    on_gauss3, on_gauss5,
    on_unsharp_mask,
    on_average,
    on_lowpass,
    on_highpass,
    on_bandstop,
    # Edge Detection menu terpisah
    on_prewitt, on_sobel,
    # Morfologi (generic callback: on_morph(op, shape, size))
    on_morph,
    # Arit
    on_open_input1, on_open_input2,
    on_arith_add, on_arith_sub, on_arith_mul, on_arith_div, on_arith_blend,
    on_arith_panel=None,
    # About
    on_about=None,
):
    menubar = tk.Menu(root)

    # File
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Buka…", command=on_open)
    filemenu.add_command(label="Simpan Sebagai…", command=on_save)
    filemenu.add_separator()
    filemenu.add_command(label="Keluar", command=on_quit)
    menubar.add_cascade(label="File", menu=filemenu)

    # View
    viewmenu = tk.Menu(menubar, tearoff=0)
    histmenu = tk.Menu(viewmenu, tearoff=0)
    histmenu.add_command(label="Input",          command=on_hist_input)
    histmenu.add_command(label="Output",         command=on_hist_output)
    histmenu.add_command(label="Input & Output", command=on_hist_both)
    viewmenu.add_cascade(label="Histogram", menu=histmenu)
    menubar.add_cascade(label="View", menu=viewmenu)

    # Colors
    colorsmenu = tk.Menu(menubar, tearoff=0)

    # RGB →
    rgbmenu = tk.Menu(colorsmenu, tearoff=0)
    for name, tint in _TINTS:
        rgbmenu.add_command(label=name, command=lambda t=tint: on_rgb_tint(t))
    colorsmenu.add_cascade(label="RGB", menu=rgbmenu)

    # RGB → Grayscale
    graymenu = tk.Menu(colorsmenu, tearoff=0)
    graymenu.add_command(label="Average",   command=on_gray_avg)
    graymenu.add_command(label="Lightness", command=on_gray_light)
    graymenu.add_command(label="Luminance", command=on_gray_lumin)
    colorsmenu.add_cascade(label="RGB → Grayscale", menu=graymenu)

    # Brightness
    br = tk.Menu(colorsmenu, tearoff=0)
    br.add_command(label="Contrast…", command=on_contrast_only)
    br.add_separator()
    inc = tk.Menu(br, tearoff=0)
    inc.add_command(label="Increase 10%", command=on_brightness_inc_10)
    inc.add_command(label="Increase 25%", command=on_brightness_inc_25)
    inc.add_command(label="Increase 50%", command=on_brightness_inc_50)
    dec = tk.Menu(br, tearoff=0)
    dec.add_command(label="Decrease 10%", command=on_brightness_dec_10)
    dec.add_command(label="Decrease 25%", command=on_brightness_dec_25)
    dec.add_command(label="Decrease 50%", command=on_brightness_dec_50)
    br.add_cascade(label="Increase", menu=inc)
    br.add_cascade(label="Decrease", menu=dec)
    br.add_separator()
    br.add_command(label="Custom Brightness…", command=on_brightness_only)
    colorsmenu.add_cascade(label="Brightness", menu=br)

    colorsmenu.add_command(label="Brightness + Contrast…", command=on_brightness_contrast)
    colorsmenu.add_command(label="Log Brightness", command=on_log_brightness)

    bd = tk.Menu(colorsmenu, tearoff=0)
    for bits in range(1, 9):
        bd.add_command(label=f"{bits}-bit", command=lambda b=bits: on_bitdepth(b))
    colorsmenu.add_cascade(label="Bit Depth", menu=bd)

    colorsmenu.add_command(label="Inverse",           command=on_invert)
    colorsmenu.add_command(label="Gamma Correction…", command=on_gamma)
    menubar.add_cascade(label="Colors", menu=colorsmenu)

    # About
    about = tk.Menu(menubar, tearoff=0)
    if on_about:
        about.add_command(label="Tentang", command=on_about)
    menubar.add_cascade(label="Tentang", menu=about)

    # Image Processing
    ip = tk.Menu(menubar, tearoff=0)
    ip.add_command(label="Histogram Equalization", command=on_hist_equalization)
    ip.add_command(label="Fuzzy HE (RGB)",         command=on_fuzzy_he_rgb)
    ip.add_command(label="Fuzzy Grayscale",        command=on_fuzzy_grayscale)
    menubar.add_cascade(label="Image Processing", menu=ip)

    # Aritmetical Operation
    ar = tk.Menu(menubar, tearoff=0)
    if on_arith_panel:
        ar.add_command(label="Open Arithmetic Panel…", command=on_arith_panel)
        ar.add_separator()
    else:
        ar.add_command(label="Open Arithmetic Panel…", state="disabled")
        ar.add_separator()
    menubar.add_cascade(label="Aritmetical Operation", menu=ar)


    # Filter (lengkap)
    fmenu = tk.Menu(menubar, tearoff=0)
    fmenu.add_command(label="Identity", command=on_filter_identity)
    ed = tk.Menu(fmenu, tearoff=0)
    ed.add_command(label="Edge Detection 1", command=on_edge1)
    ed.add_command(label="Edge Detection 2", command=on_edge2)
    ed.add_command(label="Edge Detection 3", command=on_edge3)
    ed.add_separator()
    ed.add_command(label="Canny Edge…", command=on_canny)
    fmenu.add_cascade(label="Edge Detection", menu=ed)
    fmenu.add_command(label="Sharpen", command=on_sharpen)
    gb = tk.Menu(fmenu, tearoff=0)
    gb.add_command(label="Gaussian Blur 3×3", command=on_gauss3)
    gb.add_command(label="Gaussian Blur 5×5", command=on_gauss5)
    fmenu.add_cascade(label="Gaussian Blur", menu=gb)
    fmenu.add_command(label="Unsharp Masking", command=on_unsharp_mask)
    fmenu.add_command(label="Average Filter",  command=on_average)
    fmenu.add_command(label="Low Pass Filter", command=on_lowpass)
    fmenu.add_command(label="High Pass Filter", command=on_highpass)
    fmenu.add_command(label="Bandstop Filter", command=on_bandstop)
    menubar.add_cascade(label="Filter", menu=fmenu)

    # Edge Detection (menu terpisah)
    ed2 = tk.Menu(menubar, tearoff=0)
    ed2.add_command(label="Prewitt", command=on_prewitt)
    ed2.add_command(label="Sobel",   command=on_sobel)
    menubar.add_cascade(label="Edge Detection", menu=ed2)

    # ===== Morfologi (baru) =====
    # Helper khusus untuk setiap operasi
    def _menu_erosion(parent_menu):
        sub = tk.Menu(parent_menu, tearoff=0)
        sub.add_command(label="Square 3", command=lambda: on_morph("erode", "rect", 3))
        sub.add_command(label="Square 5", command=lambda: on_morph("erode", "rect", 5))
        sub.add_separator()
        sub.add_command(label="Cross 3",  command=lambda: on_morph("erode", "cross", 3))
        return sub

    def _menu_dilation(parent_menu):
        sub = tk.Menu(parent_menu, tearoff=0)
        sub.add_command(label="Square 3", command=lambda: on_morph("dilate", "rect", 3))
        sub.add_command(label="Square 5", command=lambda: on_morph("dilate", "rect", 5))
        sub.add_separator()
        sub.add_command(label="Cross 3",  command=lambda: on_morph("dilate", "cross", 3))
        return sub

    def _menu_opening(parent_menu):
        sub = tk.Menu(parent_menu, tearoff=0)
        sub.add_command(label="Square 9", command=lambda: on_morph("open", "rect", 9))
        return sub

    def _menu_closing(parent_menu):
        sub = tk.Menu(parent_menu, tearoff=0)
        sub.add_command(label="Square 9", command=lambda: on_morph("close", "rect", 9))
        return sub

    morph = tk.Menu(menubar, tearoff=0)
    morph.add_cascade(label="Erosion",  menu=_menu_erosion(morph))
    morph.add_cascade(label="Dilation", menu=_menu_dilation(morph))
    morph.add_cascade(label="Opening",  menu=_menu_opening(morph))
    morph.add_cascade(label="Closing",  menu=_menu_closing(morph))

    menubar.add_cascade(label="Morfologi", menu=morph)


    return menubar
