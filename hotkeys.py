# ---------------------------------------------------------------------------
# Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций
# Методы для преобразования названий комбинаций в горячие клавиши и обратно
# ---------------------------------------------------------------------------


class Hotkeys:
    """Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций"""

    def __init__(self):
        self.hotkeys = {'stop': ['KeyDown_esc', 'KeyUp_esc', 'KeyDown_esc', 'KeyUp_esc'],
                        'screenshot': ['KeyDown_ctrl', 'KeyUp_ctrl', 'KeyDown_ctrl', 'KeyUp_ctrl'],
                        'copy': ['KeyDown_ctrl', 'KeyDown_c', 'KeyUp_c', 'KeyUp_ctrl'],}

    def search_hotkey(self, cmd, val, position):
        """Метод для поиска совпадения очередного события с комбинацией событий

        Принимает название команды (нажата/отпущения клавиши), название клавиши, номер события в комбинации.
        Вернет название комбинации, если событие завершило комбинацию, 'next' - комбинация совпадает, но не завершена,
        None - нет комбинаций с таким событием в этой позиции.
        """
        for hotkey in self.hotkeys:
            if self.hotkeys[hotkey][position] == cmd + '_' + val:
                if position == len(self.hotkeys[hotkey]) - 1:
                    return hotkey
                else:
                    return 'next'
        return None

    def get_hotkey(self, hotkey):
        """Метод для получения комбинации событий по названию комбинации

        """
        out = []
        for i in self.hotkeys[hotkey]:
            cmd, val = i.split('_')
            out.append({'cmd': cmd, 'val': [val], 'des': ''})  # Возвращаем список готовых словарей для создания команд
        return out


hotkeys = Hotkeys()
