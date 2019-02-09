from abc import ABC

class MoveableObject(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_to_new_position(self, x, y):
        self.x = x
        self.y = y