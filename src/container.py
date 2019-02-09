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

            for content in self.contents:
                content.x = self.x
                content.y = self.y

            for held_content in chef.held_item.contents:
                held_content.x = chef.x
                held_content.y = chef.y

            new_progress = chef.held_item.progress
            chef.held_item.progress = self.progress
            self.progress = new_progress
        elif isinstance(chef.held_item, Ingredient):
            # Add ingredients only if not processed except cut and half current progress
            if len(chef.held_item.processes_done) == 1:
                if chef.held_item.processes_done[0] == constants.PROCESS_CUT:
                    chef.held_item.x = self.x
                    chef.held_item.y = self.y
                    self.contents.append(chef.held_item)
                    chef.held_item = None
                    self.progress /= 2
    
    def move_to_new_position(self, x, y):
        super().move_to_new_position(x, y)
        for content in self.contents:
            content.x = self.x
            content.y = self.y

    def print(self):
        print(self.id, end='')    