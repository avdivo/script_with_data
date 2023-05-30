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
import logging
import pyautogui

from data_types import llist, eres
from data_input import DataInput
from settings import settings
from exceptions import DataError, NoCommandOrStop, TemplateNotFoundError, ElementNotFound
from element_images import generate_image_name, pattern_search
from define_platform import system


# создание логгера и обработчика
logger = logging.getLogger('logger')


class CommandClasses(ABC):
    """ Класс, для создания классов команд

    Свойства класса необходимо определить до создания экземпляров команд

    """
    root = None  # Родительский виджет, куда выводятся виджеты ввода
    data = None  # Объект с данными о выполнении скрипта
    tracker = None  # Объект для записи скрипта

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
        args = args + tuple(['']*15)  # Заполняем не пришедшие аргументы пустыми строками
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

# Перед кликом мыши в указанных координатах или по команде проверки изображения
# программа может выполнить поиск заданного изображения на экране, чтобы убедиться в правильности работы.
# Обычно сначала производится локальная проверка, изображение ищется в квадрате с заданными сторонами
# и центром, в указанных координатах.
# Если изображение сразу не найдено, программа может ждать его появления заданное время.
# В случае неудачного локального поиска может быть выполнен поиск по всему экрану.
# Если изображение так и не будет найдено, программа выполнит указанное действие
# или не сделает ничего в зависимости от условия выполнения действия.

# Использовать локальные настройки (открываются настройки)
# Включить локальную проверку
# Зона локальной проверки (сторона квадрата)
# Сколько секунд ждать, после 1 попытки
# Использовать поиск на всем экране
# Условие выполнения действия: найден/не найден
# Действие: ...


