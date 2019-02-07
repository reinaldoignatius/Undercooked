class Floor() :
    def __init__(self):
        self.content = None

    def print(self):
        if not self.content:
            print(' ', end='')
        else:
            self.content.print()

    def print_static(self):
        if not self.content:
            print(' ', end='')
        else:
            self.content.print_static()