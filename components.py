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
from tracker_and_player import Player

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
        self.pointer_command = -1  # Указатель на исполняемую команду или положение курсора в списке

        self.stack = deque()  # Стек для циклов и подпрограмм

        # В качестве источника данных используются 2 словаря. В качестве ключей в них Имена полей
        # В первом словаре значения - это списки данных {'key': [list data]}
        # Во втором указатели на элементы списков первого словаря {'key': int}
        self.data_source = {'one': 1, 'two': 2} # dict()  # Источник данных
        self.pointers_data_source = dict()  # Указатели на позицию чтения из поля

        self.func_execute_event = None  # Функция выполняющая событие мыши или клавиатур

        self.script_started = False  # False - остановит скрипт, True - позволит выполняться

    def next_id(self):
        """ Генерирует id новой команды """
        self.id_command += 1
        return f'cmd{self.id_command}'

    def get_fields(self):
        """ Возвращает список полей таблицы данных """
        return [i for i in self.data_source.keys()]

    def make_command(self, **kwargs):
        """ Создает объект команды на основе параметров и добавляет ее в список """
        # Создаем объект команды
        cmd = CommandClasses.create_command(
            *kwargs['val'], command=kwargs['cmd'], description=kwargs['des'])
        self.add_new_command(cmd)  # Добавляем команду

    def add_new_command(self, cmd):
        """ Добавление новой команды

        Принимает объект команды

        """
        key = self.next_id()  # Получаем новый id
        self.pointer_command += 1  # Строка добавляется в позицию за указателем и на нее ставим указатель
        self.queue_command.insert(self.pointer_command, key)  # Добавляем id в очередь
        self.obj_command.update({key: cmd})  # Добавляем объект в dict

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
            self.obj_command[self.queue_command[self.pointer_command]] = cmd  # Меняем объект команды под курсором

    def run_command(self):
        """ Выполнение очередной команды и переходна следующую"""
        if self.pointer_command == -1:
            self.pointer_command = 0

        res = self.obj_command[self.queue_command[self.pointer_command]].run_command()
        if self.pointer_command+1 < len(self.queue_command):
            # Еще есть команды в очереди
            self.pointer_command += 1
        else:
            raise ('Конец')


data = DataForWorker()  # Создаем объект с данными о скрипте


class Editor:
    """ Редактор команд

    Представляет основной интерфейс редактора: выбор команды, кнопки действий.
    Без виджетов ввода данных, они находятся в самих командах.
    А так-же принимает ссылку на фрейм для сообщений, куда размещает виджет
    и выводит сообщения через отднльный метод

    """
    # TODO Правильная обработка множественного выбора строк в списке
    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = data  # Ссылка на класс с данными о скрипте

    def __init__(self, root, root_mes):
        """ При инициализации принимает ссылку на виджет, куда выводить элементы интерфейса """
        self.root = root  # Фрейм редактора
        self.root_mes = root_mes  # Фрейм сообщений
        self.current_cmd = None  # Объект команды, с которой работает редактор

        # Формируем словарь: {название команды: класс}, для этого обращаемся к методу класса родителя команд
        # который возвращает классы потомков. В них читаем имена команд и данные о сортировке команд
        # создаем и сортируем список команд в соответствии с номерами для сортировки
        self.commands_dict = {cls.command_name: cls for cls in CommandClasses.get_all_subclasses()}
        self.commands_name = sorted(self.commands_dict, key=lambda x: self.commands_dict[x].for_sort)
        self.commands_var = StringVar(value=self.commands_name[0])  # Переменная содержит выбранное значение

        # Вывод виджета выпадающего списка команд
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
        self.to_report(self.current_cmd.command_description)
        # Установка в выпадающем списке нужной команды
        self.commands_var.set(self.current_cmd.command_name)
        self.widget.selection_clear()  # Убираем выделение с выпадающего списка

    def add_cmd_button(self, event=None):
        """ Добавление команды из редактора в список """
        print(event)
        self.current_cmd.save()
        self.data.add_new_command(self.current_cmd)  # Добавление команды в очередь
        self.display_commands.out_commands()  # Обновляем список

    def change_cmd_button(self, event=None):
        """ Изменение текущей в списке команды на ту, что в редакторе """
        self.current_cmd.save()
        self.data.change_command(self.current_cmd)  # Изменяем команду
        self.display_commands.out_commands()  # Обновляем список

    def to_report(self, message):
        """ Вывод сообщения в поле сообщений """
        self.message.set(message)


