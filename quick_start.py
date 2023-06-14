# Модуль для быстрого запуска скриптов и менеджера проектов

from tkinter import *
from tktooltip import ToolTip
import re
import os

from settings import settings
from define_platform import system


def dialog_quick_start(root, run_script_func):
    """ Диалоговое окно для загрузки проекта и запуска скрипта """
    root.withdraw()  # Скрыть главное окно программы

    # Создаем окно
    window = Toplevel(root)
    window.overrideredirect(True)  # Убираем рамку
    # Разместить окно в центре экрана
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
        root.deiconify()

    window.protocol("WM_DELETE_WINDOW", close_program)  # Функция выполнится при закрытии окна

    def to_editor(event=None):
        """ Закрыть окно и вернуться в редактор """
        close_program(event, open_editor=True)

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

    # Путь к проекту Keep
    path = os.path.join(settings.work_dir, "Keep")
    print(path)
    icon1 = PhotoImage(file="icon/play.png")
    play_button = Button(button_frame, command=lambda: run_script_func(path),
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

    # Ожидание выполнения скрипта
    # def check_work():
    #     global work
    #     if not work:
    #         label_text.set("Work is False")
    #     else:
    #         root.after(100, check_work)

    # Запускаем окно
    window.focus_force()
    window.wm_attributes("-topmost", True)
    window.wm_attributes("-type", "dock")
    # window.wm_attributes("-focus", True)
    # window.focus_set()
    entry.after(100, lambda: entry.focus_set())
    # window.grab_set()
    # entry.focus_set()  # Фокус на поле ввода
    # window.wait_window()