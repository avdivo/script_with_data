# ---------------------------------------------------------------------------
# В этом модуле собраны классы для команд скрипта
# Класс описывает:
#   название команды
#   краткое описание
#   данные для выполнения
#   описание формы для редактирования
#   метод для выполнения
# ---------------------------------------------------------------------------

from abc import ABC, abstractmethod
from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip
from tkinter import filedialog as fd
import os

from data_input import DataInput
from settings import settings
from exceptions import DataError


class CommandClasses(ABC):
    """ Класс, для создания классов команд

    Свойства класса необходимо определить до создания экземпляров команд

    """
    root = None  # Родительский виджет, куда выводятся виджеты ввода
    data = None  # Объект с данными о выполнении скрипта

    def __init__(self, description):
        """ Принимает ссылку на виджет редактора """
        self.description = description  # Описание

        # Комментарий
        self.widget_description = DataInput.CreateInput(self.root, self.description, x=10, y=37, width=31, length=50)
        ToolTip(self.widget_description.widget, msg="Комментарий", delay=0.5)

    @classmethod
    def create_command(cls, *args, command: str, description=''):
        """ Метод для создания объектов команд с помощью дочерних классов

        Получает имя команды (класса) чей экземпляр нужно создать, описание команды (пользовательское),
        и позиционные аргументы, для каждой команды своя последовательность.

        """
        args = args + ('', '', '' '', '')  # Заполняем не пришедшие аргументы пустыми строками
        required_class = globals()[command]  # В command название класса, создаем его объект
        return required_class(*args, description=description)

    @abstractmethod
    def save(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        pass

    @abstractmethod
    def commant_to_dict(self):
        """ Возвращает словарь с содержимым команды.

         {'ClassName': [параметры]}
         """
        pass


class MouseClickRight(CommandClasses):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик правой кнопкой мыши'
    command_description = 'x, y - координаты на экране.'

    def __init__(self, *args, description):
        """ Принимает координаты в списке """
        super().__init__(description=description)
        self.x = args[0]
        self.y = args[1]
        self.widget_x = None
        self.widget_y = None
        if self.root:
            # Виджет не нужно выводить, если приложение выполняется в консольном режиме
            self.paint_widgets()

    def __str__(self):
        return self.command_name

    def paint_widgets(self):
        """ Отрисовка виджета """
        # Виджеты для ввода x, y
        Label(self.root, text='x=').place(x=10, y=71)
        self.widget_x = DataInput.CreateInput(self.root, self.x, x=34, y=71)  # Ввод целого числа X
        Label(self.root, text='y=').place(x=100, y=71)
        self.widget_y = DataInput.CreateInput(self.root, self.y, x=124, y=71)  # Ввод целого числа Y

    def save(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        self.x = self.widget_x.result
        self.y = self.widget_y.result
        self.description = self.widget_description.result

    def commant_to_dict(self):
        """ Возвращает словарь с содержимым команды.

         {'ClassName': [параметры]}
         """
        pass


class MouseClickLeft(MouseClickRight):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик левой кнопкой мыши'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'

    def __init__(self, *args, description):
        """ Принимает координаты и изображение в списке """
        self.description = args[3]
        super().__init__(*args, description=description)
        self.image = args[2]
        self.element_image = None
        self.widget_button = None
        if self.root:
            # Виджет не нужно выводить, если приложение выполняется в консольном режиме
            self.paint_widgets_1()

    def __str__(self):
        return self.command_name

    def paint_widgets_1(self):
        """ Отрисовка виджета """
        # Изображение элемента
        self.element_image = PhotoImage(file=self.image)
        self.widget_button = Button(self.root, command=self.load_image, image=self.element_image, width=96, height=96, relief=FLAT)
        self.widget_button.place(x=273, y=5)
        ToolTip(self.widget_button, msg="Изображение элемента", delay=0.5)

    def load_image(self):
        """ Загрузка изображения элемента """
        # TODO: ограничить выбор одной папкой или копировать изображение в нужную папку
        try:
            self.image = fd.askopenfilename(
                filetypes=(("image", "*.png"),
                           ("All files", "*.*")))
            if self.image:
                # Удалить путь и ищем файл только в определенном пути,
                # если он не там - то не открываем
                self.image = settings.path_to_elements + os.path.basename(self.image)
                print(self.image)
                self.element_image = PhotoImage(file=self.image)
                self.widget_button.configure(image=self.element_image)
        except:
            pass


class MouseClickDouble(MouseClickLeft):
    """ Двойной щелчок мышью """
    command_name = 'Двойной щелчок мышью'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'


class KeyDown(CommandClasses):
    """ Нажать клавишу на клавиатуре """
    command_name = 'Нажать клавишу на клавиатуре'
    command_description = 'Нажатие клавиши на клавиатуре. Для отпускания клавиши есть отдельная команда.'

    def __init__(self, *args, description):
        """ Принимает название клавиши """
        super().__init__(description=description)
        self.widget = None
        self.values = ['backspace', 'tab', 'enter', 'shift', 'ctrl', 'alt', 'pause', 'caps_lock', 'esc', 'space',
                       'page_up', 'page_down', 'end', 'home', 'left', 'up', 'right', 'down', 'insert', 'delete',
                       'key_0', 'key_1', 'key_2', 'key_3', 'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9',
                       'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                       's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'numpad_0', 'numpad_1', 'numpad_2', 'numpad_3',
                       'numpad_4', 'numpad_5', 'numpad_6', 'numpad_7', 'numpad_8', 'numpad_9', 'multiply', 'add',
                       'subtract', 'decimal', 'divide', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
                       'f11', 'f12', 'num_lock', 'scroll_lock', 'left_shift', 'right_shift', 'left_ctrl', 'right_ctrl',
                       'left_alt', 'right_alt', 'menu', 'print_screen', 'left_bracket', 'right_bracket', 'semicolon',
                       'comma', 'period', 'quote', 'forward_slash', 'back_slash', 'equal', 'hyphen', 'space']
        self.current_value = args[0]
        self.value = self.value = StringVar(value=self.current_value)
        print(self.values)
        self.paint_widgets()

    def __str__(self):
        return self.command_name

    def paint_widgets(self):
        """ Отрисовка виджета """
        self.widget = ttk.Combobox(self.root, values=self.values, textvariable=self.value, state="readonly")
        self.widget.place(x=10, y=71)
        long = len(max(self.values, key=len))  # Длина самого длинного элемента, для задания ширины виджета
        self.widget.configure(width=long)
        self.value.set(self.current_value)

    def save(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        pass

    def commant_to_dict(self):
        """ Возвращает словарь с содержимым команды.

         {'ClassName': [параметры]}
         """
        pass


class KeyUp(KeyDown):
    """ Отпустить клавишу клавиатуры """
    command_name = 'Отпустить клавишу клавиатуры'
    command_description = 'Отпускание клавиши клавиатуры. Для нажатия клавиши есть отдельная команда.'


class GteDataFromField(CommandClasses):
    """ Получить данные из текущей позиции поля """
    command_name = 'Получить данные из поля'
    command_description = 'Столбцы выбранной таблицы с данными - это поля. Данные будут считаны из указанного поля ' \
                          'и вставлены на место курсора. Переход к следующей строке в столбце осуществляется командой ' \
                          'Следующий элемент поля.'

    def __init__(self, *args, description):
        """ Принимает имя поля """
        super().__init__(description=description)
        self.widget = None
        self.current_value = args[0]
        self.values = self.data.get_fields()  # Получаем имена всех полей
        if self.current_value not in self.values:
            raise DataError(f'Нет поля "{self.current_value}" в источнике данных')
        self.value = self.value = StringVar(value=self.current_value)
        self.paint_widgets()

    def __str__(self):
        return self.command_name

    def paint_widgets(self):
        """ Отрисовка виджета """
        self.widget = ttk.Combobox(self.root, values=self.values, textvariable=self.value, state="readonly")
        self.widget.place(x=10, y=71)
        long = len(max(self.values, key=len))  # Длина самого длинного элемента, для задания ширины виджета
        self.widget.configure(width=long)
        self.value.set(self.current_value)

    def save(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        pass

    def commant_to_dict(self):
        """ Возвращает словарь с содержимым команды.

         {'ClassName': [параметры]}
         """
        pass


class NextElementField(GteDataFromField):
    """ Следующий элемент поля """
    command_name = 'Следующий элемент поля '
    command_description = 'Поле таблицы (столбец) представлено в виде списка данных. Эта команда переводит ' \
                          'указатель чтения к следующему элементу списка'


class CycleForField(GteDataFromField):
    """ Цикл по полю"""
    command_name = 'Цикл по полю'
    command_description = 'Начало блока команд, которые повторятся столько раз, сколько строк до конца поля. ' \
                          'Окончание блока - команда Конец цикла.'




def spiral(x, y, n):
    """ Это функция генератор, ее надо инициализировать и далее с помощью оператора next получать координаты
     a = spiral(3, 3, 3)
     x, y = next(a)


     x, y координаты центра, n - количество слоев """
    x = [x]
    y = [y]
    end = y[0] + n + 1
    xy = [y, x, y, x]  # у - по вертикали, x - по горизонтали
    where = [1, 1, -1, -1]  # Движение: вниз, вправо, вверх, налево
    stop = [xy[i][0]+where[i] for i in range(4)]
    i = 0
    while y[0] < end:
        while True:
            yield (x[0], y[0])
            xy[i][0] = xy[i][0] + where[i]
            if xy[i][0] == stop[i]:
                stop[i] = stop[i] + where[i]
                break
        i = (i + 1) % 4




storona = 7  # Сторона квадрата
matrix = [[0 for i in range(storona)] for j in range(storona)]  # Создаем марицу

# Печать матрицы
for i in matrix:
    print(*i)
print()

# Инициализируем генератор
# Первые 2 аргумента - это координаты, вокруг которых вычисляются круги
# 3 аргумент количество кругов
# Координаты могут быть любыми, генератор будет возвращать правильные значения
a = spiral(storona//2, storona//2, storona//2)

# Это просто тестовый цикл
for i in a:
    matrix[i[1]][i[0]] = 8
    for i in matrix:
        print(*i)
    print()

# Но можно и так получать значения:
a = spiral(3, 3, 1)
print(next(a))
print(next(a))
print(next(a))
print(next(a))
print(next(a))
print(next(a))
print(next(a))
print(next(a))