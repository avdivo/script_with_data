import barcode
from barcode.writer import ImageWriter

ean = barcode.get('ean8', '09010000', writer=ImageWriter())
filename = ean.save('ean13_barcode')


class one:
    def __init__(self, n):
        self.a = {1:n}

def ch():
    global d
    d = one(2)

d = one(1)
print(d.a[1])
ch()
print(d.a[1])
