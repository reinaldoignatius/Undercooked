from container import Container
from bowl import Bowl
from plate import Plate

class CookableContainer(Container):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.is_cooked = False
    
    def put_on_chef_held_item(self, chef):
        if not self.is_cooked:
            super().put_on_chef_held_item(chef)
            if isinstance(chef.held_item, CookableContainer):
                new_progress = chef.held_item.progress
                chef.held_item.progress = self.progress
                self.progress = new_progress

                new_cooked = chef.held_item.is_cooked
                chef.held_item.is_cooked = self.is_cooked
                self.is_cooked = new_cooked
            elif isinstance(chef.held_item, Bowl):
                chef.held_item.progress = 0
                chef.held_item.is_mixed = False
        else:
            if isinstance(chef.held_item, Plate):
                while self.contents:
                    chef.held_item.contents.append(self.contents.pop())
                self.progress = 0
                self.is_cooked = False