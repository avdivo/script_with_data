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


# Список команд скрипта

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




# Источник данных
data_source = StringVar()
frame1 = LabelFrame(root, width=385, height=100, text='Источник данных')
frame1.place(x=INDENT, y=0)
Message(frame1, text='Источник данных', width=390, anchor='w', textvariable=data_source).place(x=0, y=0)
data_source.set('Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три '
                'Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три Раз два три '
                'Раз два три Раз два три')


# Запись и воспроизведение
icon1=PhotoImage(file="icon/record.png")
icon2=PhotoImage(file="icon/stop.png")
icon3=PhotoImage(file="icon/play.png")

Button(command='', image=icon1).place(x=12, y=win_h-36, width=100)
Button(command='', image=icon2).place(x=137, y=win_h-36, width=100)
Button(command='', image=icon3).place(x=262, y=win_h-36, width=100)


# Редактор команд
commands = ['Клик левой клавишей мыши', 'Клик правой клавишей мыши', 'Двойной клик мыши']
commands_var = StringVar(value=commands[0])
frame2 = LabelFrame(root, width=385, height=100, text='Редактор команд')
frame2.place(x=INDENT, y=120)
ttk.Combobox(frame2, values=commands, width=30, textvariable=commands_var, state="readonly").place(x=0, y=0)
Label(frame2, text='x=').place(x=10, y=40)
Entry(frame2, width=5).place(x=30, y=40)
Label(frame2, text='y=').place(x=100, y=40)
Entry(frame2, width=5).place(x=120, y=40)
# Label(frame1, text='Источник данных', anchor="w").place(x=0, y=0)

root.mainloop()
