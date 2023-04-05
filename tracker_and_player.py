# ---------------------------------------------------------------------------
# Модуль для записи и воспроизведения событий мыши и клавиатуры
# ---------------------------------------------------------------------------

from tkinter import *
from tktooltip import ToolTip
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key

from settings import settings


class Tracker:

    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = None  # Ссылка на класс с данными о скрипте

    def __init__(self, root):
        self.root = root  # Ссылка на главное окно программы
        self.single = False  # Для определения клика мыши, одинарный или двойной
        self.ctrl_pressed = False  # Инициализация флага нажатия клавиши ctrl
        self.listener_mouse = None  # Слушатель мыши
        self.listener_kb = None  # Слушатель клавиатуры
        self.is_listening = False  # Слушатели выключены

        # Кнопки управления записью
        self.icon1 = PhotoImage(file="icon/record.png")
        self.icon2 = PhotoImage(file="icon/stop.png")

        record_button = Button(command=self.rec_btn, image=self.icon1, width=100, height=34)
        record_button.place(x=12, y=settings.win_h - 43)
        ToolTip(record_button, msg="Запись скрипта", delay=0.5)

        stop_button = Button(command=self.stop_btn, image=self.icon2, width=100, height=34)
        stop_button.place(x=137, y=settings.win_h - 43)
        ToolTip(stop_button, msg="Останова записи", delay=0.5)

    def rec_btn(self):
        """ Обработка нажатия кнопки записи """
        # Запуск слушателя мыши
        self.listener_mouse = MouseListener(on_click=self.on_click)
        self.listener_mouse.start()

        # Запуск слушателя клавиатуры
        self.listener_kb = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.listener_kb.start()

    def stop_btn(self):
        """ Обработка нажатия кнопки стоп """
        self.listener_mouse.stop()
        self.listener_kb.stop()

    def single_click(self, args):
        """ Фиксация 1 клика, запускается по таймеру и отменяется, если есть клик второй """
        if self.single:
            self.to_export(cmd='MouseClickLeft', val=[args[0], args[1], ''], des='')
        self.single = False

    def to_export(self, **kwargs):
        """ Добавление команды в список """
        self.data.make_command(**kwargs)  # Добавляем команду
        self.display_commands.out_commands()  # Обновляем список

    def on_click(self, *args):
        """ Клик мыши любой нопкой"""
        x = args[0]
        y = args[1]
        button = args[2]
        pressed = args[3]
        if button == button.left and pressed:
            if not self.single:
                self.single = True
                self.root.after(300, lambda: self.single_click(args))
            else:
                self.to_export(cmd='MouseClickDouble', val=[args[0], args[1], ''], des='')
                self.single = False

        if button == button.right and pressed:
            # Отправляем на создание объекта команды и запись
            self.to_export(cmd='MouseClickRight', val=[args[0], args[1]], des='')

    def on_press(self, key=None):
        # Получаем название клавиши одним словом или буквой
        try:
            out = key.char
        except:
            out = str(key)[4:]
        # Отправляем на создание объекта команды и запись
        # TODO периодически возникают ошибки при неправильны названиях клавиш
        # TODO как-то предотвратить запись комбинаций остановки записи
        self.to_export(cmd='KeyDown', val=[out], des='')
        if key == Key.esc and self.ctrl_pressed:
            # Выход из программы при нажатии ctrl+esc
            self.stop_btn()
            return False
        elif key == Key.ctrl:
            self.ctrl_pressed = True

    def on_release(self, key):
        # Получаем название клавиши одним словом или буквой
        try:
            out = key.char
        except:
            out = str(key)[4:]
        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyUp', val=[out], des='')
        if key == Key.ctrl:
            self.ctrl_pressed = False
