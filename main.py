import sys
import os
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilenames
from pathlib import Path
from PIL import Image

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


def on_compute_resize(files, mode, X, Y, S, err_label, outDir, pb):
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

        im.resize(new_size, Image.NEAREST).save(outDir / file.name)
        pb.step(1)

    err_label.configure(text="Done")


def main():
    root = Tk()
    root.title("Batch Image Resizer")
    root.geometry("520x420")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("TRadiobutton", font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frm = ttk.Frame(root, padding=16)
    frm.grid(sticky="nsew")
    frm.columnconfigure(1, weight=1)

    ttk.Label(frm, text="Batch Image Resizer", style="Header.TLabel").grid(row=0, column=0, columnspan=3, pady=(0, 12))

    files_lbl = ttk.Label(frm, text="No files selected")
    ttk.Button(frm, text="Select Images", command=lambda: select_files(files_lbl)).grid(row=1, column=0, sticky="w")
    files_lbl.grid(row=1, column=1, columnspan=2, sticky="w")

    out_lbl = ttk.Label(frm, text="No output directory")
    ttk.Button(frm, text="Output Directory", command=lambda: select_dir(out_lbl)).grid(row=2, column=0, sticky="w")
    out_lbl.grid(row=2, column=1, columnspan=2, sticky="w")

    ttk.Separator(frm).grid(row=3, column=0, columnspan=3, sticky="ew", pady=12)

    mode = StringVar(value="fixed")

    ttk.Label(frm, text="Resize Mode").grid(row=4, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Fixed WxH", variable=mode, value="fixed").grid(row=5, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Scale", variable=mode, value="scale").grid(row=6, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Fixed Width", variable=mode, value="width").grid(row=7, column=0, sticky="w")
    ttk.Radiobutton(frm, text="Fixed Height", variable=mode, value="height").grid(row=8, column=0, sticky="w")

    X = ttk.Entry(frm, width=10)
    Y = ttk.Entry(frm, width=10)
    S = ttk.Entry(frm, width=10)

    ttk.Label(frm, text="Width").grid(row=5, column=1, sticky="e")
    X.grid(row=5, column=2, sticky="w")

    ttk.Label(frm, text="Height").grid(row=6, column=1, sticky="e")
    Y.grid(row=6, column=2, sticky="w")

    ttk.Label(frm, text="Scale").grid(row=7, column=1, sticky="e")
    S.grid(row=7, column=2, sticky="w")

    mode.trace_add("write", lambda *_: update_mode(mode, X, Y, S))
    update_mode(mode, X, Y, S)

    ttk.Separator(frm).grid(row=9, column=0, columnspan=3, sticky="ew", pady=12)

    pb = ttk.Progressbar(frm)
    pb.grid(row=10, column=0, columnspan=3, sticky="ew")

    err = ttk.Label(frm, text="")
    err.grid(row=11, column=0, columnspan=3)

    ttk.Button(
        frm,
        text="Resize Images",
        command=lambda: on_compute_resize(selected_files, mode, X, Y, S, err, selected_output_dir, pb)
    ).grid(row=12, column=0, pady=10)

    ttk.Button(frm, text="Exit", command=root.destroy).grid(row=12, column=2, pady=10, sticky="e")

    root.mainloop()


if __name__ == "__main__":
    main()
