from abc import ABC, abstractmethod

class Spawner(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    @abstractmethod
    def spawn(self):
        pass