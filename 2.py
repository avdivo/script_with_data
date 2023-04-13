import json

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __json__(self):
        return {'name': self.name, 'age': self.age}

person = Person('John', 30)
json_data = json.dumps(person, default=lambda o: o.__json__())
print(json_data)