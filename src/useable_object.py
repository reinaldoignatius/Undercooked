from abc import ABC, abstractmethod

class UsableObect(ABC):
    @abstractmethod
    def use(self):
        pass