class DisplayCommands:
    """ Виджет списка команд и копок операций над ним

    Отображение изменений в списке команд на экране, реакция на взаимодействие со списком.
    4 кнопки редактирования списка. Копировать, Вырезать, Вставить, Удалить.

    """
    data = data  # Ссылка на класс с данными о скрипте
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)

    def __init__(self, root, frame):
        """ Принимает ссылку на окно программы и фрейм для кнопок"""

        # Create an instance of Style widget
        style = ttk.Style()
        style.theme_use('clam')

        self.tree = ttk.Treeview(root, show="", columns=('number', 'command'), selectmode="extended", height=28)
        self.tree.column("#1", stretch=NO, width=80)
        self.tree.column("#2", stretch=NO, width=300)
        self.tree.place(x=0, y=0)
        self.out_commands()

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Рисуем кнопки для работы со списком
        self.list_copy = []  # Список хранит id скопированных строк
        self.operation = ''  # Может быть copy или cut

        self.icon6 = PhotoImage(file="icon/copy.png")
        self.icon7 = PhotoImage(file="icon/cut.png")
        self.icon8 = PhotoImage(file="icon/paste.png")
        self.icon9 = PhotoImage(file="icon/delete.png")

        copy_button = Button(frame, command=self.copy, image=self.icon6, width=160, height=34)
        copy_button.place(x=10, y=10)
        ToolTip(copy_button, msg="Копировать команды", delay=0.5)

        cut_button = Button(frame, command=self.cut, image=self.icon7, width=160, height=34)
        cut_button.place(x=200, y=10)
        ToolTip(cut_button, msg="Переместить команды", delay=0.5)

        paste_button = Button(frame, command=self.paste, image=self.icon8, width=160, height=34)
        paste_button.place(x=10, y=58)
        ToolTip(paste_button, msg="Вставить команды", delay=0.5)

        delete_button = Button(frame, command=self.delete, image=self.icon9, width=160, height=34)
        delete_button.place(x=200, y=58)
        ToolTip(delete_button, msg="Удалить команды", delay=0.5)

    def on_select(self, event):
        """ Обработка события выбора строки в списке """
        try:
            selected_item = event.widget.selection()[0]  # Получаем id команды
        except:
            # Иногда не показывает выделение
            return
        # Устанавливаем указатель списка
        self.data.pointer_command = -1 if selected_item == 'zero' else self.data.queue_command.index(selected_item)
        self.editor.command_to_editor(selected_item)  # Выводим команду в редактор по ее id

    def out_commands(self):
        """ Вывод строк в виджет

        Берет строки из объекта с данными и выводит их в виджет.
        Названия команд запрашивает у их объектов, где при наличии описания возвращается оно, а не название.

        """
        self.clear()
        self.tree.insert('', 0, 'zero', values=('', ''))  # Добавляем пустую строку
        for i, id in enumerate(data.queue_command):
            # Выводим список
            self.tree.insert('', 'end', id, values=(i+1, self.data.obj_command[id]))
        self.tree.selection_set(self.tree.get_children()[data.pointer_command+1])  # Выделяем строку
        # self.tree.focus_set()
        pass

    def clear(self):
        """ Очистка списка команд """
        for item in self.tree.get_children():
            self.tree.delete(item)

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

    def copy(self):
        """ Обработчик кнопки Копировать """
        self.list_copy = self.get_selected()  # id выделенных команд
        if not self.list_copy:
            return
        numbers = ' ,'.join(self.numbers_from_id(self.list_copy))  # Номера копируемых строк
        self.editor.to_report(f'Скопированы строки {numbers}. \nИх можно вставить кнопкой Вставить. '
                              f'\nСтроки будут вставлены после выделенной строки.')
        self.operation = 'copy'

    def cut(self):
        """ Обработчик кнопки Вырезать """
        self.list_copy = self.get_selected()  # id выделенных команд
        if not self.list_copy:
            return
        numbers = ' ,'.join(self.numbers_from_id(self.list_copy))  # Номера копируемых строк
        self.editor.to_report(f'Перенос строк {numbers}. \nИх можно вставить кнопкой Вставить. '
                              f'\nСтроки будут вставлены после выделенной строки. \nСкопированные строки будут удалены')
        self.operation = 'cut'

    def paste(self):
        """ Обработчик кнопки Вставить """
        if self.operation and self.list_copy:
            # Убеждаемся, что операция актуальна и скопированные строки есть
            for i in self.list_copy:
                # Вставляем скопированные строки
                self.data.add_new_command(self.data.obj_command[i])
                if self.operation == 'cut':
                    # При вырезании и вставке скопированные команды нужно удалить
                    self.data.del_command(i)

            # Очищаем данные операции
            self.list_copy = []
            self.operation = ''

            self.out_commands()  # Обновляем список
        else:
            # Операция не назначена или отменена
            self.editor.to_report('Операция отменена.')

    def delete(self):
        """ Обработчик кнопки Удалить """
        list_del = self.get_selected()  # id выделенных команд
        if not list_del:
            return
        for i in list_del:
            self.data.del_command(i)

        # Очищаем данные операции
        self.list_copy = []
        self.operation = ''

        self.out_commands()  # Обновляем список


if __name__ == '__main__':
    # блок кода, который будет выполнен только при запуске модуля
    a = Editor(None)
