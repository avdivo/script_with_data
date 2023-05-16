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
import queue

from threading import Thread

from settings import settings
from define_platform import system
from element_images import save_image, pattern_search
from exceptions import TemplateNotFoundError, ElementNotFound


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
        self.esc_time = time.time()  # Время последнего нажатия клавиши esc
        self.ctrl_time = time.time()  # Время последнего нажатия клавиши ctrl
        self.delete_cmd = 0  # Сколько команд удалить после остановки записи, 1 - при остановке кнопкой, 2 - esc

        # Запись событий в программу происходит сразу, если известно,
        # что текущее событие не может быть составной частью комбинации клавиш.
        # Или произойти позже, когда стало известно, что комбинация не состоялась,
        # запишутся не записанные события, а потом то, которое нарушило комбинацию.
        # Если же комбинация состоялась, она может быть заменена на сокращенную команду.
        # Для этого используем флаг (set), который указывает, сохранять событие в программу или пока в очередь.
        # И очередь, в которой сохраняются события пока не будут записаны или удалены.
        self.save_to_program = set()  #
        self.queue_event = queue.Queue()  # Очередь событий, которые необходимо записать в программу


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
        self.listener_mouse = MouseListener(on_click=self.on_click)  # Слушатель мыши
        self.listener_mouse.start()

        # Запуск слушателя клавиатуры
        self.listener_kb = KeyboardListener(on_press=self.on_press, on_release=self.on_release)  # Слушатель клавиатуры
        self.listener_kb.start()

        self.is_listening = True  # Слушатели включены
        self.data.is_listening = True  # Дублируем в data
        self.delete_cmd = 0  # Неизвестно как будет остановлена запись

        self.pressing_keys_set.clear()  # Очищаем множество нажатых клавиш

    def reset_kb(self):
        """ Вернуть состояние клавиатуры в исходное """
        # Отпустить все клавиши
        kb.release(Key.ctrl)
        kb.release(Key.alt)
        kb.release(Key.shift)

        # Вернуть состояние клавиатуры в исходное
        kb.press(Key.esc)
        kb.release(Key.esc)

    def stop_btn(self):
        """ Обработка нажатия кнопки стоп """
        if self.data.script_started:
            # Остановка выполнения скрипта
            self.data.script_started = False
            self.reset_kb()
            logger.error('Пользователь остановил выполнение скрипта.')
            return

        if self.is_listening:
            if not self.delete_cmd:
                # Переменная имеет значение, если запись остановлена нажатием esc
                self.delete_cmd = 1  # Удалить 1 команду если остановлено кнопкой

            # Остановка записи
            self.listener_mouse.stop()
            # self.listener_mouse.join()
            self.listener_kb.stop()
            # self.listener_kb.join()
            self.is_listening = False
            self.data.is_listening = False
            settings.is_saved = False  # Изменения в проекте не сохранены
            if self.delete_cmd == 2:
                # Удалить 2 команды если остановлено esc. Для этого выделим их
                self.display_commands.tree.selection_set(self.data.queue_command[self.data.pointer_command - 1],
                                                         self.data.queue_command[self.data.pointer_command])
            self.root.after(1000, self.display_commands.delete)  # Удаляем выделенные строки
            # Сохраняем историю с задержкой для фиксации последней команды
            self.root.after(800, self.save_load.save_history)

    def single_click(self, args):
        """ Фиксация 1 клика, запускается по таймеру и отменяется, если есть клик второй """
        if self.single:
            self.single = False
            self.to_export(cmd='MouseClickLeft', val=[args[0], args[1], self.img], des='')

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
        self.data.make_command(**kwargs)  # Добавляем команду
        self.display_commands.out_commands()  # Обновляем список

    def on_click(self, *args):
        """ Клик мыши любой кнопкой"""
        if not self.is_listening:
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
        return out

    def on_press(self, key=None):
        print(key, type(key))
        """ Обработка события нажатия клавиши """
        if key == Key.esc:
            # Остановка записи или воспроизведения при нажатии esc 2 раза за 0.2 сек.
            if time.time() - self.esc_time < 0.5:
                self.esc_time = 0
                self.delete_cmd = 2  # Удалить 2 команды если остановлено esc (нажатие и отпускание)
                self.stop_btn()
                return False
            else:
                self.esc_time = time.time()

        if not self.is_listening:
            return
        if key in self.pressing_keys_set:
            # Если клавиша уже нажата, то ничего не делаем
            return
        self.pressing_keys_set.add(key)  # Добавляем нажатую клавишу в множество

        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyDown', val=[self.get_str_key(key)], des='')

    def on_release(self, key):
        if not self.is_listening:
            return

        self.pressing_keys_set.discard(key)  # Удаляем клавишу из множества
        # Отправляем на создание объекта команды и запись
        self.to_export(cmd='KeyUp', val=[self.get_str_key(key)], des='')


class Player:
    """ Воспроизведение события мыши или клавиатуры """
    data = None  # Ссылка на класс с данными о скрипте
    tracker = None  # Ссылка на класс прослушивания клавиатуры и мыши

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
            mouse.position = (val[0], val[1])  # Ставим указатель в нужную позицию

            if cmd == 'MouseClickRight':
                # Клик правой копкой мыши
                mouse.press(Btn.right)
                mouse.release(Btn.right)
            else:
                if settings.s_confirm_element or settings.s_full_screen_search:
                    # Включена проверка места клика по изображению или поиск по всему экрану
                    # Координаты будут старыми, новыми (при поиске по всему экрану), или будет исключение
                    try:
                        mouse.position = pattern_search(val[2], val[0], val[1])
                    except (TemplateNotFoundError, ElementNotFound) as err:
                        if self.data.work_settings['s_error_no_element'].react == 'ignore':
                            logger.error(f'Ошибка:\n{err}\nРеакция - продолжение выполнения скрипта.')
                        else:
                            raise (err)

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

