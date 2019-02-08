from table import Table
from useable_object import UsableObect
from ingredient import Ingredient
import constants

class CuttingBoard(Table, UsableObect):
    def __init__(self):
        super().__init__()

    def use(self):
        if isinstance(self.content, Ingredient):
            if not self.content.processes_done:
                if self.content.progress < constants.CUT_TICKS:
                    self.content.progress += 1
                else:
                    self.content.processes_done.append(constants.PROCESS_CUT)

    def print_static(self):
        print('T', end='')

    def print(self):
        if self.content:
            self.content.print()
        else:
            self.print_static()