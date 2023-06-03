# ---------------------------------------------------------------------------
# Модуль для записи и воспроизведения событий мыши и клавиатуры
# ---------------------------------------------------------------------------
import string
import time
from time import sleep
from tkinter import *
from tktooltip import ToolTip
from pynput.mouse import Listener as MouseListener, Controller as mouse_Controller, Button as Btn
from pynput.keyboard import Listener as KeyboardListener, Controller as kb_Controller, Key
import logging
import pyautogui

from threading import Thread

from settings import settings
from define_platform import system
from element_images import save_image, pattern_search
from exceptions import TemplateNotFoundError, ElementNotFound
from hotkeys import hotkeys
from define_platform import system


# создание логгера и обработчика
logger = logging.getLogger('logger')

kb = kb_Controller()
mouse = mouse_Controller()

class Tracker:

    display_commands = None  # Ссылка на объект отображающий команды (реализация паттерна Наблюдатель)
    data = None  # Ссылка на класс с данными о скрипте
    save_load = None  # Ссылка на класс сохранения и загрузки

    def __init__(self, root):
        self.root = root  # Ссылка на главное окно программы
        self.single = False  # Для определения клика мыши, одинарный или двойной
        self.listener_mouse = MouseListener(on_click=self.on_click)  # Слушатель мыши
        self.listener_kb = KeyboardListener(on_press=self.on_press, on_release=self.on_release)  # Слушатель клавиатуры
        self.is_listening = False  # Слушатели выключены
        self.img = None  # Хранит изображение под курсором при последнем клике
        self.pressing_keys_set = set()  # Множество нажатых клавиш (для недопущения автоповтора)
        self.current_key = None  # сюда записывается клавиша нажатая виртуально, чтобы отсеять ее нажатие в реальных

        # Скриншот делается для клика мыши, замены изображения в клике, для команды проверки места
        # Во всех случаях включается слушатель. Однако, для обычного режима записи скрипта переменная only_screenshot
        # содержит строку, отличную от 'wait', а в режиме скриншота для замены изображения в клике - 'wait'
        self.only_screenshot = ''

        # Для скриншота и обновления координат.
        # Бывает нужно получить изображение элемента, когда над ним нет курсора
        # при наведении элемент может измениться. Тогда при выполнении скриншота координаты можно запомнить заранее
        # (например, при нажатии Alt), отвести курсор и уже при повторном нажатии Alt сделать скриншот.
        self.mouse_position = None  # Позиция курсора мыши

        # События нажатия клавиш клавиатуры и кликов мыши записываются в очередь на запись в программу.
        # После это происходит проверка очередного события на совпадение с комбинацией событий и если оно подходит,
        # а комбинация еще не завершена, событие остается в очереди.
        # Из очереди в программу события записываются только после завершения комбинации в виде одной команды. Или если
        # комбинация прервалась, то в неизменном виде. Так-же они могут не записываться, если комбинация специальная.
        self.queue_events = []  # Очередь событий, которые необходимо записать в программу


        # Кнопки управления записью
        self.icon1 = PhotoImage(file="icon/record.png")
        self.icon2 = PhotoImage(file="icon/stop.png")

        record_button = Button(command=self.rec_btn, image=self.icon1, width=100, height=34)
        record_button.place(x=12, y=settings.win_h - 43)
        ToolTip(record_button, msg="Запись скрипта", delay=0.5)

        stop_button = Button(command=self.stop_btn, image=self.icon2, width=100, height=34)
        stop_button.place(x=137, y=settings.win_h - 43)
        ToolTip(stop_button, msg="Останова записи", delay=0.5)

    def rec_btn(self):
        """ Обработка нажатия кнопки записи """
        # TODO Обозначит что идет запись/воспроизведение
        # Запуск слушателя мыши
        if self.data.script_started or self.data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        self.listener_mouse = MouseListener(on_click=self.on_click)  # Слушатель мыши
        self.listener_mouse.start()

        # Запуск слушателя клавиатуры
        self.listener_kb = KeyboardListener(on_press=self.on_press, on_release=self.on_release)  # Слушатель клавиатуры
        self.listener_kb.start()

        self.is_listening = True  # Слушатели включены
        self.data.is_listening = True  # Дублируем в data
        self.queue_events.clear()  # Очищаем очередь событий
        self.pressing_keys_set.clear()  # Очищаем множество нажатых клавиш

        self.mouse_position = None  # Координаты мыши

        logger.error('Идет запись.')

    def reset_kb(self):
        """ Вернуть состояние клавиатуры в исходное """
        # Отпустить все клавиши
        kb.release(Key.ctrl)
        kb.release(Key.alt)
        kb.release(Key.shift)

    def stop_btn(self):
        """ Обработка нажатия кнопки стоп """
        self.queue_events.clear()  # Очищаем очередь событий

        if self.data.script_started:
            # Остановка выполнения скрипта
            self.data.script_started = False
            self.reset_kb()
            logger.error('Пользователь остановил выполнение скрипта.')
            return

        if self.is_listening:
            # Остановка записи
            self.listener_mouse.stop()
            # self.listener_mouse.join()
            self.listener_kb.stop()
            # self.listener_kb.join()
            self.is_listening = False
            self.data.is_listening = False
            settings.is_saved = False  # Изменения в проекте не сохранены
            logger.error('Запись остановлена.')
            self.save_load.save_history()  # Сохраняем историю

    def to_export(self, **kwargs):
        """ Добавление команды в список программы, распознавание комбинаций клавиш

        Событие добавляется в очередь, если оно первое в очереди запускается таймер набора комбинации
        (некоторые комбинации должны быть выполнены за определенное время, например 2 нажатия esc за 0.5 сек. - стоп).
        Очередь сверяется со списком зарезервированных комбинаций. Номер текущей команды в очереди должен совпадать
        хотя бы с одной комбинацией в той же позиции. Если совпадений ней, вся очередь передается в список программы,
        если есть и команда не последняя ни в одной из комбинаций, продолжается прослушивание, в список пока не
        передается. Если же команда последняя в какой-то из комбинаций, то есть вся комбинация совпала -
        для нее выполняется программа: остановка записи, преобразование набора команд (комбинации) в одну команду, и
        передача ее в таком виде в программу (например для копирования). После этого, очередь очищается и прослушивание
        продолжается. Если комбинация не выполнена за определенное время (для некоторых комбинаций), то очередь
        просто переносится в программу, без выполнения программы предусмотренной для комбинации.
        """
        self.queue_events.append(kwargs)  # Добавляем событие в очередь
        res = hotkeys.search_hotkey(kwargs['cmd'], kwargs['val'], len(self.queue_events))  # Поиск комбинаций клавиш
        if res == 'next':
            return  # Комбинация с этим событием в этой позиции есть, но не завершена, ждем продолжения

        if res:
            # Это событие завершило комбинацию, есть совпадение
            # Название комбинации находится в res.
            # Название всегда начинается с ключевого слова и может быть разделено подчеркиванием.
            # Выполняем действия для комбинации
            res = res.split()[0]

            # ---------------------- Действия для комбинаций --------------------------

            # -------- Комбинации действующие всегда --------
            if res == 'stop':
                # Остановка записи или воспроизведения при нажатии ctrl 2 раза.
                self.only_screenshot = ''  # Получение скриншота отменено
                self.stop_btn()
                return

            if res == 'screenshot':
                """ Запись команды проверки места на экране или снятие скриншота """
                if self.only_screenshot == 'wait':
                    self.only_screenshot = save_image(*self.mouse_position)  # Получаем скриншот
                    self.stop_btn()
                    return
                # Проверка изображения в нужном месте экрана срабатывает при нажатии 2 раза подряд Alt
                # Делается скриншот, его имя и координаты передаются для создания команды проверки изображения
                # Alt, Alt
                # Подмена набора комбинации клавиш для СКРИНШОТА встроенной командой
                self.only_screenshot = save_image(*self.mouse_position)  # Получаем скриншот
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'CheckImage', 'val': [*self.mouse_position, self.only_screenshot],
                                          'des': ''})

            if res == 'mouse_position':
                """ Запоминает координаты курсора """
                self.mouse_position = mouse.position
                return

            # -------- Комбинации действующие при записи --------
            if not self.is_listening:
                self.queue_events.clear()  # Очищаем очередь
                return

            if res == 'copy':
                # Ctrl+C
                # Подмена набора комбинации клавиш для КОПИРОВАНИЯ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'CopyCmd', 'val': [], 'des': ''})

            if res == 'cut':
                # Ctrl+X
                # Подмена набора комбинации клавиш для ВЫРЕЗАНИЯ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'CutCmd', 'val': [], 'des': ''})

            if res == 'paste':
                # Ctrl+V
                # Подмена набора комбинации клавиш для ВСТАВКИ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'PasteCmd', 'val': [], 'des': ''})

            if res == 'select':
                # Ctrl+A
                # Подмена набора комбинации клавиш для ВЫБРАТЬ ВСЕ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'SelectCmd', 'val': [], 'des': ''})

            if res == 'language_change':
                # Alt+Shift
                # Подмена набора комбинации клавиш для ПЕРЕКЛЮЧЕНИЯ РАСКЛАДКИ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'LanguageChangeCmd', 'val': [], 'des': ''})

            if res == 'new_tab':
                # Ctrl+T
                # Подмена набора комбинации клавиш для НОВОЙ ВКЛАДКИ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'NewTabCmd', 'val': [], 'des': ''})

            if res == 'next_tab':
                # Ctrl+Tab
                # Подмена набора комбинации клавиш для ПЕРЕКЛЮЧЕНИЯ ВКЛАДКИ встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'NextTabCmd', 'val': [], 'des': ''})

            if res == 'next_window':
                # Alt+Tab
                # Подмена набора комбинации клавиш для ПЕРЕКЛЮЧЕНИЯ ОКОН встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'NextWindowCmd', 'val': [], 'des': ''})

            if res == 'roll_up_windows':
                # Cmd+D для Windows и Ctrl+Alt+D для Linux
                # Подмена набора комбинации клавиш для СВЕРНУТЬ ВСЕ ОКНА встроенной командой
                self.queue_events.clear()  # Очищаем очередь
                self.queue_events.append({'cmd': 'RollUpWindowsCmd', 'val': [], 'des': ''})

            res = None
            # ------------------------------------------------------------------------


        if self.only_screenshot == 'wait':
            # Ожидание скриншота не предполагает запись команд
            self.queue_events.clear()  # Очищаем очередь
            return

        if not res and self.is_listening:
            for event in self.queue_events:
                # Добавляем события в список программы
                self.data.make_command(**event)  # Добавляем команду

            self.display_commands.out_commands()  # Обновляем список
        self.queue_events.clear()  # Очищаем очередь

    def single_click(self, args):
        """ Фиксация 1 клика, запускается по таймеру и отменяется, если есть клик второй """
        if self.single:
            self.single = False
            self.to_export(cmd='MouseClickLeft', val=[args[0], args[1], self.img], des='')

    def on_click(self, *args):
        """ Клик мыши любой кнопкой"""
        if not self.is_listening:
            return
        if self.only_screenshot == 'wait':
            return
        self.img = save_image(args[0], args[1])  # Сохранить изображение элемента на котором был клик
        button = args[2]
        pressed = args[3]
        if button == button.left and pressed:
            if not self.single:
                self.single = True
                self.root.after(300, lambda: self.single_click(args))
            else:
                # Фиксация
                self.single = False
                self.to_export(cmd='MouseClickDouble', val=[args[0], args[1], self.img], des='')

        if button == button.right and pressed:
            # Отправляем на создание объекта команды и запись
            self.to_export(cmd='MouseClickRight', val=[args[0], args[1]], des='')

    def get_str_key(self, key):
        """ Получение названия клавиши в виде строки """
        # Получаем название клавиши одним словом или буквой
        try:
            out = self.listener_kb.canonical(key).char
            if not out:
                raise
        except:
            out = str(key)[4:]

            if out in system.key_replace:
                # Подмена названий некоторых клавиш например Ctrl_l на Ctrl
                out = system.key_replace[out]

        return out

    def on_press(self, key=None):
        """ Обработка события нажатия клавиши """
        print(key)
        key_str = self.get_str_key(key)  # Получаем название клавиши в виде строки
        if key_str == self.current_key:
            # Это виртуальное нажатие, не обрабатываем
            # self.current_key = None
            return
        if key in self.pressing_keys_set:
            # Если клавиша уже нажата, то ничего не делаем
            return
        self.pressing_keys_set.add(key)  # Добавляем нажатую клавишу в множество

        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyDown', val=[key_str], des='')

    def on_release(self, key):
        key_str = self.get_str_key(key)  # Получаем название клавиши в виде строки
        if key_str == self.current_key:
            # Это виртуальное нажатие, не обрабатываем
            # self.current_key = None
            return
        # Удаляем клавишу из множества
        try:
            self.pressing_keys_set.remove(key)
        except:
            return
        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyUp', val=[key_str], des='')


