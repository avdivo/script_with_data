# ---------------------------------------------------------------------------
# Составные части программы в классах.
# Импортируются в основную часть программы, предоставляя интерфейс для взаимодействия
# В составе:
# Данные для исполнителя скрипта
# Редактор команд
# ---------------------------------------------------------------------------

import os
from configparser import ConfigParser
from tkinter import *
from tkinter import ttk, messagebox, simpledialog, Toplevel
from tkinter import filedialog as fd

from tktooltip import ToolTip
from collections import deque
from time import sleep
import pandas as pd
import string
from random import choice, randint
import json
import logging
import shutil
import re
import winsound

from commands import CommandClasses
from data_input import DataInput
from exceptions import NoCommandOrStop, \
    LabelAlreadyExists, DataError, ElementNotFound, LoadError, TemplateNotFoundError
from data_types import llist
from settings import settings
from define_platform import system


# создание логгера и обработчика
logger = logging.getLogger('logger')


class CountingDict(dict):
    """ Словарь умеющий считать количество нужных объектов при создании, изменении, удалении

    Применяется для контроля списка меток и блоков в скрипте.
    Для ужаления изображений элементов (кнопок, ярлыков) при удалении команд клика мыши.
    Переопределенные методы обновляют список названий меток и блоков хранящийся в
    специальном типе данных llist каждый раз, когда происходит манипуляция с
    меткой или блоком.

    """
    def __setitem__(self, key, value):
        """ Переопределяем метод добавления и изменения элементов словаря

        Проверяет так-же наличие добавляемой метки или блока (имени) и если такая
        уже существует, возвращает ошибку.

        """
        if value.__class__.__name__ == 'BlockCmd' or value.__class__.__name__ == 'LabelCmd':
            if value.value in llist.labels:
                raise LabelAlreadyExists('Такое имя метки или блока уже существует.')

            super().__setitem__(key, value)  # Вызываем базовую реализацию метода
            names = [obj.value for obj in data.obj_command.values()
                 if obj.__class__.__name__ == 'BlockCmd' or obj.__class__.__name__ == 'LabelCmd']
            llist.labels = names
        else:
            super().__setitem__(key, value)  # Вызываем базовую реализацию метода

    def __delitem__(self, key):
        """ Переопределяем метод удаления элементов из словаря """
        if data.obj_command[key].__class__.__name__ == 'BlockCmd' \
                or data.obj_command[key].__class__.__name__ == 'LabelCmd':
            # Удаление меток
            super().__delitem__(key)  # Вызываем базовую реализацию метода
            names = [obj.value for obj in data.obj_command.values()
                 if obj.__class__.__name__ == 'BlockCmd' or obj.__class__.__name__ == 'LabelCmd']
            llist.labels = names

        else:
            super().__delitem__(key)  # Вызываем базовую реализацию метода


