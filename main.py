from tkinter import *
from tkinter import ttk
import tkinter
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from pathlib import Path
from PIL import Image

selected_files = []
selected_output_dir = None

def select_files(view: ttk.Button):
    filenames = askopenfilenames(
    title="select files to resize",
    filetypes=[                    
                ("image", ".jpeg"),
                ("image", ".png"),
                ("image", ".jpg")
                ]
            )

    filenames = list(filenames)

    global selected_files
    selected_files = list(map(lambda s: Path(s),filenames))

    
    filenames = '\n'.join(filenames)
    view.configure(text=f"{filenames}")

def select_dir(view: ttk.Button):
    outdir = askdirectory(title="select output directory")
    outdir = Path(outdir)
    view.configure(text=f"{outdir}")

    global selected_output_dir
    selected_output_dir = outdir

def on_compute_resize(files: list[Path], X: ttk.Entry,Y: ttk.Entry, err_label: ttk.Label, outDir: Path, pb: ttk.Progressbar):
    try:
        X = int(X.get())
        Y = int(Y.get())
        err_label.configure(text="")
    except:
        err_label.configure(text="X and Y need to be integer numbers")


    print("task:")
    print(files)
    print(X,Y)

    pb.configure(orient="horizontal", length=len(files), mode="determinate")
    pb.start()
    for file in files:
        im = Image.open(file)
        im = im.resize((X,Y), resample=Image.NEAREST)
        out = outDir / file.name
        im.save(out)
        print(f"saved resized image to {out}")
        pb.step()

    pb.stop()
    
    print("done")

    err_label.configure(text="done")
        


def main():
    root = Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    
    ttk.Label(frm, text="Batch Image Resizer").grid(column=0, row=0)

    images_display = ttk.Label(frm, text="selected_files")
    ttk.Button(frm, text="select images to resize", command=lambda: select_files(images_display)).grid(row=1)
    images_display.grid(column=0, row=2)

    outdir_display = ttk.Label(frm, text="out_dir")
    ttk.Button(frm, text="select output directory", command=lambda: select_dir(outdir_display)).grid(row=3)
    outdir_display.grid(column=0, row=4)

    ttk.Label(frm,text="X").grid(row=5,column=1)
    ttk.Label(frm,text="Y").grid(row=5,column=2)
    targetX = ttk.Entry(frm)
    targetX.grid(row=6,column=1)
    targetY = ttk.Entry(frm)
    targetY.grid(row=6,column=2)

    pb = ttk.Progressbar(frm)

    errLabel = ttk.Label(frm,text="")
    errLabel.grid(column=0,row=8)
    ttk.Button(frm,text="compute",command=lambda: on_compute_resize(selected_files, targetX, targetY,errLabel, selected_output_dir, pb)).grid(column=0,row=7)
    pb.grid(column=0,row=8)



    ttk.Button(frm, text="exit", command=root.destroy).grid(column=0, row=10)
    root.mainloop()

if __name__ =='__main__':
    main()