class Player:
    """ Воспроизведение события мыши или клавиатуры """
    data = None  # Ссылка на класс с данными о скрипте
    tracker = None  # Ссылка на класс прослушивания клавиатуры и мыши
    data_source = None  # Ссылка на объект источник данных

    def __init__(self, root, run_script):
        """ Принимает ссылку на главное окно и функцию, которую нужно запустить для выполнения скрипта """
        self.root = root
        self.run_script = run_script  # Функи выполнения скрипта
        self.icon3 = PhotoImage(file="icon/play.png")

        play_button = Button(
            command=lambda: root.after(3000, self.run_thread), image=self.icon3, width=100, height=34)

        play_button.place(x=262, y=settings.win_h - 43)
        ToolTip(play_button, msg="Выполнение скрипта", delay=0.5)

    def run_thread(self):
        """ Запуск функции выполнения скрипта в отдельном потоке """
        if self.data.script_started or self.data.is_listening:
            return  # Операция невозможна при выполнении или записи скрипта

        if not len(self.data.queue_command):
            logger.warning('Нет команд для выполнения')
            return

        # Запуск слушателя клавиатуры для остановки
        self.tracker.listener_kb = KeyboardListener(on_press=self.tracker.on_press, on_release=self.tracker.on_release)
        self.tracker.listener_kb.start()

        self.data.work_settings = settings.get_dict_settings()  # Рабочая копия настроек
        self.data.work_labels = dict()  # Заполняем словарь меток и названий блоков
        for key, obj in self.data.obj_command.items():
            if obj.__class__.__name__ == 'BlockCmd' or obj.__class__.__name__ == 'LabelCmd':
                # Это метка или блок, добавляем в словарь
                self.data.work_labels[obj.value] = self.data.queue_command.index(key)

        # Сбрасываем источник данных
        if settings.s_reset_data_source:
            # Сброс разрешен в настройках
            if self.data_source:
                self.data_source.menu_reset_pointers()

        new_thread = Thread(target=self.run_script)  # Создаём поток
        logger.warning('Выполнение скрипта')
        new_thread.start()  # Запускаем поток

    def run_command(self, cmd, val, des=None):
        """ Выполняет одну команду для мыши или клавиатуры

        Принимает команду и параметры. Для каждого события свои.
        Обрабатывает команды (cmd):
        MouseClickLeft, MouseClickDouble, MouseClickRight,
        KeyDown, KeyUp, Write

        """
        if cmd[:3] == 'Mou':
            # Команда мыши
            # mouse.position = (val[0], val[1])  # Ставим указатель в нужную позицию
            pyautogui.moveTo(val[0], val[1], 0.3)

            if cmd == 'MouseClickRight':
                # Клик правой копкой мыши
                mouse.press(Btn.right)
                mouse.release(Btn.right)

            if cmd == 'MouseClickLeft':
                # Клик левой копкой мыши
                mouse.press(Btn.left)
                mouse.release(Btn.left)

            elif cmd == 'MouseClickDouble':
                # Двойной клик
                mouse.click(Btn.left, 2)

            sleep(self.data.work_settings['s_click_pause']) # Пауза после клика мыши

        elif cmd[:3] == 'Key':
            # Подготовка к распознаванию как отдельных символов, так и специальных клавиш
            insert = val[0]
            self.tracker.current_key = insert  # Запоминаем, какую клавишу нажмем, чтобы отличить от реальных нажатий
            if len(insert) == 1:
                insert = f"'{insert}'"
            else:
                insert = f"Key.{insert}"

            if cmd == 'KeyDown':
                # Нажать клавишу
                exec(f"kb.press({insert})")
            else:
                # Отпустить клавишу
                exec(f"kb.release({insert})")
                sleep(self.data.work_settings['s_key_pause'])  # Пауза между нажатием клавиш клавиатуры

        else:
            # печатает используя костыли
            # с помощью tkinter копируем в буфер обмена, а потом Ctrl+v
            try:
                mem = self.root.clipboard_get()
            except:
                mem = ''

            # Функция работает для Windows, но для Linux русские буквы не работают
            # определить операционную систему и реализовать вывод русского текста в Linux
            if system.os == 'Windows':
                # Для Windows
                kb.type(val[0])
            else:
                # Вывод русского текста в Linux
                try:
                    mem = self.root.clipboard_get()
                    self.root.clipboard_clear()
                    self.root.clipboard_append(val[0])
                except:
                    mem = ''
                kb.press(Key.ctrl)
                kb.press('v')
                kb.release('v')
                kb.release(Key.ctrl)
                sleep(0.2)  # Без паузы видимо успевает очистить раньше, чем вставить
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(mem)
                except:
                    pass
                self.root.update()