class DataForWorker:
    """ Данные для исполнителя скрипта

    Класс для одиночного объекта, в котором хранятся данные
    необходимые для выполнения скрипта:
    очередь выполнения, объекты команд, стек для циклов и подпрограмм, источник данных.

    """
    root = None  # Ссылка на главное окно программы

    def __init__(self):
        """ Инициализация

         В очереди команд идентификаторы под которыми они записаны в словаре объектов команд и
         в виджете для визуального представления. Очередь определяет последовательность исполнения.

         """
        self.queue_command = []  # Очередь команд (ключи - id команды)
        self.obj_command = CountingDict()  # Объекты команд по ключам из очереди
        self.id_command = 0  # Счетчик для идентификаторов команд
        self.pointer_command = -1  # Указатель на исполняемую команду или положение курсора в списке

        # Стек для циклов и подпрограмм хранит списки:
        # Для циклов - [индекс команды for, сколько повторов осталось]
        # Для блока - индекс команды после run
        self.stack = deque()

        # В качестве источника данных используются 2 словаря. В качестве ключей в них Имена полей
        # В первом словаре значения - это списки данных {'key': [list data]}
        # Во втором указатели на элементы списков первого словаря {'key': int}
        self.data_source = None  # dict()  Источник данных {'field': list}
        self.pointers_data_source = None  # dict() Указатели на позицию чтения из поля {'field': n}

        self.func_execute_event = None  # Функция выполняющая событие мыши или клавиатуры

        self.script_started = False  # False - остановит скрипт, True - позволит выполняться
        self.is_listening = False  # False - не работает слушатель, True - работает слушатель
        self.work_settings = None  # Тут создается копия настроек программы во время выполнения скрипта

        # Словарь: {метка или блок (ключи): индекс ее в очереди команд queue_command.
        # Заполняется перед выполнением скрипта
        self.work_labels = None

        # Обеспечение работы модального окна диалога с пользователем
        self.modal_stop = False  # Если в модальном окне диалога с пользователем нажато Остановка
        self.widget = None  # Виджет пользовательского типа llist (метка для перехода)

        # Флаг обозначающий режим ожидания скоиншота под курсором (все функции программы остановлены)
        self.wait_screenshot = False

    def next_id(self):
        """ Генерирует id новой команды """
        self.id_command += 1
        return f'cmd{self.id_command}'

    def get_fields(self):
        """ Возвращает список полей таблицы данных """
        if self.data_source:
            return [i for i in self.data_source.keys()]
        else:
            raise DataError('Не выбран источник данных.')

    def make_command(self, **kwargs):
        """ Создает объект команды на основе параметров и добавляет ее в список """
        # Создаем объект команды
        cmd = CommandClasses.create_command(
            *kwargs['val'], command=kwargs['cmd'], description=kwargs['des'])
        self.add_new_command(cmd)  # Добавляем команду

    def add_new_command(self, cmd):
        """ Добавление новой команды

        Принимает объект команды
        Возвращает id команды
        """
        key = self.next_id()  # Получаем новый id
        try:
            self.obj_command[key] = cmd  # Добавляем объект в dict
            self.pointer_command += 1  # Строка добавляется в позицию за указателем и на нее ставим указатель
            self.queue_command.insert(self.pointer_command, key)  # Добавляем id в очередь
            return key  # Возвращаем id команды
        except LabelAlreadyExists as err:
            # При неудачном добавлении в случае совпадения имен блоков и меток
            # добавление отменяется
            raise

    def del_command(self, id_cmd: str):
        """ Удаление команды

         Принимает id команды

         """
        self.queue_command.remove(id_cmd)  # Удаляем id из очереди
        del(self.obj_command[id_cmd])  # Удаляем объект команды из словаря
        if len(self.queue_command) == self.pointer_command:
            # При удалении последней строки указатель установить на последнюю
            self.pointer_command -= 1

    def change_command(self, cmd):
        """ Изменение команды """
        if self.pointer_command >= 0:
            # Объект удаляется, но пока он на месте, его имя,  если это метка или блок
            # может совпасть с заменяющим, тогда будет совпадение имен, поэтому меняем имя
            temp = self.queue_command[self.pointer_command]
            del self.obj_command[temp]
            self.obj_command[temp] = cmd  # Меняем объект команды под курсором

    def stop_for_dialog(self, mess):
        """ Остановка скрипта для диалога. Получение указаний от пользователя

        Выводится модальное окно, которое предлагает пользователю выбор действия:
        - Продолжить выполнение скрипта
        - Остановить скрипт
        - Перейти к указанной метке или блоку
        - Перезапустить скрипт
        """
        # Выводим модальное окно размером 300х200 с заголовком и текстовым сообщением о причине остановки выполнения
        # скрипта.
        # Ниже выпадающий список с метками и блоками и кнопкой Перейти.
        # Еще ниже кнопки Перезапустить, Остановить, Продолжить.
        # При закрытии окна (можно по Esc), скрипт продолжает выполняться.

        # Звуковой сигнал при появлении окна.
        if system.os == 'Windows':
            winsound.MessageBeep()
        else:
            os.system('play -nq -t alsa synth {} sine {}'.format(0.5, 440))

        self.modal_stop = False  # Сообщаем главной программе, продолжать выполнение скрипта

        self.top = Toplevel(self.root)  # Новое окно
        self.top.title("Остановка скрипта для диалога")  # Заголовок

        self.top.resizable(width=False, height=False)  # Запрет изменения размеров
        self.top.geometry(f'{500}x{200}+{0}+{0}')  # Рисуем окно

        m = Message(self.top, width=500, anchor='w', text=mess)  # Сообщение о причине остановки
        m.place(x=0, y=10)
        m.config(foreground='#0000FF')

        # Выпадающий список с метками и блоками и кнопкой Перейти
        frame = LabelFrame(self.top, width=480, height=70, text='Перейти к метке или блоку', foreground='#083863')
        frame.place(x=10, y=70)
        self.widget = DataInput.CreateInput(frame, llist(), x=5, y=10)  # Виджет для типа данных меток
        Button(frame, text='Перейти', command=self.goto_label).place(x=380, y=6)  # Кнопка для перехода к метке или блоку

        # 3 кнопки для действий
        Button(self.top, text='Перезапустить', width=15, command=self.restart).place(x=10, y=160)
        Button(self.top, text='Остановить', width=15, command=self.stop_script).place(x=175, y=160)
        Button(self.top, text='Продолжить', width=15, command=self.top.destroy).place(x=340, y=160)

        self.top.focus_set()  # Установка фокуса
        self.top.bind('<Escape>', lambda event: self.top.destroy())  # Закрытие по Esc

        self.top.grab_set()
        # self.top.focus_set()
        # self.top.wait_window()
        while not self.top.winfo_ismapped():
            self.top.update()
        while self.top.winfo_exists():
            self.top.update()
            sleep(0.1)

    def restart(self):
        """ Перезапуск скрипта сначала """
        self.pointer_command = -1
        self.top.destroy()

    def stop_script(self):
        """ Остановить скрипт """
        self.modal_stop = True  # Остановить скрипт
        self.top.destroy()

    def goto_label(self):
        """ Запуск скрипта с указанной метки или блока """
        llist_value = self.widget.result  # Результат выбора метки для перехода в формате llist
        if llist_value:
            # Создаем объект команды перехода и просто выполняем ее
            cmd = CommandClasses.create_command(llist_value, command='RunCmd')
            cmd.run_command()
            self.top.destroy()

    def run_command(self):
        """ Выполнение очередной команды и переход на следующую"""
        try:
            self.obj_command[self.queue_command[self.pointer_command]].run_command()
        except IndexError:
            raise NoCommandOrStop('Нет команд для выполнения.')
        except DataError as err:
            # Обработка ошибок данных в зависимости от текущих настроек реакции
            if data.work_settings['s_error_no_data'].react == 'stop':
                raise NoCommandOrStop(f'Остановка выполнения скрипта\nРеакция на ошибку данных\n"{err}"')
            elif data.work_settings['s_error_no_data'].react == 'ignore':
                logger.error(f'Ошибка:\n"{err}"\nРеакция - продолжение выполнения скрипта.')
            elif data.work_settings['s_error_no_data'].react == 'dialog':
                # Остановка выполнения скрипта и вывод модального окна
                self.stop_for_dialog(f'Остановка выполнения скрипта\nРеакция на ошибку данных\n"{err}"')
                if self.modal_stop:
                    raise NoCommandOrStop('Пользователь остановил выполнение скрипта.')
            else:
                # Продолжение выполнения скрипта, но с другого места
                label = data.work_settings['s_error_no_data'].label
                self.pointer_command = self.work_labels[label.label]
                raise DataError(f'Ошибка данных:\n{err}\nРеакция - переход к метке "{label}".')

        except (ElementNotFound, TemplateNotFoundError) as err:
            # Ошибка связанная с элементами изображения
            if data.work_settings['s_error_no_element'].react == 'stop':
                raise NoCommandOrStop(f'Остановка выполнения скрипта\nРеакция на ошибку \n"{err}"')
            elif data.work_settings['s_error_no_element'].react == 'ignore':
                logger.error(f'Ошибка:\n"{err}"\nРеакция - продолжение выполнения скрипта.')
            elif data.work_settings['s_error_no_element'].react == 'dialog':
                # Остановка выполнения скрипта и вывод модального окна
                self.stop_for_dialog(f'Остановка выполнения скрипта\nРеакция на ошибку изображения.\n"{err}"')
                if self.modal_stop:
                    raise NoCommandOrStop('Пользователь остановил выполнение скрипта.')
            else:
                # Продолжение выполнения скрипта, но с другого места
                label = data.work_settings['s_error_no_element'].label
                self.pointer_command = self.work_labels[label.label]
                raise DataError(f'Ошибка\n"{err}"\nРеакция - переход к метке "{label}".')

        if self.pointer_command+1 < len(self.queue_command):
            # Еще есть команды в очереди
            self.pointer_command += 1
            # Между выполнением команд есть регулируемая пауза
            sleep(self.work_settings['s_command_pause'])  # Пауза между командами (всеми)
        else:
            raise NoCommandOrStop('Нет команд для выполнения.')