class MouseClickRight(CommandClasses):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик правой кнопкой мыши'
    command_description = 'x, y - координаты на экране.'
    for_sort = 20

    def __init__(self, *args, description):
        """ Принимает параметры в списке и пользовательское описание команды

        Паваметры:
        0 - координата x, 1 - координата y, 2 - имя изображения, 3 - использовать локальные настройки (True/False),
        4 - включить локальную проверку (True/False), 5 - зона локальной проверки (сторона квадрата, int >= 48),
        6 - сколько секунд ждать, после 1 попытки (int, 0 не проверять), 7 - искать на всем экране (True/False),
        8 - условие выполнения действия: ('Найдено'/'Не найдено'), 9 - Действие (eres),
        10 - сообщение, в случае выполнения действия (str).

        """
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

        # Для изображения
        self.image = args[2]
        self.element_image = None
        self.icon_edit = None
        self.icon_del = None
        self.widget_button = None
        self.widget_button_edit = None
        self.widget_button_del = None

        # Дополнительные параметры
        self.widget_button_more = None  # Виджет кнопки "еще"
        self.local_settings = bool(args[3])  # Использовать локальные настройки
        self.local_check = True if args[4] == '' else args[4]  # Включить локальную проверку
        self.local_check_size = 96 if not args[5] else args[5]  # Зона локальной проверки (сторона квадрата)
        # Сколько секунд ждать, после 1 попытки. По умолчанию берется из основных настроек
        self.repeat = args[6] if isinstance(args[6], int) else settings.s_search_attempt
        # По умолчанию поиск на всем экране включен для мыши и выключен для проверки изображения
        if self.__class__.__name__ != 'CheckImage':
            self.full_screen = True if args[7] == '' else args[7]
        else:
            self.full_screen = args[7]
        self.condition = 'Не найдено' if args[8] == '' else args[8]  # Условие выполнения действия: найден/не найден
        # Действие при отсутствии изображения типа eres
        try:
            self.action = eres(str(args[9])) if args[9] else eres(str(settings.s_error_no_element))
        except ValueError as err:
            # Метка не найдена или другая ошибка типа данных Llist
            logger.error(f'{err}\nПереход заменен на Stop.')
            self.action = 'stop:'
        self.message = args[5]  # Сообщение при отсутствии изображения

        # Виджеты для дополнительных настроек
        self.widget_local_settings = None  # Виджет для использования локальных настроек
        self.widget_local_check = None  # Виджет для включения локальной проверки
        self.widget_local_check_size = None  # Виджет для ввода размера зоны локальной проверки
        self.widget_repeat = None  # Виджет для ввода количества повторений
        self.widget_full_screen = None  # Виджет для включения поиска на всем экране
        self.widget_condition = None  # Виджет для выбора условия выполнения действия
        self.widget_action = None  # Виджет для выбора действия
        self.widget_message = None  # Виджет для ввода сообщения
        self.window = None  # Окно с дополнительными настройками
        self.widget_frame = None  # Фрейм для виджетов дополнительных настроек

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
        self.widget_y = DataInput.CreateInput(self.root, self.y, x=124, y=71)  # Ввод целого числа

        # Изображение элемента
        img = os.path.join(settings.path_to_elements, self.image) if self.image else ''
        # Если изображение есть, то загружаем его, если нет, то подставляем заглушку
        if not os.path.exists(img):
            img = 'icon/no_element.png'
        self.element_image = PhotoImage(file=img)
        self.icon_edit = PhotoImage(file="icon/record.png")
        self.icon_del = PhotoImage(file="icon/delete.png")

        self.widget_button = Button(self.root, command=self.load_image, image=self.element_image, width=96, height=96)
        self.widget_button.place(x=273, y=5)
        ToolTip(self.widget_button, msg="Изображение элемента", delay=0.5)

        self.widget_button_edit = Button(self.root, command=self.edit_image, image=self.icon_edit, width=34, height=34)
        self.widget_button_edit.place(x=273, y=106)
        ToolTip(self.widget_button_edit, msg="Скриншот", delay=0.5)

        self.widget_button_del = Button(self.root, command=self.delete_image, image=self.icon_del, width=34, height=34)
        self.widget_button_del.place(x=334, y=106)
        ToolTip(self.widget_button_del, msg="Удалить изображение", delay=0.5)

        """ Отрисовка виджетов для редактирования команды
        Добавляется мелкая кнопка "еще" правее от координаты y,
        при нажатии на которую открывается окно с дополнительными настройками
        """
        def save_settings():
            """ Сохранение дополнительных настроек """
            self.local_settings = self.widget_local_settings.result
            self.local_check = self.widget_local_check.result
            self.local_check_size = self.widget_local_check_size.result
            self.repeat = self.widget_repeat.result
            self.full_screen = self.widget_full_screen.result
            self.condition = self.widget_condition.get()
            self.action = self.widget_action.result
            self.message = self.widget_message.result
            self.window.destroy()

        def show_frame():
            """ Показать фрейм с виджетами дополнительных настроек """
            if self.widget_local_settings.result:
                self.widget_frame.place(x=20, y=50)
            else:
                self.widget_frame.place_forget()

        def additional_settings_modal():
            """ Вызов окна с дополнительными настройками """
            # Создаем окно
            self.window = Toplevel()
            self.window.title('Дополнительные настройки')
            # Разместить окно в центре экрана
            w = 700  # Ширина окна
            h = 320  # Высота окна
            x = (self.window.winfo_screenwidth() - w) / 2
            y = (self.window.winfo_screenheight() - h) / 2
            self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
            self.window.transient(self.root)  # Поверх окна
            self.window.update_idletasks()
            self.window.resizable(False, False)

            # Создаем виджеты
            # Чекбокс для включения локальных настроек и фрейм для их виджетов
            # При переключении чекбокса фрейм показывается/скрывается
            self.widget_local_settings = DataInput.CreateInput(
                self.window, self.local_settings, func_event=show_frame, x=20, y=20)
            Label(self.window, text='Использовать локальные настройки').place(x=50, y=20)
            self.widget_frame = Frame(self.window, width=w-40, height=h-120)
            self.widget_frame.place(x=20, y=50)
            show_frame()

            Label(self.widget_frame, text='Включить локальную проверку').place(x=20, y=20)
            self.widget_local_check = DataInput.CreateInput(self.widget_frame, self.local_check, x=400, y=20)

            Label(self.widget_frame, text='Зона локальной проверки (сторона квадрата)').place(x=20, y=50)
            self.widget_local_check_size = DataInput.CreateInput(self.widget_frame, self.local_check_size, x=400, y=50)

            Label(self.widget_frame, text='Сколько секунд ждать, после 1 попытки').place(x=20, y=80)
            self.widget_repeat = DataInput.CreateInput(self.widget_frame, self.repeat, x=400, y=80)

            Label(self.widget_frame, text='Искать на всем экране').place(x=20, y=110)
            self.widget_full_screen = DataInput.CreateInput(self.widget_frame, self.full_screen, x=400, y=110)

            # Выпадающий список tkinter с вариантами условий 'Найдено' и 'Не найдено'
            Label(self.widget_frame, text='Выполнить действие если изображение').place(x=20, y=140)
            self.widget_condition = ttk.Combobox(
                self.widget_frame, values=['Найдено', 'Не найдено'], width=11, state='readonly')
            self.widget_condition.set(self.condition)
            self.widget_condition.place(x=400, y=140)

            Label(self.widget_frame, text='Какое действие выполнить').place(x=20, y=170)
            self.widget_action = DataInput.CreateInput(self.widget_frame, self.action, x=400, y=170)

            Label(self.widget_frame, text='Сообщение при выполнении действия').place(x=20, y=200)
            self.widget_message = DataInput.CreateInput(self.widget_frame, self.message, x=400, y=200)

            Button(self.window, text='Сохранить', command=save_settings).place(x=w-120, y=h-55)

            # Запускаем окно
            self.window.grab_set()
            self.window.focus_set()
            self.window.wait_window()

        self.widget_button_more = Button(self.root, text='ЕЩЕ', command=additional_settings_modal, pady=1)
        self.widget_button_more.place(x=205, y=71)

        self.paint_description()  # Комментарий

    # Методы для работы с изображением элемента
    def load_image(self):
        """ Загрузка изображения элемента """
        if self.data.script_started or self.data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        try:
            new_path_image = fd.askopenfilename(initialdir=settings.path_to_elements,
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
            self.widget_button.update()  # Применяем настройки к кнопке
        except:
            pass

    def edit_image(self):
        """ Редактирование изображения элемента """
        if self.data.script_started or self.data.is_listening:
            return

        try:
            logger.warning('Ctrl, Ctrl (правый) - новые координаты и скриншот.\n'
                           'Ctrl (правый), Ctrl, Ctrl, Ctrl - только координаты.\n'
                           'Ctrl, Ctrl - отмена.\n'
                           'После первого Ctrl координаты зафиксируются и курсор можно убрать.')
            self.root.update()  # Обновляем окно
            self.tracker.only_screenshot = 'wait'
            self.tracker.rec_btn()  # Запускаем запись скрипта, но при only_screenshot = 'waite'

            pos_not = True
            while self.tracker.only_screenshot == 'wait':
                sleep(0.1)  # Ждем пока не будет получен скриншот
                if self.tracker.mouse_position and pos_not:
                    # В процессе ожидания стали доступны координаты (после 1 нажатия кнопки)
                    # Обновляем координаты в виджетах
                    self.widget_x.value.set(self.tracker.mouse_position[0])
                    self.widget_y.value.set(self.tracker.mouse_position[1])
                    self.root.update()
                    pos_not = False  # Координаты уже получены

            if self.tracker.only_screenshot:
                # Если скриншот получен, то меняем им изображение элемента
                self.image = self.tracker.only_screenshot
                img = os.path.join(settings.path_to_elements, self.image)
                self.element_image = PhotoImage(file=img)
                self.widget_button.configure(image=self.element_image)
                self.widget_button.update()  # Применяем настройки к кнопке
                logger.error('Скриншот получен.')
        except:
            pass

    def delete_image(self):
        """ Удаление изображения элемента """
        if self.data.script_started or self.data.is_listening:
            return

        self.image = ''
        img = 'icon/no_element.png'
        self.element_image = PhotoImage(file=img)
        self.widget_button.configure(image=self.element_image)
        self.widget_button.update()  # Применяем настройки к кнопке

    def save(self):
        """ Записывает содержимое виджетов в объект.

         """
        self.x = self.widget_x.result
        self.y = self.widget_y.result
        self.description = self.widget_description.result

    def command_to_dict(self):
        """ Возвращает словарь с содержимым команды """
        return {'cmd': self.__class__.__name__, 'val': [
            self.x, self.y, self.image, self.repeat, self.action, self.message], 'des': self.description}

    def destroy_widgets(self):
        """ Удаление виджетов созданных командой в редакторе. И виджета описания, созданного родителем """
        self.label_x.destroy()
        self.label_y.destroy()
        self.widget_x.destroy_widgets()
        self.widget_y.destroy_widgets()
        self.widget_description.destroy_widgets()

        self.widget_button.destroy()
        self.widget_button_edit.destroy()
        self.widget_button_del.destroy()

        self.widget_button_more.destroy()

    def run_command(self):
        """ Выполнение команды """
        try:
            self.x, self.y = pattern_search(self.image, self.x, self.y)
        except (TemplateNotFoundError, ElementNotFound) as err:
            if self.action.react == 'stop':
                raise NoCommandOrStop(f'Проверка изображения - нет изображения.\nОстановка выполнения скрипта.\n'
                                      f'"{self.message}"')
            elif self.action.react == 'ignore':
                logger.error(f'Проверка изображения - нет изображения.\n"{self.message}"'
                             f'\nВыполнения скрипта продолжено.')
            elif self.action.react == 'dialog':
                # Остановка выполнения скрипта и вывод модального окна
                self.data.stop_for_dialog(f'Проверка изображения - нет изображения.\n"{self.message}"')
                if self.data.modal_stop:
                    raise NoCommandOrStop('Пользователь остановил выполнение скрипта.')
            else:
                # Продолжение выполнения скрипта, но с другого места
                label = self.action.label
                self.data.pointer_command = self.data.work_labels[label.label]
                logger.warning(f'Проверка изображения - нет изображения.\n"{self.message}"\n'
                               f'Переход к метке "{label.label}"')

        # Выполнение команды если класс не CheckImage
        if self.__class__.__name__ != 'CheckImage':
            # В свойстве data ссылка на функцию выполняющую события мыши и клавиатуры
            self.data.func_execute_event(**self.command_to_dict())


class MouseClickLeft(MouseClickRight):
    """ Клик левой кнопкой мыши """
    command_name = 'Клик левой кнопкой мыши'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'
    for_sort = 0


class MouseClickDouble(MouseClickLeft):
    """ Двойной щелчок мышью """
    command_name = 'Двойной щелчок мышью'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'
    for_sort = 10


class CheckImage(MouseClickLeft):
    """ Проверка изображения в указанных координатах

    Делает скриншот изображения в указанных координатах, если там то изображение, которое указано в команде,
    то продолжается выполнение скрипта иначе выполняются действия в соответствии с настройками скрипта при отсутствии
    элемента.
    """
    command_name = 'Проверка изображения'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'
    for_sort = 25


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


class CopyCmd(CycleEnd):
    """ Копировать """
    command_name = 'Копировать Ctrl+C'
    command_description = 'Копирует в буфер обмена (аналог Ctrl+C).'
    for_sort = 190

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 'c')


