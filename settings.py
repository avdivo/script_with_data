# Настройки программы
# Объект с настройками создается при импорте и может существовать только в одном экземпляре
# Все атрибуты объекта являются настройками, любой добавленный атрибут будет сохраняться
# в файле скрипта как настройка.
# Позволяет получать и менять отдельные настройки при прямом обращении к атрибуту объекта,
# возвращать все настройки в словаре и устанавливать их из словаря.

from tkinter import *

from data_input import DataInput, FieldInt, FieldStr, FieldFloat
from data_types import llist


class Settings(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.key_pause = (0.1, 'Пауза между нажатием клавиш клавиатуры (после отпускания)')
        self.click_pause = (0.5, 'Пауза после клика мыши')
        self.command_pause = (0, 'Пауза между командами')
        self.confirm_element = (True, 'Убеждаться, что нужный элемент (кнопка, иконка ...) присутствует')
        self.search_attempt = (3, 'Сколько раз следует повторить паузу в 1 секунду')
        self.full_screen_search = (True, 'Производить поиск элемента на всем экране')
        self.error_no_element = ('stop', "Остановить выполнение скрипта при исключении 'no element'")
        self.error_no_data = ('ignore', "Остановить выполнение скрипта при исключении 'no data'")
        self.description = ('', 'Описание скрипта')

    def get_dict_settings(self) -> dict:
        """ Возвращает все настройки в словаре """
        print(self.__dict__['error_no_data'][1])
        return {var: val[0] for var, val in self.__dict__.items()}

    def set_settings_from_dict(self, settings_dict: dict):
        """ Перезаписывает настройки

         Принимает словарь с настройками в текстовом виде. Настройки (ключи) из словаря находятся в названиях
         атрибутов, если атрибут найден, ему присваивается новое значение из словаря, но оно приводится к
         прежнему типу атрибута. Если такого атрибута не было, создается новый, с текстовым типом.

         """
        for var, val in settings_dict.items():
            if var in self.__dict__:
                self.__dict__[var] = (type(self.__dict__[var][0])(val), self.__dict__[var][1])
            else:
                self.__dict__[var] = (val, self.__dict__[var][1])

    def __getattribute__(self, name):
        print(type(self).__name__, '--', name)
        if type(self).__name__ == name:
            print("Internal call")
        if isinstance(object.__getattribute__(self, name), tuple):
            return object.__getattribute__(self, name)[0]
        return object.__getattribute__(self, name)

    def test(self):
        window = Tk()
        window.title("Проверка")
        self.a = DataInput.CreateInput(window, 120, x=30, y=50, width=10,
                                  length=4, func_event=self.test_event)
        window.mainloop()

    def test_event(self, event):
        print(self.a.value)

# FieldInt(window, x=30, y=50, width=5, func_event=self.test_event)
# FieldStr(window, x=30, y=50, width=5, length=3, black_list='1', func_event=self.test_event)


a = Settings()
a.test()

# settings = Settings()
# print(settings.get_dict_settings())
# settings.set_settings_from_dict({'key_pause': 4, 'click_pause': 4})
# print(settings.get_dict_settings())
# print(settings.key_pause)