data = DataForWorker()  # Создаем объект с данными о скрипте


class Editor:
    """ Редактор команд

    Представляет основной интерфейс редактора: выбор команды, кнопки действий.
    Без виджетов ввода данных, они находятся в самих командах.
    А так-же принимает ссылку на фрейм для сообщений, куда размещает виджет
    и выводит сообщения через отдельный метод

    """
    # TODO Правильная обработка множественного выбора строк в списке
    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = data  # Ссылка на класс с данными о скрипте
    save_load = None  # Ссылка на объект класса SaveLoad

    def __init__(self, root):
        """ При инициализации принимает ссылку на виджет, куда выводить элементы интерфейса """
        self.root = root  # Фрейм редактора
        self.current_cmd = None  # Объект команды, с которой работает редактор

        # Формируем словарь: {название команды: класс}, для этого обращаемся к методу класса родителя команд
        # который возвращает классы потомков. В них читаем имена команд и данные о сортировке команд
        # создаем и сортируем список команд в соответствии с номерами для сортировки
        self.commands_dict = {cls.command_name: cls for cls in CommandClasses.get_all_subclasses()}
        self.commands_name = sorted(self.commands_dict, key=lambda x: self.commands_dict[x].for_sort)
        self.commands_var = StringVar(value=self.commands_name[0])  # Переменная содержит выбранное значение

        # Вывод виджета выпадающего списка команд
        self.widget = ttk.Combobox(self.root, values=self.commands_name, width=30,
                     textvariable=self.commands_var, state="readonly", height=100)
        self.widget.place(x=5, y=5)
        self.widget.bind("<<ComboboxSelected>>", self.select_command)

        self.select_command(None)  # Создаем чистый объект команды, будто совершен выбор в списке

        # Кнопки
        self.icon4 = PhotoImage(file="icon/new.png")
        self.icon5 = PhotoImage(file="icon/edit.png")

        new_button = Button(self.root, command=self.add_cmd_button, image=self.icon4, width=100, height=34)
        new_button.place(x=10, y=106)
        ToolTip(new_button, msg="Добавить команду", delay=0.5)

        edit_button = Button(self.root, command=self.change_cmd_button, image=self.icon5, width=100, height=34)
        edit_button.place(x=130, y=106)
        ToolTip(edit_button, msg="Изменить команду", delay=0.5)

    def select_command(self, event):
        """ Обработка выбора команды в выпадающем списке """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if self.current_cmd:
            self.current_cmd.destroy_widgets()  # Удаляем старые виджеты
        try:
            # Получаем имя класса команды, для создания команды
            name = self.commands_dict[self.commands_var.get()].__name__
            # Зная имя класса команды создаем ее объект
            self.current_cmd = CommandClasses.create_command('', command=name)
            # Рисуем его виджеты
            self.current_cmd.paint_widgets()
            # Выводим справку о команде
            logger.info(self.current_cmd.command_description)
        except DataError as err:
            # Ошибки при создании команды
            self.current_cmd = None  # Объект команды, с которой работает редактор
            self.commands_var.set(self.commands_name[0])  # Задаем вывод первой команды
            self.select_command(None)  # Создаем чистый объект команды, будто совершен выбор в списке
            logger.error(err)


    def command_to_editor(self, id_command):
        """ Загрузка команды в редактор """
        if self.current_cmd:
            self.current_cmd.destroy_widgets()  # Удаляем старые виджеты
        if id_command == 'zero':
            # Выбрана пустая строка, создать объект с параметрами по умолчанию
            name = self.commands_dict[self.commands_name[0]].__name__
            # Зная имя класса команды создаем ее объект
            self.current_cmd = CommandClasses.create_command('', command=name)
        else:
            # Делаем копию выбранной команды и все операции выполняем с ней.
            # Получаем краткую запись объекта выбранной команды (dict)
            temp = self.data.obj_command[id_command].command_to_dict()
            # Создаем копию объекта команды по краткой записи (сам объект не меняем)
            self.current_cmd = CommandClasses.create_command(*temp['val'], command=temp['cmd'], description=temp['des'])
        # Рисуем его виджеты
        self.current_cmd.paint_widgets()
        # Выводим справку о команде
        logger.info(self.current_cmd.command_description)
        # Установка в выпадающем списке нужной команды
        self.commands_var.set(self.current_cmd.command_name)
        self.widget.selection_clear()  # Убираем выделение с выпадающего списка

    def add_cmd_button(self, event=None):
        """ Добавление команды из редактора в список """
        if self.data.script_started or self.data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.current_cmd.save()
        try:
            self.data.add_new_command(self.current_cmd)  # Добавление команды в очередь
            self.display_commands.out_commands()  # Обновляем список
            self.save_load.save_history()  # Сохраняем историю
            settings.is_saved = False  # Изменения в проекте не сохранены

        except LabelAlreadyExists as err:
            # При неудачном добавлении в случае совпадения имен блоков и меток
            # добавление отменяется и выводится сообщение
            logger.error(err)

    def change_cmd_button(self, event=None):
        """ Изменение текущей в списке команды на ту, что в редакторе """
        if self.data.script_started or self.data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.current_cmd.save()
        self.data.change_command(self.current_cmd)  # Изменяем команду
        self.display_commands.out_commands()  # Обновляем список
        self.save_load.save_history()  # Сохраняем историю
        settings.is_saved = False  # Изменения в проекте не сохранены

    def menu_delete_images(self):
        """ Удаление неиспользуемых изображений элементов.

        В процессе редактирования изображения элементов для координации мыши остаются после удаления самого
        клика мышью. Это сделано для возможностей истории, чтобы можно было вернуть удаленное действие.
        Эта функция находит неиспользуемые изображения и удаляет их.
        """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        # Составляем список изображений используемых в командах
        images = []
        for command in self.data.obj_command.values():
            if command.__class__.__name__ == 'MouseClickLeft' \
                    or command.__class__.__name__ == 'MouseClickDouble' \
                    or command.__class__.__name__ == 'CheckImage':
                images.append(command.image)

        # Просматриваем все изображения в папке и удаляем неиспользуемые
        i = 0
        for image in os.listdir(settings.path_to_elements):
            if image not in images:
                try:
                    os.remove(os.path.join(settings.path_to_elements, image))
                except:
                    i -= 1
                i += 1

        logger.warning(f'Удалено {i} изображений элементов')


