from table import Table
from useable_object import UsableObect
from ingredient import Ingredient
import constants

class CuttingBoard(Table, UsableObect):
    def __init__(self, x, y):
        super().__init__(x, y)

    def use(self):
        if isinstance(self.content, Ingredient):
            if not self.content.processes_done:
                if self.content.progress < constants.CUT_TICKS:
                    self.content.progress += 1
                    if self.content.progress >= constants.CUT_TICKS:
                        self.content.processes_done.append(constants.PROCESS_CUT)
                    
    def print_static(self):
        print('K', end='')