import json
import random
import copy

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
from order import Order

class World():

    def __init__(self):
        self.map = []
        self.chefs = []
        self.plates = []
        self.bowls = []
        self.cookeable_containers = []
        self.mixers = []
        self.stoves = []
        self.ingredients = []
        self.possible_orders = []
        self.current_orders = []
        self.return_counter = None
        self.obtained_reward = 0

        self.__time_between_orders = 0
        self.__time_until_next_order = 0
        self.__current_bowl_id = '('
        self.__current_cookable_container_id = '-'


    def __create_order(self):
        print(len(self.possible_orders))
        selected_order = self.possible_orders[random.randint(0, len(self.possible_orders) - 1)]
        self.current_orders.append(Order(
            required_ingredients=copy.deepcopy(selected_order['required_ingredients']), 
            allocated_time=selected_order['allocated_time'],
            maximum_reward=selected_order['maximum_reward']
        ))


    def load_level(self, level_name, number_of_players):
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
                                self.map[row][col].content = Table(x=col, y=row)
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
                                self.map[row][col].content = Mixer(x=col, y=row)
                                self.map[row][col].content.content = Bowl(
                                    id=self.__current_bowl_id,
                                    x=col,
                                    y=row                             
                                )
                                self.mixers.append(self.map[row][col].content)
                                self.bowls.append(self.map[row][col].content.content)
                                self.__current_bowl_id = ')'
                            elif char == 'O':
                                self.map[row][col].content = Stove(x=col, y=row)
                                self.map[row][col].content.content = CookableContainer(
                                    id=self.__current_cookable_container_id,
                                    x=col,
                                    y=row
                                )
                                self.stoves.append(self.map[row][col].content)
                                self.cookeable_containers.append(self.map[row][col].content.content)
                                self.__current_cookable_container_id = '+'
                            elif char == 'K':
                                self.map[row][col].content = CuttingBoard(x=col, y=row)
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
                    id=idx + 1, 
                    x=chef_position['x'],
                    y=chef_position['y']
                )
                self.chefs.append(self.map[chef_position['y']][chef_position['x']].content)

            for idx, plate_position in enumerate(position.get('plates')):
                self.map[plate_position['y']][plate_position['x']].content.content = Plate(
                    id=idx + 5,
                    x=plate_position['x'],
                    y=plate_position['y']
                )
                self.plates.append(self.map[plate_position['y']][plate_position['x']].content.content)
        
        with open('levels/%s/orders.json' % level_name) as infile:
            order_dict = json.load(infile)
            self.possible_orders = [order for order in order_dict['orders']]
            self.__time_between_orders = order_dict['time_between_orders']
            self.__time_until_next_order = self.__time_between_orders / 3

        self.__create_order()


    def __handle_move_action(self, chef, direction, distance):
        possible_distance = 1
        if direction == constants.DIRECTION_UP and not self.map[chef.y - possible_distance][chef.x].content:
            while not self.map[chef.y - (possible_distance + 1)][chef.x].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y - possible_distance][chef.x].content = chef
            self.map[chef.y][chef.x].content = None
            chef.move_to_new_position(y=chef.y - possible_distance, x=chef.x)
        elif direction == constants.DIRECTION_LEFT and not self.map[chef.y][chef.x - possible_distance].content:
            while not self.map[chef.y][chef.x - (possible_distance + 1)].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y][chef.x - possible_distance].content = chef
            self.map[chef.y][chef.x].content = None
            chef.move_to_new_position(y=chef.y, x=chef.x - possible_distance)
        elif direction == constants.DIRECTION_RIGHT and not self.map[chef.y][chef.x + possible_distance].content:
            while not self.map[chef.y][chef.x + (possible_distance + 1)].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y][chef.x + possible_distance].content = chef
            self.map[chef.y][chef.x].content = None
            chef.move_to_new_position(y=chef.y, x=chef.x + possible_distance)
        elif direction == constants.DIRECTION_DOWN and not self.map[chef.y + possible_distance][chef.x].content:
            while not self.map[chef.y + (possible_distance + 1)][chef.x].content and possible_distance < distance:
                possible_distance += 1
            self.map[chef.y + possible_distance][chef.x].content = chef
            self.map[chef.y][chef.x].content = None
            chef.move_to_new_position(y=chef.y + possible_distance, x=chef.x)


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
                chef.pick_up(self.map[chef.y - 1][chef.x].content.put_off_content())
            elif direction == constants.DIRECTION_LEFT and isinstance(self.map[chef.y][chef.x - 1].content, Table):
                chef.pick_up(self.map[chef.y][chef.x - 1].content.put_off_content())
            elif direction == constants.DIRECTION_RIGHT and isinstance(self.map[chef.y][chef.x + 1].content, Table):
                chef.pick_up(self.map[chef.y][chef.x + 1].content.put_off_content())
            elif direction == constants.DIRECTION_DOWN and isinstance(self.map[chef.y + 1][chef.x].content, Table):
                chef.pick_up(self.map[chef.y + 1][chef.x].content.put_off_content())
            

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


    def simulate(self):
        for mixer in self.mixers:
            mixer.mix()
        for stove in self.stoves:
            stove.cook()
        for current_order in self.current_orders:
            current_order.remaining_time -= 1
            if current_order.remaining_time == 0:
                self.obtained_reward -= constants.PENALTY
                current_order.remaining_time = current_order.allocated_time

        self.__time_until_next_order -= 1
        if self.__time_until_next_order <= 0:
            self.__create_order()
            self.__time_until_next_order = self.__time_between_orders

    
    def submit(self, plate):
        match_idx = -1
        for idx, current_order in enumerate(self.current_orders):
            if current_order.match(plate.contents):
                match_idx = idx
                remaining_time_percentage = current_order.remaining_time / current_order.allocated_time
                if remaining_time_percentage >= 0.67:
                    self.obtained_reward += current_order.maximum_reward
                elif remaining_time_percentage >= 0.33:
                    self.obtained_reward += 2 / 3 * current_order.maximum_reward
                else:
                    self.obtained_reward += current_order.maximum_reward / 3
        if match_idx != -1:
            self.current_orders.pop(match_idx)

    def print_current_map(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                self.map[row][col].print()
            print()

    
    def print_current_orders(self):
        for current_order in self.current_orders:
            print('Time remaining:', current_order.remaining_time)
            print('Required ingredients:')
            for required_ingredient in current_order.required_ingredients:
                print('Name: %s Required processes:' % (required_ingredient['name']), end=' ')
                for required_process in required_ingredient['required_processes']:
                    print(required_process, end=' ')
                print()        


    def print_static_map(self):
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                self.map[row][col].print_static()
            print()


    def print_chefs(self):
        for chef in self.chefs:
            print('Id: %d X: %d Y:%d' % (chef.id, chef.x, chef.y))


    def print_ingredients(self):
        for ingredient in self.ingredients:
            print('Name: %s X: %d Y: %d Progress: %d' % (ingredient.name, ingredient.x, ingredient.y, ingredient.progress))
            for process_done in ingredient.processes_done:
                print('  %s' % process_done, end=' ')
            print()


    def print_containers(self):
        for bowl in self.bowls:
            print('Bowl X: %d Y: %d Progress: %d' % (bowl.x, bowl.y, bowl.progress))
        for cookable_container in self.cookeable_containers:
            print('Cookable container X: %d Y: %d Progress: %d' % (cookable_container.x, cookable_container.y, cookable_container.progress))


    def print_plates(self):
        for plate in self.plates:
            print('Id: %d X: %d Y: %d Dirty: %s' % (plate.id, plate.x, plate.y, plate.is_dirty))