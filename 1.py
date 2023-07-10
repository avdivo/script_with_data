import barcode
from barcode.writer import ImageWriter

ean = barcode.get('ean8', '09010000', writer=ImageWriter())
filename = ean.save('ean13_barcode')


import tkinter as tk

root = tk.Tk()

menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label="Open")
file_menu.add_command(label="Save")
file_menu.add_command(label="Exit")

# Для изменения первой строки меню
file_menu.entryconfigure(0, label="New")

menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

root.mainloop()