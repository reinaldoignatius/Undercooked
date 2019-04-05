from table import Table
from bowl import Bowl
import constants

class Mixer(Table):
    def __init__(self, x, y, world):
        super().__init__(x, y)
        self.__world = world

    def put_on_chef_held_item(self, chef):
        if self.content:
            self.content.put_on_chef_held_item(chef)
        elif isinstance(chef.held_item, Bowl):
            self.content = chef.held_item
            self.content.move_to_new_position(x=self.x, y=self.y)
            chef.held_item = None

    def mix(self):
        if self.content:
            if self.content.contents:
                if self.content.progress < constants.OVERMIX_TICKS:
                    self.content.progress += 1
                    if self.content.progress == constants.MIX_TICKS:
                        for ingredient in self.content.contents:
                            ingredient.processes_done.append(constants.PROCESS_MIXED)
                        self.contentis_mixed = True
                    elif self.content.progress >= constants.OVERMIX_TICKS:
                        self.__world.is_done = True
        
    def print_static(self):
        print('M', end='')