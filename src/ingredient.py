class Ingredient():
    def __init__(self, name, processes_done = []):
        self.name = name
        self.processes_done = processes_done
        self.progress = 0

    def print(self):
        print(self.name, end="")