from abc import abstractmethod

class Table():
    def __init__(self, x, y):
        self.content = None
        self.x = x
        self.y = y

    def put_on_chef_held_item(self, chef):
        if self.content and hasattr(self.content, 'put_on_chef_held_item'):
            self.content.put_on_chef_held_item(chef)
        else:
            self.content = chef.held_item
            self.content.move_to_new_position(x=self.x, y=self.y)
            chef.held_item = None
    
    def put_off_content(self):
        if self.content:
            content = self.content
            self.content = None
            return content

    @abstractmethod
    def print_static(self):
        print('T', end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()