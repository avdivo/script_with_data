# Есть  13 номеров 1-13.
# Напиши все возможные комбинации групп по 3 номера,
# чтобы не было 2 групп в которых одинаковые номера

import itertools

# 1. Создаем список из 13 номеров
names = ['Елена', 'Ира', 'Ксюша', 'Саша', 'Юля', 'Юльчатай', 'Надя', 'Оля', 'Катя', 'Ольга', 'Эля', 'Сауле', 'Настя']
numbers = list(range(1, 14))
s = 0

for j in range(2, 14):
    # 2. Создаем список из всех возможных комбинаций по 3 номера
    combinations = list(itertools.combinations(names, j))

    for i, comb in enumerate(combinations):
        print(i+1, comb)
        pass
    s += i+1
    print(i+1)

print(s)