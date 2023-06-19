
# Модуль для быстрого запуска скриптов и менеджера проектов

from tkinter import *
from tkinter import ttk
from tktooltip import ToolTip
import re
import os
import json

from settings import settings
from define_platform import system
# from components import data

def dialog_quick_start(root, run_script_func, load_old_script_func):
    """ Диалоговое окно для загрузки проекта и запуска скрипта """
    root.withdraw()  # Скрыть главное окно программы
    settings.run_from = 1  # Скрипт запускается из быстрого запуска

    # Создаем окно
    window = Toplevel(root)
    window.overrideredirect(True)  # Убираем рамку
    # Разместить окно в центре экрана
    window.wm_attributes("-topmost", True)
    root.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = (window.winfo_screenwidth() - window_width) // 2
    y = (window.winfo_screenheight() - window_height) // 2
    window.geometry("+%d+%d" % (x, y))

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

    def run(event=None):
        """ Запустить скрипт """

        # Ожидание выполнения скрипта
        def check_work():
            """ Функция вызывая себя через промежутки времени,
            проверяет каждый раз не завершилось ли выполнение скрипта, чтобы отобразить окно """
            if settings.script_started:
                root.after(100, check_work)
            else:
                window.deiconify()  # Вернуть окно программы
                window.focus_force()
                entry.after(100, lambda: entry.focus_set())

        # code = entry.get()
        # if not code:
        #     return

        # Путь к проекту Keep
        window.withdraw()  # Скрыть окно программы
        path = os.path.join(settings.work_dir, "Keep")
        run_script_func(path)
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
        print(code)
        if code == system.hotkeys['Ctrl_E']:
            # Ctrl+e
            to_editor()

    check = (window.register(is_valid), "%P")  # Назначаем функцию валидации
    entry = Entry(window, font=("Helvetica", 20), width=4, validatecommand=check, validate="key")
    entry.pack(side=LEFT, padx=20, pady=10)

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
        settings_button = Button(button_frame, image=icon3, width=50, height=50)
        settings_button.image = icon3
        settings_button.pack(side=LEFT)
        ToolTip(settings_button, msg="Настройка быстрого запуска", delay=0.5)

    icon4 = PhotoImage(file="icon/close.png")
    close_button = Button(button_frame, image=icon4, width=50, height=50, command=close_program)
    close_button.image = icon4
    close_button.pack(side=LEFT)
    ToolTip(close_button, msg="Закрыть", delay=0.5)

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
    def __init__(self):
        """ Чтение файла со списком проектов, обновление его в соответствии с изменениями в рабочей папке

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

        projects_from_file = {}  # Словарь с описанием проектов
        if os.path.isfile(os.path.join(settings.work_dir, settings.projects_list)):
            with open(os.path.join(settings.work_dir, settings.projects_list), "r", encoding="utf-8") as file:
                projects_from_file = json.load(file)

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
        self.used_codes_projects = []
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
                    self.used_codes_projects.append(int(project_code))

                if project_code:
                    # Если номер проекта получен (проект новый или изменился), то формируем словарь проекта
                    self.projects_dict[name] = {
                        "code": project_code,
                        "saved": data.get("saved", ""),
                        "updated": data.get("updated", ""),
                        "s_description": data.get("settings", {}).get("description", ""),
                        "data": {},
                    }

                # Код ниже для обработки файлов данных проекта
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
                        self.used_codes_data.append(int(file_code))
                        self.projects_dict[name]["data"][file_name] = file_code

            except Exception as e:
                print(f"Ошибка при обработке проекта {name}: {e}")
                continue  # Игнорируем проекты при обработке которых возникли ошибки

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
        """ Возвращает первый свободный код для проекта """
        return self.free_code(self.used_codes_projects)

    def free_code_for_data(self):
        """ Возвращает первый свободный код для файла данных """
        return self.free_code(self.used_codes_data)

def project_manager(root, run_script_func, load_old_script_func):
    """ Диалоговое окно настройки проектов для быстрого запуска

    Автоматически сканирует рабочую папку, генерирует номера скриптов, ведет список проектов,
    генерирует штрих-коды для быстрого запуска. Позволяет редактировать номера, запускать проекты,
    загружать проекты в редакторе.
    """
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

    # Размер окна
    win_w = 1100
    win_h = 600
    # Размер экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()

    window.geometry(f'{win_w}x{win_h}+{(w - win_w) // 2}+{(h - win_h) // 2}')  # Рисуем окно
    window.resizable(width=False, height=False)

    # Разместить окно в центре экрана
    window.wm_attributes("-topmost", True)
    root.update_idletasks()

    # Создаем дерево
    tree = ttk.Treeview(window, show="tree")
    scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    style = ttk.Style(window)
    style.configure('Treeview', rowheight=28)
    # Устанавливаем шрифт для всех элементов
    tree.tag_configure('font', font=('TkDefaultFont', 14, 'bold'))
    tree.tag_configure('font1', font=('TkDefaultFont', 14))

    tree.place(x=10, y=10, width=win_w - 20, height=win_h - 100)

    # Создаем список проектов
    projects = ProjectList()

    # Добавляем элементы в дерево
    for name, also in projects.projects_dict.items():
        # Вывод проектов
        project_id = also.get('code')
        string = f"{project_id + '00'}     Создан: {also.get('saved')}     Изменен: {also.get('updated')}     {name}"
        tree.insert("", project_id, project_id, text=string, tags=('font'))
        for file_name, code in also.get('data').items():
            # Вывод файлов данных
            data_code = project_id + code
            string = f"{data_code}    {file_name}"
            tree.insert(project_id, data_code, data_code, text=string, tags='font1')





    # Запускаем окно
    window.focus_force()
    # window.focus_set()
    # entry.after(100, lambda: entry.focus_set())
    # window.grab_set()


def a(window):

    # Создаем и настраиваем tree
    tree = ttk.Treeview(window, columns=("code", "saved", "updated", "description"), height=20)
    tree.column("#0", width=200, minwidth=200, stretch=NO)
    tree.column("code", width=50, minwidth=50, stretch=NO)
    tree.column("saved", width=100, minwidth=100, stretch=NO)
    tree.column("updated", width=100, minwidth=100, stretch=NO)
    tree.column("description", width=150, minwidth=150, stretch=NO)
    tree.heading("#0", text="Проекты", anchor=W)
    tree.heading("code", text="Код", anchor=W)
    tree.heading("saved", text="Создан", anchor=W)
    tree.heading("updated", text="Обновлен", anchor=W)
    tree.heading("description", text="Описание", anchor=W)
    tree.place(x=0, y=0)

    # Создаем и настраиваем полосу прокрутки для tree
    scrollbar = ttk.Scrollbar(window, orient=VERTICAL, command=tree.yview)
    scrollbar.place(x=580, y=0, height=580)
    tree.configure(yscrollcommand=scrollbar.set)

    # Создаем и настраиваем кнопки
    button_change =Button(window, text="Изменить", width=50, height=50, command=None)
    button_change.place(x=0, y=580)
    button_run =Button(window, text="Запустить проект", width=50, height=50, command=None)
    button_run.place(x=50, y=580)
    button_edit =Button(window, text="Открыть в редакторе", width=50, height=50, command=None)
    button_edit.place(x=100, y=580)
    button_barcode =Button(window, text="Получить штрих-код", width=50, height=50, command=None)
    button_barcode.place(x=150, y=580)
    button_quick_run =Button(window, text="Быстрый запуск", width=50, height=50, command=None)
    button_quick_run.place(x=200, y=580)
    button_open_folder =Button(window, text="Открыть рабочую папку", width=50, height=50, command=None)
    button_open_folder.place(x=250, y=580)
    button_change_folder =Button(window, text="Поменять рабочую папку", width=50, height=50, command=None)
    button_change_folder.place(x=300, y=580)

    # Создаем и настраиваем поле ввода для кода проекта или файла данных
    entry_code =Entry(window, width=2, font=("Arial", 20))
    entry_code.place(x=350, y=580)
    entry_code.bind("<Return>", None)

    # Создаем и настраиваем поле ввода для кода проекта
    entry_project_code =Entry(window, width=4, font=("Arial", 20))
    entry_project_code.place(x=400, y=580)
    entry_project_code.bind("<Return>", None)




