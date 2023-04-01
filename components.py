# ---------------------------------------------------------------------------
# Составные части программы в классах.
# Импортируются в основную часть программы, предоставляя интерфейс для взаимодействия
# В составе:
# Редактор команд
# ---------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk

from commands import CommandClasses


class Editor:
    """ Редактор команд

    Представляет основной интерфейс редактора: выбор команды, кнопки действий.
    Без виджетов ввода данных, они находятся в самих командах.

    """

    def __init__(self, root):
        """ При инициализации принимает ссылку на виджет, куда выводить элементы интерфейса """
        self.root = root
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
        self.select_command(None)  # Создаем чистый объект команды, будто совершен выбор в списке

    def select_command(self, event):
        """ Обработка выбора команды в выпадающем списке """
        # Получаем имя класса команды, для создания команды
        name = self.commands_dict[self.commands_var.get()].__name__
        # Зная имя класса команды создаем ее объект
        self.current_cmd = CommandClasses.create_command([], command=name)


if __name__ == '__main__':
    # блок кода, который будет выполнен только при запуске модуля
    a = Editor(None)