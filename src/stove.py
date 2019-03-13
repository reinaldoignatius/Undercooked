from table import Table
from cookable_container import CookableContainer
import constants

class Stove(Table):
    def __init__(self, x, y):
        super().__init__(x, y)

    def put_on_chef_held_item(self, chef):
        if self.content:
            self.content.put_on_chef_held_item(chef)
        elif isinstance(chef.held_item, CookableContainer):
            self.content = chef.held_item
            self.content.move_to_new_position(x=self.x, y=self.y)
            chef.held_item = None
    
    def cook(self):
        if self.content:
            if self.content.contents:
                if self.content.progress < constants.COOK_TICKS:
                    self.content.progress += 1
                    if self.content.progress >= constants.COOK_TICKS:
                        for ingredient in self.content.contents:
                            ingredient.processes_done.append(constants.PROCESS_COOKED)
                        self.content.is_cooked = True

    def print_static(self):
        print('O', end='')