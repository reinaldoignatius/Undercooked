from moveable_object import MoveableObject

class Plate(MoveableObject):
    def __init__(self, id, x, y):
        super().__init__(x, y)
        self.id = id
        self.contents = []
        self.is_dirty = False
    
    def print(self):
        print(self.id, end='')
    