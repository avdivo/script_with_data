# Тип данных для хранения переменной Реакция на ошибку
# Могут быть 3 типа реакции на ошибку:
# stop - остановит скрипт
# ignore - проигнорировать ошибку
# run - запустить скрипт с указанной метки
# Класс создает объект из строкового представления: stop: / ignore: / run:name
# и возвращает в таком виде

# Исключения

class eres:
    """ Тип данных определяющий реакцию на ошибку """
    react_list = ['stop', 'ignore', 'run']

    def __init__(self, sting: str):
        react, label = sting.split(':')
        if react not in self.react_list:
            raise ValueError('Неверное значение. Принимаются: stop/ignore/run.')
        self.react = react
        self.label = label

    def __str__(self):
        return f'{self.react}:{self.label}'
