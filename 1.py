import tkinter as tk

class ModalWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.result = tk.StringVar()  # Создаем переменную для хранения результата
        self.button = tk.Button(self, text="Generate exception", command=self.raise_exception)
        self.button.pack(padx=20, pady=20)

    def raise_exception(self):
        try:
            # Генерируем исключение
            raise Exception("Something went wrong")

        except Exception as e:
            self.result.set(str(e))  # Сохраняем текст ошибки в переменную
            self.destroy()  # Закрываем модальное окно


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.error_text = tk.Text(self, fg="red")
        self.error_text.pack(padx=20, pady=20)

        self.button = tk.Button(self, text="Open Modal", command=self.open_modal)
        self.button.pack(padx=20, pady=20)

    def open_modal(self):
        modal_window = ModalWindow(self)
        modal_window.grab_set()  # Блокируем основное окно
        self.wait_window(modal_window)  # Ожидаем закрытия модального окна

        error_message = modal_window.result.get()  # Получаем текст ошибки из переменной модального окна
        if error_message:
            self.error_text.insert("end", error_message + "\n")  # Выводим текст ошибки на главном окне

        self.focus_set()  # Фокус на главном окне

if __name__ == "__main__":
    app = Application()
    app.mainloop()