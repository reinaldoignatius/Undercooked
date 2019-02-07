class Table():
    def __init__(self):
        self.content = None

    def put_on_chef_held_item(self, chef):
        if not self.content:
            self.content = chef.held_item
            chef.held_item = None

    def print_static(self):
        print('T', end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()