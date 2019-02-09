from moveable_object import MoveableObject

class Ingredient(MoveableObject):
    def __init__(self, name, x, y):
        super().__init__(x, y)
        self.name = name
        self.processes_done = []
        self.progress = 0

    def print(self):
        print(self.name, end="")