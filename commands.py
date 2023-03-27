# ---------------------------------------------------------------------------
# В этом модуле собраны классы для команд скрипта
# Класс описывает:
#   название команды
#   краткое описание
#   данные для выполнения
#   описание формы для редактирования
#   метод для выполнения
# ---------------------------------------------------------------------------

from tkinter import *
from tktooltip import ToolTip
from tkinter import filedialog as fd

from data_input import DataInput



class MouseClickLeft:
    """ Клик левой кнопкой мыши """
    command_name = 'Клик левой кнопкой мыши'
    command_description = 'x, y - координаты на экране. Изображение - элемент, который программа ожидает "увидеть" ' \
                         'в этом месте. Если изображения не будет в этих координатах, будут произведены действия ' \
                         'в соответствии с настройками скрипта.'

    def __init__(self, *args, root=None):
        """ Принимает координаты и изображение в списке """
        args = args + ('', '', '')  # Заполняем не пришедшие аргументы пустыми строками
        self.root = root  # Родительский виджет, куда выводятся виджеты ввода
        self.x = args[0]
        self.y = args[1]
        self.image = args[2]
        self.description = ''
        self.widget_x = None
        self.widget_y = None
        self.element_image = None
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

        # Изображение элемента
        self.element_image = PhotoImage(file=self.image)
        element_button = Button(self.root, command=self.load_image, image=self.element_image, width=96, height=96, relief=FLAT)
        element_button.place(x=273, y=5)
        ToolTip(element_button, msg="Изображение элемента", delay=0.5)

    def load_image(self):
        """ Загрузка изображения элемента """
        self.image = fd.askopenfilename(
            filetypes=(("image", "*.jpg;*.png"),
                       ("All files", "*.*")))
        if self.image:
            print(self.image)
            self.element_image = PhotoImage(file=self.image)