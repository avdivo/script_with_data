# ---------------------------------------------------------------------------
# Набор классов для создания различных элементов ввода данных.
# Классы используют виджеты tkinter
# ---------------------------------------------------------------------------


import re
from tkinter import *
from tkinter import ttk

from data_types import llist

class DataInput:
    """ Базовый класс

     В зависимости от типа принимаемых данных создает объект (виджет)
     нужного подкласса с переданными параметрами.
     Валидирует ввод, запускает переданную функцию по определенному событию.

     """

    def __init__(self, root, value, x, y, func_event, black_list='', width=None, length=None):

        # Установка параметров
        self.root = root
        self.type = type(value)
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.func_event = func_event
        self.black_list = black_list
        self.value = value

    def widget_event(self, event):
        """ Определяет одно (нужное для работы) событие и выполняет функцию назначенную при создании объекта"""
        return self.func_event(event)

    @property
    def result(self):
        """ Возвращает результат нужного типа """
        try:
            res = self.type(self.value.get())
        except ValueError:
            # При типе int и float пустая строка выдает ошибку
            res = self.type(0)
        return res

    @classmethod
    def CreateInput(cls, root, value, width=None, length=None, x=0, y=0, func_event=None, black_list=''):
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

        class_name = f'Field{type(value).__name__.capitalize()}'  # Формируем имя класса из типа переменной
        required_class = globals()[class_name]
        return required_class(root, value, x=x, y=y, func_event=func_event,
                              black_list=black_list, width=width, length=length)

    @classmethod
    def get_all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses += cls.get_all_subclasses(subclass)
        return subclasses


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

    def __init__(self, root, value, x, y, func_event, black_list, width, length):
        super().__init__(root, value, x=x, y=y, func_event=func_event, black_list=black_list,
                         width=width, length=length)

        # Если значения не заданы, определяем по умолчанию
        self.width = width if width else 6
        self.length = length if length else 6

        check = (self.root.register(self.is_valid), "%P")  # Назначаем функцию валидации

        self.value = StringVar(value=self.value)  # Переменная хранящая введенный текст
        self.widget = Entry(self.root, width=self.width, validate="key", validatecommand=check, textvariable=self.value)
        self.widget.place(x=self.x, y=self.y)

        self.widget.bind('<Return>', self.func_event)  # Ловим нажатие Enter

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

    def __init__(self, root, value, x, y, func_event, black_list, width, length):

        # Если значения не заданы, определяем по умолчанию
        width = width if width else 31
        length = length if length else 50

        super().__init__(root, value, x=x, y=y, func_event=func_event, black_list=black_list,
                         width=width, length=length)

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

    def __init__(self, root, value, x, y, func_event, **kwargs):
        super().__init__(root, value, x=x, y=y, func_event=func_event)

        self.value = IntVar(value=self.value)
        self.widget = Checkbutton(self.root, variable=self.value, command=self.func_event)
        self.widget.place(x=self.x, y=self.y)

class FieldLlist(DataInput):
    """ Ввод имени метки в скрипте

    Для хранения метки используется специальный тип данных llist
    он предоставляет список всех меток, а его экземпляры хранят выбранные метки

    Параметры:
    root - родительский виджет
    x, y - координаты на родительском виджете
    func_event - функция, обрабатывающая нажатие Enter

    """

    def __init__(self, root, value, x, y, func_event, **kwargs):
        super().__init__(root, value, x=x, y=y, func_event=func_event)

        values = self.value.labels  # Список для вывода
        self.value = StringVar(value=self.value)
        long = len(max(values, key=len))  # Длина самого длинного элемента, для задания ширины виджета

        self.widget = ttk.Combobox(self.root, values=values, textvariable=self.value, state="readonly")
        self.widget.place(x=self.x, y=self.y)

        self.widget.configure(width=long)
        self.widget.bind("<<ComboboxSelected>>", self.func_event)

    def update(self, value: llist):
        """ Обновляем список, выставляя новое значение """
        self.value.set(value.label)


class FieldEres(DataInput):
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

    def __init__(self, root, value, x, y, func_event, **kwargs):
        super().__init__(root, value, x=x, y=y, func_event=func_event)

        # Выбор реакции
        self.selected_react = StringVar(value=self.value.react)

        long = len(max(self.value.react_list, key=len))
        combobox = ttk.Combobox(self.root, values=self.value.react_list,
                                textvariable=self.selected_react, state="readonly")
        combobox.place(x=self.x, y=self.y)

        combobox.configure(width=long)
        combobox.bind("<<ComboboxSelected>>", self.change_react)
        # Выбор метки
        self.widget = DataInput.CreateInput(self.root, self.value.label, x=self.x+70, y=self.y,
                                            func_event=self.change_label)

        self.set_status_label()  # Активность второго виджета

    def change_react(self, event):
        """ Реакция на изменение первого списка

        При инициализации значение приходит типа eres, это значение будет и на выходе.
        Эта функция меняет значение вошедшей переменной, второй список в ней тоже меняется,
        затем обновляет второй виджет.
        И в соответствии с логикой типа eres активирует или деактивирует второй виджет. """
        self.value.react = self.selected_react.get()
        self.widget.update(self.value)
        self.change_label()
        self.set_status_label()

    def change_label(self, event=None):
        self.value.label = self.widget.result
        if self.func_event:
            self.func_event()

    def set_status_label(self):
        """ Активирует/деактивирует виджет выбора метки (второй) """
        if self.value.react == 'run':
            self.widget.widget['state'] = 'readonly'
        else:
            self.widget.widget['state'] = 'disabled'

    @property
    def result(self):
        """ Возвращает результат нужного типа, переопределение метода родительского класса """
        return self.value


