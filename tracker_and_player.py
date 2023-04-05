# ---------------------------------------------------------------------------
# Модуль для записи и воспроизведения событий мыши и клавиатуры
# ---------------------------------------------------------------------------

from tkinter import *
from tktooltip import ToolTip
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key

from settings import settings


class Tracker:
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

    def single_click(self):
        if self.single:
            print('Один клик')
        self.single = False

    def on_click(self, x, y, button, pressed):
        if button == button.left and pressed:
            if not self.single:
                self.single = True
                self.root.after(300, self.single_click)
            else:
                print('Двойной клик')
                self.single = False

        if button == button.right and pressed:
            print('Right click at ({0}, {1})'.format(x, y))

    def on_press(self, key=None):
        print('Key {0} pressed'.format(key))
        if key == Key.esc and self.ctrl_pressed:
            # Выход из программы при нажатии ctrl+esc
            self.stop_btn()
            return False
        elif key == Key.ctrl:
            self.ctrl_pressed = True

    def on_release(self, key):
        print('Key {0} released'.format(key))
        if key == Key.ctrl:
            self.ctrl_pressed = False


# tracker = Tracker()
# tracker.ctrl_pressed = False  # Инициализация флага нажатия клавиши ctrl
#
# # Запуск слушателя мыши
# mouse_listener = MouseListener(on_click=tracker.on_click)
# mouse_listener.start()
#
# # Запуск слушателя клавиатуры
# keyboard_listener = KeyboardListener(on_press=tracker.on_press, on_release=tracker.on_release)
# keyboard_listener.start()
#
# # Ожидание завершения программы
# mouse_listener.join()
# keyboard_listener.join()