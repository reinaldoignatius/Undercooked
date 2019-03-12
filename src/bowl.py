from container import Container

class Bowl(Container):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.is_mixed = False

    def put_on_chef_held_item(self, chef):
        if not self.is_mixed:
            super().put_on_chef_held_item(chef)
            if isinstance(chef.held_item, Bowl):
                new_mixed = chef.held_item.is_mixed
                chef.held_item.is_mixed = selfis_mixed
                selfis_mixed = new_mixed