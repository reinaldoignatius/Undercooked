import copy
import json

from floor import Floor
from wall import Wall
from table import Table
from sink import Sink
from return_counter import ReturnCounter
from submission_counter import SubmissionCounter
from garbage_bin import GarbageBin
from mixer import Mixer
from bowl import Bowl
from stove import Stove
from cookable_container import CookableContainer
from cutting_board import CuttingBoard
from ingredient_box import IngredientBox
from plate import Plate
from chef import Chef

class World():

    def __init__(self):
        self.map = []
        self.chefs = []
        self.plates = []
        self.bowls = []
        self.cookeable_containers = []
        self.return_counter = None

        self.__current_bowl_id = '('
        self.__current_cookable_container_id = '-'

    def load_map(self, level_name, number_of_players):
        with open('levels/%s/.map' % level_name) as infile:
            for row, line in enumerate(infile.readlines()):
                self.map.append([])
                for col, char in enumerate(line):
                    if char != '\n':
                        self.map[row].append(Floor())
                        if char == '#':
                            self.map[row][col].content = Wall()
                        elif char == 'T':
                            self.map[row][col].content = Table()
                        elif char == 'W':
                            self.map[row][col].content = Sink()
                        elif char == 'R':
                            self.return_counter = ReturnCounter()
                            self.map[row][col].content = self.return_counter
                        elif char == 'S':
                            self.map[row][col].content = SubmissionCounter(self)
                        elif char == 'G':
                            self.map[row][col].content = GarbageBin()
                        elif char == 'M':
                            self.map[row][col].content = Mixer()
                            self.map[row][col].content.content = Bowl(self.__current_bowl_id)
                            self.bowls.append(self.map[row][col].content.content)
                            self.__current_bowl_id = ')'
                        elif char == 'O':
                            self.map[row][col].content = Stove()
                            self.map[row][col].content.content = CookableContainer(self.__current_cookable_container_id)
                            self.cookeable_containers.append(self.map[row][col].content.content)
                            self.__current_cookable_container_id = '+'
                        elif char == 'T':
                            self.map[row][col].content = CuttingBoard()
                        else:
                            self.map[row][col].content = IngredientBox(char)
                        
        with open('levels/%s/pos.json' % level_name) as infile:
            position = json.load(infile)
            for idx, chef_position in enumerate(position['chefs']):
                self.map[chef_position['y']][chef_position['x']].content = Chef(
                    self, 
                    idx + 1, 
                    chef_position['x'],
                    chef_position['y']
                )
                self.chefs.append(self.map[chef_position['y']][chef_position['x']].content)

            for idx, plate_position in enumerate(position.get('plates')):
                self.map[plate_position['y']][plate_position['x']].content.content = Plate(idx + 5)
                self.plates.append(self.map[plate_position['y']][plate_position['x']].content.content)


    def print_current_map(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                self.map[row][col].print()
            print()

    def print_static_map(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                self.map[row][col].print_static()
            print()
        

def main():
    world = World()
    level_name = 'level_1'
    number_of_players = 4
    world.load_map(level_name, number_of_players)
    world.print_current_map()
    world.print_static_map()

main()