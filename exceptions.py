# Исключения
class Error(Exception):
    """Базовый класс для других исключений"""
    pass


class TemplateNotFoundError(Error):
    """Шаблон с таким именем не найден в папке с изображениями элементов"""
    pass


class ElementNotFound(Error):
    """Элемент не найден в заданной области или на всем экране"""
    pass


class DataError(Error):
    """ Ошибка данных, не найдено поле в таблице или нет больше данных в столбце """
    pass


class NoCommandOrStop(Error):
    """ Нет команд для выполнения или команда Стоп """
    pass


class LabelAlreadyExists(Error):
    """ При добавлении имени метки или блока, если такое имя уже существует """
    pass


class LoadError(Error):
    """ Ошибки при чтении и преобразовании данных """
    pass