class DisplayCommands:
    """ Виджет списка команд и копок операций над ним

    Отображение изменений в списке команд на экране, реакция на взаимодействие со списком.
    4 кнопки редактирования списка. Копировать, Вырезать, Вставить, Удалить.

    """
    data = data  # Ссылка на класс с данными о скрипте
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)
    save_load = None  # Ссылка на класс сохранения и загрузки

    def __init__(self, root, frame):
        """ Принимает ссылку на окно программы и фрейм для кнопок"""

        # Функция обновления списка out_commands должна выполняться только когда после последнего ее вызова
        # прошло заданное время. Т.е. в серии из нескольких вызовов с частотой меньше заданного промежутка
        # она выполнится только 1 раз после последнего вызова. Переменная для этого механизма.
        self.start_if_zero = 0

        # Create an instance of Style widget
        style = ttk.Style()
        style.theme_use('clam')

        self.root = root
        self.tree = ttk.Treeview(root, show="", columns=('number', 'command'), selectmode="extended", height=28)
        self.tree.column("#1", stretch=NO, width=80)
        self.tree.column("#2", stretch=NO, width=300)
        self.tree.place(x=0, y=0)
        self.out_commands()
        # Выделить третью строку в списке
        self.tree.bind("<Delete>", self.delete)  # Обработка нажатия del на списке
        self.tree.bind("<<TreeviewSelect>>", self.on_select)  # Обработка выбора строки в списке
        self.tree.bind("<Control-KeyPress>", self.keypress)  # Обработка нажатия клавиш на списке
        # Рисуем кнопки для работы со списком
        self.list_copy = []  # Список хранит id скопированных строк
        self.operation = ''  # Может быть copy или cut

        self.icon6 = PhotoImage(file="icon/copy.png")
        self.icon7 = PhotoImage(file="icon/cut.png")
        self.icon8 = PhotoImage(file="icon/paste.png")
        self.icon9 = PhotoImage(file="icon/delete.png")
        self.icon_up = PhotoImage(file="icon/up.png")
        self.icon_down = PhotoImage(file="icon/down.png")

        up_button = Button(frame, command=self.up, image=self.icon_up, width=80, height=34)
        up_button.place(x=10, y=10)
        ToolTip(up_button, msg="Переместить вверх", delay=0.5)

        copy_button = Button(frame, command=self.copy, image=self.icon6, width=120, height=34)
        copy_button.place(x=105, y=10)
        ToolTip(copy_button, msg="Переместить вниз", delay=0.5)

        cut_button = Button(frame, command=self.cut, image=self.icon7, width=120, height=34)
        cut_button.place(x=240, y=10)
        ToolTip(cut_button, msg="Переместить команды", delay=0.5)

        down_button = Button(frame, command=self.down, image=self.icon_down, width=80, height=34)
        down_button.place(x=10, y=58)
        ToolTip(down_button, msg="Копировать команды", delay=0.5)

        paste_button = Button(frame, command=self.paste, image=self.icon8, width=120, height=34)
        paste_button.place(x=105, y=58)
        ToolTip(paste_button, msg="Вставить команды", delay=0.5)

        delete_button = Button(frame, command=self.delete, image=self.icon9, width=120, height=34)
        delete_button.place(x=240, y=58)
        ToolTip(delete_button, msg="Удалить команды", delay=0.5)

    def keypress(self, event):
        """ Обработка нажатия клавиш на списке """
        code = event.keycode
        if code == system.hotkeys['Ctrl_A']:
            # Ctrl+a
            if data.script_started or data.is_listening:
                return  # Операция невозможна при выполнении или записи скрипта
            self.tree.selection_set(self.tree.get_children())
        elif code == system.hotkeys['Ctrl_C']:
            # Ctrl+c
            self.copy()
        elif code == system.hotkeys['Ctrl_X']:
            # Ctrl+x
            self.cut()
        elif code == system.hotkeys['Ctrl_V']:
            # Ctrl+v
            self.paste()
        elif code == system.hotkeys['Ctrl_Up']:
            # Ctrl+up
            self.up()
        elif code == system.hotkeys['Ctrl_Down']:
            # Ctrl+down
            self.down()

    def on_select(self, event):
        """ Обработка события выбора строки в списке """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        try:
            selected_item = event.widget.selection()[0]  # Получаем id команды
        except:
            # Иногда не показывает выделение
            return
        # Устанавливаем указатель списка
        self.data.pointer_command = -1 if selected_item == 'zero' else self.data.queue_command.index(selected_item)
        self.editor.command_to_editor(selected_item)  # Выводим команду в редактор по ее id

    def out_commands(self):
        """ Вывод строк в виджет (Обновление списка)

        Берет строки из объекта с данными и выводит их в виджет.
        Названия команд запрашивает у их объектов, где при наличии описания возвращается оно, а не название.

        Поддерживает умное обновление, только при записи.
        Обновляет список не каждый раз при вызове, а только когда после последнего
        вызова пройдет заданное время. Чтобы не выполнять обновления для каждой часто идущей команды обновления.
        Для этого запускает функцию обновления с отсрочкой и добавляет счетчику 1. Функция обновления отнимает 1
        от счетчика и если он стал 0 - выполняет обновление.
        """
        def update_list():
            self.start_if_zero -= 1
            if self.start_if_zero < 1:
                # Отменит все предыдущие обновления, если есть запрос на новое
                self.start_if_zero = 0
                self.clear()
                self.tree.insert('', 0, 'zero', values=('', ''))  # Добавляем пустую строку
                for i, id in enumerate(data.queue_command):
                    # Выводим список
                    self.tree.insert('', 'end', id, values=(i+1, self.data.obj_command[id]))
                self.tree.selection_set(self.tree.get_children()[data.pointer_command+1])  # Выделяем строку
                pass
        # Запускаем функцию обновления списка, с отсрочкой
        if data.is_listening:
            # Умное обновление работает только при записи
            self.start_if_zero += 1
            self.root.after(500, update_list)
        else:
            self.start_if_zero = 0
            update_list()

    def clear(self):
        """ Очистка списка команд """
        self.tree.delete(*self.tree.get_children())

    def get_selected(self):
        """ Возвращает список выделенных в списке id строк """
        list_copy = list(self.tree.selection())  # id выделенных команд
        if 'zero' in list_copy:
            # Удаляем пустую строку
            list_copy.remove('zero')
        return list_copy

    def numbers_from_id(self, ids: list) -> list[str]:
        """ Принимает список id строк, возвращает их номера str """
        return [str(self.data.queue_command.index(i)+1) for i in ids]

    def copy(self, event=None):
        """ Обработчик кнопки Копировать """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.list_copy = self.get_selected()  # id выделенных команд
        if not self.list_copy:
            return
        numbers = ' ,'.join(self.numbers_from_id(self.list_copy))  # Номера копируемых строк
        logger.warning(f'Скопированы строки {numbers}. \nИх можно вставить кнопкой Вставить. '
                              f'\nСтроки будут вставлены после выделенной строки.')
        self.operation = 'copy'

    def cut(self, event=None):
        """ Обработчик кнопки Вырезать """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.list_copy = self.get_selected()  # id выделенных команд
        if not self.list_copy:
            return
        numbers = ' ,'.join(self.numbers_from_id(self.list_copy))  # Номера копируемых строк
        logger.warning (f'Перенос строк {numbers}. \nИх можно вставить кнопкой Вставить. '
                              f'\nСтроки будут вставлены после выделенной строки. '
                          f'\nСкопированные строки будут удалены')
        self.operation = 'cut'

    def paste(self, event=None):
        """ Обработчик кнопки Вставить

        Вставка при копировании и переносе происходит по разному. При копировании создается новый
        объект с параметрами старого, при переносе объекты просто меняют положение в списке.

        """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if self.operation and self.list_copy:
            # Убеждаемся, что операция актуальна и скопированные строки есть

            # При вставке команд может возникнуть осложнение, вызванное дублированием
            # имени метки или блока. В этом случае будет возвращено исключение.
            # При копировании нужно сгенерировать новое название метки и изменить его,
            # после чего повторить попытку добавления команды.
            list_select = []  # Запишем сюда вставленные строки, чтобы выделить их после вставления
            # Строки будут вставлены за последней выделенной строкой, определяем ее
            if self.get_selected():
                data.pointer_command = self.data.queue_command.index(self.get_selected()[-1])
            else:
                data.pointer_command = -1
            mess = 'Операция выполнена успешно.'
            if self.operation == 'copy':
                # Копирование элементов
                for i in self.list_copy:
                    # Делаем копию команды.
                    temp = self.data.obj_command[i].command_to_dict()
                    # Создаем копию объекта команды по краткой записи
                    obj = CommandClasses.create_command(*temp['val'], command=temp['cmd'],
                                                                     description=temp['des'])
                    ok = True
                    while ok:
                        try:
                            # Вставляем скопированные команды
                            key = self.data.add_new_command(obj)
                            list_select.append(key)  # Записываем id вставленной команды
                            ok = False  # Операция прошла успешно

                        except LabelAlreadyExists:
                            # Добавление команды не выполнено по причине дублирования имени метки или блока
                            obj.value += f"_{choice(string.ascii_lowercase) + str(randint(0, 100))}"
                            mess = 'Копирование и перенос меток и блоков произведено с изменением их названий.'

            else:
                # Перенос элементов
                # Находим индексы элементов по названию
                old_indexes = [self.data.queue_command.index(elem) for elem in self.list_copy]
                # Извлекаем элементы из списка в обратном порядке, чтобы не нарушить порядок индексов
                elements = [self.data.queue_command.pop(i) for i in sorted(old_indexes, reverse=True)]
                elements.reverse()  # Разворачиваем список
                # Вставляем элементы на новые позиции
                for i, elem in enumerate(elements):
                    self.data.queue_command.insert(self.data.pointer_command+1+i, elem)

                list_select = self.list_copy.copy()  # Список строк для выделения
                # Очищаем данные операции
                self.list_copy = []
                self.operation = ''

            self.out_commands()  # Обновляем список
            self.tree.selection_set(list_select)  # Выделяем вставленные строки
            self.save_load.save_history()  # Сохраняем историю
            settings.is_saved = False  # Изменения в проекте не сохранены

            logger.warning(mess)

        else:
            # Операция не назначена или отменена
            logger.warning('Операция отменена.')
            pass

    def delete(self, event=None):
        """ Обработчик кнопки Удалить """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        list_del = self.get_selected()  # id выделенных команд
        if not list_del:
            return
        for i in list_del:
            self.data.del_command(i)

        # Очищаем данные операции
        self.list_copy = []
        self.operation = ''

        self.save_load.save_history()  # Сохраняем историю
        settings.is_saved = False  # Изменения в проекте не сохранены

        self.out_commands()  # Обновляем список

    def up(self, event=None):
        """ Перемещение выделенных строк вверх

        Используя вырезать и вставить переносим выделенные строки на 1 вверх,
        после вставки выделяем перенесенные строки на новых местах.
        """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        # Определяем индекс строки куда вставлять
        try:
            where_to_insert = self.data.queue_command.index(self.get_selected()[0]) - 2
            if where_to_insert < -1:
                return
        except:
            where_to_insert = -1
        self.cut()  # Вырезаем выделенные строки
        self.tree.selection_set(self.tree.get_children()[where_to_insert+1])  # Выделяем строку куда вставлять
        self.paste()  # Вставляем выделенные строки

    def down(self, event=None):
        """ Перемещение выделенных строк вниз """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        all_selected =self.get_selected()
        if not all_selected:
            return
        where_to_insert = self.data.queue_command.index(self.get_selected()[0]) + 1 # Индекс строки куда вставлять
        last_index = self.data.queue_command.index(self.get_selected()[-1])  # Индекс последней выделенной строки
        if last_index == len(self.data.queue_command) - 1:
            return
        self.cut()
        self.tree.selection_set(self.tree.get_children()[where_to_insert])  # Выделяем строку куда вставлять
        self.paste()


