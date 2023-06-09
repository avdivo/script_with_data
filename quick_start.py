# Модуль для быстрого запуска скриптов и менеджера проектов

from tkinter import *
from tktooltip import ToolTip
import re

from settings import settings


def dialog_quick_start(root):
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

    def close_window(event=None):
        """ Закрыть окно и вернуться в редактор """
        window.destroy()
        root.deiconify()
    window.protocol("WM_DELETE_WINDOW", close_window)  # Функция выполнится при закрытии окна

    def is_valid(val):
        """ Пускает только целое число длиной не более кода запуска """
        if not val:
            return True  # Строка может быть пустой

        if len(val) > settings.len_start_code:
            return False

        return bool(re.fullmatch(r'\d+', val))  # Строка состоит только из цифр

    check = (window.register(is_valid), "%P")  # Назначаем функцию валидации
    entry = Entry(window, font=("Helvetica", 20), width=4, validatecommand=check, validate="key")
    entry.pack(side=LEFT, padx=20, pady=10)

    button_frame = Frame(window)
    button_frame.pack(side=RIGHT, padx=20, pady=10)

    icon1 = PhotoImage(file="icon/play.png")
    play_button = Button(button_frame, image=icon1, width=50, height=50)
    play_button.image = icon1
    play_button.pack(side=LEFT)
    ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)

    icon2 = PhotoImage(file="icon/edit.png")
    editor_button = Button(button_frame, command=close_window, image=icon2, width=50, height=50)
    editor_button.image = icon2
    editor_button.pack(side=LEFT)
    ToolTip(editor_button, msg="Перейти в редактор", delay=0.5)

    icon3 = PhotoImage(file="icon/settings.png")
    settings_button = Button(button_frame, image=icon3, width=50, height=50)
    settings_button.image = icon3
    settings_button.pack(side=LEFT)
    ToolTip(settings_button, msg="Настройка быстрого запуска", delay=0.5)

    # Клавиша esc закрывает это окно и делает видимым главное
    window.bind("<Escape>", close_window)

    # Ожидание выполнения скрипта
    # def check_work():
    #     global work
    #     if not work:
    #         label_text.set("Work is False")
    #     else:
    #         root.after(100, check_work)

    # Запускаем окно
    window.focus_force()
    entry.after(100, lambda: entry.focus_set())
    # window.grab_set()
    # window.focus_set()
    # entry.focus_set()  # Фокус на поле ввода
    # window.wait_window()