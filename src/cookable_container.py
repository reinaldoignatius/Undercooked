from container import Container
from plate import Plate

class CookableContainer(Container):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.cooked = False
    
    def put_on_chef_held_item(self, chef):
        if not self.cooked:
            super().put_on_chef_held_item(chef)
            if isinstance(chef.held_item, CookableContainer):
                new_cooked = chef.held_item.cooked
                chef.held_item.cooked = self.cooked
                self.cooked = new_cooked
        else:
            if isinstance(chef.held_item, Plate):
                while self.contents:
                    chef.held_item.contents.append(self.contents.pop())