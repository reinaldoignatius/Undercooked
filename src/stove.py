from cookable_container import CookableContainer
import constants

class Stove():
    def __init__(self):
        self.content = None

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, CookableContainer):
            self.content = chef.held_item
            chef.held_item = None
    
    def cook(self):
        if self.content:
            if self.content.contents:
                if self.content.progress < constants.COOK_TICKS:
                    self.content.progress += 1
                else:
                    if not self.content.cooked:
                        for ingredient in self.content.contents:
                            ingredient.processes_done.append(constants.PROCESS_COOKED)
                        self.content.cooked = True

    def print_static(self):
        print('O', end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()