from table import Table

class ReturnCounter(Table):
    def __init__(self, x, y):
        super().__init__(x, y)

    def put_on_chef_held_item(self, chef):
        pass

    def add_dirty_plate(self, dirty_plate):
        dirty_plate.x = self.x
        dirty_plate.y = self.y
        if self.content:
            top_dirty_plate = self.content
            while top_dirty_plate.contents:
                top_dirty_plate = top_dirty_plate.contents[0]
            top_dirty_plate.contents.append(dirty_plate)
        else:
            self.content = dirty_plate

    def print_static(self):
        print('R', end='')