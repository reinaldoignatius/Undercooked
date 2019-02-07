import constants

class Chef():
    def __init__(self, world, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.held_item = None

    def pick_up(self, holdableObject):
        self.held_item = holdableObject

    def print_static(self):
        print(self.id, end='')

    def print(self):
        self.print_static()

