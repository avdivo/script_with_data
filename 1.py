import tkinter as tk


def copy_text(event):
    entry.clipboard_clear()
    entry.clipboard_append(entry.selection_get())


def paste_text(event):
    entry.insert(tk.INSERT, entry.clipboard_get())


root = tk.Tk()

entry = tk.Entry(root)
entry.pack(pady=10)
entry.bind("<Control-c>", copy_text)
entry.bind("<Control-v>", paste_text)

root.mainloop()