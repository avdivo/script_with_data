# Настройки программы
# Объект с настройками создается при импорте и может существовать только в одном экземпляре
# Все имена атрибутов начинаются с s_
# Позволяет получать и менять отдельные настройки при прямом обращении к атрибуту объекта,
# возвращать все настройки в словаре и устанавливать их из словаря.

import os
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
        # Настройки для программы
        self.data_folder = 'data'  # Папка с данными
        self.elements_folder = 'elements_img'  # Папка с изображениями элементов
        self.path_to_project = ''  # Путь к файлу проекта
        self.project_name = ''  # Имя проекта
        self.path_to_script = ''  # Путь к файлу скрипта
        self.path_to_data = ''  # Путь к файлам - источникам данных
        self.path_to_elements = ''  # Путь к папке с изображениями элементов

        self.update_settings()

        # Настройки изображений элементов
        self.first_region = 96  # Сторона квадрата, в котором ищутся сохраненные элементы
        self.region = 48  # Сторона квадрата с сохраняемым элементом
        self.basename = "elem"  # Префикс для имени файла при сохранении изображения элемента
        self.region_for_search = 96  # Сторона квадрата в котором производится первоначальный поиск элемента

        # Размер окна
        self.win_w = 800
        self.win_h = 610

        # Настройки скрипта по умолчанию
        self.default_settings()

    def default_settings(self):
        self.is_saved = True  # Проект сохранен (сбрасывается при изменении)
        # Все настройки скрипта начинаются с s_
        self.s_key_pause = (0.0, 'Пауза между нажатием клавиш клавиатуры')
        self.s_click_pause = (0.5, 'Пауза после клика мыши')
        self.s_command_pause = (0.0, 'Пауза между командами (всеми)')
        self.s_reset_data_source = (True, 'Сбрасывать источник данных при запуске скрипта')
        self.s_confirm_element = (True, 'Включить локальную проверку')
        self.s_local_check_size = (96, 'Зона локальной проверки (сторона квадрата)')
        self.s_search_attempt = (3, 'Сколько секунд ждать, после 1 попытки')
        self.s_full_screen_search = (True, 'Искать на всем экране')
        self.s_error_no_element = (eres('dialog:'), "Какое действие выполнить если нет изображения")
        self.s_error_no_data = (eres('dialog:'), "Какое действие выполнить если нет данных")
        self.s_description = ('', 'Описание скрипта')

    def update_settings(self):
        """ Обновляет настройки """
        self.path_to_script = os.path.join(self.path_to_project, self.project_name)  # Путь к файлу скрипта
        self.path_to_data = os.path.join(self.path_to_script, self.data_folder)  # Путь к файлам - источникам данных
        self.path_to_elements = os.path.join(self.path_to_script, self.elements_folder)  # Путь к папке с изображениями элементов

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
        win_h = 380
        self.top.geometry(f'{win_w}x{win_h}+{(w - win_w) // 2}+{(h - win_h) // 2}')  # Рисуем окно
        self.top.resizable(width=False, height=False)

        # Вывод настроек в окно, запоминаем возвращаемые объекты, чтоб собрать настройки после подтверждения
        self.obj = dict()
        start = 20
        Label(self.top, text=f'Проект: {os.path.join(self.path_to_project, self.project_name)}').place(x=20, y=start)  # Название настройки
        start += 25
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
        self.is_saved = False  # Изменения в проекте не сохранены
        self.top.destroy()  # Закрытие окна


# Создание объекта настроек, передаем ему ссылку на родительское окно и разрешение экрана
settings = Settings()

