# Набор классов для создания различных элементов ввода данных.
# Классы используют виджеты tkinter

import re
from tkinter import *


class DataInput():
    """ Базовый класс

     В зависимости от типа принимаемых данных создает объект (виджет)
     нужного подкласса с переданными параметрами.
     Валидирует ввод, запускает переданную функцию по определенному событию.

     """
    def __init__(self, **kvargs):

        # Параметры по умолчанию
        self.x = self.y = 0
        self.width = 5
        self.length = 1000
        self.black_list = ''
        self.func_event = None

        # Создаем атрибуты всех присланных параметров
        for key, val in kvargs.items():
            self.__dict__[key] = val

        self.obj = None  # Сюда сохраняем объект виджета

    def widget_event(self, event):
        """ Определяет одно (нужное для работы) событие и выполняет функцию назначенную при создании объекта"""
        return self.func_event(event)


class FieldInt(DataInput):
    """ Ввод целых чисел

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    width - ширина виджета в символах
    length - ограничение по длине
    func_event - функция, обрабатывающая нажатие Enter

    """

    def __init__(self, root, **kvargs):
        super().__init__(**kvargs)

        check = (root.register(self.is_valid), "%P")  # Назначаем функцию валидации

        en = Entry(root, width=kvargs['width'], validate="key", validatecommand=check)
        en.place(x=kvargs['x'], y=kvargs['y'])

        en.bind('<Return>', self.func_event)  # Ловим нажатие Enter

    def is_valid(self, val):
        """ Пускает только целое число или пустую строку """

        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return re.fullmatch('\d+', val)  # Строка состоит только из цифр


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
        """ Пускает только целое число или пустую строку """

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
        """ Пускает только целое число или с точкой между цифрами """

        if not val:
            return True  # Строка может быть пустой

        if len(val) > self.length:
            return False  # Недопустимая длина

        return re.fullmatch('^\d+(?:[\.,]\d*)?$', val) # Пропускает целые и дробные числа


