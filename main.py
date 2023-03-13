# ---------------------------------------------------------------------------
# Редактор и исполнитель скриптов с подстановкой данных
#
# Программа предназначена для создания, редактирования и исполнения скриптов
# управляющих компьютером через графический интерфейс пользователя.
# Позволяет автоматизировать заполнение различных форм и выполнение других
# рутинных операций.
# ---------------------------------------------------------------------------
"""
Treeview
https://metanit.com/python/tkinter/4.1.php


"""

#
# from tkinter import *
#
#
# # Интерфейс
# root = Tk()
#
# # Размер экране
# w = root.winfo_screenwidth()
# h = root.winfo_screenheight()
#
# # Размер окна
# win_w = 700
# win_h = 600
#
# root.title("Редактор скриптов")
# root.geometry(f'{win_w}x{win_h}+{(w-win_w)//2}+{(h-win_h)//2}')  # Рисуем окно


import tkinter as tk
from tkinter import ttk

# def select():
#     for i in tree.selection():
#         item_iid = i
#         print ("".join([str(tree.item(i)['text'])])# for i in curItems]))


import tkinter as tk
from tkinter import ttk

root = tk.Tk()

tree = ttk.Treeview(root, show="headings", columns=('size', 'modified'), selectmode='browse')

tree.heading('size', text='SIZE')
tree.heading('modified', text='MODIFIED')

tree.insert('', 0, 'gallery1', text='Applications1')
tree.insert('gallery1', 0, 'gallery3', text='Applications1')
tree.insert('gallery1', 0, 'gallery4', text='Applications1')

tree.insert('', 1, 'gallery2', text='Applications2')

tree.selection_set('gallery1')

tree.focus_set()

tree.grid()
root.mainloop()