class DataSource:
    """ Источник данных """
    # TODO добавить кнопку сброса указателей источника данных
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)
    save_load = None  # Ссылка на объект класса Сохранение/загрузка (реализация паттерна Наблюдатель)

    def __init__(self, root):
        self.data_source_file = None
        self.value = StringVar()  # Список полей источника данных через запятую (текст)
        Message(root, text='Источник данных', width=370, anchor='w', textvariable=self.value).place(x=0, y=0)

    def menu_data_source(self):
        """ Выбор и подключение источника данных """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        try:
            new_file = fd.askopenfilename(initialdir=settings.path_to_data,
                filetypes=(("image", "*.xlsx"), ("image", "*.xls"),
                           ("All files", "*.*")))
            if new_file:
                name = os.path.basename(new_file)  # Имя файла
                if os.path.dirname(new_file).replace('/', '\\') != settings.path_to_data.replace('/', '\\'):
                    # Если файл не находится в папке для данных, то копируем его туда
                    # сравниваем пути, учитывя, что слэши в пути могут быть разные
                    if os.path.exists(os.path.join(settings.path_to_data, name)):
                        # Есть ли такой файл в папке для данных спрашиваем, заменить ли его
                        if messagebox.askyesno('Замена файла', f'Файл {name} уже существует. Заменить?'):
                            os.remove(os.path.join(settings.path_to_data, name))
                    else:
                        # Копирование источника данных в папку для данных data
                        shutil.copy(new_file, settings.path_to_data)
                self.load_file(name)  # Загрузка файла
                logger.warning(f'Источник данных {self.data_source_file} загружен.')

        except Exception as err:
            # При ошибках с источником данных
            logger.error(err)

    def load_file(self, name):
        """ Загрузка excel файла """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        try:
            path_and_name = os.path.join(settings.path_to_data, name)
            if not os.path.exists(path_and_name):
                raise DataError(f'Файл {name} не найден.')
            data_frame = pd.read_excel(path_and_name)  # Читаем таблицу в pandas DataFrame
            data.data_source = data_frame.to_dict('list')  # Превращаем DataFrame в словарь
            fields = data.get_fields()  # Список полей данных
            # Выводим ключи словаря в список полей источника данных
            self.value.set(', '.join(fields))
            data.pointers_data_source = dict.fromkeys(fields, 0)  # Конвертация списка в словарь (ставим указатели)

            # Добавление информации об источнике в конфигурационный файл
            self.save_load.config_file(action='set', data=name)
            self.data_source_file = name  # Назначаем новый источник данных

        except Exception as err:
            # При ошибках с источником данных
            raise DataError(f'Ошибка загрузки источника данных {err}')

    def menu_reset_pointers(self):
        """ Сброс указателей источника данных """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        data.pointers_data_source = dict.fromkeys(data.pointers_data_source, 0)
        logger.warning('Указатели источника данных сброшены.')

    def menu_delete_data_source(self):
        """ Отключение источника данных """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.data_source_file = None
        self.value.set('')
        data.data_source.clear()
        data.pointers_data_source.clear()
        # Удаление информации об источнике в конфигурационном файле
        self.save_load.config_file(action='del')
        logger.warning('Источник данных отключен.')


