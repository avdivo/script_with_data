# Настройки программы
# Объект с настройками создается при импорте
# и может существовать только в одном экземпляре

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

        # Запоминаем имена и типы атрибутов для их приведения при загрузке из файла
        self.types_attrs = {var: type(val) for var, val in self.__dict__.items()}

    # def get_seting


s = Settings()
print(s.types_attrs)