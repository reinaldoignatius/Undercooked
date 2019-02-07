from ingredient import Ingredient
import constants

class CuttingBoard():
  def __init__(self):
    self.content = None

  def put_on_chef_held_item(self, chef):
    if not self.content:
      self.content = chef.held_item
      chef.held_item = None

  def use(self, id):
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