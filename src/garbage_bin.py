from plate import Plate
from ingredient import Ingredient

class GarbageBin():
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.__world = world

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Plate):
            for ingredient in chef.held_item.contents:
                self.__world.ingredients.remove(ingredient)
            chef.held_item.contents.clear()
        elif isinstance(chef.held_item, Ingredient):
            self.__world.ingredients.remove(chef.held_item)
            chef.held_item = None

    def print_static(self):
        print('G', end='')

    def print(self):
        self.print_static()
        