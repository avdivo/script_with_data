
# Модуль для быстрого запуска скриптов и менеджера проектов

from tkinter import *
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
    root.update_idletasks()
    window.wm_attributes("-topmost", True)
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


def project_manager(root, run_script_func, load_old_script_func):
    """ Диалоговое окно настройки проектов для быстрого запуска

    Автоматически сканирует рабочую папку, генерирует номера скриптов, ведет список проектов,
    генерирует штрих-коды для быстрого запуска. Позволяет редактировать номера, запускать проекты,
    загружать проекты в редакторе.
    """
    def free_code(used_number: list[int]) -> str:
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

    # Формат словаря:
    #   { "project_name": {
    #                       "code": "12",
    #                       "saved": "07.06.2023",
    #                       "updated": "14.06.2023",
    #                       "s_description": "",
    #                       "data": {
    #                                "file_name.xlsx": "34",
    #                                },
    #                     },
    #   }

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
    used_codes_projects = []
    for name in projects_list:
        number = projects_from_file.get(name, {}).get("code", "")
        if number:
            used_codes_projects.append(int(number))

    # Собираем новый словарь с описанием проектов из записей прошлого и новых, если их не было
    projects_dict = {}
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
                    projects_dict[name] = projects_from_file[name]
                    projects_dict[name]["data"] = {}  # Очищаем словарь файлов данных
                else:
                    # Если изменился, то получаем его номер
                    project_code = projects_from_file[name]["code"]
            else:
                # Если проект новый, то получаем его номер и добавляем в список занятых номеров
                project_code = free_code(used_codes_projects)
                used_codes_projects.append(int(project_code))

            if project_code:
                # Если номер проекта получен (проект новый или изменился), то формируем словарь проекта
                projects_dict[name] = {
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
            used_codes_data = [int(number) for number in data_files_dict.values()]

            # Собираем новый словарь с именами файлов данных из записей прошлого и новых, если их не было
            for file_name in data_files:
                if file_name in data_files_dict:
                    # Если файл уже был, то добавляем его в словарь проекта
                    projects_dict[name]["data"][file_name] = data_files_dict[file_name]
                else:
                    # Если не было, то получаем номер для него, добавляем в словарь проекта и в список занятых номеров
                    file_code = free_code(used_codes_data)
                    used_codes_data.append(int(file_code))
                    projects_dict[name]["data"][file_name] = file_code

        except Exception as e:
            print(f"Ошибка при обработке проекта {name}: {e}")
            continue  # Игнорируем проекты при обработке которых возникли ошибки

    with open(os.path.join(settings.work_dir, settings.projects_list), "w", encoding="utf-8") as f:
        json.dump(projects_dict, f, indent=4)