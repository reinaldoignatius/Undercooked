from plate import Plate

class GarbageBin():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Plate):
            del chef.held_item.contents[:] 

    def print_static(self):
        print('G', end='')

    def print(self):
        self.print_static()
        