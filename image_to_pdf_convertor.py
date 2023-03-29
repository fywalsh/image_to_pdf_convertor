"""
Traverses an input directory and all of it's sub directories 
and generates a PDF file for each directory containing image files.
"""

import os
import tkinter as tk
from datetime import datetime
from os import listdir
from os.path import isfile, join
from threading import Thread
from tkinter import filedialog, messagebox, scrolledtext, ttk

from PIL import Image

__author__ = "Fiona Walsh"
__version__ = "1.0.0"


def set_in_out_directories():
    """
    Sets the input and output directory values (based on the selected input directory).

    Args:
        n/a
    Returns:
        n/a
    """
    file_path = filedialog.askdirectory().replace("/", "\\")
    input_dir.configure(state="normal")
    in_dir_var.set(file_path)
    input_dir.configure(state="disabled")
    out_dir_var.set(file_path)


def check_for_empty_dir():
    """
    Checks if an input directory has not been selected.

    Args:
        n/a
    Returns:
        n/a
    """
    if not in_dir_var.get():
        messagebox.showerror("Error", "You must select an input directory first!")
    else:
        # Performs processing in the background to stop the GUI hanging
        daemon = Thread(
            target=load_images_and_generate_pdf(), daemon=True, name="PDF Generation"
        )
        daemon.start()


def load_images_and_generate_pdf():
    """
    Traverses each sub directory (found in the input directory), loads any
    images that are found and generates a PDF

    Args:
        n/a
    Returns:
        n/a
    """
    start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    progress_area.configure(state="normal")
    progress_area.insert(
        tk.END,
        "#################### " + start_time + " - STARTED ####################\n\n",
    )

    folder_count = 1
    in_dir = in_dir_var.get().replace("/", "\\")
    out_dir = out_dir_var.get() if out_dir_var.get() else in_dir

    subdirs = [x[0] for x in os.walk(in_dir)]
    if len(subdirs) == 0:
        progress_step = 100
    else:
        progress_step = 100 / len(subdirs)

    for folder in subdirs:
        progress_bar["value"] += progress_step
        mainframe.update_idletasks()

        progress_area.insert(
            tk.END, "Reading folder #" + str(folder_count) + ": " + folder + "\n"
        )

        all_images = [
            file
            for file in sorted(listdir(folder))
            if isfile(join(folder, file))
            and file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        ]

        progress_area.insert(tk.END, str(len(all_images)) + " image(s) found.\n")

        if len(all_images) > 0:
            generate_pdf(all_images, folder, out_dir)
        else:
            progress_area.insert(tk.END, "-------------------------------------\n")

        folder_count += 1

    end_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    progress_area.insert(
        tk.END,
        "\n#################### " + end_time + " - FINISHED ####################\n\n",
    )

    progress_area.configure(state="disabled")
    progress_area.see("end")

    progress_bar.stop()
    progress_bar["value"] = 100


def generate_pdf(all_images, folder, out_dir):
    """
    Generates a PDF containing images.

    Args:
        all_images: List of image file names
        folder: File path for folder of images
        out_dir: File path for the output directory

    Returns:
        n/a
    """
    pdf_image_list = []

    for image in all_images:
        opened_image = Image.open(join(folder, image))
        converted_image = opened_image.convert("RGB")
        pdf_image_list.append(converted_image)

    pdf_file_name = join(out_dir, folder.split("\\")[-1]) + ".pdf"
    pdf_image_list[0].save(
        pdf_file_name, save_all=True, append_images=pdf_image_list[1:]
    )

    progress_area.insert(tk.END, "PDF file generated: " + pdf_file_name + "\n")
    progress_area.insert(tk.END, "-------------------------------------\n")
    progress_area.see("end")


def reset_screen():
    """
    Resets the application screen.

    Args:
        n/a
    Returns:
        n/a
    """
    in_dir_var.set("")
    out_dir_var.set("")
    progress_bar["value"] = 0
    progress_area.configure(state="normal")
    progress_area.delete("1.0", tk.END)
    progress_area.configure(state="disabled")


root = tk.Tk()
root.title("Images To PDF Convertor")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Labels
ttk.Label(mainframe, text="Input Directory:").grid(column=2, row=1, sticky=tk.E)
ttk.Label(mainframe, text="Output Directory:").grid(column=2, row=2, sticky=tk.E)

# Buttons
s = ttk.Style()
s.configure("Green.TButton", background="green")
ttk.Button(
    mainframe,
    text="(1) Select Input Directory",
    style="Green.TButton",
    command=set_in_out_directories,
).grid(column=1, row=1, sticky=(tk.W, tk.E))
ttk.Button(
    mainframe,
    text="(2) Generate PDF File(s)",
    style="Green.TButton",
    command=check_for_empty_dir,
).grid(column=1, row=2, sticky=(tk.W, tk.E))
s.configure("Blue.TButton", background="blue")
ttk.Button(
    mainframe, text="Reset All", style="Blue.TButton", command=reset_screen
).grid(column=1, row=5, sticky=tk.W)
s.configure("Red.TButton", background="red")
ttk.Button(mainframe, text="Exit", style="Red.TButton", command=root.destroy).grid(
    column=6, row=5, sticky=tk.E
)

# Text Entry
in_dir_var = tk.StringVar()
input_dir = ttk.Entry(mainframe, textvariable=in_dir_var)
input_dir.grid(column=3, row=1, columnspan=6, sticky=tk.W + tk.E)
input_dir.configure(state="disabled")

out_dir_var = tk.StringVar()
output_dir = ttk.Entry(mainframe, textvariable=out_dir_var)
output_dir.grid(column=3, row=2, columnspan=6, sticky=tk.W + tk.E)

# Progress Bar
progress_bar = ttk.Progressbar(
    mainframe, orient="horizontal", mode="determinate", maximum=100, value=0
)
progress_bar.grid(column=1, row=3, columnspan=6, sticky=tk.W + tk.E)

# Scrolled Text
progress_area = scrolledtext.ScrolledText(mainframe, wrap=tk.WORD, state="disabled")
progress_area.grid(column=1, row=4, columnspan=6, sticky=tk.W + tk.E)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.bind("<Return>", load_images_and_generate_pdf)

root.resizable(False, False)
root.mainloop()
