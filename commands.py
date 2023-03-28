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
from tktooltip import ToolTip
from tkinter import filedialog as fd
import os

from data_input import DataInput
from settings import settings


class CommandClasses(ABC):
    """ Класс, для создания классов команд """
    def __init__(self, root, description):
        """ Принимает ссылку на виджет редактора """
        self.root = root  # Родительский виджет, куда выводятся виджеты ввода
        self.description = description  # Описание

        # Комментарий
        self.widget_description = DataInput.CreateInput(self.root, self.description, x=5, y=37, width=32, length=32)
        ToolTip(self.widget_description.widget, msg="Комментарий", delay=0.5)

    @classmethod
    def create_command(cls, *args, command: str, root=None, description=''):
        """ Метод для создания объектов команд с помощью дочерних классов

        Получает имя команды (класса) чей экземпляр нужно создать, ссылку на родительский
        виджет (куда выводить виджеты ввода) и позиционные аргументы, для акждой команды
        своя последовательность.

        """
        args = args + ('', '', '')  # Заполняем не пришедшие аргументы пустыми строками
        required_class = globals()[command]  # В command название класса, создаем его объект
        return required_class(*args, root=root, description=description)

    @abstractmethod
    def result(self):
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

    def __init__(self, *args, root, description):
        """ Принимает координаты в списке """
        super().__init__(root=root, description=description)
        self.x = args[0]
        self.y = args[1]
        self.widget_x = None
        self.widget_y = None
        if root:
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

    def result(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        pass

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

    def __init__(self, *args, root, description):
        """ Принимает координаты и изображение в списке """
        self.description = args[3]
        super().__init__(*args, root=root, description=description)
        self.image = args[2]
        self.element_image = None
        self.widget_button = None
        if root:
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


