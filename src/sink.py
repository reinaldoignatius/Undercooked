import constants

from table import Table
from useable_object import UsableObect
from plate import Plate

class Sink(Table, UsableObect):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.progress = 0
        self.dirty_plates = []
        self.clean_plates = []

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Plate):
            plate = chef.held_item
            if plate.is_dirty:
                plate.move_to_new_position(x=self.x, y=self.y)
                chef.held_item = None
                while plate:
                    self.dirty_plates.append(plate)
                    if plate.contents:
                        new_plate = plate.contents[0]
                        plate.contents.clear()
                        plate = new_plate
                    else:
                        plate = None
            else:
                if not self.content:
                    self.content = plate
                    chef.held_item = None
                    plate.move_to_new_position(x=self.x, y=self.y)
                else:
                    self.content.put_on_chef_held_item(chef)
    
    def put_off_content(self):
        if self.content:
            content = self.content
            if self.clean_plates:
                self.content = self.clean_plates.pop()
            else:
                self.content = None
            return content

    def use(self):
        if self.dirty_plates:
            self.progress += 1
            if self.progress == constants.WASH_TICKS:
                self.progress = 0
                plate = self.dirty_plates.pop()
                plate.is_dirty = False
                if self.content:
                    self.clean_plates.append(plate)
                else:
                    self.content = plate

    def print_static(self):
        print('W', end='')
            

                
