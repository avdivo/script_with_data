# Модуль для быстрого запуска скриптов и менеджера проектов

from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from tktooltip import ToolTip
import re
import os
import json
import subprocess
import barcode
from barcode.writer import ImageWriter

from settings import settings
from define_platform import system


# from components import data

def dialog_quick_start(root, run_script_func, load_old_script_func, open_project_func):
    """ Диалоговое окно для загрузки проекта и запуска скрипта """
    root.withdraw()  # Скрыть главное окно программы
    settings.run_from = 1  # Скрипт запускается из быстрого запуска

    # Создаем окно
    window = Toplevel(root)
    window.overrideredirect(True)  # Убираем рамку
    # Разместить окно в центре экрана
    window.wm_attributes("-topmost", True)

    def close_program(event=None, open_editor=False):
        """ Закрыть программу """
        window.destroy()
        if not open_editor:
            root.destroy()
            return
        load_old_script_func()  # Загрузка последнего редактированного проекта в редактор
        root.deiconify()  # Отобразить окно редактора

    window.protocol("WM_DELETE_WINDOW", close_program)  # Функция выполнится при закрытии окна

    def to_editor(event=None):
        """ Закрыть окно и вернуться в редактор """
        settings.run_from = 0  # Теперь скрипт будет запускаться от имени редактора
        close_program(event, open_editor=True)

    def to_project_manager(event=None):
        """ Закрыть окно и перейти в менеджер проектов """
        window.destroy()
        project_manager(root, run_script_func, load_old_script_func, open_project_func)

    def run(event=None):
        """ Запустить скрипт """

        # Ожидание выполнения скрипта
        def check_work():
            """ Функция вызывая себя через промежутки времени,
            проверяет каждый раз не завершилось ли выполнение скрипта, чтобы отобразить окно """
            if settings.script_started:
                root.after(500, check_work)
            else:
                window.deiconify()  # Вернуть окно программы
                window.focus_force()
                entry.after(100, lambda: entry.focus_set())
                entry.delete(0, END)  # Очистить поле ввода

        code = entry.get()  # Получаем содержимое поля ввода
        if len(code) < settings.len_start_code//2:
            # Если не введен даже код проекта то выходим
            return

        code += '0' * (settings.len_start_code - len(code))  # Дополняем код нулями до длины полного кода
        projects = ProjectList(read_only=True)  # Создать объект с проектами
        projects.project_activation_by_number(code)  # Делаем проект и файл активными по коду
        if projects.only_project is None:
            return  # Выйти, если проект не выбран

        window.withdraw()  # Скрыть окно программы
        run_script_func(projects.active_project, projects.active_file)  # Запуск скрипта
        check_work()

    def is_valid(val):
        """ Пускает только целое число длиной не более кода запуска """
        if not val:
            return True  # Строка может быть пустой

        if len(val) > settings.len_start_code:
            return False

        return bool(re.fullmatch(r'\d+', val))  # Строка состоит только из цифр

    def keypress(event):
        """ Обработка нажатия клавиш на поле ввода """
        code = event.keycode
        if code == system.hotkeys['Ctrl_E']:
            # Ctrl+e
            to_editor()

    check = (window.register(is_valid), "%P")  # Назначаем функцию валидации
    entry = Entry(window, font=("Helvetica", 20), width=4, validatecommand=check, validate="key")
    entry.pack(side=LEFT, padx=20, pady=10)
    entry.bind("<Return>", run)  # Событие Enter в поле ввода (запуск скрипта)

    button_frame = Frame(window)
    button_frame.pack(side=RIGHT, padx=20, pady=10)

    icon1 = PhotoImage(file="icon/play.png")
    play_button = Button(button_frame, command=run,
                         image=icon1, width=50, height=50)
    play_button.image = icon1
    play_button.pack(side=LEFT)
    ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)

    if settings.developer_mode:
        # В режиме разработчика отображаются дополнительные кнопки
        icon2 = PhotoImage(file="icon/edit.png")
        editor_button = Button(button_frame, command=to_editor, image=icon2, width=50, height=50)
        editor_button.image = icon2
        editor_button.pack(side=LEFT)
        ToolTip(editor_button, msg="Перейти в редактор", delay=0.5)

        icon3 = PhotoImage(file="icon/settings.png")
        settings_button = Button(button_frame, image=icon3, width=50, height=50, command=to_project_manager)
        settings_button.image = icon3
        settings_button.pack(side=LEFT)
        ToolTip(settings_button, msg="Настройка быстрого запуска", delay=0.5)

    icon4 = PhotoImage(file="icon/close.png")
    close_button = Button(button_frame, image=icon4, width=50, height=50, command=close_program)
    close_button.image = icon4
    close_button.pack(side=LEFT)
    ToolTip(close_button, msg="Закрыть", delay=0.5)

    # Перемещение окна в центр экрана
    root.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = (window.winfo_screenwidth() - window_width) // 2
    y = (window.winfo_screenheight() - window_height) // 2
    window.geometry("+%d+%d" % (x, y))

    # Клавиша esc закрывает это окно и делает видимым главное
    window.bind("<Escape>", close_program)
    # Клавиши Ctrl+E закрывают это окно и делают видимым главное (переход в редактор)
    # window.bind("<Control-e>", close_window)
    window.bind("<Control-KeyPress>", keypress)  # Обработка нажатия клавиш на поле ввода

    # Запускаем окно
    window.focus_force()
    #
    # window.wm_attributes("-type", "dock")
    # window.focus_set()
    entry.after(100, lambda: entry.focus_set())
    # window.grab_set()
    # entry.focus_set()  # Фокус на поле ввода
    # window.wait_window()


