from container import Container

class Bowl(Container):
    def __init__(self, id):
        super().__init__(id)
        self.mixed = False

    def put_on_chef_held_item(self, chef):
        super().put_on_chef_held_item(chef)
        if isinstance(chef.held_item, Bowl):
            new_mixed = chef.held_item.mixed
            chef.held_item.mixed = self.mixed
            self.mixed = new_mixed