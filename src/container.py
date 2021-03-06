from abc import ABC
from moveable_object import MoveableObject
from ingredient import Ingredient
import constants

class Container(MoveableObject, ABC):
    def __init__(self, x ,y):
        super().__init__(x, y)
        self.contents = []
        self.progress = 0

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Container):
            # Swap contents and progress
            new_contents = chef.held_item.contents
            chef.held_item.contents = self.contents
            self.contents = new_contents

            for content in self.contents:
                content.move_to_new_position(self.x, self.y)

            for held_content in chef.held_item.contents:
                held_content.move_to_new_position(chef.x, chef.y)
        elif isinstance(chef.held_item, Ingredient):
            if chef.held_item.name not in list(map(
                lambda content: content.name,
                self.contents
            )):
                # Half current progress if new ingredient is added
                chef.held_item.move_to_new_position(self.x, self.y)
                self.contents.append(chef.held_item)
                chef.held_item = None
                self.progress /= 2
    
    def move_to_new_position(self, x, y):
        super().move_to_new_position(x, y)
        for content in self.contents:
            content.move_to_new_position(self.x, self.y)