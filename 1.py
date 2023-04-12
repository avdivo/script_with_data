import json
import tkinter as tk
from tkinter import filedialog

# функция для сохранения словаря в файл
def save_dict():
    # исходный словарь
    my_dict = {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": "subvalue2"
        }
    }

    # открываем диалоговое окно для выбора файла
    file_path = filedialog.asksaveasfilename(initialdir="/", title="Save File",
                                             filetypes=(("JSON files", "*.json"),))

    # сохраняем в файл
    with open(file_path, "w") as f:
        json.dump(my_dict, f)

# функция для чтения словаря из файла
def load_dict():
    # открываем диалоговое окно для выбора файла
    file_path = filedialog.askopenfilename(initialdir="/", title="Open File",
                                           filetypes=(("JSON files", "*.json"),))

    # читаем из файла
    with open(file_path, "r") as f:
        loaded_dict = json.load(f)

    # выводим загруженный словарь в консоль
    print(loaded_dict)

# создаем окно tkinter
root = tk.Tk()

# добавляем кнопку для сохранения словаря
save_button = tk.Button(root, text="Save Dictionary", command=save_dict)
save_button.pack()

# добавляем кнопку для чтения словаря
load_button = tk.Button(root, text="Load Dictionary", command=load_dict)
load_button.pack()

# запускаем главный цикл окна tkinter
root.mainloop()