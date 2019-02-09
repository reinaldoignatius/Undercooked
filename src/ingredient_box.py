from table import Table
from spawner import Spawner
from useable_object import UsableObect
from ingredient import Ingredient

class IngredientBox(Table, Spawner, UsableObect):
    def __init__(self, world, name, x, y):
        Table.__init__(self, x, y)
        Spawner.__init__(self, x, y)
        self.world = world
        self.name = name

    def spawn(self):
        if not self.content:
            self.content = Ingredient(
                self.name.lower(),
                self.x,
                self.y
            )
            self.world.ingredients.append(self.content)

    def use(self):
        self.spawn()

    def print_static(self):
        print(self.name, end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()