import sys
import os
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilenames
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    base_dir = Path(sys._MEIPASS)
except:
    base_dir = Path(os.getcwd())

selected_files = []
selected_output_dir = None


def select_files(view: ttk.Label):
    files = askopenfilenames(
        title="Select images",
        filetypes=[("Images", "*.jpg *.jpeg *.png")]
    )
    global selected_files
    selected_files = [Path(f) for f in files]
    view.configure(text=f"{len(selected_files)} files selected")


def select_dir(view: ttk.Label):
    global selected_output_dir
    selected_output_dir = Path(askdirectory(title="Select output directory"))
    view.configure(text=str(selected_output_dir))


def update_mode(mode, x, y, s):
    x.configure(state="normal" if mode.get() in ("fixed", "width", "height") else "disabled")
    y.configure(state="normal" if mode.get() in ("fixed", "width", "height") else "disabled")
    s.configure(state="normal" if mode.get() == "scale" else "disabled")


def apply_watermark(im: Image.Image, text: str) -> Image.Image:
    if not text:
        return im

    im = im.convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = im.size
    font_size = max(12, int(min(w, h) * 0.035))

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    margin = int(font_size * 0.6)
    x = w - tw - margin
    y = h - th - margin

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 120))

    return Image.alpha_composite(im, overlay).convert("RGB")


def on_compute_resize(files, mode, X, Y, S, watermark, err_label, outDir, pb):
    if not files or outDir is None:
        err_label.configure(text="Select files and output directory")
        return

    try:
        x = int(X.get()) if X.get() else None
        y = int(Y.get()) if Y.get() else None
        s = float(S.get()) if S.get() else None
    except:
        err_label.configure(text="Invalid numeric input")
        return

    pb.configure(maximum=len(files), value=0)

    for file in files:
        im = Image.open(file)
        w, h = im.size

        if mode.get() == "scale":
            new_size = (int(w * s), int(h * s))
        elif mode.get() == "fixed":
            new_size = (x, y)
        elif mode.get() == "width":
            new_size = (x, int(h * x / w))
        elif mode.get() == "height":
            new_size = (int(w * y / h), y)

        im = im.resize(new_size, Image.NEAREST)
        im = apply_watermark(im, watermark.get())
        im.save(outDir / file.name)

        pb.step(1)

    err_label.configure(text="Done")


def main():
    root = Tk()
    root.title("Batch Image Resizer")
    root.geometry("540x460")

    style = ttk.Style(root)
    style.theme_use("clam")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frm = ttk.Frame(root, padding=16)
    frm.grid(sticky="nsew")
    frm.columnconfigure(1, weight=1)

    ttk.Label(frm, text="Batch Image Resizer", font=("Segoe UI", 13, "bold")).grid(
        row=0, column=0, columnspan=3, pady=(0, 12)
    )

    files_lbl = ttk.Label(frm, text="No files selected")
    ttk.Button(frm, text="Select Images", command=lambda: select_files(files_lbl)).grid(row=1, column=0, sticky="w")
    files_lbl.grid(row=1, column=1, columnspan=2, sticky="w")

    out_lbl = ttk.Label(frm, text="No output directory")
    ttk.Button(frm, text="Output Directory", command=lambda: select_dir(out_lbl)).grid(row=2, column=0, sticky="w")
    out_lbl.grid(row=2, column=1, columnspan=2, sticky="w")

    ttk.Separator(frm).grid(row=3, column=0, columnspan=3, sticky="ew", pady=12)

    mode = StringVar(value="fixed")

    ttk.Radiobutton(frm, text="Fixed WxH", variable=mode, value="fixed").grid(row=4, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Scale", variable=mode, value="scale").grid(row=5, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Fixed Width", variable=mode, value="width").grid(row=6, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Fixed Height", variable=mode, value="height").grid(row=7, column=0, sticky="w")

    X = ttk.Entry(frm, width=10)
    Y = ttk.Entry(frm, width=10)
    S = ttk.Entry(frm, width=10)

    ttk.Label(frm, text="Width").grid(row=4, column=1, sticky="e")
    X.grid(row=4, column=2, sticky="w")
    ttk.Label(frm, text="Height").grid(row=5, column=1, sticky="e")
    Y.grid(row=5, column=2, sticky="w")
    ttk.Label(frm, text="Scale").grid(row=6, column=1, sticky="e")
    S.grid(row=6, column=2, sticky="w")

    mode.trace_add("write", lambda *_: update_mode(mode, X, Y, S))
    update_mode(mode, X, Y, S)

    ttk.Separator(frm).grid(row=8, column=0, columnspan=3, sticky="ew", pady=12)

    ttk.Label(frm, text="Watermark (optional)").grid(row=9, column=0, sticky="w")
    watermark = ttk.Entry(frm)
    watermark.grid(row=9, column=1, columnspan=2, sticky="ew")

    pb = ttk.Progressbar(frm)
    pb.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(12, 0))

    err = ttk.Label(frm, text="")
    err.grid(row=11, column=0, columnspan=3)

    ttk.Button(
        frm,
        text="Resize Images",
        command=lambda: on_compute_resize(
            selected_files, mode, X, Y, S, watermark, err, selected_output_dir, pb
        )
    ).grid(row=12, column=0, pady=10)

    ttk.Button(frm, text="Exit", command=root.destroy).grid(row=12, column=2, pady=10, sticky="e")

    root.mainloop()


if __name__ == "__main__":
    main()
