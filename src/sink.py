import constants

from useable_object import UsableObect
from plate import Plate

class Sink(UsableObect):
    def __init__(self):
        self.__progress = 0
        self.__dirty_plates = []
        self.content = None

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Plate):
            plate = chef.held_item
            if plate.is_dirty:
                self.__dirty_plates.append(plate)
            else:
                if not self.content:
                    self.content = plate
                else:
                    return None
        else:
            return None

    def use(self):
        self.__progress += 1
        if self.__progress >= constants.WASH_TICKS:
            self.__progress = 0
            plate = self.__dirty_plates[0]
            plate.is_dirty = False
            if self.content:
                plate.content = self.content
            self.content = plate

    def print_static(self):
        print('W', end='')

    def print(self):
        if self.content:
            self.content.print()     
        else:
            self.print_static()
            

                
