# Настройки программы
# Объект с настройками создается при импорте и может существовать только в одном экземпляре
# Все имена атрибутов начинаются с s_
# Позволяет получать и менять отдельные настройки при прямом обращении к атрибуту объекта,
# возвращать все настройки в словаре и устанавливать их из словаря.

import tkinter as tk

from data_input import *
from data_types import eres


class Settings(object):
    """ Класс настроек """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):

        # Все настройки начинаются с s_
        self.s_key_pause = (0.1, 'Пауза между нажатием клавиш клавиатуры')
        self.s_click_pause = (0.5, 'Пауза после клика мыши')
        self.s_command_pause = (0, 'Пауза между командами')
        self.s_confirm_element = (True, 'Проверять наличие элемента (кнопки, иконки...)')
        self.s_search_attempt = (3, 'Сколько раз следует повторить паузу в 1 секунду')
        self.s_full_screen_search = (True, 'Производить поиск элемента на всем экране')
        self.s_error_no_element = (eres('stop:'), "Реакция скрипта на исключение 'Нет элемента'")
        self.s_error_no_data = (eres('ignore:'), "Реакция скрипта на исключение 'Нет данных'")
        self.s_description = ('', 'Описание скрипта')

    def get_dict_settings(self) -> dict:
        """ Возвращает все настройки в словаре """
        return {var: val[0] for var, val in self.__dict__.items() if var[:2] == 's_'}

    def set_settings_from_dict(self, settings_dict: dict):
        """ Перезаписывает настройки

         Принимает словарь с настройками. Настройки (ключи) из словаря находятся в названиях
         атрибутов, если атрибут найден, ему присваивается новое значение из словаря, но оно приводится к
         прежнему типу атрибута. Если такого атрибута не было, создается новый, с текстовым типом.

         """
        for var, val in settings_dict.items():
            if var[:2] != 's_':
                continue  # Пропускаем, если атрибут не настройка

            if var in self.__dict__:
                self.__dict__[var] = (type(self.__dict__[var][0])(val), self.__dict__[var][1])
            else:
                self.__dict__[var] = (val, self.__dict__[var][1])

    def __getattribute__(self, name):
        """ При обращении к атрибуту настройки пропускает только саму настройку, без комментария  """
        if name[:2] == 's_':
            return object.__getattribute__(self, name)[0]
        return object.__getattribute__(self, name)

    def show_window_settings(self, root, w, h):
        """ Отрытие окна настроек """
        self.top = tk.Toplevel()  # Новое окно
        self.top.title("Настройки")
        self.top.transient(root)  # Поверх окна

        # Размер окна
        win_w = 700
        win_h = 300
        self.top.geometry(f'{win_w}x{win_h}+{(w - win_w) // 2}+{(h - win_h) // 2}')  # Рисуем окно
        self.top.resizable(width=False, height=False)

        # Вывод настроек в окно, запоминаем возвращаемые объекты, чтоб собрать настройки после подтверждения
        self.obj = dict()
        start = 20
        for var, val in self.__dict__.items():
            if var[:2] != 's_':
                continue  # Обработка только настроек
            Label(self.top, text=self.__dict__[var][1]).place(x=20, y=start)  # Название настройки
            if var == 's_description':
                self.obj[var] = DataInput.CreateInput(self.top, val[0], x=195, y=start, width=50, length=50,
                                func_event=lambda *args, var=var: self.func_event(args, var))  # Для описания отдельно
            else:
                self.obj[var] = DataInput.CreateInput(self.top, val[0], x=430, y=start,
                                func_event=lambda *args, var=var: self.func_event(args, var))  # Виджет настройки
            start += 25

        Button(self.top, command=self.save, text='Сохранить').place(x=585, y=start+15)

        self.top.transient(root)
        self.top.grab_set()
        self.top.focus_set()
        self.top.wait_window()

    def func_event(self, *args):
        """ Результат в виджете печатает при событии """
        print(self.obj[args[1]].result)

    def save(self):
        """ Сохранение настроек в объекте """
        for var, val in self.obj.items():
            self.obj[var] = val.result  # Собираем результаты настроек
        self.set_settings_from_dict(self.obj)  # Эта же функция используется при чтении настроек из файла
        self.top.destroy()  # Закрытие окна

