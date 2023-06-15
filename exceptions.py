# Исключения
import time

from settings import settings


class Error(Exception):
    """Базовый класс для других исключений"""
    pass


class TemplateNotFoundError(Error):
    """Шаблон с таким именем не найден в папке с изображениями элементов"""
    def __init__(self, message):
        super().__init__(message)
        with open('log.txt', 'a') as f:
            f.write(f"Скрипт {settings.project_name}. "
            f"{time.strftime('%d.%m.%Y %H:%M')}. {message}. Строка {settings.pointer_command}\n")


class ElementNotFound(Error):
    """Элемент не найден в заданной области или на всем экране"""
    def __init__(self, message):
        super().__init__(message)
        with open('log.txt', 'a') as f:
            f.write(f"Скрипт {settings.project_name}. "
            f"{time.strftime('%d.%m.%Y %H:%M')}. {message}. Строка {settings.pointer_command}\n")


class DataError(Error):
    """ Ошибка данных, не найдено поле в таблице или нет больше данных в столбце """
    pass
    def __init__(self, message):
        super().__init__(message)
        with open('log.txt', 'a') as f:
            f.write(f"Скрипт {settings.project_name}. "
            f"{time.strftime('%d.%m.%Y %H:%M')}. {message}. Строка {settings.pointer_command}\n")


class NoCommandOrStop(Error):
    """ Нет команд для выполнения или команда Стоп """
    pass


class LabelAlreadyExists(Error):
    """ При добавлении имени метки или блока, если такое имя уже существует """
    pass


class LoadError(Error):
    """ Ошибки при чтении и преобразовании данных """
    pass

