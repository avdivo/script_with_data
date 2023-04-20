from tkinter import *
import time
import logging


class Messages:

    def write(self, message):
        # здесь можно реализовать вывод сообщения в нужное место с учетом важности
        level, message = message.split(':')
        # здесь можно реализовать вывод сообщения в нужное место с учетом важности
        print(f"level {level} {message}")

class Messages:
    """ Вывод сообщений

    Сообщения могут быть 3 типов: help, info, warn
    Сообщения более высоких уровней заменяют сообщения более низких.
    Для обратной замены должно пройти не менее 5 секунд от публикации
    сообщения более высокого уровня, иначе новое игнорируется.
    """
    # root = None  # Объект фрейма для вывода сообщений

    def __init__(self, root):
        self.message = StringVar()
        self.widget_mes = Message(root, width=370, anchor='w', textvariable=self.message)
        self.widget_mes.place(x=0, y=0)
        self.old_rating = 0
        self.rating = ['warning', 'error', 'critical']  # Текущий уровень сообщения
        self.time = 0  # Время последнего сообщения

    def write(self, message):
        # здесь можно реализовать вывод сообщения в нужное место с учетом важности
        level, message = message.split(':')

        """ Вывод сообщения в поле сообщений """
        if level not in self.rating:
            return
        if self.rating.index(level) < self.old_rating:
            if self.time + 5 < time.time():
                return
        self.widget_mes.config(foreground='#083863')
        self.message.set(message)
        self.time = time.time()
        self.old_rating = self.rating.index(level)


