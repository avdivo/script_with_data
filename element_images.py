"""
Сохранение изображения кнопки/иконки (элемента) и подтверждение его присутствия

$ sudo apt-get install scrot
$ sudo apt-get install python-tk python-dev
$ sudo apt-get install python3-tk python3-dev
$ workon your_virtualenv
$ pip install pillow imutils
$ pip install python3_xlib python-xlib
$ pip install pyautogui
https://pyimagesearch.com/2018/01/01/taking-screenshots-with-opencv-and-python/

"""

import os, sys
import datetime
import numpy as np
import pyautogui
import cv2
from time import sleep

from exceptions import TemplateNotFoundError, ElementNotFound
from settings import settings


def screenshot(x_reg: int = 0, y_reg: int = 0, region: int = 0):
    """ Скриншот заданного квадрата или всего экрана

    В качестве аргументов принимает координаты верхней левой точки квадрата и его стороны.
    Если сторона на задана (равна 0) то делает скриншот всего экрана

    """
    if region:
        image = pyautogui.screenshot(region=(x_reg, y_reg, region, region))  # x, y, x+n, y+n (с верхнего левого угла)
    else:
        image = pyautogui.screenshot()
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def generate_image_name() -> str:
    """ Генерация имени нового изображения элемента

    Возвращает имя нового изображения элемента в формате:
    <имя проекта>_<дата и время>.png

    """
    return f'{settings.basename}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'


def compare_2_images(small, big):
    """ Поиск маленького изображения в большом

    Возвращает True или False.
    Поиск производится стандартным методом openCV, однако перед этим маленькое изображение проверяется на одноцветность
    и если оно одноцветное, то большое изображение обрезается до размера маленького и если оно тоже одноцветное и имеет
    тот же цвет, что и маленькое - они признаются одинаковыми.
    """
    threshold = 0.85 # Порог
    method = cv2.TM_CCOEFF_NORMED  # Метод расчёта корреляции между изображениями

    if np.all(small == small[0,0]):
        # Все пиксели маленького изображения имеют одинаковый цвет
        # Получение размеров маленького изображения
        small_height, small_width = small.shape

        # Получение размеров большого изображения
        large_height, large_width = big.shape

        # Вычисление размеров обрезки
        crop_height = (large_height - small_height) // 2
        crop_width = (large_width - small_width) // 2

        # Обрезка большого изображения
        cropped_image = big[crop_height:large_height - crop_height, crop_width:large_width - crop_width]

        if np.all(cropped_image == small[0,0]):
            # Все пиксели обрезанного большого изображения имеют такой же цвет, как и маленькое изображение
            return True
        else:
            return False

    res = cv2.matchTemplate(big, small, method)
    # Ищем координаты совпадающего местоположения в массиве numpy
    loc = np.where(res >= threshold)
    if any(loc[-1]):
        return True

    return False

