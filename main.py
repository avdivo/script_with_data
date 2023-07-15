
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
from tkinter import *
from tkinter import messagebox
from tktooltip import ToolTip
import logging
import subprocess
import argparse

import components
from settings import settings
from commands import CommandClasses
from components import Editor, DisplayCommands, SaveLoad, data
from tracker_and_player import Tracker, Player
from exceptions import NoCommandOrStop, DataError, TemplateNotFoundError, ElementNotFound
from messages import Messages
from define_platform import system
from quick_start import dialog_quick_start, project_manager, ProjectList


def on_closing():
    """ Действия при закрытии программы """
    if data.script_started or data.is_listening:
        return  # Операция невозможна при выполнении или записи скрипта

    if not settings.is_saved:
        # Если проект не сохранен, то предложить сохранить проект
        result = messagebox.askyesnocancel('Сохранение проекта', 'Сохранить проект?')
        if result:
            save_load.save_project()
        elif result is None:
            return

    settings.config_file(action='set', name=settings.project_name, path=settings.path_to_project)
    root.destroy()


# Интерфейс
root = Tk()
data.root = root  # Передаем ссылку ссылку на главное окно

root.protocol("WM_DELETE_WINDOW", on_closing)  # Функция выполнится при закрытии окна

# Размер экране
w = root.winfo_screenwidth()
h = root.winfo_screenheight()


# Рисуем окно
root.title("Редактор скриптов")
root.geometry(f'{settings.win_w}x{settings.win_h}+{(w-settings.win_w)//2}+{(h-settings.win_h)//2}')
# иконка
if system == 'Windows':
    root.iconbitmap('icon/edit.ico')
else:
    root.iconphoto(True, PhotoImage(file='icon/ed.png'))

INDENT = 400  # Отступ второй колонки от левого края окна

# Источник данных -------------------------------
frame1 = LabelFrame(root, width=385, height=85, text='Источник данных', foreground='#083863')
frame1.place(x=INDENT, y=0)


# Редактор команд ----------------------------
frame2 = LabelFrame(root, width=385, height=170, text='Редактор команд', foreground='#083863')
frame2.place(x=INDENT, y=100)

# Редактор скрипта ----------------------------
frame3 = LabelFrame(root, width=385, height=130, text='Редактор скрипта', foreground='#083863')
frame3.place(x=INDENT, y=285)

# # Информация
frame4 = LabelFrame(root, width=385, height=135, text='Информация', foreground='#083863')
frame4.place(x=INDENT, y=430)


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
            settings.pointer_command = data.pointer_command + 1
            data.run_command()  # Выполнить следующую в очереди команду
        except NoCommandOrStop as err:
            logger.error(err)
            data.script_started = False
            tracker.reset_kb()  # Сбросить клавиатуру
        except (DataError, TemplateNotFoundError, ElementNotFound) as err:
            logger.error(err)
        except:
            data.script_started = False
            tracker.reset_kb()  # Сбросить клавиатуру
            raise

    return

def run(project, file):
    """ Запуск скрипта без окон. Ожидание завершения и закрытие программы

    Получает параметры для запуска скрипта. Загружает, сапрячет основное окно,
    выполняет скрипт, закрывает программу.
    """
    def check_work():
        """ Функция вызывая себя через промежутки времени,
        проверяет каждый раз не завершилось ли выполнение скрипта, чтобы отобразить окно """
        if settings.script_started:
            root.after(500, check_work)
        else:
            root.destroy()  # Закрытие программы
            # exit()

    root.withdraw()  # Скрыть окно программы
    player.load_and_run(path=project, data_source=file)  # Запускаем скрипт передавая путь к нему и источник данных
    check_work()  # Ожидаем завершения программы

def open_file_explorer(path, file=None):
    """ Открыть папку в проводнике или файл в приложении по умолчанию """
    if data.script_started or data.is_listening:
        return  # Операция невозможна при выполнении или записи скрипта
    if file:
        path = os.path.join(path, file)
    if system.os == 'Windows':
        os.startfile(path)
    elif system.os == 'Linux':
        subprocess.Popen(['xdg-open', path])
    else:
        print('Операционная система не поддерживается')


