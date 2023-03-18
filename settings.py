# Настройки программы
# Объект с настройками создается при импорте и может существовать только в одном экземпляре
# Все атрибуты объекта являются настройками, любой добавленный атрибут будет сохраняться
# в файле скрипта как настройка.
# Позволяет получать и менять отдельные настройки при прямом обращении к атрибуту объекта,
# возвращать все настройки в словаре и устанавливать их из словаря.

class Settings(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.key_pause = 0.1            # пауза между нажатием клавиш клавиатуры (после отпускания)
        self.click_pause = 0.5          # пауза после клика мыши
        self.command_pause = 0          # пауза между командами
        self.confirm_element = True     # убеждаться, что нужный элемент (кнопка, иконка ...) присутствует
        self.search_attempt = 3         # сколько раз следует повторить паузу в 1 секунду
        self.full_screen_search = True  # производить поиск элемента на всем экране
        self.error_no_element = 'stop'  # остановить выполнение скрипта при исключении 'no element'
        self.error_no_data = 'ignore'   # остановить выполнение скрипта при исключении 'no data'
        self.description = ''           # комментарий

    def get_dict_settings(self) -> dict:
        """ Возвращает все настройки в словаре """
        return {var: val for var, val in self.__dict__.items()}

    def set_settings_from_dict(self, settings_dict: dict):
        """ Перезаписывает настройки

         Принимает словарь с настройками в текстовом виде. Настройки (ключи) из словаря находятся в названиях
         атрибутов, если атрибут найден, ему присваивается новое значение из словаря, но оно приводится к
         прежнему типу атрибута. Если такого атрибута не было, создается новый, с текстовым типом.

         """
        for var, val in settings_dict.items():
            if var in self.__dict__:
                self.__dict__[var] = type(self.__dict__[var])(val)
            else:
                self.__dict__[var] = val


settings = Settings()
