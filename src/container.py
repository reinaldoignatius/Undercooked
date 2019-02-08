from abc import ABC
from moveable_object import MoveableObject
from ingredient import Ingredient
import constants

class Container(MoveableObject, ABC):
    def __init__(self, id, x ,y):
        super().__init__(x, y)
        self.contents = []
        self.progress = 0
        self.id = id

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Container):
            # Swap contents and progress
            new_contents = chef.held_item.contents
            chef.held_item.contents = self.contents
            self.contents = new_contents

            new_progress = chef.held_item.progress
            chef.held_item.progress = self.progress
            self.progress = new_progress
        elif isinstance(chef.held_item, Ingredient):
            # Add ingredients only if not processed except cut and half current progress
            if len(chef.held_item.processes_done) == 1:
                if chef.held_item.processes_done[0] == constants.PROCESS_CUT:
                    self.contents.append(Ingredient)
                    self.progress /= 2
    
    def print(self):
        print(self.id, end='')    