import json

import constants

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
from useable_object import UsableObect

class World():

    def __init__(self):
        self.map = []
        self.chefs = []
        self.plates = []
        self.bowls = []
        self.cookeable_containers = []
        self.ingredients = []
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
                        if char != ' ':
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
                                self.map[row][col].content.content = Bowl(
                                    id=self.__current_bowl_id,
                                    x=col,
                                    y=row                             
                                )
                                self.bowls.append(self.map[row][col].content.content)
                                self.__current_bowl_id = ')'
                            elif char == 'O':
                                self.map[row][col].content = Stove()
                                self.map[row][col].content.content = CookableContainer(
                                    id=self.__current_cookable_container_id,
                                    x=col,
                                    y=row
                                )
                                self.cookeable_containers.append(self.map[row][col].content.content)
                                self.__current_cookable_container_id = '+'
                            elif char == 'T':
                                self.map[row][col].content = CuttingBoard()
                            else:
                                self.map[row][col].content = IngredientBox(
                                    world=self, 
                                    name=char,
                                    x=col,
                                    y=row
                                )
                        
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
                self.map[plate_position['y']][plate_position['x']].content.content = Plate(
                    idx + 5,
                    plate_position['y'],
                    plate_position['x']
                )
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


    def __handle_move_action(self, chef, direction, distance):
        possible_distance = 1
        if direction == constants.DIRECTION_UP and not self.map[chef.y - possible_distance][chef.x].content:
            while not self.map[chef.y - (possible_distance + 1)][chef.x].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y - possible_distance][chef.x].content = chef
            self.map[chef.y][chef.x].content = None
            chef.y -= possible_distance
        elif direction == constants.DIRECTION_LEFT and not self.map[chef.y][chef.x - possible_distance].content:
            while not self.map[chef.y][chef.x - (possible_distance + 1)].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y][chef.x - possible_distance].content = chef
            self.map[chef.y][chef.x].content = None
            chef.x -= possible_distance
        elif direction == constants.DIRECTION_RIGHT and not self.map[chef.y][chef.x + possible_distance].content:
            while not self.map[chef.y][chef.x + (possible_distance + 1)].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y][chef.x + possible_distance].content = chef
            self.map[chef.y][chef.x].content = None
            chef.x += possible_distance
        elif direction == constants.DIRECTION_DOWN and not self.map[chef.y + possible_distance][chef.x].content:
            while not self.map[chef.y + (possible_distance + 1)][chef.x].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y + possible_distance][chef.x].content = chef
            self.map[chef.y][chef.x].content = None
            chef.y += possible_distance


    def __handle_use_action(self, chef, direction):
        if not chef.held_item:
            if direction == constants.DIRECTION_UP and isinstance(self.map[chef.y - 1][chef.x].content, UsableObect):
                self.map[chef.y - 1][chef.x].content.use()
            elif direction == constants.DIRECTION_LEFT and isinstance(self.map[chef.y][chef.x - 1].content, UsableObect):
                self.map[chef.y][chef.x - 1].content.use()
            elif direction == constants.DIRECTION_RIGHT and isinstance(self.map[chef.y][chef.x + 1].content, UsableObect):
                self.map[chef.y][chef.x + 1].content.use()
            elif direction == constants.DIRECTION_DOWN and isinstance(self.map[chef.y + 1][chef.x].content, UsableObect):
                self.map[chef.y + 1][chef.x].content.use()


    def __handle_pick_action(self, chef, direction):
        if not chef.held_item:
            if direction == constants.DIRECTION_UP and isinstance(self.map[chef.y - 1][chef.x].content, Table):
                chef.held_item = self.map[chef.y - 1][chef.x].content.put_off_content()
            elif direction == constants.DIRECTION_LEFT and isinstance(self.map[chef.y][chef.x - 1].content, Table):
                chef.held_item = self.map[chef.y][chef.x - 1].content.put_off_content()
            elif direction == constants.DIRECTION_RIGHT and isinstance(self.map[chef.y][chef.x + 1].content, Table):
                chef.held_item = self.map[chef.y][chef.x + 1].content.put_off_content()
            elif direction == constants.DIRECTION_DOWN and isinstance(self.map[chef.y + 1][chef.x].content, Table):
                chef.held_item = self.map[chef.y + 1][chef.x].content.put_off_content()
            

    def __handle_put_action(self, chef, direction):
        if chef.held_item:
            if direction == constants.DIRECTION_UP and self.map[chef.y - 1][chef.x].content and not isinstance(self.map[chef.y - 1][chef.x].content, Wall):
                self.map[chef.y - 1][chef.x].content.put_on_chef_held_item(chef)
            elif direction == constants.DIRECTION_LEFT and self.map[chef.y][chef.x - 1].content and not isinstance(self.map[chef.y][chef.x - 1].content, Wall):
                self.map[chef.y][chef.x - 1].content.put_on_chef_held_item(chef)
            elif direction == constants.DIRECTION_RIGHT and self.map[chef.y][chef.x + 1].content and not isinstance(self.map[chef.y][chef.x + 1].content, Wall):
                self.map[chef.y][chef.x + 1].content.put_on_chef_held_item(chef)
            elif direction == constants.DIRECTION_DOWN and self.map[chef.y + 1][chef.x].content and not isinstance(self.map[chef.y + 1][chef.x].content, Wall):
                self.map[chef.y + 1][chef.x].content.put_on_chef_held_item(chef)


    def handle_action(self, agent, action):
        chef = self.chefs[int(agent[-1:]) - 1] # convert to base 0
        splitted_action = action.split()
        if splitted_action[0] == constants.ACTION_WALK:
            self.__handle_move_action(chef, splitted_action[1], constants.WALK_DISTANCE)
        elif splitted_action[0] == constants.ACTION_DASH:
            self.__handle_move_action(chef, splitted_action[1], constants.DASH_DISTANCE)
        elif splitted_action[0] == constants.ACTION_USE:
            self.__handle_use_action(chef, splitted_action[1])
        elif splitted_action[0] == constants.ACTION_PICK:
            self.__handle_pick_action(chef, splitted_action[1])
        elif splitted_action[0] == constants.ACTION_PUT:
            self.__handle_put_action(chef, splitted_action[1])