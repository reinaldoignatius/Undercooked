from moveable_object import MoveableObject
from ingredient import Ingredient

import constants

class Plate(MoveableObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.contents = []
        self.is_dirty = False
        self.time_until_respawn = 0

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Ingredient):
            if constants.PROCESS_CUT in chef.held_item.processes_done:
                self.contents.append(chef.held_item)
                chef.held_item.move_to_new_position(self.x, self.y)
                chef.held_item = None

    def move_to_new_position(self, x, y):
        super().move_to_new_position(x, y)
        for content in self.contents:
            content.move_to_new_position(x, y)
    
    def print(self):
        print('p', end='')
    