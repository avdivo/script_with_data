# ---------------------------------------------------------------------------
# Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций
# Методы для преобразования названий комбинаций в горячие клавиши и обратно
# ---------------------------------------------------------------------------


class Hotkeys:
    """Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций"""

    def __init__(self):
        self.hotkeys = {'stop': ['KeyDown_ctrl', 'KeyUp_ctrl', 'KeyDown_ctrl', 'KeyUp_ctrl'],
                        'screenshot': ['KeyDown_alt', 'KeyUp_alt', 'KeyDown_alt', 'KeyUp_alt'],
                        'copy': ['KeyDown_ctrl', 'KeyDown_c', 'KeyUp_c', 'KeyUp_ctrl'],}

        self.hotkeys_actual = set()  # Сет для хранения названий комбинаций, которые удовлетворяют текущему набору событий

    def search_hotkey(self, cmd, val, position):
        """Метод для поиска совпадения очередного события с комбинацией событий

        Принимает название команды (нажата/отпущения клавиши), название клавиши, номер события в комбинации.
        Вернет название комбинации, если событие завершило комбинацию, 'next' - комбинация совпадает, но не завершена,
        None - нет комбинаций с таким событием в этой позиции.
        """
        current = set()
        for hotkey in self.hotkeys:
            if self.hotkeys[hotkey][position-1] == f"{cmd}_{val[0]}":
                current.add(hotkey)

        self.hotkeys_actual = self.hotkeys_actual.intersection(current) if self.hotkeys_actual else current
        if not self.hotkeys_actual:
            return None  # Если нет совпадений, то возвращаем None
        if len(self.hotkeys_actual) == 1:
            # Если совпадение только одно, то проверяем, завершена ли комбинация
            hotkey = next(iter(self.hotkeys_actual))  # Получаем название комбинации
            if position == len(self.hotkeys[hotkey]):
                # Если событие последнее в комбинации, то возвращаем название комбинации
                self.hotkeys_actual.clear()
                return hotkey

        return 'next'  # Одна или более комбинаций совпадают, но не завершены

    def get_hotkey(self, hotkey):
        """Метод для получения комбинации событий по названию комбинации

        """
        out = []
        for i in self.hotkeys[hotkey]:
            cmd, val = i.split('_')
            out.append({'cmd': cmd, 'val': [val], 'des': ''})  # Возвращаем список готовых словарей для создания команд
        return out


hotkeys = Hotkeys()
