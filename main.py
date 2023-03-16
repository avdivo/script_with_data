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
from tktooltip import ToolTip


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

# Меню
mainmenu = Menu(root)
root.config(menu=mainmenu)

filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Новый скрипт")
filemenu.add_command(label="Открыть скрипт")
filemenu.add_command(label="Сохранить скрипт")
filemenu.add_command(label="Сохранить скрипт как...")
filemenu.add_separator()
filemenu.add_command(label="Источник данных")
filemenu.add_separator()
filemenu.add_command(label="Выход")

mainmenu.add_cascade(label="Файл",
                     menu=filemenu)

mainmenu.add_cascade(label="Настройки скрипта")


# Список команд скрипта ------------------------------

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
tree.insert('', 0, 'gallery0', values=('', ''))

tree.selection_set('gallery1')
tree.focus_set()
tree.place(x=0, y=0)

INDENT = 400  # Отступ второй колонки от левого края окна


# Источник данных -------------------------------
data_source = StringVar()
frame1 = LabelFrame(root, width=385, height=100, text='Источник данных')
frame1.place(x=INDENT, y=0)
Message(frame1, text='Источник данных', width=390, anchor='w', textvariable=data_source).place(x=0, y=0)
data_source.set('Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три '
                'Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три '
                'Раз два три Раз два три')


# Кнопки записи и воспроизведения ---------------------------
icon1 = PhotoImage(file="icon/record.png")
icon2 = PhotoImage(file="icon/stop.png")
icon3 = PhotoImage(file="icon/play.png")

record_button = Button(command='', image=icon1, width=100)
record_button.place(x=12, y=win_h-36)
ToolTip(record_button, msg="Запись скрипта", delay=0.5)

stop_button = Button(command='', image=icon2, width=100)
stop_button.place(x=137, y=win_h-36)
ToolTip(stop_button, msg="Останова записи", delay=0.5)

play_button = Button(command='', image=icon3, width=100)
play_button.place(x=262, y=win_h-36)
ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)


# Редактор команд ----------------------------
commands = ['Клик левой клавишей мыши', 'Клик правой клавишей мыши', 'Двойной клик мыши']
commands_var = StringVar(value=commands[0])
frame2 = LabelFrame(root, width=385, height=140, text='Редактор команд')
frame2.place(x=INDENT, y=120)

# Поля ввода
ttk.Combobox(frame2, values=commands, width=30, textvariable=commands_var, state="readonly").place(x=5, y=5)
Label(frame2, text='x=').place(x=10, y=41)
Entry(frame2, width=5).place(x=34, y=41)
Label(frame2, text='y=').place(x=100, y=41)
Entry(frame2, width=5).place(x=124, y=41)

# Изображение элемента
element_image = PhotoImage(file="elements/elem_230228_163525.png")
element_button = Button(frame2, command='', image=element_image, width=96, height=96, relief=FLAT)
element_button.place(x=273, y=5)
ToolTip(element_button, msg="Изображение элемента", delay=0.5)

# Кнопки
icon4 = PhotoImage(file="icon/new.png")
icon5 = PhotoImage(file="icon/edit.png")

new_button = Button(frame2, command='', image=icon4, width=100)
new_button.place(x=10, y=78)
ToolTip(new_button, msg="Добавить команду", delay=0.5)

edit_button = Button(frame2, command='', image=icon5, width=100)
edit_button.place(x=130, y=78)
ToolTip(edit_button, msg="Изменить команду", delay=0.5)


# Редактор скрипта ----------------------------
frame3 = LabelFrame(root, width=385, height=100, text='Редактор скрипта')
frame3.place(x=INDENT, y=280)

# Кнопки
icon6 = PhotoImage(file="icon/copy.png")
icon7 = PhotoImage(file="icon/cut.png")
icon8 = PhotoImage(file="icon/paste.png")
icon9 = PhotoImage(file="icon/delete.png")

copy_button = Button(frame3, command='', image=icon6, width=100)
copy_button.place(x=10, y=78)
ToolTip(copy_button, msg="Добавить команду", delay=0.5)

edit_button = Button(frame3, command='', image=icon7, width=100)
edit_button.place(x=130, y=78)
ToolTip(edit_button, msg="Изменить команду", delay=0.5)

new_button = Button(frame3, command='', image=icon8, width=100)
new_button.place(x=10, y=78)
ToolTip(new_button, msg="Добавить команду", delay=0.5)

edit_button = Button(frame3, command='', image=icon9, width=100)
edit_button.place(x=130, y=78)
ToolTip(edit_button, msg="Изменить команду", delay=0.5)
# Label(frame1, text='Источник данных', anchor="w").place(x=0, y=0)

root.mainloop()
