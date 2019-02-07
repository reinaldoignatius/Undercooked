from container import Container

class CookableContainer(Container):
    def __init__(self, id):
        super().__init__(id)
        self.cooked = False
    
    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, CookableContainer):
            new_cooked = chef.held_item.cooked
            chef.held_item.cooked = self.cooked
            self.cooked = new_cooked