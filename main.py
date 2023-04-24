
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
Он также хранит ссылку на функцию-исполнитель, которая выполняет фактические действия скрипта.
Он передается методам объектов команд.

"""
import os
from configparser import ConfigParser
from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip
import logging

import components
from settings import settings
from commands import CommandClasses
from components import Editor, DisplayCommands, DataSource, SaveLoad, data
from tracker_and_player import Tracker, Player
from exceptions import NoCommandOrStop, DataError, TemplateNotFoundError, ElementNotFound
from messages import Messages
from data_types import llist


def on_closing():
    """ Действия при закрытии программы """
    load_save.config_file(name=settings.project_name, path=settings.path_to_project, data=data_source.data_source_file)
    root.destroy()


# Интерфейс
root = Tk()

root.protocol("WM_DELETE_WINDOW", on_closing)  # Функция выполнится при закрытии окна

# Размер экране
w = root.winfo_screenwidth()
h = root.winfo_screenheight()

# Рисуем окно
root.title("Редактор скриптов")
root.geometry(f'{settings.win_w}x{settings.win_h}+{(w-settings.win_w)//2}+{(h-settings.win_h)//2}')

INDENT = 400  # Отступ второй колонки от левого края окна

# Источник данных -------------------------------
frame1 = LabelFrame(root, width=385, height=85, text='Источник данных', foreground='#083863')
frame1.place(x=INDENT, y=0)


# Редактор команд ----------------------------
frame2 = LabelFrame(root, width=385, height=170, text='Редактор команд', foreground='#083863')
frame2.place(x=INDENT, y=100)

# Изображение элемента
# element_image = PhotoImage(file="elements/elem_230228_163525.png")

# Редактор скрипта ----------------------------
frame3 = LabelFrame(root, width=385, height=130, text='Редактор скрипта', foreground='#083863')
frame3.place(x=INDENT, y=285)

# # Информация
frame4 = LabelFrame(root, width=385, height=135, text='Информация', foreground='#083863')
frame4.place(x=INDENT, y=430)


# История ---------------------------------------
icon10 = PhotoImage(file="icon/undo.png")
icon11 = PhotoImage(file="icon/return.png")

undo_button = Button(root, command='', image=icon10, width=160, height=34)
undo_button.place(x=412, y=settings.win_h-43)
ToolTip(undo_button, msg="Отменить", delay=0.5)

delete_button = Button(root, command='', image=icon11, width=160, height=34)
delete_button.place(x=602, y=settings.win_h-43)
ToolTip(delete_button, msg="Вернуть", delay=0.5)


def run_script():
    """ Выполнение скрипта """
    data.script_started = True  # Скрипт работает
    if data.pointer_command == -1:
        data.pointer_command = 0
    while data.script_started:
        try:
            children = display_commands.tree.get_children()
            if len(children) <= data.pointer_command+1:
                raise NoCommandOrStop('Нет команд для выполнения.')
            display_commands.tree.selection_set(children[data.pointer_command + 1])  # Выделяем строку
            data.run_command()  # Выполнить следующую в очереди команду
        except NoCommandOrStop as err:
            logger.error(err)
            data.script_started = False
        except (DataError, TemplateNotFoundError, ElementNotFound) as err:
            logger.error(err)
        except:
            data.script_started = False
            raise


    return


# создание логгера и обработчика
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=Messages(frame4))

# добавление обработчика в логгер
handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
# '%(asctime)s %(name)s %(levelname)s: %(message)s'
logger.addHandler(handler)

# Уровни логирования в верхнем регистре: DEBUG, INFO, WARNING, ERROR, CRITICAL
# logger.error('message')

CommandClasses.root = frame2
components.CommandClasses.data = components.data
editor = Editor(frame2)  # Первый фрейм для редактора
display_commands = DisplayCommands(root, frame3)  # Передаем ссылку на окно программы


# Реализация паттерна Наблюдатель, сообщаем объектам ссылки друг на друга для оповещения при изменениях
editor.display_commands = display_commands
display_commands.editor = editor


# a = CommandClasses.create_command(*args, command='StopCmd', description='Ок')

tracker = Tracker(root)  # Трекер клавиатуры и мыши
tracker.data = data  # Даем трекеру ссылку на данные скрипта
tracker.display_commands = display_commands  # И на список команд


player = Player(root, run_script)
player.data = data
data.func_execute_event = player.run_command  # Назначаем функцию, которая будет выполнять события мыши и клавиатуры


data_source = components.DataSource(frame1)
data_source.editor = editor  # Передаем ссылку на редактор


SaveLoad.editor = editor  # Передаем ссылку на редактор
SaveLoad.display_commands = display_commands  # Передаем ссылку на список команд
SaveLoad.data_source = data_source  # Передаем ссылку на источник данных

load_save = SaveLoad(root)

data_source.save_load = load_save  # Передаем ссылку на объект сохранения/загрузки

# Меню
mainmenu = Menu(root)
root.config(menu=mainmenu)

filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Новый проект", command=load_save.menu_new_project)
filemenu.add_command(label="Открыть проект", command=load_save.menu_open_project)
filemenu.add_command(label="Сохранить проект", command=load_save.menu_save_project)
filemenu.add_command(label="Сохранить проект как...", command=load_save.menu_save_as_project)
filemenu.add_separator()
filemenu.add_command(label="Очистить проект", command=load_save.menu_save_as_project)
filemenu.add_separator()
filemenu.add_command(label="Выход")
mainmenu.add_cascade(label="Файл", menu=filemenu)

menu_data_source = Menu(mainmenu, tearoff=0)
menu_data_source.add_command(label="Подключить источник данных", command=data_source.menu_data_source)
menu_data_source.add_command(label="Сбросить источник данных", command=data_source.menu_reset_pointers)
menu_data_source.add_command(label="Отключить источник данных", command=data_source.menu_delete_data_source)
mainmenu.add_cascade(label="Данные", menu=menu_data_source)

mainmenu.add_command(label="Настройки",
                     command=lambda root=root, w=w, h=h: settings.show_window_settings(root, w, h))

# TODO: Добавить иконки в меню
# save_icon = PhotoImage(file="icon/copy.png")
# mainmenu.entryconfigure(3, image=save_icon)
# mainmenu.entryconfigure(4, image=save_icon)


root.mainloop()