class SaveLoad:
    """ Сохранение и чтение проекта """
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)
    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data_source = None  # Ссылка на объект источника данных (реализация паттерна Наблюдатель)

    def __init__(self, root):
        """ Подготовка программы к запуску

         Чтение файла конфигурации, если его нет, то создание нового.
         В фале хранится путь к последнему открытому проекту и путь к источнику данных.
         Если найдены данные о проекте, то проект открывается.
         Если папки с проектом не существует или файл конфигурации новый,
         то и проект создается новый с именем по умолчанию.
         """
        self.new_project_name = ''
        self.new_path_to_project = ''
        self.new_project_cancel = True  # Отмена создания нового проекта
        self.root = root  # Ссылка на главное окно

        settings.is_saved = False  # Изменения в проекте не сохранены
        # История скрипта, сохраняет каждое предыдущее состояние скрипта в виде списка словарей
        self.history = deque(maxlen=100)  # Помнит последние 100 состояний скрипта
        self.history_pointer = -1  # Указатель на текущее состояние скрипта

    def load_old_project(self):
        # Проверка файла конфигурации
        if os.path.exists('config.ini'):
            # Если файл конфигурации есть, то читаем его
            config = self.config_file()
            self.new_project_name = config['name']
            self.new_path_to_project = config['path']
            self.data_source.data_source_file = config['data']

        if self.new_project_name:
            # Если данные о проекте есть, то открываем проект
            try:
                self.open_project()
            except LoadError as err:
                self.new_project_name = ''

        if self.new_project_name == '':
            # Если данные о проекте не найдены, проекта нет или он не открылся,
            # то создаем новый проект и переписываем файл конфигурации.

            # Создаем имя проекта по умолчанию
            name = 'script_'
            i = 1
            while os.path.exists(os.path.join(name + str(i))):
                i += 1
            self.new_project_name = name + str(i)
            self.new_path_to_project = os.getcwd()
            self.create_project()

    def create_project(self):
        """ Создание проекта """
        try:
            name = self.new_project_name
            path = self.new_path_to_project
            os.makedirs(os.path.join(path, name))
            os.makedirs(os.path.join(path, name, 'data'))
            os.makedirs(os.path.join(path, name, 'elements_img'))
            with open(os.path.join(path, name, f'{name}.json'), 'w') as f:
                json.dump({"script": "[]", "settings": "{}"}, f)

            logger.warning(f'Создан новый проект {name}.')
            settings.is_saved = True  # Изменения в проекте не сохранены

            settings.default_settings()  # Сброс настроек по умолчанию

            # Запись новых настроек в файл конфигурации
            self.config_file(action='set', name=name, path=path)

            # Сохраняем новые настройки проекта
            settings.path_to_project = self.new_path_to_project
            settings.project_name = self.new_project_name
            settings.update_settings()

            self.open_project()  # Открываем новый проект

        except Exception as err:
            logger.error(f'Ошибка при создании проекта {err}')

    def menu_new_project(self):
        """ Пункт меню Создание нового проекта """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if not settings.is_saved:
            # Если проект не сохранен, то предложить сохранить проект
            result = messagebox.askyesnocancel('Сохранение проекта', 'Сохранить проект?')
            if result:
                self.save_project()
            elif result is None:
                return

        self.dialog_new_project()  # Открываем диалоговое окно для выбора пути и имени проекта
        if self.new_project_name:
            self.create_project()  # Создаем проект

    def menu_open_project(self):
        """ Пункт меню Открыть проект """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if not settings.is_saved:
            # Если проект не сохранен, то предложить сохранить проект
            result = messagebox.askyesnocancel('Сохранение проекта', 'Сохранить проект?')
            if result:
                self.save_project()
            elif result is None:
                return

        # Открываем диалоговое окно для выбора проекта
        path = fd.askdirectory(initialdir=self.new_path_to_project, title="Открыть проект")
        if not path:
            return

        # Последней в пути папка проекта, отделяем ее от пути
        self.new_project_name = os.path.basename(path)  # получаем имя проекта
        self.new_path_to_project = os.path.dirname(path)  # получаем путь к проекту
        try:
            self.open_project()
        except LoadError as err:
            logger.error(err)

    def menu_save_project(self):
        """ Пункт меню Сохранить проект """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.save_project()

    def menu_save_as_project(self):
        """ Пункт меню Сохранить проект как """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        # Открываем диалоговое окно для выбора проекта
        self.dialog_new_project('Сохранить проект как...')  # Открываем диалоговое окно для выбора пути и имени проекта
        if self.new_project_name:
            try:
                new_project = os.path.join(self.new_path_to_project, self.new_project_name)
                # Копируем содержимое папки проекта  новую папку
                shutil.copytree(os.path.join(settings.path_to_project, settings.project_name), new_project)
                # Удаляем в новом проекте файл скрипта
                os.remove(os.path.join(new_project, f'{settings.project_name}.json'))
                # Сохраняем новые настройки проекта
                settings.path_to_project = self.new_path_to_project
                settings.project_name = self.new_project_name
                settings.update_settings()
                # Сохраняем актуальный скрипт в новый проект
                self.save_project()

                logger.warning(f'Проект {self.new_project_name} сохранен.')
                settings.is_saved = True
            except Exception:
                raise

    def data_preparation(self):
        """ Подготовка данных для сохранения """
        script = json.dumps([data.obj_command[label].command_to_dict() for label in data.queue_command],
                            default=lambda o: o.__json__())  # Подготовка скрипта
        sett = json.dumps(settings.get_dict_settings(), default=lambda o: o.__json__())  # Подготовка настроек
        # Еще добавляем имя файла - источника данных
        return {'script': script, 'settings': sett, 'data_source': self.data_source.data_source_file}

    def save_project(self):
        """ Сохранение проекта """
        for_save = self.data_preparation()  # Подготовка данных для сохранения
        # сохраняем в файл
        file_path = os.path.join(settings.path_to_script, f'{settings.project_name}.json')
        with open(file_path, "w") as f:
            json.dump(for_save, f)
        # Исправляем файл конфигурации
        self.config_file(action='set', name=settings.project_name, path=settings.path_to_project,
                         data=self.data_source.data_source_file)
        logger.warning(f'Проект {settings.project_name} сохранен.')
        settings.is_saved = True

    def change_script_and_settings(self, data_dict):
        """ Замена скрипта и настроек

        Принимает словарь с данными скрипта и настроек из файла или истории
        """
        script = json.loads(data_dict['script'])
        sett = json.loads(data_dict['settings'])

        # Удаляем старый скрипт и записываем новый
        data.queue_command.clear()  # Очередь команд
        data.obj_command.clear()  # Список команд
        llist.labels.clear()  # Список меток
        data.pointer_command = 0

        # При построении скрипта команды меток и названий блоков должны быть созданы и добавлены в первую очередь
        # Поэтому создаем их, добавляем
        for i, cmd_dict in enumerate(script):
            # Создаем объект команды с метками по краткой записи
            if cmd_dict['cmd'] == 'BlockCmd' or cmd_dict['cmd'] == 'LabelCmd':
                insert = CommandClasses.create_command(
                    *cmd_dict['val'], command=cmd_dict['cmd'], description=cmd_dict['des'])
                data.add_new_command(insert)

        # Создаем остальные и вставляем на свои места
        for i, cmd_dict in enumerate(script):
            # Добавляем остальные команды по краткой записи
            if cmd_dict['cmd'] != 'BlockCmd' and cmd_dict['cmd'] != 'LabelCmd':
                data.pointer_command = i - 1  # Указатель, куда вставить команду
                data.add_new_command(CommandClasses.create_command(
                    *cmd_dict['val'], command=cmd_dict['cmd'], description=cmd_dict['des']))

        # Обновляем список, предварительно установив указатель на начало
        data.pointer_command = -1
        self.display_commands.out_commands()

        settings.set_settings_from_dict(sett)  # Устанавливаем настройки

    def open_project(self):
        """ Загрузка проекта """

        # Папка проекта должна содержать 2 вложенные папки: data и elements_img и файл скрипта
        # с таким же именем, как и папка проекта, но с расширением .json, проверим это
        this_project = True
        if not os.path.exists(os.path.join(self.new_path_to_project, self.new_project_name, settings.data_folder)):
            this_project = False
        if not os.path.exists(os.path.join(
                self.new_path_to_project, self.new_project_name, settings.elements_folder)):
            this_project = False
        if not os.path.exists(os.path.join(
                self.new_path_to_project, self.new_project_name, f'{self.new_project_name}.json')):
            this_project = False
        if not this_project:
            raise LoadError('Выбранная папка не является проектом')

        try:
            file_path = os.path.join(self.new_path_to_project, self.new_project_name, f'{self.new_project_name}.json')
            # Загружаем данные из файла в переменную
            with open(file_path, "r") as f:
                data_dict = json.load(f)
            self.change_script_and_settings(data_dict)  # Заменяем скрипт и настройки

            # Запоминаем путь к проекту и его имя в настройках
            settings.path_to_project = self.new_path_to_project
            settings.project_name = self.new_project_name
            settings.update_settings()

            mess = f'Проект {self.new_project_name} открыт.'
            self.root.title(f'Редактор скриптов ({self.new_project_name})')
            self.save_history()  # Сохраняем историю
            settings.is_saved = True

        except Exception as err:
            raise LoadError(f'Ошибка загрузки проекта {err}')

        # Загружаем файл источника данных
        source = data_dict.get('data_source')
        try:
            if source:
                self.data_source.load_file(source)
                mess += f'\nИсточник данных {source} загружен.'
        except:
            mess += f'\nОшибка загрузки источника данных {source}.'
            # raise
        logger.warning(mess)

    def rename_project(self):
        """ Переименование проекта """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        try:
            # Диалоговое окно для ввода имени проекта
            # создаем диалоговое окно для ввода текста
            text = simpledialog.askstring("Переименование проекта", "Новое имя проекта:")
            # Проверка на пустую строку и допустимые символы файловой системы
            if text is None or text == '':
                return
            if not re.match(r'^[a-zA-Zа-яА-Я0-9_\- ]+$', text):
                logger.warning('Недопустимое имя проекта.')
                return
            # Проверка на существование проекта с таким именем
            if os.path.exists(os.path.join(self.new_path_to_project, text)):
                logger.warning('Проект с таким именем уже существует.')
                return

            # Переименовываем файл скрипта
            os.rename(os.path.join(settings.path_to_script, f'{settings.project_name}.json'),
                      os.path.join(settings.path_to_script, f'{text}.json'))
            # Переименовываем папку проекта
            os.rename(os.path.join(settings.path_to_project, settings.project_name),
                      os.path.join(settings.path_to_project, text))

            logger.warning(f'Текущий проект "{settings.project_name}" переименован в "{text}".')

            # Запоминаем новое имя в настройках
            settings.project_name = text
            settings.update_settings()

            # Вносим изменения в файл конфигурации
            self.config_file(action='set', name='text')

        except Exception as err:
            raise
            logger.error(f'Ошибка переименования проекта "{err}"')

    def dialog_new_project(self, operation='Создание нового проекта'):
        """ Диалоговое окно для создания нового проекта

        Проект - это папка с 2 вложенными папками: data  и elements_img.
        Для этого выводим диалоговое окно  с полем для ввода названия проекта и кнопкой
        для выбора папки, где сохранится проект. Под этими элементами выводится строка с полным путем к
        проекту и его именем. При изменении названия проекта или пути к нему, меняется и строка.
        По умолчанию путь к проекту - текущая директория. Если такой проект уже существует в этой папке
        в строке выводится ошибка и предложение выбрать новое имя.
        Ниже кнопка для создания проекта. Если окно закрыть, то путь и имя очистятся.
        """
        self.new_project_cancel = True  # Отмена создания нового проекта
        self.new_project_name = ''
        self.new_path_to_project = ''

        def choose_path(name, label):
            """ Выбор пути к проекту """
            path = fd.askdirectory()
            if path:
                path_mem = self.new_path_to_project
                self.new_path_to_project = path
                if not check_name(name, label):
                    self.new_path_to_project = path_mem

        def check_name(name, label):
            """ Проверка уникальности названия проекта """
            name = name.get()
            self.new_project_name = name
            if name:
                if os.path.exists(os.path.join(self.new_path_to_project, name)):
                    label['text'] = 'Такой проект уже существует.'
                    self.new_project_name = ''
                    return False
            label['text'] = os.path.join(self.new_path_to_project, name)
            return True

        def create_project():
            """ Создание проекта """
            if self.new_project_name:
                self.new_project_cancel = False  # Проект можно создавать
                on_closing()

        def on_closing():
            """ Закрытие окна

            При закрытии окна, если переменная отмены создания проекта
            говорит об отмене - очищаем путь и имя.
            """
            if self.new_project_cancel:
                self.new_path_to_project = ''
                self.new_project_name = ''
            window.destroy()

        # Создаем окно
        window = Toplevel()
        window.title(operation)
        # Разместить окно в центре экрана
        window.geometry('400x215')
        window.transient(self.root)  # Поверх окна
        window.update_idletasks()
        x = (window.winfo_screenwidth() - 400) / 2
        y = (window.winfo_screenheight() - 215) / 2
        window.geometry("+%d+%d" % (x, y))
        window.resizable(False, False)

        # Создаем элементы окна
        label_name = Label(window, text='Название проекта')
        label_name.place(x=10, y=10)
        entry_name = Entry(window)
        entry_name.place(x=10, y=30, width=380)
        button_path = Button(window, text='Выбрать папку', command=lambda: choose_path(entry_name, label_full_path))
        button_path.place(x=10, y=80)
        label_full_path = Label(window, text='')
        label_full_path.place(x=10, y=140)
        button_create = Button(window, text='Применить', command=create_project)
        button_create.place(x=250, y=170)

        # Подписываемся на события
        entry_name.bind('<KeyRelease>', lambda event: check_name(entry_name, label_full_path))
        window.protocol("WM_DELETE_WINDOW", on_closing)  # Функция выполнится при закрытии окна
        # Запускаем окно
        window.grab_set()
        window.focus_set()
        window.wait_window()

    def config_file(self, action='get', name='', path='', data=''):
        """ Изменение файла конфигурации

        Действие get, set, del указывает операцию с файлом конфигурации.
        del - удаление данных только о файле источника данных.
        """
        config = ConfigParser()
        """ Получение файла конфигурации """
        config.read('config.ini')
        if action == 'set':
            if name:
                config['DEFAULT']['project_name'] = name
            if path:
                config['DEFAULT']['path_to_project'] = path
            if data:
                config['DEFAULT']['data_file'] = data
        elif action == 'del':
            config['DEFAULT']['data_file'] = ''
        else:
            out = dict()
            out['name'] = config['DEFAULT'].get('project_name', '')
            out['path'] = config['DEFAULT'].get('path_to_project', '')
            out['data'] = config['DEFAULT'].get('data_file', '')
            return out

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def save_history(self):
        """ Сохранение истории

        История изменений сохраняется в свойстве self.history. Имеет лимит записей, старые
        записи уничтожаются по мере добавления новых. Записи добавляются после совершения операций.
        """
        state = self.data_preparation()
        selected = self.display_commands.get_selected()  # Находим выделенные строки
        # Определяем их номера в списке и записываем в историю
        state['selected'] = [self.display_commands.tree.index(item) for item in selected]
        self.history.append(state)
        self.history_pointer = len(self.history)-1  # Указатель истории на последнюю запись

    def undo_button(self):
        """ Отмена последнего изменения """
        if data.script_started or data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if self.history_pointer > 0:
            self.history_pointer -= 1
            state = self.history[self.history_pointer]
            self.change_script_and_settings(state)  # Заменяем скрипт и настройки
            # Получаем номера выделенных строк, формируем список индексов в списке и выделяем
            selected = []
            for item in state['selected']:
                try:
                    selected.append(self.display_commands.tree.get_children()[item])
                except IndexError:
                    # Предотвращаем ошибки если не найдет индекса
                    pass
            if not selected:
                selected = ['zero']
            self.display_commands.tree.selection_set(selected)
            logger.warning(f'Состояние {self.history_pointer+1}')

    def return_button(self):
        """ Возврат к более позднему изменению (отмененному ранее) """
        if data.script_started or data.is_listening or self.history_pointer == len(self.history) - 1:
            return  # Возврат невозможен, если запущен скрипт или слушатель или указатель на последней записи

        self.history_pointer += 1
        state = self.history[self.history_pointer]
        self.change_script_and_settings(state)  # Заменяем скрипт и настройки
        # Получаем номера выделенных строк, формируем список индексов в списке и выделяем
        selected = []
        for item in state['selected']:
            try:
                selected.append(self.display_commands.tree.get_children()[item])
            except IndexError:
                # Предотвращаем ошибки если не найдет индекса
                pass
        if not selected:
            selected = ['zero']
        self.display_commands.tree.selection_set(selected)
        logger.warning(f'Состояние {self.history_pointer+1}')