class CutCmd(CycleEnd):
    """ Вырезать """
    command_name = 'Вырезать Ctrl+X'
    command_description = 'Вырезает в буфер обмена (аналог Ctrl+X).'
    for_sort = 200

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 'x')

class PasteCmd(CycleEnd):
    """ Вставить """
    command_name = 'Вставить Ctrl+V'
    command_description = 'Вставляет из буфера обмена (аналог Ctrl+V).'
    for_sort = 210

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 'v')


class SelectCmd(CycleEnd):
    """ Выделить все """
    command_name = 'Выделить все Ctrl+A'
    command_description = 'Выделяет все (аналог Ctrl+A).'
    for_sort = 220

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 'a')


class LanguageChangeCmd(CycleEnd):
    """ Сменить язык """
    command_name = 'Сменить язык Alt+Shift'
    command_description = 'Сменить язык раскладки клавиатуры (аналог Alt+Shift).'
    for_sort = 230

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('alt', 'shift')


class NewTabCmd(CycleEnd):
    """ Новая вкладка """
    command_name = 'Новая вкладка Ctrl+T'
    command_description = 'Открывает новую вкладку (аналог Ctrl+T).'
    for_sort = 240

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 't')


class NextTabCmd(CycleEnd):
    """ Следующая вкладка """
    command_name = 'Следующая вкладка Ctrl+Tab'
    command_description = 'Переходит на следующую вкладку (аналог Ctrl+Tab).'
    for_sort = 250

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('ctrl', 'tab')


class NextWindowCmd(CycleEnd):
    """ Следующее окно """
    command_name = 'Следующее окно Alt+Tab'
    command_description = 'Переходит на следующее окно (аналог Alt+Tab).'
    for_sort = 260

    def run_command(self):
        """ Выполнение команды """
        pyautogui.hotkey('alt', 'tab')


class RollUpWindowsCmd(CycleEnd):
    """ Свернуть все окна """
    command_name = 'Свернуть все окна Win+D'
    command_description = 'Свернуть все окна (аналог Cmd+D для Windows и Ctrl+Alt+D для Linux).'
    for_sort = 270

    def run_command(self):
        """ Выполнение команды """
        if system.os == 'Windows':
            pyautogui.hotkey('win', 'd')
        elif system.os == 'Linux':
            pyautogui.hotkey('ctrl', 'alt', 'd')
