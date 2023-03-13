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


from tkinter import *
from tkinter import ttk

# Интерфейс
root = Tk()

# Размер экране
w = root.winfo_screenwidth()
h = root.winfo_screenheight()

# Размер окна
win_w = 800
win_h = 600

root.title("Редактор скриптов")
root.geometry(f'{win_w}x{win_h}+{(w-win_w)//2}+{(h-win_h)//2}')  # Рисуем окно

# Create an instance of Style widget
style=ttk.Style()
style.theme_use('clam')

tree = ttk.Treeview(root, show="", columns=('size', 'modified'), selectmode="extended", height=28)
tree.column("# 1", stretch=NO, width=80)
# tree.heading("# 1", text="ID")
tree.column("# 2", stretch=NO, width=300)
# tree.heading("# 2", text="Programming Language")


tree.insert('', 0, 'gallery1', values=(1, 'Один'))
tree.insert('', 0, 'gallery3', values=(2, 'Два'))
tree.insert('', 0, 'gallery4', values=(100, 'Три'))
tree.insert('', 0, 'gallery2', values=(1000, 'Четыре'))

tree.selection_set('gallery1')
tree.focus_set()
tree.place(x=0, y=0)

root.mainloop()
