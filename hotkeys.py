# ---------------------------------------------------------------------------
# Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций
# Методы для преобразования названий комбинаций в горячие клавиши и обратно
# ---------------------------------------------------------------------------


class Hotkeys:
    """Класс для настройки горячих клавиш и сопоставления их с названиями комбинаций"""

    def __init__(self):
        self.hotkeys = {'stop': ['KeyDown_ctrl', 'KeyUp_ctrl', 'KeyDown_ctrl', 'KeyUp_ctrl'],
                        'screenshot': ['KeyDown_alt', 'KeyUp_alt', 'KeyDown_alt', 'KeyUp_alt'],
                        'mouse_position': ['KeyDown_alt', 'KeyUp_alt'],
                        'copy': ['KeyDown_ctrl', 'KeyDown_c', 'KeyUp_c', 'KeyUp_ctrl'],
                        'copy_rus': ['KeyDown_ctrl', 'KeyDown_с', 'KeyUp_с', 'KeyUp_ctrl'],
                        'cut': ['KeyDown_ctrl', 'KeyDown_x', 'KeyUp_x', 'KeyUp_ctrl'],
                        'cut_rus': ['KeyDown_ctrl', 'KeyDown_ч', 'KeyUp_ч', 'KeyUp_ctrl'],
                        'paste': ['KeyDown_ctrl', 'KeyDown_v', 'KeyUp_v', 'KeyUp_ctrl'],
                        'paste_rus': ['KeyDown_ctrl', 'KeyDown_м', 'KeyUp_м', 'KeyUp_ctrl'],
                        'select': ['KeyDown_ctrl', 'KeyDown_a', 'KeyUp_a', 'KeyUp_ctrl'],
                        'select_rus': ['KeyDown_ctrl', 'KeyDown_ф', 'KeyUp_ф', 'KeyUp_ctrl'],
                        'language_change': ['KeyDown_alt', 'KeyDown_shift', 'KeyUp_shift', 'KeyUp_alt']}

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
            if self.hotkeys[hotkey][position-1] == f"{cmd}_{val[0]}":
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
            cmd, val = i.split('_')
            out.append({'cmd': cmd, 'val': [val], 'des': ''})  # Возвращаем список готовых словарей для создания команд
        return out


hotkeys = Hotkeys()
