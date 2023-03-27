
# ---------------------------------------------------------------------------
# Редактор и исполнитель скриптов с подстановкой данных
#
# Программа предназначена для создания, редактирования и исполнения скриптов
# управляющих компьютером через графический интерфейс пользователя.
# Позволяет автоматизировать заполнение различных форм и выполнение других
# рутинных операций.
# ---------------------------------------------------------------------------
"""

Скрипт выполняется в основном цикле программы.
Для каждой команды существует свой объект, который хранит:
- название команды,
- краткое описание,
- данные для выполнения,
- описание и методы обработки формы для редактирования,
- метод для выполнения команды.
Контроль за выполнением и параметры хранятся в специальном объекте, контролирующем:
очередь выполнения, объекты команд, стек для циклов и подпрограмм, источник данных.
Он также хранит ссылку на функция-исполнитель, которая выполняет фактические действия скрипта.
Он передается методам объектов команд в качестве аргумента.

"""
from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip

from settings import settings
from commands import CommandClasses


# Интерфейс
root = Tk()

# Размер экране
w = root.winfo_screenwidth()
h = root.winfo_screenheight()

# Размер окна
win_w = 800
win_h = 610

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

mainmenu.add_cascade(label="Файл", menu=filemenu)

mainmenu.add_command(label="Настройки скрипта",
                     command=lambda root=root, w=w, h=h: settings.show_window_settings(root, w, h))

# Список команд скрипта ------------------------------

# Create an instance of Style widget
style=ttk.Style()
style.theme_use('clam')


tree = ttk.Treeview(root, show="", columns=('size', 'modified'), selectmode="extended", height=28)
tree.column("# 1", stretch=NO, width=80)
tree.column("# 2", stretch=NO, width=300)


tree.insert('', 1000, 'gallery1', values=(1, 'Клик левой клавишей мыши'))
tree.insert('', 1000, 'gallery3', values=(2, 'Клик правой клавишей мыши'))
tree.insert('', 1000, 'gallery4', values=(3, "Следующий элемент поля 'field_name'"))
tree.insert('', 1000, 'gallery2', values=(4, 'Двойной клик мыши'))
tree.insert('', 0, 'gallery0', values=('', ''))

tree.selection_set('gallery1')
tree.focus_set()
tree.place(x=0, y=0)


# Кнопки записи и воспроизведения ---------------------------
icon1 = PhotoImage(file="icon/record.png")
icon2 = PhotoImage(file="icon/stop.png")
icon3 = PhotoImage(file="icon/play.png")

record_button = Button(command='', image=icon1, width=100, height=34)
record_button.place(x=12, y=win_h-43)
ToolTip(record_button, msg="Запись скрипта", delay=0.5)

stop_button = Button(command='', image=icon2, width=100, height=34)
stop_button.place(x=137, y=win_h-43)
ToolTip(stop_button, msg="Останова записи", delay=0.5)

play_button = Button(command='', image=icon3, width=100, height=34)
play_button.place(x=262, y=win_h-43)
ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)


INDENT = 400  # Отступ второй колонки от левого края окна

# Источник данных -------------------------------
data_source = StringVar()
frame1 = LabelFrame(root, width=385, height=85, text='Источник данных', foreground='#083863')
frame1.place(x=INDENT, y=0)
Message(frame1, text='Источник данных', width=370, anchor='w', textvariable=data_source).place(x=0, y=0)
data_source.set('Fielf 4 Fielf 1, Fielf 2, Fielf 3, Fielf 4 Fielf 1')


# Редактор команд ----------------------------
commands = ['Клик левой клавишей мыши', 'Клик правой клавишей мыши', 'Двойной клик мыши']
commands_var = StringVar(value=commands[0])
frame2 = LabelFrame(root, width=385, height=170, text='Редактор команд', foreground='#083863')
frame2.place(x=INDENT, y=100)

# Список команд
ttk.Combobox(frame2, values=commands, width=30, textvariable=commands_var, state="readonly").place(x=5, y=5)

# Комментарий
comment = Entry(frame2, width=32)
comment.place(x=5, y=37)
ToolTip(comment, msg="Комментарий", delay=0.5)

# Поля ввода
# Label(frame2, text='x=').place(x=10, y=71)
# Entry(frame2, width=5).place(x=34, y=71)
# Label(frame2, text='y=').place(x=100, y=71)
# Entry(frame2, width=5).place(x=124, y=71)

# Изображение элемента
element_image = PhotoImage(file="elements/elem_230228_163525.png")
# element_button = Button(frame2, command='', image=element_image, width=96, height=96, relief=FLAT)
# element_button.place(x=273, y=5)
# ToolTip(element_button, msg="Изображение элемента", delay=0.5)

# Кнопки
icon4 = PhotoImage(file="icon/new.png")
icon5 = PhotoImage(file="icon/edit.png")

new_button = Button(frame2, command='', image=icon4, width=100, height=34)
new_button.place(x=10, y=106)
ToolTip(new_button, msg="Добавить команду", delay=0.5)

edit_button = Button(frame2, command='', image=icon5, width=100, height=34)
edit_button.place(x=130, y=106)
ToolTip(edit_button, msg="Изменить команду", delay=0.5)


# Редактор скрипта ----------------------------
frame3 = LabelFrame(root, width=385, height=130, text='Редактор скрипта', foreground='#083863')
frame3.place(x=INDENT, y=285)

# Кнопки
icon6 = PhotoImage(file="icon/copy.png")
icon7 = PhotoImage(file="icon/cut.png")
icon8 = PhotoImage(file="icon/paste.png")
icon9 = PhotoImage(file="icon/delete.png")

copy_button = Button(frame3, command='', image=icon6, width=160, height=34)
copy_button.place(x=10, y=10)
ToolTip(copy_button, msg="Копировать команды", delay=0.5)

cut_button = Button(frame3, command='', image=icon7, width=160, height=34)
cut_button.place(x=200, y=10)
ToolTip(cut_button, msg="Вырезать команды", delay=0.5)

paste_button = Button(frame3, command='', image=icon8, width=160, height=34)
paste_button.place(x=10, y=58)
ToolTip(paste_button, msg="Вставить команды", delay=0.5)

delete_button = Button(frame3, command='', image=icon9, width=160, height=34)
delete_button.place(x=200, y=58)
ToolTip(delete_button, msg="Удалить команды", delay=0.5)


# Информация
information = StringVar()
frame4 = LabelFrame(root, width=385, height=135, text='Информация', foreground='#083863')
frame4.place(x=INDENT, y=430)

Message(frame4, width=390, anchor='w', textvariable=information).place(x=0, y=0)
information.set('Поле таблицы (столбец) представлено в виде списка данных.\nЭта команда '
                'переводит указатель чтения к следующему элементу списка')


# История ---------------------------------------
icon10 = PhotoImage(file="icon/undo.png")
icon11 = PhotoImage(file="icon/return.png")

undo_button = Button(root, command='', image=icon10, width=160, height=34)
undo_button.place(x=412, y=win_h-43)
ToolTip(undo_button, msg="Отменить", delay=0.5)

delete_button = Button(root, command='', image=icon11, width=160, height=34)
delete_button.place(x=602, y=win_h-43)
ToolTip(delete_button, msg="Вернуть", delay=0.5)

args = [17, 71, f"{settings.path_to_elements}elem_230228_163525.png"]

a = CommandClasses.create_command(*args, command='MouseClickLeft', root=frame2)








root.mainloop()
