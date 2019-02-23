import constants

from plate import Plate

class SubmissionCounter():
    def __init__(self, world):
        self.__world = world

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Plate):
            plate = chef.held_item
            chef.held_item = None
            if not plate.is_dirty:
                self.__world.submit_plate(plate)
                plate.x = -1
                plate.y = -1
                plate.is_dirty = True
                plate.time_until_respawn = constants.PLATE_RESPAWN_TIME
                for content in plate.contents:
                    self.__world.ingredients.remove(content)
                plate.contents.clear()

    def print_static(self):
        print('S', end="")

    def print(self):
        self.print_static()