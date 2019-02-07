import constants

class Chef():
  def __init__(self, world, id, x, y):
    self.world = world
    self.id = id
    self.x = x
    self.y = y
    self.holdedItem = None

  def move(self, direction, distance):
    if direction == constants.DIRECTION_UP:
      self.y -= distance
    elif direction == constants.DIRECTION_LEFT:
      self.x -= distance
    elif direction == constants.DIRECTION_RIGHT:
      self.x += distance
    elif direction == constants.DIRECTION_DOWN:
      self.y += distance

  def pick_up(self, holdableObject):
    self.holdedItem = holdableObject

  def print_static(self):
    print(self.id, end='')

  def print(self):
    self.print_static()