#  h_image(x_point: int,    y_point: i
    """ Сохранение изображения кнопки/иконки (элемента) если он еще не сохранен

    Функция принимает в качестве аргументов координаты точки на экране.
    Предполагается, что эта точка расположена на элементе, изображение которого нужно сохранить или найти.
    Точка принимается как центр квадрата со стороной settings.first_region внутри которого должен находиться
    элемент (кнопка, иконка...). Проверяются сохраненные элементы. Если такого нет квадрат обрезается
    до размера стороны settings.region и сохраняется. Если есть, возвращается его имя.
    Возвращает имя нового или существующего изображения.

    """
    # Вычисляем координаты квадрата для скриншота
    x_reg = x_point - settings.first_region // 2
    y_reg = y_point - settings.first_region // 2

    # Делаем скриншот нужного квадрата
    image = screenshot(x_reg, y_reg, settings.first_region-1)

    # Перевод изображения в оттенки серого
    grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Перебор сохраненных элементов, был ли ранее такой сохранен
    for name in os.listdir(settings.path_to_elements):
        template = cv2.imread(os.path.join(settings.path_to_elements, name), 0)
        if compare_2_images(template, grayimg):
            # Сравнение изображений. Такое изображение уже сохранено
            return name

    # Если выбранный элемент ранее не был сохранен, сохраним его
    # Обрезаем квадрат
    a = (settings.first_region - settings.region) // 2
    image = image[a: a + settings.region, a: a + settings.region]

    # Координаты точки на новом регионе
    x_point = x_point - x_reg - a
    y_point = y_point - y_reg - a

    # cv2.imshow('', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # Перевод изображения в оттенки серого
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply binary thresholding
    # Применение бинарного порога к изображению
    ret, thresh = cv2.threshold(gray_img, 40, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("in_memory_to_disk.png", thresh)

    # Нахождение контуров
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Ищем контур, которому принадлежит np.array(image)точка
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if x_point >= x and x_point <= x+w and y_point >= y and y_point <= y+h:
            # Координаты точки принадлежат прямоугольнику описанному вокруг контура
            break
    else:
        # Проверены все контуры, точка не принадлежит ни одному
        # Выбираем весь квадрат
        x = y = 0
        w = h = settings.region

    # Сохраняем изображение найденного элемента
    ROI = image[y:y+h, x:x+w]
    filename = generate_image_name()  # e.g. 'mylogfile_120508_171442'
    cv2.imwrite(os.path.join(settings.path_to_elements, filename), ROI)

    return filename

def invert_result(func):
    """ Декоратор, который интерпретирует возврат функции поиска изображения в соответствии с настройками """
    def wrapper(*args):
        condition = False  # Вернуть ошибку (выполнить действие) при ошибке, как предусмотрено изначально
        if args[3]:
            # Если используются локальные настройки то используем их для интерпретации результата
            condition = False if args[8] == 'Не найдено' else True
        try:
            result = func(*args)
            if condition:
                # Получен результат, но если найдено нужно вернуть ошибку
                raise ElementNotFound('Изображение найдено.')
            return result
        except (TemplateNotFoundError, ElementNotFound):
            if condition:
                # Получена ошибка, но при ошибке нужно вернуть результат,
                # результат - это подтверждение координат
                return (args[0], args[1])
            raise

    return wrapper

@invert_result
def pattern_search(*args) -> tuple:
    """ Подтверждение присутствия нужного изображения в указанных координатах или поиск его на экране

    Принимает параметры:
    0 - координата x, 1 - координата y, 2 - имя изображения, 3 - использовать локальные настройки (True/False),
    4 - включить локальную проверку (True/False), 5 - зона локальной проверки (сторона квадрата, int >= 48),
    6 - сколько секунд ждать, после 1 попытки (int, 0 не проверять), 7 - искать на всем экране (True/False),
    8 - условие выполнения действия: ('Найдено'/'Не найдено'), 9 - Действие (eres),
    10 - сообщение, в случае выполнения действия (str).

    Имя изображения (кнопки или ее части), ищет в папке изображений проекта. x, y - координаты на экране
    где должна присутствовать кнопка.
    Если 3 аргумент True используются настройки из args, иначе общие для программы.
    Локальная проверка - это поиск шаблона изображения в квадрате со стороной (в аргументе 5) и центром x, y.
    В случае неудачи поиск может повторяться через 1 секунду еще столько раз, сколько указано в (аргументе 6) - 1.
    Если изображение не появилось, (не найдено) может пройти поиск по всему экрану (аргумент 7).
    Результат поиска интерпретируется в соответствии с арг. 8 и в зависимости от него вернуть координаты или ошибку.
    В случае использования глобальных настроек вернет ошибку если изображение не найдено.
    Не производит поиск и сообщает результат сразу, если пришло пустое имя файла или количество попыток 0.
    Вернет координаты центра найденного элемента (если не найден, вернет вошедшие координаты) или исключение.
    """
    x_point, y_point, name_template = args[:3]  # Получаем координаты и имя изображения
    local_check = args[4] if args[3] else settings.s_confirm_element  # Включить ли локальную проверку
    local_check_size = args[5] if args[3] else settings.s_local_check_size  # Размер квадрата локальной проверки
    repeat = args[6] if args[3] else settings.s_search_attempt  # Сколько раз проверить наличие элемента с паузой 1 сек.
    full_screen = args[7] if args[3] else settings.s_full_screen_search  # Искать на всем экране

    if not name_template or repeat == 0:
        # Если нет изображения элемента или попыток 0, то проверка отменяется, подтверждаем наличие элемента
        return (x_point, y_point)

    # Получение шаблона
    if not os.path.exists(os.path.join(settings.path_to_elements, name_template)):
        raise TemplateNotFoundError('Шаблон с таким именем не найден.')
    template = cv2.imread(os.path.join(settings.path_to_elements, name_template), 0)

    # Сохранить ширину в переменной w и высоту в переменной h шаблона
    w, h = template.shape

    threshold = 0.8  # Порог
    method = cv2.TM_CCOEFF_NORMED  # Метод расчёта корреляции между изображениями
    # Вычисляем координаты квадрата для скриншота
    x_reg = x_point - local_check_size // 2
    y_reg = y_point - local_check_size // 2

    while repeat and local_check:
        # Проверка включена и попытки еще есть.
        if not settings.script_started:
            # Если скрипт остановлен, то прерываем проверку
            raise ElementNotFound('Скрипт остановлен.')

        # Делаем скриншот нужного квадрата
        image = screenshot(x_reg, y_reg, local_check_size)

        # Перевод изображения в оттенки серого
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if compare_2_images(template, gray_img):
            # Элемент присутствует в этом месте, подтверждаем координаты
            return (x_point, y_point)

        repeat -= 1
        if repeat:
            # После последнего поиска или если он единственный - пауза не нужна
            sleep(1)

    if not full_screen:
        raise ElementNotFound('Изображение не найдено в указанной области. Поиск по всему экрану отключен.')
    # Если поиск шаблона в заданных координатах не принес результата any(loc[-1] будет пустым.
    # Поиск элемента на всем экране

    # Делаем скриншот экрана
    image = screenshot()

    # Перевод изображения в оттенки серого
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Операция сопоставления
    res = cv2.matchTemplate(gray_img, template, method)

    # Ищем координаты совпадающего местоположения в массиве numpy
    loc = np.where(res >= threshold)
    xy = list(zip(*loc[::-1]))[-1] if list(zip(*loc[::-1])) else []

    # Проверка, найден ли шаблон на всем экране
    if xy:
        # Вернуть координаты центра нового положения элемента
        return (xy[0] + w / 2, xy[1] + h / 2)

    else:
        # Заданный шаблон на экране не найден
        raise ElementNotFound('Указанное изображение на экране не найдено.')
