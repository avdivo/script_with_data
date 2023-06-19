import barcode
from barcode.writer import ImageWriter

ean = barcode.get('ean8', '00999900', writer=ImageWriter())
filename = ean.save('ean13_barcode')


import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Создаем дерево
tree = ttk.Treeview(root, columns=(1,2), show="tree")

# Устанавливаем шрифт для всех элементов
tree.tag_configure('font', font=('TkDefaultFont', 12, 'bold'))
tree.tag_configure('font1', font=('TkDefaultFont', 12))

# Добавляем элементы в дерево
tree.insert("", "end", "parent", text="Parent", tags=('font'))
tree.insert("parent", "end", "child1", text="Child 1", tags='font1')
tree.insert("parent", "end", "child2", text="Child 2", tags='font1')
tree.insert("parent", "end", "child3", text="Child 3", tags='font1')

# Выделение элементов верхнего уровня жирным
# tree.tag_configure('bold', font=('TkDefaultFont', 12, 'bold'))

# Размещаем дерево на форме
tree.pack()

root.mainloop()