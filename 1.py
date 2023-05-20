from tkinter import *

root = Tk()
root.geometry("200x200")

# Создаем переменную, которую будем изменять при нажатии кнопок
result = StringVar()

# Функция, которая будет запускать процесс и ждать ответа
def long_running_function():
    # Тут запускается процесс, который ждет нажатия кнопок
    # И когда кнопка будет нажата, он устанавливает значение переменной
    result.set("Button 1 pressed") # здесь нужно установить значение в соответствии с нажатой кнопкой

# Создаем кнопки и добавляем им обработчики
button1 = Button(root, text="Button 1", command=lambda: result.set("Button 1 pressed"))
button1.pack()

button2 = Button(root, text="Button 2", command=lambda: result.set("Button 2 pressed"))
button2.pack()

# Запускаем функцию и ждем изменения переменной
long_running_function()
result.trace("w", lambda name, index, mode, sv=result: root.quit())
root.wait_variable(result)

# После выхода из цикла ожидания можно использовать значение переменной
print(result.get())

root.mainloop()