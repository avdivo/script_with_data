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


# Настройки в settings.py

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


def save_image(x_point: int, y_point: int) -> str:
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


def pattern_search(name_template: str, x_point: int = 0, y_point: int = 0) -> tuple:
    """ Подтверждение присутствия нужной кнопки в указанных координатах или поиск ее на экране

    Принимает в качестве первого аргумента имя шаблона (изображения кнопки или ее части),
    которое ищет по пути в константе PATH. Второй и третий аргументы - координаты на экране
    где должна присутствовать кнопка.
    В зависимости от настроек может повторять поиск с задержкой в секунду нужное количество раз,
    не выполнять поиск вообще или искать только в координатах или только на всем экране.
    В случае, если кнопка не найдена, поднимается исключение "Элемент не найден". Иначе
    возвращаются координаты (x, y в tuple) куда нужно совершить клик.

    """
    if not name_template:
        # Если нет изображения элемента то проверка отменяется
        return (x_point, y_point)

    # Получение шаблона
    if not os.path.exists(os.path.join(settings.path_to_elements, name_template)):
        raise TemplateNotFoundError('Шаблон с таким именем не найден.')
    template = cv2.imread(os.path.join(settings.path_to_elements, name_template), 0)

    # Сохранить ширину в переменной w и высоту в переменной h шаблона
    w, h = template.shape

    threshold = 0.8  # Порог
    method = cv2.TM_CCOEFF_NORMED  # Метод расчёта корреляции между изображениями
    repeat = settings.s_search_attempt  # Сколько раз проверить наличие элемента с паузой 1 сек.
    while repeat and settings.s_confirm_element:
        # Проверка включена и попытки заданы.
        # Вычисляем координаты квадрата для скриншота
        x_reg = x_point - settings.region_for_search // 2
        y_reg = y_point - settings.region_for_search // 2

        # Делаем скриншот нужного квадрата
        image = screenshot(x_reg, y_reg, settings.region_for_search - 1)

        # Перевод изображения в оттенки серого
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if compare_2_images(template, gray_img):
            # Элемент присутствует в этом месте, подтверждаем координаты
            return (x_point, y_point)

        repeat -= 1
        if repeat:
            # После последнего поиска или если он единственный - пауза не нужна
            sleep(1)

    if not settings.s_full_screen_search:
        raise ElementNotFound('Элемент не найден в указанной области. Поиск по всему экрану отключен.')

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
        raise ElementNotFound('Указанный элемент на экране не найден.')
