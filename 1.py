import tkinter as tk

root = tk.Tk()

menu_bar = tk.Menu(root)
menu = tk.Menu(menu_bar, tearoff=0)

menu.add_command(label="enable")

def change_label():
    menu.entryconfigure(0, label="disable")

menu.add_command(label="change label", command=change_label)

menu_bar.add_cascade(label="Menu", menu=menu)
root.config(menu=menu_bar)

root.mainloop()