class ReturnCounter():
  def __init__(self):
    self.__dirty_plates = []

  def add_dirty_plate(self, dirty_plate):
    self.__dirty_plates.append(dirty_plate)

  def empty(self):
    temp = self.__dirty_plates
    self.__dirty_plates = None
    return temp

  def print_static(self):
    print('R', end='')

  def print(self):
    self.print_static()