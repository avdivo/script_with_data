import platform


class ThisPlatform:
    """ Класс для определения платформы и настройки горячих клавиш """
    def __init__(self):
        self.os = platform.system()
        if self.os == 'Windows':
            self.hotkeys = {'Ctrl_A': 65, 'Ctrl_C': 67, 'Ctrl_X': 88, 'Ctrl_V': 86,
                       'Ctrl_Up': 38, 'Ctrl_Down': 40}  # Windows
        else:
            self.hotkeys = {'Ctrl_A': 38, 'Ctrl_C': 54, 'Ctrl_X': 53, 'Ctrl_V': 55,
                       'Ctrl_Up': 111, 'Ctrl_Down': 116}  # Linux
        self.hotkeys_names = {'Ctrl_A': 'Ctrl+A', 'Ctrl_C': 'Ctrl+C', 'Ctrl_X': 'Ctrl+X', 'Ctrl_V': 'Ctrl+V',
                       'Ctrl_Up': 'Ctrl+Up', 'Ctrl_Down': 'Ctrl+Down'}  # Linux


system = ThisPlatform()