from bowl import Bowl
import constants

class Mixer():
    def __init__(self):
        self.content = None

    def put_on_chef_held_item(self, chef):
        if isinstance(chef.held_item, Bowl):
            self.content = chef.held_item
            chef.held_item = None

    def mix(self):
        if self.content:
            if self.content.contents:
                if self.content.progress < constants.MIX_TICKS:
                    self.content.progress += 1
                else:
                    if not self.content.mixed:
                        for ingredient in self.content.contents:
                            ingredient.processes_done.append(constants.PROCESS_MIXED)
                        self.content.mixed = True
        
    def print_static(self):
        print('M', end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static