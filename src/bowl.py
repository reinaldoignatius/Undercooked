from container import Container

class Bowl(Container):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_mixed = False

    def put_on_chef_held_item(self, chef):
        if not self.is_mixed:
            super().put_on_chef_held_item(chef)
            if isinstance(chef.held_item, Bowl):
                new_mixed = chef.held_item.is_mixed
                chef.held_item.is_mixed = self.is_mixed
                self.is_mixed = new_mixed

    def print(self):
        print('(', end='')  
