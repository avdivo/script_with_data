# Генератор QR кода. Вводим строку, получаем QR код
# pip install qrcode
# pip install pillow
# Описать действие каждой строки кода
# Переписать код с использованием классов


import qrcode
import os
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


class QrCode:
    def __init__(self):
        # Создаем окно
        self.root = tk.Tk()
        self.root.title('QR code generator')
        self.root.geometry('400x400')
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text='Введите текст для генерации QR кода')
        self.label.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()

        self.button = tk.Button(self.root, text='Сгенерировать QR код', command=self.generate_qr_code)
        self.button.pack()

        self.root.mainloop()

    def generate_qr_code(self):
        """" Генерируем QR код """
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )

        data = self.entry.get()

        if data == '':
            # Если данные не введены, то выводим сообщение об ошибке
            messagebox.showerror('Ошибка', 'Введите данные для генерации QR кода')
        else:
            # Добавляем данные
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            img.save('qr_code.png')

            # Открываем окно с QR кодом
            self.new_window = tk.Toplevel(self.root)
            self.new_window.title('QR code')
            self.new_window.geometry('300x300')
            self.new_window.resizable(False, False)

            self.label = tk.Label(self.new_window, text='QR code')
            self.label.pack()

            self.image = Image.open('qr_code.png')
            self.image = self.image.resize((250, 250), Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(self.image)

            self.label_image = tk.Label(self.new_window, image=self.photo)
            self.label_image.pack()

            self.button = tk.Button(self.new_window, text='Закрыть', command=self.new_window.destroy)
            self.button.pack()

            os.remove('qr_code.png')


if __name__ == '__main__':
    QrCode()

