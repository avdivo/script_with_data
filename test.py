
from time import sleep
class test:
    def __init__(self):
        self.a: int = True
        self.b: str = '1'
        print(self.__dict__)
    def t(self):
        print(test.__annotations__)

a = test()

