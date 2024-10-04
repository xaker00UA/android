class Parents:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def cal(self):
        self.res = self.age * 2

    def display(self):
        self.cal()
        print(f"Name: {self.name}, Age: {self.age}")


class Child(Parents):
    def __init__(self, name, age):
        super().__init__(name, age)

    def cal(self):
        self.res = self.age * 5