def developer_mode_change():
    """ Изменение режима разработчика через меню """
    if settings.developer_mode:
        settings.developer_mode = ''
        menu_options.entryconfigure(6, label="Режим разработчика: Выключен")
    else:
        settings.developer_mode = 'on'
        menu_options.entryconfigure(6, label="Режим разработчика: Включен")
    settings.config_file(action='set', developer=settings.developer_mode)

# hhh11
def minimize_window_on_recording_change():
    """ Изменение режима окна редактора при записи через меню """
    if settings.minimize_window_on_recording:
        settings.minimize_window_on_recording = ''
        menu_options.entryconfigure(8, label="Свернуть окно при записи: Нет")
    else:
        settings.minimize_window_on_recording = 'yes'
        menu_options.entryconfigure(8, label="Свернуть окно при записи: Да")
    settings.config_file(action='set', minimize_window=settings.minimize_window_on_recording)

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
CommandClasses.tracker = tracker  # Передаем ссылку на трекер в классы команд


player = Player(root, run_script)
player.tracker = tracker
player.data = data
data.func_execute_event = player.run_command  # Назначаем функцию, которая будет выполнять события мыши и клавиатуры


data_source = components.DataSource(frame1)
data_source.editor = editor  # Передаем ссылку на редактор

SaveLoad.editor = editor  # Передаем ссылку на редактор
SaveLoad.display_commands = display_commands  # Передаем ссылку на список команд
SaveLoad.data_source = data_source  # Передаем ссылку на источник данных
player.data_source = data_source  # Передаем ссылку на источник данных

save_load = SaveLoad(root)

data_source.save_load = save_load  # Передаем ссылку на объект сохранения/загрузки
editor.save_load = save_load  # Передаем ссылку на объект сохранения/загрузки
display_commands.save_load = save_load  # Передаем ссылку на объект сохранения/загрузки
tracker.save_load = save_load  # Передаем ссылку на объект сохранения/загрузки

# Меню
mainmenu = Menu(root)
root.config(menu=mainmenu)

filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Новый проект", command=save_load.menu_new_project)
filemenu.add_command(label="Открыть проект", command=save_load.menu_open_project)
filemenu.add_command(label="Сохранить проект", command=save_load.menu_save_project)
filemenu.add_command(label="Сохранить проект как...", command=save_load.menu_save_as_project)
filemenu.add_command(label="Переименовать проект", command=save_load.rename_project)
filemenu.add_separator()
filemenu.add_command(label="Удалить лишние изображения", command=editor.menu_delete_images)
filemenu.add_command(label="Просмотр изображений", command=lambda: open_file_explorer(settings.path_to_elements))
filemenu.add_separator()
filemenu.add_command(label="Выход", command=on_closing)
mainmenu.add_cascade(label="Проект", menu=filemenu)

menu_data_source = Menu(mainmenu, tearoff=0)
menu_data_source.add_command(label="Подключить источник данных", command=data_source.menu_data_source)
menu_data_source.add_command(label="Сбросить источник данных", command=data_source.menu_reset_pointers)
menu_data_source.add_command(label="Отключить источник данных", command=data_source.menu_delete_data_source)
menu_data_source.add_command(label="Открыть файл данных", command=lambda: open_file_explorer(
    settings.path_to_data, data_source.data_source_file))
menu_data_source.add_command(label="Открыть папку с данными", command=lambda: open_file_explorer(settings.path_to_data))

mainmenu.add_cascade(label="Данные", menu=menu_data_source)

menu_options = Menu(mainmenu, tearoff=0)
menu_options.add_command(label="Быстрый запуск", command=lambda: dialog_quick_start(
    root, player.load_and_run, save_load.load_old_project, save_load.open_project))
menu_options.add_command(label="Менеджер проектов", command=lambda: project_manager(
    root, player.load_and_run, save_load.load_old_project, save_load.open_project))
