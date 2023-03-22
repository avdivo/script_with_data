# Набор классов для создания различных элементов ввода данных.
# Классы используют виджеты tkinter

import re
from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont

class DataInput:
    """ Базовый класс

     В зависимости от типа принимаемых данных создает объект (виджет)
     нужного подкласса с переданными параметрами.
     Валидирует ввод, запускает переданную функцию по определенному событию.

     """

    def widget_event(self, event):
        """ Определяет одно (нужное для работы) событие и выполняет функцию назначенную при создании объекта"""
        return self.func_event(event)

    @classmethod
    def CreateInput(cls, root, value, x=0, y=0, width=20, length=30, func_event=None, black_list=''):
        """ Общий интерфейс для всех типов полей ввода

        Параметры:
        root - родительский виджет
        x, y - координаты на родительском виджета
        width - ширина виджета в символах
        length - ограничение по длине
        func_event - функция, обрабатывающая нажатие Enter (или другое событие ввода)
        black_list - список запрещенных символов (для строк)
        value - значение при инициализации

        Вывод данных:
        свойство value каждого объекта содержит результат ввода данных,
        свойство widget каждого объекта - доступ к выведенному виджету

        """


        # Установка параметров
        cls.root = root
        cls.type = type(value)
        cls.x = x
        cls.y = y
        cls.width = width
        cls.length = length
        cls.func_event = func_event
        cls.black_list = black_list
        cls.value = value

        class_name = f'Field{type(value).__name__.capitalize()}'  # Формируем имя класса из типа переменной
        required_class = globals()[class_name]
        return required_class()

    # Источник: https: // pythonstart.ru / osnovy / classmethod - staticmethod - python
class FieldInt(DataInput):
    """ Ввод целых чисел

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    func_event - функция, обрабатывающая нажатие Enter
    value - значение при инициализации

    """

    def __init__(self):
        super().__init__()

        check = (self.root.register(self.is_valid), "%P")  # Назначаем функцию валидации

        self.value = StringVar(value=self.value)  # Переменная хранящая введенный текст
        en = Entry(self.root, width=self.width, validate="key", validatecommand=check, textvariable=self.value)
        en.place(x=self.x, y=self.y)

        en.bind('<Return>', self.func_event)  # Ловим нажатие Enter

    def is_valid(self, val):
        """ Пускает только целое число или пустую строку """
        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return bool(re.fullmatch(r'\d+', val))  # Строка состоит только из цифр


class FieldStr(FieldInt):
    """ Ввод строк

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    black_list - список запрещенных символов
    func_event - функция, обрабатывающая нажатие Enter

    """

    def is_valid(self, val):
        """ Пропускает строку с заданными параметрами """

        for i in self.black_list:
            if i in val:
                return False  # Содержит символы из черного списка

        if len(val) > self.length:
            return False  # Недопустимая длина строки

        return True


class FieldFloat(FieldInt):
    """ Ввод числа с плавающей точкой

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    func_event - функция, обрабатывающая нажатие Enter

    """

    def is_valid(self, val):
        """ Пускает целое число, дробное, пустую строку """

        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return bool(re.fullmatch(r'^\d+(?:[\.,]\d*)?$', val))  # Пропускает целые и дробные числа


class FieldBool(DataInput):
    """ Ввод логического значения

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    func_event - функция, обрабатывающая нажатие Enter

    """

    def __init__(self):
        super().__init__()

        self.value = IntVar(value=self.value)

        en = Checkbutton(self.root, width=self.width, variable=self.value, command=self.func_event)
        en.place(x=self.x, y=self.y)


class FieldLlist(DataInput):
    """ Ввод имени метки в скрипте

    Для хранения метки используется специальный тип данных llist
    он предоставляет список всех меток, а его экземпляры хранят выбранные метки

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    func_event - функция, обрабатывающая нажатие Enter

    """

    def __init__(self):
        super().__init__()
        self.selected = StringVar(value=self.value)

        long = len(max(self.value.labels, key=len))
        combobox = ttk.Combobox(self.root, values=self.value.labels,
                                textvariable=self.selected, state="readonly")
        combobox.place(x=self.x, y=self.y)

        combobox.configure(width=long)
        combobox.bind("<<ComboboxSelected>>", self.func_event)


class FieldLEres(DataInput):
    """ Выбор реакции на ошибку

    Могут быть 3 типа реакции на ошибку:
    stop - остановит скрипт
    ignore - проигнорировать ошибку
    run - запустить скрипт с указанной метки
    Для выбора используется 2 ComboBox списка, в первом - реакция (3 варианта),
    во втором тип llist определяющий метку в скрипте, если в 1 списке выбран run.
    Принимает и возвращает тип eres

    Параметры:
    root - родительский виджет
    x, y - координаты первого виджета на родительском, второй идет справа
    func_event - функция, обрабатывающая нажатие Enter

    """

    def __init__(self):
        super().__init__()

        # Выбор реакции
        self.selected_react = StringVar(value=self.value.react)

        long = len(max(self.value.react_list, key=len))
        combobox = ttk.Combobox(self.root, values=self.value.react_list,
                                textvariable=self.selected_react, state="readonly")
        combobox.place(x=self.x, y=self.y)

        combobox.configure(width=long)
        combobox.bind("<<ComboboxSelected>>", self.change_react)

        # Выбор метки
        DataInput.CreateInput((self.root, llist('name 4'), x=30, y=50, width=10,
                                  length=4, func_event=self.test_event)

    def change_react(self):
        if self.

        self.selected = StringVar(value=self.value)

        combobox = ttk.Combobox(self.root, values=self.value.labels, textvariable=self.selected, state="readonly")
        combobox.place(x=self.x, y=self.y)

        combobox.bind("<<ComboboxSelected>>", self.func_event)

