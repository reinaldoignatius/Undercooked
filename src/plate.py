class Plate():
    def __init__(self, id):
        self.id = id
        self.contents = []
        self.is_dirty = False
    
    def print(self):
        print(self.id, end='')
    