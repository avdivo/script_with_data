# ---------------------------------------------------------------------------
# Составные части программы в классах.
# Импортируются в основную часть программы, предоставляя интерфейс для взаимодействия
# В составе:
# Данные для исполнителя скрипта
# Редактор команд
# ---------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip
from collections import deque

from commands import CommandClasses


class DataForWorker:
    """ Данные для исполнителя скрипта

    Класс для одиночного объекта, в котором хранятся данные
    необходимые для выполнения скрипта:
    очередь выполнения, объекты команд, стек для циклов и подпрограмм, источник данных.

    """
    def __init__(self):
        """ Инициализация

         В очереди команд идентификаторы под которыми они записаны в словаре объектов команд и
         в виджете для визуального представления. Очередь определяет последовательность исполнения.

         """
        self.queue_command = []  # Очередь команд (ключи - id команды)
        self.obj_command = dict()  # Объекты команд по ключам из очереди
        self.id_command = 0  # Счетчик для идентификаторов команд
        self.pointer_command = 0  # Указатель на исполняемую команду или положение курсора в списке

        self.stack = deque()  # Стек для циклов и подпрограмм

        # В качестве источника данных используются 2 словаря. В качестве ключей в них Имена полей
        # В первом словаре значения - это списки данных {'key': [list data]}
        # Во втором указатели на элементы списков первого словаря {'key': int}
        self.data_source = {'one': 1, 'two': 2} # dict()  # Источник данных
        self.pointers_data_source = dict()  # Указатели на позицию чтения из поля

        self.func_execute_command = None  # Функция выполняющая 1 команду макроса

    def next_id(self):
        """ Генерирует id новой команды """
        self.id_command += 1
        return f'cmd{self.id_command}'

    def get_fields(self):
        """ Возвращает список полей таблицы данных """
        return [i for i in self.data_source.keys()]

    def add_new_command(self, cmd):
        """ Добавление новой команды """
        key = self.next_id()
        self.queue_command.insert(self.pointer_command, key)
        self.obj_command.update({key: cmd})
        print(self.queue_command, self.obj_command)


data = DataForWorker()  # Создаем объект с данными о скрипте


class Editor:
    """ Редактор команд

    Представляет основной интерфейс редактора: выбор команды, кнопки действий.
    Без виджетов ввода данных, они находятся в самих командах.
    А так-же принимает ссылку на фрейм для сообщений, куда размещает виджет
    и выводит сообщения через отднльный метод

    """
    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = data  # Ссылка на класс с данными о скрипте

    def __init__(self, root, root_mes):
        """ При инициализации принимает ссылку на виджет, куда выводить элементы интерфейса """
        self.root = root
        self.root_mes = root_mes
        self.current_cmd = None  # Объект команды, с которой работает редактор

        # Формируем словарь: {название команды: класс}, для этого обращаемся к методу класса родителя команд
        # который возвращает классы потомков. В них читаем имена команд и данные о сортировке команд
        # создаем и сортируем список команд в соответствии с номерами для сортировки
        self.commands_dict = {cls.command_name: cls for cls in CommandClasses.get_all_subclasses()}
        self.commands_name = sorted(self.commands_dict, key=lambda x: self.commands_dict[x].for_sort)
        self.commands_var = StringVar(value=self.commands_name[0])  # Переменная содержит выбранное значение

        # Вывод виджетов
        self.widget = ttk.Combobox(self.root, values=self.commands_name, width=30,
                     textvariable=self.commands_var, state="readonly")
        self.widget.place(x=5, y=5)
        self.widget.bind("<<ComboboxSelected>>", self.select_command)

        # Информация
        self.message = StringVar()
        self.widget_mes = Message(root_mes, width=370, anchor='w', textvariable=self.message)
        self.widget_mes.place(x=0, y=0)

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
        if self.current_cmd:
            self.current_cmd.destroy_widgets()  # Удаляем старые виджеты
        # Получаем имя класса команды, для создания команды
        name = self.commands_dict[self.commands_var.get()].__name__
        # Зная имя класса команды создаем ее объект
        self.current_cmd = CommandClasses.create_command('', command=name)
        # Рисуем его виджеты
        self.current_cmd.paint_widgets()
        # Выводим справку о команде
        self.to_report(self.current_cmd.command_description)

    def add_cmd_button(self, event=None):
        print('Добавить')
        data.add_new_command(self.current_cmd)  # Добавление команды в очередь

    def change_cmd_button(self, event=None):
        print('Изменить')

    def to_report(self, message):
        self.message.set(message)


class DisplayCommands:
    """ Виджет списка команд

    Отображение изменений в списке команд на экране, реакция на взаимодействие со списком.

    """
    data = data  # Ссылка на класс с данными о скрипте
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)

    def __init__(self, root):
        """ Принимает ссылку на окно программы """

        # Create an instance of Style widget
        style = ttk.Style()
        style.theme_use('clam')

        self.tree = ttk.Treeview(root, show="", columns=('number', 'command'), selectmode="extended", height=28)
        self.tree.column("#1", stretch=NO, width=80)
        self.tree.column("#2", stretch=NO, width=300)

        self.tree.insert('', 0, 'gallery0', values=('', ''))
        self.tree.insert('', 'end', 'gallery1', values=(1, 'Клик левой клавишей мыши'))

        self.tree.selection_set('gallery1')
        self.tree.focus_set()
        self.tree.place(x=0, y=0)

    def out_string(self):
        """ Вывод строк в виджет

        Берет строки из объекта с данными и выводит их в виджет.
        Названия команд запрашивает у их объектов, где при наличии описания возвращается оно, а не название.


        """

if __name__ == '__main__':
    # блок кода, который будет выполнен только при запуске модуля
    a = Editor(None)
