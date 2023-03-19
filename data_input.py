# Набор классов для создания различных элементов ввода данных.
# Классы используют виджеты tkinter

from tkinter import *
from abc import ABC, abstractmethod

class DataInput(ABC):
    """ Базовый класс

     В зависимости от типа принимаемых данных создает объект
     нужного подкласса с переданными параметрами

     """
    def __init__(self, **kvargs):
        self.func_event = kvargs['func_event']
        self.obj = None
        print("Выполняю...")

    def widget_event(self, event):
        """ Определяет одно (нужное для работы) событие и выполняет функцию назначенную при создании объекта"""
        return self.func_event(event)


class FieldInt(DataInput):
    """  """
    def __init__(self, root, **kvargs):
        super().__init__(**kvargs)
        print('Выполнил')
        en = Entry(root, width=5).place(x=34, y=71)
        en.bind('<Click>', kvargs['func_event'])