class ProjectList:
    """ Класс для управления списком проектов и сохранением его в файле """

    def __init__(self, read_only=False):
        """ Чтение файла со списком проектов, обновление его в соответствии с изменениями в рабочей папке

            Аргумент read_only говорит о том, что список не будет обновляться, из него нужно только получить
            данные. Поэтому нужно только считать список проектов.

            Формат словаря:
              { "project_name": {
                                  "code": "12",
                                  "saved": "07.06.2023",
                                  "updated": "14.06.2023",
                                  "s_description": "",
                                  "data": {
                                           "file_name.xlsx": "34",
                                           },
                                },
              }
        """

        self.reinit(read_only)

    def reinit(self, read_only):
        self.active_project = ''  # Название проекта активного в данный момент
        self.active_file = ''  # Имя активного файла в активном проекте
        self.project_code = ''  # Код проекта
        self.file_code = ''  # Код файла
        self.only_project = None  # Содержит True, если файла данных нет, только проект. None - ничего не активно
        self.used_codes_projects = []
        self.used_codes_data = []

        projects_from_file = {}  # Словарь с описанием проектов
        if os.path.isfile(os.path.join(settings.work_dir, settings.projects_list)):
            with open(os.path.join(settings.work_dir, settings.projects_list), "r", encoding="utf-8") as file:
                projects_from_file = json.load(file)

        if read_only:
            # Только заполняем словарь проектов и выходим
            self.projects_dict = projects_from_file
            return

        # Сканирование рабочей папки и составление списка проектов
        projects_list = []
        for name in os.listdir(settings.work_dir):
            path = os.path.join(settings.work_dir, name)
            # Папка признается проектом, если содержит json файл с таким же именем,
            # папку с изображениями и папку с данными
            if os.path.isfile(os.path.join(path, name + ".json")) and \
                    os.path.isdir(os.path.join(path, settings.elements_folder)) and \
                    os.path.isdir(os.path.join(path, settings.data_folder)):
                projects_list.append(name)

        # Составляем список (типа int) занятых номеров проектов
        # Если проекта уже нет в папке, то его номер освобождается
        for name in projects_list:
            number = projects_from_file.get(name, {}).get("code", "")
            if number:
                self.used_codes_projects.append(int(number))

        # Собираем новый словарь с описанием проектов из записей прошлого и новых, если их не было
        self.projects_dict = {}
        for name in projects_list:
            # Считываем скрипт проекта из json файла
            try:
                path = os.path.join(settings.work_dir, name)
                with open(os.path.join(path, name + ".json"), "r", encoding="utf-8") as file:
                    data = json.load(file)

                project_code = ""  # Код проекта
                data_files_dict = {}  # Словарь с именами и кодами файлов данных
                if name in projects_from_file:
                    data_files_dict = projects_from_file[name]["data"]  # Запоминаем старый словарь файлов данных
                    # Если проект уже был, то проверяем, не изменился ли он
                    if projects_from_file[name]["updated"] == data.get("updated", ""):
                        # Если не изменился, то просто переносим его в новый словарь
                        self.projects_dict[name] = projects_from_file[name]
                        self.projects_dict[name]["data"] = {}  # Очищаем словарь файлов данных
                    else:
                        # Если изменился, то получаем его номер
                        project_code = projects_from_file[name]["code"]
                else:
                    # Если проект новый, то получаем его номер и добавляем в список занятых номеров
                    project_code = self.free_code_for_project()

                if project_code:
                    # Если номер проекта получен (проект новый или изменился), то формируем словарь проекта
                    self.projects_dict[name] = {
                        "code": project_code,
                        "saved": data.get("saved", ""),
                        "updated": data.get("updated", ""),
                        "s_description": data.get("settings", {}).get("description", ""),
                        "data": {},
                    }

                # Код ниже для обработки файлов данных проекта ----------------------------------
                # Считываем список файлов с данными только табличного типа
                data_files = [name for name in os.listdir(os.path.join(path, settings.data_folder))
                              if name.endswith(('.xls', '.xlsx', '.csv'))]

                # Составляем список (типа int) занятых номеров файлов данных
                # Если файл данных уже нет в папке, то его номер освобождается
                self.used_codes_data = [int(number) for number in data_files_dict.values()]

                # Собираем новый словарь с именами файлов данных из записей прошлого и новых, если их не было
                for file_name in data_files:
                    if file_name in data_files_dict:
                        # Если файл уже был, то добавляем его в словарь проекта
                        self.projects_dict[name]["data"][file_name] = data_files_dict[file_name]
                    else:
                        # Если не было, то получаем номер для него, добавляем в словарь проекта и в список занятых номеров
                        file_code = self.free_code_for_data()
                        self.projects_dict[name]["data"][file_name] = file_code

            except Exception as e:
                print(f"Ошибка при обработке проекта {name}: {e}")
                continue  # Игнорируем проекты при обработке которых возникли ошибки

        self.save()  # Сохраняем список проектов в файл

    def save(self):
        """ Сохраняет список проектов в файл """
        with open(os.path.join(settings.work_dir, settings.projects_list), "w", encoding="utf-8") as f:
            json.dump(self.projects_dict, f, indent=4)

    def free_code(self, used_number: list[int]) -> str:
        """ Возвращает первый свободный код для проекта или файла данных

        Номера состоят из цифр, количество их в номере всегда одинаковое. В настройках параметр len_start_code
        указывает общую длину кода, она состоит из 2 равных частей: код проекта и код файла данных. Код представляется
        цифрой в формате str с предшествующими нулями (чтобы длина кода была одинаковой).
        Функция находит в предложенном списке номеров первый свободный код и возвращает строку длиной len_start_code/2.
        """
        code_len = settings.len_start_code // 2
        for i in range(1, 10 ** code_len):
            if i not in used_number:
                return str(i).zfill(code_len)
        raise ValueError("Нет свободных номеров")

    def free_code_for_project(self):
        """ Возвращает первый свободный код для проекта и добавляет его в список используемых """
        code = self.free_code(self.used_codes_projects)
        self.used_codes_projects.append(int(code))
        return code

    def free_code_for_data(self):
        """ Возвращает первый свободный код для файла данных и добавляет его в список используемых """
        code = self.free_code(self.used_codes_data)
        self.used_codes_data.append(int(code))
        return code

    def project_activation_by_number(self, code: str):
        """ Активирует проект и файл данных с заданным номером

        Принимает код проекта в расширенном виде (дополненный кодом файла). Длина его должна быть
        как в настройках. Устанавливает в свойствах активный проект и файл данных. Если файла данных нет
        его код состоит из нулей.

        """
        self.project_code = code[:len(code)//2]  # Код проекта
        self.file_code = code[len(code) // 2:]  # Код файла данных

        self.active_project = ''
        self.active_file = ''
        self.only_project = None  # Ничего не активно

        # Ищем имя проекта по коду
        for name in self.projects_dict:
            if self.projects_dict[name].get('code') == self.project_code:
                self.active_project = name
                self.only_project = True  # Активен только проект, без файла данных
                break

        if self.only_project:
            # Ищем имя файла данных в активном проекте по коду если проект выбран
            for file, code in self.projects_dict[self.active_project].get('data').items():
                if code == self.file_code:
                    self.active_file = file
                    self.only_project = False  # Активен проект, и есть файл данных
                    # Обновляем список занятых кодов для файлов проекта
                    self.used_codes_data.clear()
                    self.used_codes_data = [
                        int(number) for number in self.projects_dict[self.active_project].get('data').values()]
                    break
        return

    def change_project_code(self, val):
        """ Изменение кода проекта

        Если код текущего проекта как заменяющий - то не меняется.
        Если код еще не использован для других проектов, то просто назначаем текущему.
        Если код используется, то тому проекту, которым он используется назначаем свободный код,
        а текущему назначаем заменяющий.
        Возвращаем результат bool удалось или нет.
        """
        if self.project_code == val:
            return False # Выходим, если активный проект и так имеет этот код
        self.used_codes_projects.remove(int(self.project_code))  # Освобождаем код активного проекта

        if int(val) in self.used_codes_projects:
            # Код используется для другого проекта, заменяем его свободным
            # Ищем имя проекта который занимает нужный код
            found_name = None
            for name, value in self.projects_dict.items():
                if value['code'] == val:
                    found_name = name
                    break
            if found_name is None:
                self.used_codes_projects.append(int(self.project_code))  # Возвращаем код активного проекта
                return False  # Такого быть не должно, если номер есть, а проект не найден

            # Получаем свободный код для проекта
            try:
                new_code = self.free_code_for_project()
                self.used_codes_projects.remove(int(val))  # Освобождаем код проекта у которого берем код
            except:
                # Не удалось получить свободный код
                messagebox.showerror('Не удалось получит код', 'Вероятно нет свободного кода для замещения, '
                                                               'удалите не используемые проекты из рабочей папки. '
                                                               'Или обратитесь к разработчику.')
                self.used_codes_projects.append(int(self.project_code))  # Возвращаем код активного проекта
                return False

            # Заменяем код использующего нужный код проекта на новый
            self.projects_dict[found_name]['code'] = new_code

        self.projects_dict[self.active_project]['code'] = val  # Назначаем новый код активному проекту
        self.project_code = val  # Меняем номер активного проекта
        self.used_codes_projects.append(int(val))  # Добавляем новый код в список занятых
        return True

    def change_file_code(self, val):
        """ Изменение кода файла данных

        Если код текущего файла как заменяющий - то не меняется.
        Если код еще не использован для других файлов, то просто назначаем текущему.
        Если код используется, то тому файлу, которым он используется назначаем свободный код,
        а текущему назначаем заменяющий.
        Возвращаем результат bool удалось или нет.
        """
        if self.file_code == val:
            return False  # Выходим, если активный файл и так имеет этот код
        self.used_codes_data.remove(int(self.file_code))  # Освобождаем код активного файла

        if int(val) in self.used_codes_data:
            # Код используется для другого файла, заменяем его свободным
            # Ищем имя файла который занимает нужный код
            found_name = None
            for name, code in self.projects_dict[self.active_project]['data'].items():
                if code == val:
                    found_name = name
                    break
            if found_name is None:
                self.used_codes_data.append(int(self.file_code))  # Возвращаем код активного файла
                return False  # Такого быть не должно, если номер есть, а файл не найден

            # Получаем свободный код для файла
            try:
                new_code = self.free_code_for_data()
                self.used_codes_data.remove(int(val))  # Освобождаем код файла у которого берем код
            except:
                # Не удалось получить свободный код
                messagebox.showerror('Не удалось получит код', 'Вероятно нет свободного кода для замещения, '
                                                               'удалите не используемые файлы данных из проекта. '
                                                               'Или обратитесь к разработчику.')
                self.used_codes_data.append(int(self.file_code))  # Возвращаем код активного файла
                return False

            # Заменяем код использующего нужный код файла на новый
            self.projects_dict[self.active_project]['data'][found_name] = new_code

        self.projects_dict[self.active_project]['data'][self.active_file] = val  # Назначаем новый код
        self.file_code = val  # Меняем номер активного файла
        self.used_codes_data.append(int(val))  # Добавляем новый код в список занятых
        return True

    def get_fool_code(self):
        """ Получение полного кода проекта и файла данных

        Если нет активного проекта, то возвращаем None
        Если нет активного файла, дополняем код проекта нулями до количества  символов в настройеах
        """
        if self.only_project is None or not self.active_project:
            return None
        if not self.active_file:
            return self.project_code + '0' * len(self.project_code)
        return self.project_code + self.file_code


def project_manager(root, run_script_func, load_old_script_func, open_project_func):
    """ Диалоговое окно настройки проектов для быстрого запуска

    Автоматически сканирует рабочую папку, генерирует номера скриптов, ведет список проектов,
    генерирует штрих-коды для быстрого запуска. Позволяет редактировать номера, запускать проекты,
    загружать проекты в редакторе.
    Для работы с редактором принимает функции для запуска скрипты, открытия старого проекта и открытия любого проекта.
    """
    def on_select(event):
        """ Обработка события выбора строки в списке """
        selected_item = event.widget.selection()[0]  # Получаем id команды
        projects.project_activation_by_number(selected_item)  # Делаем проект и файл активными
        if projects.only_project is None:
            return
        # Выводим код в поле для смены кода
        code_value.set(projects.project_code if projects.only_project else projects.file_code)

    def change_code(event=None):
        """ Изменение кода проекта или файла

         Берется 2 значный код из поля для изменения, он может указывать нв проект или файл
         в зависимости от активной строки. Этот код присваивается выделенному элементу.
         Если код занят другим проектом или файлом, то другому элементу подбирается свободное
         значение, а указанное присваивается выбранному.
         """
        if projects.only_project is None:
            return  # Выходим, если ничего не выбрано
        val = code_value.get()
        if len(val) < 2:
            return   # Выходим, если длина меньше 2 символов

        if projects.only_project:
            # Работа с кодом проекта
            if not projects.change_project_code(val):
                return  # Если не удалось изменить, выходим
        else:
            # Работа с кодом файла
            if not projects.change_file_code(val):
                return  # Если не удалось изменить, выходим

        new_code = projects.get_fool_code()  # Получаем новый код
        projects.save()  # Сохраняем изменения
        update_cast()  # Обновляем список проектов
        tree.selection_set(new_code)  # Выделяем новый элемент

    def update_cast():
        """ Обновить список проектов """
        tree.delete(*tree.get_children())  # Очищаем дерево
        # Добавляем элементы в дерево
        # TODO: Обратить внимание на сортировку
        for name, also in projects.projects_dict.items():
            # Вывод проектов
            # Добавляем в id проекта нули вместо кода файла, длиной в соответствии с настройками
            project_id = also.get('code') + ('0' * (settings.len_start_code // 2))
            string = f"{project_id}     Создан: {also.get('saved')}     Изменен: {also.get('updated')}     {name}"
            tree.insert("", "end", project_id, text=string, tags=('font'))
            for file_name, code in also.get('data').items():
                # Вывод файлов данных
                data_code = also.get('code') + code
                string = f"{data_code}    {file_name}"
                tree.insert(project_id, "end", data_code, text=string, tags='font1')

    def close_program(event=None, open_editor=False):
        """ Закрыть программу """
        window.destroy()
        if not open_editor:
            root.destroy()
            return
        if projects.only_project is None:
            load_old_script_func()  # Загрузка последнего редактированного проекта в редактор
        else:
            open_project_func(projects.active_project, projects.active_file)  # Открытие выбранного проекта в редакторе
        root.deiconify()  # Отобразить окно редактора

    def to_editor(event=None):
        """ Закрыть окно и вернуться в редактор """
        settings.run_from = 0  # Теперь скрипт будет запускаться от имени редактора
        close_program(event, open_editor=True)

    def keypress(event):
        """ Обработка нажатия клавиш на поле ввода """
        code = event.keycode
        if code == system.hotkeys['Ctrl_E']:
            # Ctrl+e
            to_editor()

    def to_quick_start():
        """ Закрыть окно и перейти в окно быстрого запуска """
        window.destroy()
        dialog_quick_start(root, run_script_func, load_old_script_func, open_project_func)

    def select_work_dir():
        """ Выбор рабочей папки """
        new = filedialog.askdirectory(initialdir=settings.work_dir, title='Выбор рабочей папки')
        if new:
            settings.work_dir = new
            # Сохраняем новую рабочую папку в файл настроек, но поскольку изменение файла настроек
            # разрешено только из редактора, временно действуем от имени редактора
            settings.run_from = 0
            settings.config_file(action='set', work_dir=new)
            settings.run_from = 2
            # Сканируем новую рабочую папку и обновляем список проектов, создавая новый объект класса ProjectsList
            projects.reinit(False)
            update_cast()  # Обновить список проектов в окне

    def run(event=None):
        """ Запустить скрипт """
        if projects.only_project is None:
            return  # Проект не выбран

        # Ожидание выполнения скрипта
        def check_work():
            """ Функция вызывая себя через промежутки времени,
            проверяет каждый раз не завершилось ли выполнение скрипта, чтобы отобразить окно """
            if settings.script_started:
                root.after(500, check_work)
            else:
                window.deiconify()  # Вернуть окно программы
                window.focus_force()
                code_run.after(100, lambda: code_run.focus_set())

        window.withdraw()  # Скрыть окно программы
        path = os.path.join(settings.work_dir, projects.active_project)  # Путь к проекту
        run_script_func(path, projects.active_file)  # Запускаем скрипт передавая путь к нему и источник данных
        check_work()

    def is_valid(val, max_len):
        """ Пускает только целое число длиной не более кода запуска """
        if not val:
            return True
        if len(val) <= int(max_len):
            return bool(re.fullmatch(r'\d+', val))  # Строка состоит только из цифр
        return False

    def on_key_release_code_run(*args):
        """ При вводе кода выделяем подходящую строку в списке

        При вводе цифры дополняем оставшиеся знаки нулями и
        производим поиск по этому значению.
        """
        val = code_run_value.get()
        val = val + '0' * (settings.len_start_code - len(val))
        if val and tree.exists(val):
            tree.selection_set(val)
            tree.see(val)
            # tree.focus_set()
            # tree.focus(val)

    def open_file_explorer():
        """ Открыть рабочую папку в проводнике """
        if system.os == 'Windows':
            os.startfile(settings.work_dir)
        elif system.os == 'Linux':
            subprocess.Popen(['xdg-open', settings.work_di])
        else:
            print('Операционная система не поддерживается')

    def save_barcode():
        """ Сохранить штрихкод """
        if projects.only_project is None:
            return  # Выходим, если ничего не выбрано

        code = projects.get_fool_code()
        filename = filedialog.asksaveasfilename(
            initialdir=settings.work_dir, title="Сохранение штрих-кода", initialfile=f'{code}',
            filetypes=(("png files", "*.png"), ("all files", "*.*")))

        if filename:
            ean = barcode.get('ean8', f'{code}0000', writer=ImageWriter())
            filename = ean.save(filename)

    # Вывод окна Toplevel со следующими параметрами:
    #   Размер окна: 600x600, размещено в центре экрана, с кнопками управления
    #   Заголовок окна: Менеджер проектов
    #   В верхней части окна расположен список tree пустой. Шириной на все окно, высотой 500.
    #   В нижней части окна расположены элементы управления одной строкой, разбитые на группы:
    #   1. Поле ввода для 2 цифр кода проекта или файла данных, рядом кнопка Изменить
    #   2. 3 кнопки: Запустить проект, Открыть в редакторе, Получить штрих-код
    #   3. 3 кнопки: Быстрого запуск, Открыть рабочую папку, Поменять рабочую папку
    #   4. Поле ввода на 4 цифры для кода проекта.
    #   Все кнопки размером 50x50, с изображением вместо текста
    #   Поля ввода с крупным шрифтом - 20 пт

    root.withdraw()  # Скрыть главное окно программы
    settings.run_from = 2  # Скрипт запускается из менеджера проектов

    # Создаем окно
    window = Toplevel(root)
    window.title("Менеджер проектов")
    window.iconbitmap('icon.ico')
    # Размер окна
    win_w = 1100
    win_h = 600
    # Размер экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()

    window.geometry(f'{win_w}x{win_h}+{(w - win_w) // 2}+{(h - win_h) // 2}')  # Рисуем окно
    window.resizable(width=False, height=False)

    root.update_idletasks()
    # Разместить окно в центре экрана
    # window.wm_attributes("-topmost", True)

    window.protocol("WM_DELETE_WINDOW", close_program)  # Функция выполнится при закрытии окна
    window.bind("<Escape>", close_program)  # Клавиша esc закрывает - Закрыть программу
    window.bind("<Control-KeyPress>", keypress)  # Обработка нажатия клавиш

    # Создаем дерево
    style = ttk.Style()
    style.configure('my.Treeview', rowheight=28)

    tree = ttk.Treeview(window, show="tree", selectmode='browse')
    scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set, style='my.Treeview')

    # Устанавливаем шрифт для всех элементов
    tree.tag_configure('font', font=('TkDefaultFont', 14, 'bold'))
    tree.tag_configure('font1', font=('TkDefaultFont', 14))

    tree.place(x=10, y=10, width=win_w - 20, height=win_h - 100)
    tree.bind("<<TreeviewSelect>>", on_select)  # Обработка выбора строки в списке

    # Создаем список проектов
    projects = ProjectList()
    update_cast()  # Обновить список проектов в окне

    # Создание полей ввода
    check = (window.register(is_valid), "%P")  # Назначаем функцию валидации полей ввода

    code_value = StringVar()  # Код в поле ввода для изменения кода
    code = Entry(window, font=("Helvetica", 26), width=2, validatecommand=(*check, 2), validate="key",
                 textvariable=code_value)
    code.place(x=20, y=win_h-72)
    ToolTip(code, msg="Код проекта или файла данных", delay=0.5)
    code.bind("<Return>", change_code)  # Событие Enter в поле ввода
    code.bind("<FocusIn>", lambda event: code.select_range(0, END))  # Выделение текста в поле при получении фокуса

    code_run_value = StringVar()  # Код в поле ввода для запуска скрипта
    code_run = Entry(window, font=("Helvetica", 26), width=4, validatecommand=(*check, 4), validate="key",
                     textvariable=code_run_value)
    code_run.place(x=win_w-125, y=win_h-72)
    ToolTip(code_run, msg="Поиск и запуск по коду", delay=0.5)
    code_run_value.trace("w", on_key_release_code_run)  # Событие изменения текста в поле ввода
    code_run.bind("<Return>", run)  # Событие Enter в поле ввода (запуск скрипта)
    code_run.bind("<FocusIn>", lambda event: code_run.delete(0, END))  # Очистка поля ввода при получении фокуса
    y = win_h-72
    x = 90

    # Создаем и настраиваем кнопки
    icon1 = PhotoImage(file="icon/apply.png")
    button_change = Button(window, image=icon1, width=50, height=50, command=change_code)
    button_change.image = icon1
    button_change.place(x=x, y=y)
    ToolTip(button_change, msg="Изменить код", delay=0.5)
    x += 150
    icon2 = PhotoImage(file="icon/play.png")
    button_run = Button(window, image=icon2, width=50, height=50, command=run)
    button_run.image = icon2
    button_run.place(x=x, y=y)
    ToolTip(button_run, msg="Запустить", delay=0.5)
    x += 150
    icon4 = PhotoImage(file="icon/barcode.png")
    button_barcode = Button(window, image=icon4, width=50, height=50, command=save_barcode)
    button_barcode.image = icon4
    button_barcode.place(x=x, y=y)
    ToolTip(button_barcode, msg="Получить штрих-код", delay=0.5)
    x += 150
    icon3 = PhotoImage(file="icon/edit.png")
    button_edit = Button(window, image=icon3, width=50, height=50, command=to_editor)
    button_edit.image = icon3
    button_edit.place(x=x, y=y)
    ToolTip(button_edit, msg="Открыть в редакторе", delay=0.5)
    x += 70
    icon5 = PhotoImage(file="icon/to_quick_start.png")
    button_quick_run = Button(window, image=icon5, width=50, height=50, command=to_quick_start)
    button_quick_run.image = icon5
    button_quick_run.place(x=x, y=y)
    ToolTip(button_quick_run, msg="Открыть окно быстрого запуска", delay=0.5)
    x += 150
    icon6 = PhotoImage(file="icon/folder.png")
    button_open_folder = Button(window, image=icon6, width=50, height=50, command=open_file_explorer)
    button_open_folder.image = icon6
    button_open_folder.place(x=x, y=y)
    ToolTip(button_open_folder, msg="Открыть рабочую папку", delay=0.5)
    x += 70
    icon7 = PhotoImage(file="icon/change.png")
    button_change_folder = Button(window, image=icon7, width=50, height=50, command=select_work_dir)
    button_change_folder.image = icon7
    button_change_folder.place(x=x, y=y)
    ToolTip(button_change_folder, msg="Сменить рабочую папку", delay=0.5)


    # Запускаем окно
    # window.focus_force()
    # window.focus_set()
    code_run.after(100, lambda: code_run.focus_set())
    # window.grab_set()