menu_options.add_separator()
menu_options.add_command(label="Выбрать рабочую папку", command=save_load.select_work_dir)
menu_options.add_command(label="Открыть рабочую папку", command=lambda: open_file_explorer(settings.work_dir))
menu_options.add_separator()
onoff = 'Включен' if settings.developer_mode else 'Выключен'
menu_options.add_command(label=f"Режим разработчика: {onoff}", command=developer_mode_change)
menu_options.add_separator()
onoff = 'Да' if settings.minimize_window_on_recording else 'Нет'
menu_options.add_command(label=f"Свернуть окно при записи: {onoff}", command=minimize_window_on_recording_change)
mainmenu.add_cascade(label="Опции", menu=menu_options)

mainmenu.add_command(label="Настройки скрипта",
                     command=lambda root=root, w=w, h=h: settings.show_window_settings(root, w, h))
mainmenu.add_command(label="Менеджер проектов", command=lambda: project_manager(
    root, player.load_and_run, save_load.load_old_project, save_load.open_project))


# TODO: Добавить иконки в меню
# save_icon = PhotoImage(file="icon/copy.png")
# mainmenu.entryconfigure(3, image=save_icon)
# mainmenu.entryconfigure(4, image=save_icon)


# История ---------------------------------------
icon10 = PhotoImage(file="icon/undo.png")
icon11 = PhotoImage(file="icon/return.png")

undo_button = Button(root, command=save_load.undo_button, image=icon10, width=160, height=34)
undo_button.place(x=412, y=settings.win_h-43)
ToolTip(undo_button, msg="Отменить", delay=0.5)

return_button = Button(root, command=save_load.return_button, image=icon11, width=160, height=34)
return_button.place(x=602, y=settings.win_h-43)
ToolTip(return_button, msg="Вернуть", delay=0.5)

# -----------------------------------------------
# Запуск программы
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                 description='Программа для создания, редактирования и воспроизведения '
                                             'последовательности действий пользователя.')
parser.add_argument('-c', '--code', action='store_true', help='Открыть окно старта по коду проекта.\n'
                                                        'Без ключей откроется это же окно.')
parser.add_argument('-e', '--editor', action='store_true', help='Открыть редактор c последним проектом.')
parser.add_argument('-m', '--manager', action='store_true', help='Открыть менеджер проектов.')
parser.add_argument('-r', '--run', nargs='+', metavar=('<Project>', '<File>'), help='Запуск скрипта.\n'
                                          'Первый аргумент - полный путь к проекту,\n'
                                          'второй - имя файла данных (не обязательно).\nПример: '
                                          '--run C:\Scripts\Script_1 data.xlsx\n'
                                          'Для запуска скрипта из текущей рабочей папки\nможно указать 1 аргумент - '
                                          'цифровой код проекта.\nПример: --run 0101')

args = parser.parse_args()  # Получение аргументов командной строки

if args.code:
    # Если программа запущена с ключом -c (--code) , то открывается окно быстрого запуска
    dialog_quick_start(root, player.load_and_run, save_load.load_old_project, save_load.open_project)

elif args.manager:
    # Если программа запущена с ключом -m (--manager) , то открывается менеджер проектов
    project_manager(root, player.load_and_run, save_load.load_old_project, save_load.open_project)

elif args.editor:
    save_load.load_old_project()  # Загрузка последнего проекта в редакторе

elif args.run:
    project = args.run[0]
    file = args.run[1] if len(args.run) == 2 else ''
    if len(args.run) == 1:
        # Если аргумент 1, то это код проекта или путь к проекту. Код проекта - это число типа int
        if project.isdigit():
            # Если аргумент - число, то это код проекта, получаем путь к проекту по коду и файл данных
            projects = ProjectList(read_only=True)
            projects.project_activation_by_number(args.run[0])
            project = projects.get_path_to_project()
            file = projects.active_file
    # Если аргумент - строка, то это путь к проекту. Тут уже только строки
    run(project, file)  # Запуск скрипта


else:
    # Если программа запущена без ключей, то открывается окно быстрого запуска
    dialog_quick_start(root, player.load_and_run, save_load.load_old_project, save_load.open_project)

root.mainloop()
