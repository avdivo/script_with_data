import numpy as np

def fill(matrix, x, y):
    """ Обход точек и формирование списка смещения каждой точки от заданной """
    start_x, start_y = x, y
    out = []
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if matrix[x][y] == 1:
            matrix[x][y] = 2
            out.append((x - start_x, y - start_y))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == dy == 0:
                        continue
                    new_x = x + dx
                    new_y = y + dy
                    if 0 <= new_x < matrix.shape[0] and 0 <= new_y < matrix.shape[1]:
                        stack.append((new_x, new_y))
    return out

# Начальный рисунок
matrix = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0]

])

# Найти координаты верхней левой точки объекта в матрице
for x in range(matrix.shape[0]):
    for y in range(matrix.shape[1]):
        if matrix[x][y] == 1:
            break
    else:
        continue
    break


offset = fill(matrix, x, y)  # Список смещений точек от начальной
print(offset)  # Как выглядит список смещений

# Восстановить рисунок из списка смещений в матрице размера 20х20
# со смещением начальной точки 5, 5

matrix = np.zeros((20, 20), dtype=int)
x, y = 5, 5
for dx, dy in offset:
    matrix[x + dx][y + dy] = 1

print(matrix)
