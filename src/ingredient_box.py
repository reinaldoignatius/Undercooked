from useable_object import UsableObect
from ingredient import Ingredient

class IngredientBox(UsableObect):
    def __init__(self, world, name):
        self.world = world
        self.name = name
        self.content = None

    def put_on_chef_held_item(self, chef):
        if not self.content:
            self.content = chef.held_item
            chef.held_item = None

    def use(self):
        if not self.content:
            self.content = Ingredient(self.name.lower())
            self.world.ingredients.append(self.content)

    def print_static(self):
        print(self.name, end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()