# ---------------------------------------------------------------------------
# Тип данных для классов ввода данных.
# При вводе int или str понятно какой виджет использовать и как настроить.
# Тут типы данных для случаев, когда нужна комбинация виджетов для приема информации.
# Или когда тип данных тот-же str, но при этом нужно использовать не поле ввода, а список.
# А поскольку программа ориентируется по типам данных, какие виджеты применять, нужны новые типы.
# ---------------------------------------------------------------------------

class llist:
    """ Тип данных представляет выпадающий список label list для меток в скрипте и имен блоков

    Класс хранит актуальный список данных об именах для перехода, экземпляры класса
    пользуются этим списком и помнят выбранный элемент.
    При всех операциях экземпляры класса сверяются со списком, для уточнения актуальности своих данных.

     """

    labels = []

    def __init__(self, label=''):
        if label and label not in self.labels:
            raise ValueError(f'Неверное значение. Mетка "{label}" отсутствует в списке.')
        self.label = label

    def __str__(self):
        return self.label

    def isthere(self):
        """ Уточняет свою актуальность """
        return self.label in self.labels

    @classmethod
    def set_list(cls, l):
        """ Записываем метки в список класса """
        cls.labels = l


class eres:
    """ Тип данных определяющий реакцию на ошибку

    Могут быть 3 типа реакции на ошибку:
    stop - остановит скрипт
    ignore - проигнорировать ошибку
    run - запустить скрипт с указанной метки
    Класс создает объект из строкового представления: stop: / ignore: / run:name
    В первых 2 случаях второй аргумент не нужен, в третьем указывает метку в скрипте

    """

    react_list = ['stop', 'ignore', 'run']
    def __new__(cls, arg):
        """ Позволяем принимать аргументы своего типа, при этом не создавая новый объект """
        if isinstance(arg, cls):
            return arg
        else:
            return super().__new__(cls)

    def __init__(self, string):
        if isinstance(string, str):
            # Принимает только данные типа str для создания объекта
            if ':' not in string:
                raise ValueError('Неверное значение. Нет разделителя ":".')
            react, label = string.split(':')
            if react not in self.react_list:
                raise ValueError('Неверное значение. Принимаются: stop/ignore/run.')
            self._label = llist(label)  # Тип данных - метки
            self._react = react
        elif not isinstance(string, eres):
            raise ValueError(f'Тип данных "{type(string).__name__}" не поддерживается.')

    def __str__(self):
        return f'{self._react}:{self._label}'

    @property
    def react(self):
        return self._react

    @property
    def label(self):
        return self._label

    @react.setter
    def react(self, react: str):
        if react not in self.react_list:
            raise ValueError('Неверное значение. Принимаются: stop/ignore/run.')
        self._react = react
        self.label = ''  # Тип данных - метки

    @label.setter
    def label(self, label: llist):
        self._label = label  # Тип данных - метки


llist.set_list(['name 1', 'name 2', 'name 3', 'name 4', 'name 5 или'])
# a = llist()
# print(a)
