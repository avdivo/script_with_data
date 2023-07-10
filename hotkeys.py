# ---------------------------------------------------------------------------
# Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций
# Методы для преобразования названий комбинаций в горячие клавиши и обратно
# ---------------------------------------------------------------------------


class Hotkeys:
    """Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций"""

    def __init__(self):
        self.hotkeys = {'stop': ['KeyDown-ctrl', 'KeyUp-ctrl', 'KeyDown-ctrl', 'KeyUp-ctrl'],
                        'screenshot Win': ['KeyDown-ctrl_r', 'KeyUp-ctrl_r', 'KeyDown-ctrl_r', 'KeyUp-ctrl_r'],
                        'mouse_position Win': ['KeyDown-ctrl_r', 'KeyUp-ctrl_r'],
                        'copy': ['KeyDown-ctrl', 'KeyDown-c', 'KeyUp-c', 'KeyUp-ctrl'],
                        'copy rus': ['KeyDown-ctrl', 'KeyDown-с', 'KeyUp-с', 'KeyUp-ctrl'],
                        'cut': ['KeyDown-ctrl', 'KeyDown-x', 'KeyUp-x', 'KeyUp-ctrl'],
                        'cut rus': ['KeyDown-ctrl', 'KeyDown-ч', 'KeyUp-ч', 'KeyUp-ctrl'],
                        'paste': ['KeyDown-ctrl', 'KeyDown-v', 'KeyUp-v', 'KeyUp-ctrl'],
                        'paste rus': ['KeyDown-ctrl', 'KeyDown-м', 'KeyUp-м', 'KeyUp-ctrl'],
                        'select': ['KeyDown-ctrl', 'KeyDown-a', 'KeyUp-a', 'KeyUp-ctrl'],
                        'select rus': ['KeyDown-ctrl', 'KeyDown-ф', 'KeyUp-ф', 'KeyUp-ctrl'],
                        'language_change': ['KeyDown-alt', 'KeyDown-shift', 'KeyUp-shift', 'KeyUp-alt'],
                        'new_tab': ['KeyDown-ctrl', 'KeyDown-t', 'KeyUp-t', 'KeyUp-ctrl'],
                        'new_tab rus': ['KeyDown-ctrl', 'KeyDown-е', 'KeyUp-е', 'KeyUp-ctrl'],
                        'next_tab': ['KeyDown-ctrl', 'KeyDown-tab', 'KeyUp-tab', 'KeyUp-ctrl'],
                        'next_window': ['KeyDown-alt', 'KeyDown-tab', 'KeyUp-tab', 'KeyUp-alt'],
                        'roll_up_windows Ubuntu': ['KeyDown-ctrl', 'KeyDown-alt', 'KeyDown-d',
                                                   'KeyUp-d', 'KeyUp-alt', 'KeyUp-ctrl'],
                        'roll_up_windows Win': ['KeyDown-cmd', 'KeyDown-d', 'KeyUp-d', 'KeyUp-cmd'],
                        'roll_up_windows WinRus': ['KeyDown-cmd', 'KeyDown-в', 'KeyUp-в', 'KeyUp-cmd']}

        self.hotkeys_actual = []  # Названия комбинаций, которые удовлетворяют текущей последовательности событий

    def search_hotkey(self, cmd, val, position):
        """Метод для поиска совпадения очередного события с комбинацией событий

        Принимает название команды (нажата/отпущения клавиши), название клавиши, номер события в комбинации.
        Вернет название комбинации, если событие завершило комбинацию, 'next' - комбинация совпадает, но не завершена,
        None - нет комбинаций с таким событием в этой позиции.

        Если список актуальных комбинаций пуст, копируем в него все комбинации, или оставляем как есть.
        Создаем пустой список для перебора и меняем его со списком актуальных комбинаций.
        Перебираем новый список, добавляя в список актуальных комбинаций (он пуст после обмена) только те,
        которые имеют следующее событие такое, какое пришло.
        Полученный список проверяем и в зависимости от этого возвращаем результат.
        """
        if not self.hotkeys_actual:
            self.hotkeys_actual = self.hotkeys.keys()
        iterator = []
        iterator, self.hotkeys_actual = self.hotkeys_actual, iterator

        for hotkey in iterator:
            # Создаем список комбинаций, которые имеют следующее событие такое, какое пришло
            if self.hotkeys[hotkey][position-1] == f"{cmd}-{val[0]}":
                self.hotkeys_actual.append(hotkey)

        # На данный момент у нас список комбинаций, последовательность событий в которых такая-же,
        # как последние пришедшие, среди них может быть завершенные и незавершенные комбинации.
        # Если есть завершенная, вернем ее название и удалим ее из списка актуальных комбинаций.
        # Если нет завершенных, но список не пуст, то вернем 'next'.
        # Если список пуст, то вернем None.

        for hotkey in self.hotkeys_actual:
            if position == len(self.hotkeys[hotkey]):
                self.hotkeys_actual.remove(hotkey)
                return hotkey

        if self.hotkeys_actual:
            return 'next'

        return None

    def get_hotkey(self, hotkey):
        """Метод для получения комбинации событий по названию комбинации
        """
        out = []
        for i in self.hotkeys[hotkey]:
            cmd, val = i.split('-')
            out.append({'cmd': cmd, 'val': [val], 'des': ''})  # Возвращаем список готовых словарей для создания команд
        return out


hotkeys = Hotkeys()
