import constants

class Chef():
    def __init__(self, world, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.held_item = None

    def move_to_new_position(self, x, y):
        self.x = x
        self.y = y
        if self.held_item:
            self.held_item.move_to_new_position(x, y)

    def pick_up(self, holdableObject):
        self.held_item = holdableObject
        self.held_item.x = self.x
        self.held_item.y = self.y

    def print_static(self):
        print(self.id, end='')

    def print(self):
        self.print_static()

