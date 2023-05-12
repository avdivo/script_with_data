# ---------------------------------------------------------------------------
# В этом модуле собраны классы для команд скрипта
# Класс описывает:
#   название команды
#   краткое описание
#   данные для выполнения
#   описание формы для редактирования
#   метод для выполнения
# ---------------------------------------------------------------------------
import shutil
from time import sleep
from abc import ABC, abstractmethod
from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip
from tkinter import filedialog as fd
import os

from data_types import llist, eres
from data_input import DataInput
from settings import settings
from exceptions import DataError, NoCommandOrStop
from element_images import generate_image_name


class CommandClasses(ABC):
    """ Класс, для создания классов команд

    Свойства класса необходимо определить до создания экземпляров команд

    """
    root = None  # Родительский виджет, куда выводятся виджеты ввода
    data = None  # Объект с данными о выполнении скрипта

    def __init__(self, description):
        """ Принимает пользовательское описание команды """
        self.description = description  # Описание

    def paint_description(self):
        # Комментарий
        self.widget_description = DataInput.CreateInput(self.root, self.description, x=10, y=37, width=31, length=50)
        ToolTip(self.widget_description.widget, msg="Комментарий", delay=0.5)

    @classmethod
    def create_command(cls, *args, command: str, description=''):
        """ Метод для создания объектов команд с помощью дочерних классов

        Получает имя команды (класса) чей экземпляр нужно создать, описание команды (пользовательское),
        и позиционные аргументы, для каждой команды своя последовательность.
        Аргументы могут приходить в текстовом виде, каждый класс сам определяет тип своих данных.

        """
        args = args + ('', '', '', '', '')  # Заполняем не пришедшие аргументы пустыми строками
        try:
            required_class = globals()[command]  # В command название класса, создаем его объект
            return required_class(*args, description=description)
        except:
            # Ошибка при создании команды
            raise
    @abstractmethod
    def paint_widgets(self):
        """ Вывод виджетов команды """
        pass

    @abstractmethod
    def save(self):
        """ Записывает содержимое виджетов в объект.

         Метод реализуется в наследниках.

         """
        pass

    @abstractmethod
    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды.

         {'cmd': 'ClassName', 'val': [параметры], 'des': 'Описание'}
         """
        pass

    @abstractmethod
    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        pass

    @abstractmethod
    def run_command(self):
        """ Выполнение команды """
        pass

    @classmethod
    def get_all_subclasses(cls):
        """ Возвращает список всех подклассов класса и их подклассов """
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses += subclass.get_all_subclasses()
        return subclasses


class MouseClickRight(CommandClasses):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик правой кнопкой мыши'
    command_description = 'x, y - координаты на экране.'
    for_sort = 20

    def __init__(self, *args, description):
        """ Принимает координаты в списке и пользовательское описание команды"""
        super().__init__(description=description)
        # Задаем тип данных
        try:
            self.x = int(args[0])
            self.y = int(args[1])
        except:
            self.x = 0
            self.y = 0
        self.widget_x = None
        self.widget_y = None
        self.label_x = None
        self.label_y = None

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return self.command_name

    def paint_widgets(self):
        """ Отрисовка виджета """
        # Виджеты для ввода x, y
        self.label_x = Label(self.root, text='x=')
        self.label_x.place(x=10, y=71)
        self.widget_x = DataInput.CreateInput(self.root, self.x, x=34, y=71)  # Ввод целого числа X
        self.label_y = Label(self.root, text='y=')
        self.label_y.place(x=100, y=71)
        self.widget_y = DataInput.CreateInput(self.root, self.y, x=124, y=71)  # Ввод целого числа Y
        self.paint_description()

    def save(self):
        """ Записывает содержимое виджетов в объект.

         """
        self.x = self.widget_x.result
        self.y = self.widget_y.result
        self.description = self.widget_description.result

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [self.x, self.y], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.label_x.destroy()
        self.label_y.destroy()
        self.widget_x.destroy_widgets()
        self.widget_y.destroy_widgets()
        self.widget_description.destroy_widgets()

    def run_command(self):
        """ Выполнение команды """
        # В свойстве data ссылка на функцию выполняющую события мыши и клавиатуры
        self.data.func_execute_event(**self.command_to_dict())


class MouseClickLeft(MouseClickRight):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик левой кнопкой мыши'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'
    for_sort = 0

    def __init__(self, *args, description):
        """ Принимает координаты, изображение в списке и пользовательское описание команды"""
        self.description = args[3]
        super().__init__(*args, description=description)
        self.image = args[2]
        self.element_image = None
        self.widget_button = None

    def paint_widgets(self):
        """ Отрисовка виджетов """
        # Виджеты для ввода x, y
        self.label_x = Label(self.root, text='x=')
        self.label_x.place(x=10, y=71)
        self.widget_x = DataInput.CreateInput(self.root, self.x, x=34, y=71)  # Ввод целого числа X
        self.label_y = Label(self.root, text='y=')
        self.label_y.place(x=100, y=71)
        self.widget_y = DataInput.CreateInput(self.root, self.y, x=124, y=71)  # Ввод целого числа Y

        # Изображение элемента
        img = os.path.join(settings.path_to_elements, self.image) if self.image else ''
        # Если изображение есть, то загружаем его, если нет, то подставляем заглушку
        if not os.path.exists(img):
            img = 'icon/no_element.png'
        self.element_image = PhotoImage(file=img)
        self.widget_button = Button(self.root, command=self.load_image, image=self.element_image, width=96, height=96)
        self.widget_button.place(x=273, y=5)
        ToolTip(self.widget_button, msg="Изображение элемента", delay=0.5)
        self.paint_description()  # Комментарий

    def load_image(self):
        """ Загрузка изображения элемента """
        # TODO: ограничить выбор одной папкой или копировать изображение в нужную папку
        try:
            new_path_image = fd.askopenfilename(
                filetypes=(("image", "*.png"),
                           ("All files", "*.*")))

            # Если файл с выбранным именем уже существует в папке изображений элементов текущего проекта
            # то копируем его с новым именем в эту папку (имя генерируем функцией generate_image_name из element_image)
            # если нет, то просто копируем и устанавливаем новое имя текущему элементу
            new_image = os.path.basename(new_path_image)
            if os.path.exists(os.path.join(settings.path_to_elements, new_image)):
                self.image = generate_image_name()
                shutil.copy(new_path_image, os.path.join(settings.path_to_elements, self.image))
            else:
                self.image = new_image
                shutil.copy(new_path_image, settings.path_to_elements)

            # Загружаем изображение в виджет
            self.element_image = PhotoImage(file=os.path.join(settings.path_to_elements, self.image))
            self.widget_button.configure(image=self.element_image)
            # Применяем настройки к кнопке
            self.widget_button.update()
        except:
            pass

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [self.x, self.y, self.image], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.label_x.destroy()
        self.label_y.destroy()
        self.widget_x.destroy_widgets()
        self.widget_y.destroy_widgets()
        self.widget_button.destroy()
        self.widget_description.destroy_widgets()


class MouseClickDouble(MouseClickLeft):
    """ Двойной щелчок мышью """
    command_name = 'Двойной щелчок мышью'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'
    for_sort = 10


class KeyDown(CommandClasses):
    """ Нажать клавишу на клавиатуре """
    command_name = 'Нажать клавишу'
    command_description = 'Нажатие клавиши на клавиатуре. Для отпускания клавиши есть отдельная команда.'
    for_sort = 30

    def __init__(self, *args, description):
        """ Принимает название клавиши и пользовательское описание команды"""
        super().__init__(description=description)
        self.widget = None

        self.values = ['backspace', 'tab', 'enter', 'esc', 'space', 'shift', 'shift_r', 'shift_l', 'control', 'cmd',
                        'ctrl', 'ctrl_r', 'ctrl_l', 'alt', 'alt_r', 'alt_gr', 'alt_l', 'pause', 'caps_lock',
                        'scroll_lock', 'print_screen', 'insert', 'delete', 'home', 'end', 'page_up', 'page_down',
                        'left', 'up', 'right', 'down', 'menu',
                        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                        '`', '-', '=', ']', '[', '\\', ';', "'", ',', '.', '/',
                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u', 'v', 'w', 'x', 'y', 'z',
                        'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                        'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э']
        self.value = args[0]
        if self.value in self.values:
            self.value_var = StringVar(value=self.value)
        else:
            self.value = self.values[0]
            self.value_var = StringVar(value=self.value)
    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value}"

    def paint_widgets(self):
        """ Отрисовка виджета """
        self.widget = ttk.Combobox(self.root, values=self.values, textvariable=self.value_var, state="readonly")
        self.widget.place(x=10, y=71)
        long = len(max(self.values, key=len))  # Длина самого длинного элемента, для задания ширины виджета
        self.widget.configure(width=long)
        self.value_var.set(self.value)
        self.paint_description()

    def save(self):
        """ Записывает содержимое виджетов в объект """
        self.value = self.value_var.get()
        self.description = self.widget_description.result

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [self.value], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.widget.destroy()
        self.widget_description.destroy_widgets()

    def run_command(self):
        """ Выполнение команды """
        self.data.func_execute_event(**self.command_to_dict())


class KeyUp(KeyDown):
    """ Отпустить клавишу клавиатуры """
    command_name = 'Отпустить клавишу'
    command_description = 'Отпускание клавиши клавиатуры. Для нажатия клавиши есть отдельная команда.'
    for_sort = 40


class WriteDataFromField(CommandClasses):
    """ Вывести из текущей позиции поля """
    command_name = 'Вывод из поля'
    command_description = 'Столбцы выбранной таблицы с данными - это поля. Данные будут считаны из указанного поля ' \
                          'и вставлены на место курсора. Переход к следующей строке в столбце осуществляется командой ' \
                          'Следующий элемент поля.'
    for_sort = 60

    def __init__(self, *args, description):
        """ Принимает имя поля и пользовательское описание команды"""
        super().__init__(description=description)
        self.widget = None
        try:
            self.values = self.data.get_fields()  # Получаем имена всех полей
        except DataError as err:
            # Ошибка, если полей нет
            self.values = ['Полей нет']

        self.value = args[0] if args[0] else self.values[0]  # Устанавливаем поле которое будет выбрано
        self.value_var = StringVar()

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value}"

    def paint_widgets(self):
        """ Отрисовка виджета """
        self.widget = ttk.Combobox(self.root, values=self.values, textvariable=self.value_var, state="readonly")
        self.widget.place(x=10, y=71)
        long = len(max(self.values, key=len))  # Длина самого длинного элемента, для задания ширины виджета
        self.widget.configure(width=long)
        self.value_var.set(self.value)
        self.paint_description()

    def save(self):
        """ Записывает содержимое виджетов в объект """
        self.value = self.value_var.get()
        self.description = self.widget_description.result

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [self.value], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.widget.destroy()
        self.widget_description.destroy_widgets()

    def run_command(self):
        """ Выполнение команды """
        if self.value not in self.data.data_source:
            raise DataError(f'Нет поля "{self.value}" у источника данных. ')
        # Читаем текущую ячейку указанного поля
        text = self.data.data_source[self.value][self.data.pointers_data_source[self.value]]
        # Запуск функции выводящей текст
        self.data.func_execute_event(cmd=self.__class__.__name__, val=[text])


class NextElementField(WriteDataFromField):
    """ Следующий элемент поля """
    command_name = 'Следующий элемент поля'
    command_description = 'Поле таблицы (столбец) представлено в виде списка данных. Эта команда переводит ' \
                          'указатель чтения к следующему элементу списка'
    for_sort = 70

    def run_command(self):
        """ Выполнение команды

        Находим нужное поле, выясняем его длину, если указатель можно увеличить - делаем, если нельзя
        бросаем исключение связанное с ошибкой данных.

        """
        if self.value not in self.data.data_source:
            raise DataError(f'Нет поля "{self.value}" у источника данных. ')
        pointer = self.data.pointers_data_source[self.value]
        pointer += 1
        if pointer >= len(self.data.data_source[self.value]):
            raise DataError(f'Нет больше данных в поле "{self.value}".')
        self.data.pointers_data_source[self.value] = pointer


class CycleForField(WriteDataFromField):
    """ Цикл по полю """
    command_name = 'Цикл по полю'
    command_description = 'Начало блока команд, которые повторятся столько раз, сколько строк до конца поля. ' \
                          'Окончание блока - команда Конец цикла.'
    for_sort = 80

    def run_command(self):
        """ Выполнение команды

        Цикл выполнится 1 раз в любом случае, входные параметры 0 или 1 не отличаются.
        Команда просто записывает в стек список: свой индекс и количество итераций.
        Итерации вычисляются по количеству ячеек до конца заданного поля

        """
        if self.value not in self.data.data_source:
            raise DataError(f'Нет поля "{self.value}" у источника данных. ')
        pointer = self.data.pointers_data_source[self.value]  # Где указатель
        temp = len(self.data.data_source[self.value]) - pointer  # Сколько ячеек до конца
        self.data.stack.append([self.data.pointer_command, temp])


class PauseCmd(CommandClasses):
    """ Пауза n секунд """
    command_name = 'Пауза (секунд)'
    command_description = 'В любом месте скрипта можно сделать паузу, указав количество секунд.'
    for_sort = 170

    def __init__(self, *args, description, value=None ):
        """ Принимает количество секунд, пользовательское описание команды и значение от классов-потомков """
        # Если инициализируется объект класса-потомка, то получаем от него данные нужного типа
        # Поскольку классы формирующие виджет по типу определяют какой виджет рисовать
        self.value = float(args[0] if args[0] else 0) if value is None else value

        super().__init__(description=description)
        self.widget = None

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value} сек."

    def paint_widgets(self):
        """ Отрисовка виджета """
        self.widget = DataInput.CreateInput(self.root, self.value, x=10, y=71)  # Виджеты для разных типов данных
        self.paint_description()

    def save(self):
        """ Записывает содержимое виджетов в объект """
        self.value = self.widget.result
        self.description = self.widget_description.result

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [self.value], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.widget.destroy_widgets()
        self.widget_description.destroy_widgets()

    def run_command(self):
        """ Выполнение команды """
        sleep(self.value)


class WriteCmd(PauseCmd):
    """ Вывести текст """
    command_name = 'Вывести текст'
    command_description = 'Эта команда напечатает указанный текст в месте, где установлен курсор. ' \
                          'Длина текста не должна превышать 500 символов.'
    for_sort = 50

    def __init__(self, *args, description):
        """ Принимает текст и пользовательское описание команды """
        value = str(args[0])
        super().__init__(*args, description=description, value=value)

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value}"

    def run_command(self):
        """ Выполнение команды """
        self.data.func_execute_event(**self.command_to_dict())

class RunCmd(PauseCmd):
    """ Переход и выполнение скрипта с указанной метки или блока """
    command_name = 'Выполнить'
    command_description = 'Выполняет блок или совершает переход к метке с указанным именем.'
    for_sort = 140

    def __init__(self, *args, description):
        """ Принимает значение типа llist и пользовательское описание команды """
        self.value = llist(args[0])
        super().__init__(*args, description=description, value=self.value)

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value}"

    def run_command(self):
        """ Выполнение команды

        Указатель ставим на метку, если это блок - добавляем данные в стек

        """
        pointer = self.data.work_labels[self.value.label]
        if self.data.obj_command[self.data.queue_command[pointer]].__class__.__name__ == 'BlockCmd':
            # Если переход к блоку добавляем место возврата в стек
            self.data.stack.append([self.data.pointer_command])
        self.data.pointer_command = pointer  # Ставим указатель на блок или метку


class ErrorNoElement(PauseCmd):
    """ Реакция на ошибку 'Нет элемента' """
    command_name = 'Реакция на ошибку "Нет элемента"'
    command_description = 'Меняет текущую реакцию скрипта на возникновение ошибки: ' \
                          'остановить скрипт/игнорировать/выполнить блок или перейти к метке с указанным именем.'
    for_sort = 150

    def __init__(self, *args, description):
        """ Принимает значение типа eres и пользовательское описание команды """
        self.value = eres(args[0])
        super().__init__(*args, description=description, value=self.value)

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name}"

    def run_command(self):
        """ Выполнение команды """
        self.data.work_settings['s_error_no_element'] = self.value


class ErrorNoData(ErrorNoElement):
    """ Реакция на ошибку 'Нет данных' """
    command_name = 'Реакция на ошибку "Нет данных"'
    command_description = 'Меняет текущую реакцию скрипта на возникновение ошибки: ' \
                          'остановить скрипт/игнорировать/выполнить блок или перейти к метке с указанным именем.'
    for_sort = 160

    def run_command(self):
        """ Выполнение команды """
        self.data.work_settings['s_error_no_data'] = self.value


class BlockCmd(WriteCmd):
    """ Начало блока команд """
    command_name = 'Блок команд'
    command_description = 'Поименованный блок команд который не выполняется в обычном порядке. ' \
                          'Он вызывается командой Выполнить или Ошибка. Завершается командой Конец блока. ' \
                          'После чего скрипт выполняется от команды вызвавшей блок.'
    for_sort = 110

    def run_command(self):
        """ Выполнение команды

        Блок нужно обойти. Находим конец блока и делаем его текущей командой.
        Если команды конца блока нет выполняем его как обычную последовательность.
        При этом, если встретится вложенный блок, его конец будет воспринят как конец этого,
        поэтому вложенность блоков не допускается.

        """
        i = self.data.pointer_command
        for name in [self.data.obj_command[label].__class__.__name__
                     for label in self.data.queue_command[self.data.pointer_command+1:]]:
            # Перебираем список команд от текущей позиции до конца и ищем конец блока
            if name == 'BlockEnd':
                self.data.pointer_command = i
                return
            elif name == 'BlockCmd':
                raise NoCommandOrStop('Скрипт остановлен. Вложенность блоков не допускается.')
            i += 1
            # Если команда конца блока не найдена выполняем его как обычную последовательность (пропускаем)


class LabelCmd(WriteCmd):
    """ Метка для перехода """
    command_name = 'Метка'
    command_description = 'Метка в скрипте, куда может быть совершен переход командами Выполнить или Ошибка.'
    for_sort = 130

    def run_command(self):
        """ Выполнение команды """
        pass


class CycleCmd(PauseCmd):
    """ Цикл заданное число раз"""
    command_name = 'Цикл'
    command_description = 'Начало блока команд, которые повторятся указанное количество раз. ' \
                          'Окончание блока - команда Конец цикла.'
    for_sort = 90

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name} {self.value} раз"

    def run_command(self):
        """ Выполнение команды

        Цикл выполнится 1 раз в любом случае, входные параметры 0 или 1 не отличаются.
        Команда просто записывает в стек список: свой индекс и количество итераций.

        """
        self.data.stack.append([self.data.pointer_command, self.value])


class CycleEnd(CommandClasses):
    """ Конец цикла """
    command_name = 'Конец цикла'
    command_description = 'Конец блока команд повторяющихся столько раз, сколько указано в начале блока, ' \
                          'начатого командой Цикл.'
    for_sort = 100

    def __init__(self, *args, description):
        """ Принимает пользовательское описание команды"""
        super().__init__(description=description)

    def __str__(self):
        """ Возвращает название команды, иногда с параметрами.
        Но если есть пользовательское описание - то его """
        if self.description:
            return self.description
        return f"{self.command_name}"

    def paint_widgets(self):
        """ Вывод виджетов команды """
        self.paint_description()

    def save(self):
        """ Записывает содержимое виджетов в объект """
        self.description = self.widget_description.result
    
    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.widget_description.destroy_widgets()

    def run_command(self):
        """ Выполнение команды

        Выбирает из стека верхний элемент, уменьшает 2 значение на 1 и если еще > 0 записывает результат назад и
        переходит к команде по индексу из 1 значения.
        Любые ошибки при выполнении игнорирует.

        """
        try:
            temp = self.data.stack.pop()
            temp[1] -= 1
            if temp[1] > 0:
                self.data.stack.append(temp)
                # После выполнения этой команды указатель увеличится на 1
                # и перейдет на команду следующую за началом цикла
                self.data.pointer_command = temp[0]  # Индекс команды начала цикла
        except:
            raise


class BlockEnd(CycleEnd):
    """ Конец блока """
    command_name = 'Конец блока'
    command_description = 'Завершение списка команд относящихся к последнему (перед этой командой) объявленному блоку. ' \
                          'Начало блока - команда Блок.'
    for_sort = 120

    def run_command(self):
        """ Выполнение команды

        Выбирает из стека верхний элемент. Переходит к команде по индексу из 0 значения.
        Любые ошибки при выполнении игнорирует.

        """
        try:
            temp = self.data.stack.pop()
            self.data.pointer_command = temp[0]  # Индекс команды от которой был переход к блоку
        except:
            pass


class StopCmd(CycleEnd):
    """ Конец скрипта """
    command_name = 'Конец скрипта'
    command_description = 'Остановить выполнение скрипта.'
    for_sort = 180

    def run_command(self):
        """ Выполнение команды """
        raise NoCommandOrStop(f'Выполнена команда Стоп.')


class DialogCmd(WriteCmd):
    """ Остановка скрипта и вывод диалогового окна пользователю для выбора дальнейших действий """
    command_name = 'Диалоговое окно'
    command_description = 'Остановить выполнение скрипта. Сообщить пользователю по какой причине остановлен скрипт.' \
                          ' Длина сообщения не должна превышать 500 символов.'
    for_sort = 145

    def run_command(self):
        """ Выполнение команды """
        self.data.stop_for_dialog(self.value)
        if self.data.modal_stop:
            raise NoCommandOrStop('Пользователь остановил выполнение скрипта.')
