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
        bowl = self.content
        if bowl:
            if bowl.contents:
                if bowl.progress < constants.OVERMIX_TICKS:
                    bowl.progress += 1
                    if int(bowl.progress) == constants.MIX_TICKS:
                        if len(bowl.contents) < 2:
                            self.__world.is_done = True
                        else:
                            for ingredient in bowl.contents:
                                ingredient.processes_done.append(constants.PROCESS_MIXED)
                            bowl.is_mixed = True
                    elif self.content.progress >= constants.OVERMIX_TICKS:
                        self.__world.is_done = True
        
    def print_static(self):
        print('M', end='')