import random
import math
import copy
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from . import constants
import constants as game_constants
from ingredient import Ingredient
from bowl import Bowl
from plate import Plate
from cookable_container import CookableContainer

class Agent():

    def __init__(self, name, side):
        self.__side = side

        self.name = name

        self.memory = deque(maxlen=constants.MEMORY_MAX_LENGTH)

        self.current_game_info = {}
        self.current_state = None
        self.current_action = None


    def __a_star(self, current_map, origin, destination):
        closed_set = []
        open_set = [(origin[0], origin[1])]
        came_from = {}
        
        g_score = {}
        f_score = {}
        for row, map_row in enumerate(current_map):
            for col in range(len(map_row)):
                g_score[(col, row)] = math.inf        
                f_score[(col, row)] = math.inf
        g_score[(origin[0], origin[1])] = 0
        f_score[(origin[0], origin[1])] = (abs(destination[0] - origin[0]) + abs(
            destination[1] - origin[1])) / game_constants.DASH_DISTANCE

        while open_set:
            current = min(
                { open_key: f_score[open_key] for open_key in open_set }, 
                key=f_score.get
            )
            if current[0] - 1 == destination[0] and current[1] - 1 == destination[1] or \
                    current[0] - 1 == destination[0] and current[1] == destination[1] or \
                    current[0] - 1 == destination[0] and current[1] + 1 == destination[1] or \
                    current[0] == destination[0] and current[1] - 1 == destination[1] or \
                    current[0] == destination[0] and current[1] + 1 == destination[1] or \
                    current[0] + 1 == destination[0] and current[1] - 1 == destination[1] or \
                    current[0] + 1 == destination[0] and current[1] == destination[1] or \
                    current[0] + 1 == destination[0] and current[1] + 1 == destination[1]:
                found = False
                distance = 0
                while current in came_from and not found:
                    if came_from[current] != origin:
                        current = came_from[current]
                    else:
                        found = True
                    distance += 1
                path = { 'distance': distance }
                if distance > 0:
                    x_direction = current[0] - origin[0]
                    y_direction = current[1] - origin[1]
                else:
                    x_direction = destination[0] - current[0] 
                    y_direction = destination[1] - current[1]

                if x_direction < 0 and y_direction < 0:
                    path['direction'] = game_constants.DIRECTION_UPPER_LEFT
                elif x_direction == 0 and y_direction < 0:
                    path['direction'] = game_constants.DIRECTION_UP
                elif x_direction > 0 and y_direction < 0:
                    path['direction'] = game_constants.DIRECTION_UPPER_RIGHT
                elif x_direction < 0 and y_direction == 0:
                    path['direction'] = game_constants.DIRECTION_LEFT
                elif x_direction > 0 and y_direction == 0:
                    path['direction'] = game_constants.DIRECTION_RIGHT
                elif x_direction < 0 and y_direction > 0:
                    path['direction'] = game_constants.DIRECTION_LOWER_LEFT
                elif x_direction == 0 and y_direction > 0:
                    path['direction'] = game_constants.DIRECTION_DOWN
                elif x_direction > 0 and y_direction > 0:
                    path['direction'] = game_constants.DIRECTION_LOWER_RIGHT
                
                if abs(x_direction) > 1 or abs(y_direction) > 1:
                    path['should_dash'] = True
                else:
                    path['should_dash'] = False
                    
                return path
            
            open_set.remove(current)
            closed_set.append(current)

            neighbors = []

            possible_distance = 1
            if not current_map[current[1] - possible_distance] \
                    [current[0] - possible_distance].content:
                neighbors.append((
                    current[0] - possible_distance,
                    current[1] - possible_distance
                ))
                while not current_map[current[1] - (possible_distance + 1)] \
                        [current[0] - (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((
                        current[0] - possible_distance,
                        current[1] - possible_distance
                    ))
            possible_distance = 1
            if not current_map[current[1] - possible_distance][current[0]].content:
                neighbors.append((current[0], current[1] - possible_distance))
                while not current_map[current[1] - (possible_distance + 1)] \
                        [current[0]].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((current[0], current[1] - possible_distance))
            possible_distance = 1
            if not current_map[current[1] - possible_distance] \
                    [current[0] + possible_distance].content:
                neighbors.append((
                    current[0] + possible_distance,
                    current[1] - possible_distance
                ))
                while not current_map[current[1] - (possible_distance + 1)] \
                        [current[0] + (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((
                        current[0] + possible_distance,
                        current[1] - possible_distance
                    ))
            possible_distance = 1
            if not current_map[current[1]][current[0] - possible_distance].content:
                neighbors.append((current[0] - possible_distance, current[1]))
                while not current_map[current[1]] \
                        [current[0] - (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((current[0] - possible_distance, current[1]))
            possible_distance = 1
            if not current_map[current[1]][current[0] + possible_distance].content:
                neighbors.append((current[0] + possible_distance, current[1]))
                while not current_map[current[1]] \
                        [current[0] + (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((current[0] + possible_distance, current[1]))
            possible_distance = 1
            if not current_map[current[1] + possible_distance] \
                    [current[0] - possible_distance].content:
                neighbors.append((
                    current[0] - possible_distance,
                    current[1] + possible_distance
                ))
                while not current_map[current[1] + (possible_distance + 1)] \
                        [current[0] - (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((
                        current[0] - possible_distance,
                        current[1] + possible_distance
                    ))
            possible_distance = 1
            if not current_map[current[1] + possible_distance][current[0]].content:
                neighbors.append((current[0], current[1] + possible_distance))
                while not current_map[current[1] + (possible_distance + 1)] \
                        [current[0]].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((current[0], current[1] + possible_distance))
            possible_distance = 1
            if not current_map[current[1] + possible_distance] \
                    [current[0] + possible_distance].content:
                neighbors.append((
                    current[0] + possible_distance,
                    current[1] + possible_distance
                ))
                while not current_map[current[1] + (possible_distance + 1)] \
                        [current[0] + (possible_distance + 1)].content and \
                        possible_distance < game_constants.DASH_DISTANCE:
                    possible_distance += 1
                if possible_distance > 1:
                    neighbors.append((
                        current[0] + possible_distance,
                        current[1] + possible_distance
                    ))

            for neighbor in neighbors:
                if not neighbor in closed_set:
                    if not neighbor in open_set:
                        open_set.append(neighbor)
                    elif g_score[current] + 1 >= g_score[neighbor]:
                        continue
                    came_from[neighbor] = current
                    g_score[neighbor] = g_score[current] + 1
                    f_score[neighbor] = g_score[neighbor] + \
                        (abs(destination[0] - neighbor[0]) + \
                        abs(destination[1] - neighbor[1])) / 3
    

    def __get_nearest_path(self, current_map, origin, destinations):
        chosen_path = None
        for destination in destinations:
            if not chosen_path:
                chosen_path = self.__a_star(current_map, origin, destination)
            else:
                candidate_path = self.__a_star(current_map, origin, destination)
                if candidate_path:
                    if candidate_path['distance'] < chosen_path['distance']:
                        chosen_path = candidate_path
        return chosen_path


    def translate_to_state(self, game_info, blackboard_recent_writings):
        pass


    def translate_to_game_action(self):
        action = constants.LEFT_SIDE_ACTION_CHOICES[self.current_action] if \
            self.__side == constants.SIDE_LEFT else \
            constants.RIGHT_SIDE_ACTION_CHOICES[self.current_action]

        own_chef = self.current_game_info['chefs'][int(self.name[-1:]) - 1]

        bound_ingredients = []
        for container in self.current_game_info['chefs'] + \
                self.current_game_info['bowls'] + \
                self.current_game_info['cookable_containers'] + \
                self.current_game_info['plates']:
            bound_ingredients += list(filter(
                lambda ingredient: ingredient.x == container.x and \
                    ingredient.y == container.y,
                self.current_game_info['ingredients']
            ))
        unbound_ingredients = [ingredient for ingredient in \
            self.current_game_info['ingredients'] if ingredient not in bound_ingredients]

        ingredient_boxes = {}
        for ingredient_box in self.current_game_info['ingredient_boxes']:
            ingredient_boxes[ingredient_box.name.lower()] = ingredient_box

        empty_passing_table_positions = list(map(
            lambda table: (table.x, table.y),
            list(filter(
                lambda table: table.x == constants.PASSING_TABLE_X and not table.content,
                self.current_game_info['tables']
            ))
        ))

        nearest_path = None
        if self.__side == constants.SIDE_LEFT:
            on_cutting_board_a_ingredients = []
            for cutting_board in self.current_game_info['cutting_boards']:        
                on_cutting_board_a_ingredients += list(filter(
                    lambda ingredient: ingredient.x == cutting_board.x and \
                        ingredient.y == cutting_board.y and ingredient.name == \
                        game_constants.INGREDIENT_A_NAME,
                    unbound_ingredients
                ))
            on_mixer_bowls = []
            for mixer in self.current_game_info['mixers']:
                on_mixer_bowls += list(filter(
                    lambda bowl: bowl.x == mixer.x and bowl.y == mixer.y,
                    self.current_game_info['bowls']
                ))
            empty_left_side_table_positions = list(map(
                lambda table: (table.x, table.y),
                list(filter(
                    lambda table: table.x < constants.PASSING_TABLE_X and not table.content,
                    self.current_game_info['tables']
                ))
            ))

            if action == constants.ACTION_CUT_A:
                if not own_chef.held_item:
                    uncut_a_ingredients = list(filter(
                        lambda ingredient: \
                            ingredient.name == game_constants.INGREDIENT_A_NAME and \
                            not ingredient.processes_done,
                        unbound_ingredients
                    ))
                    on_cutting_board_uncut_a_ingredients = list(filter(
                        lambda on_cutting_board_a: not on_cutting_board_a.processes_done,
                        on_cutting_board_a_ingredients
                    ))
                    not_on_cutting_board_uncut_a_ingredients = [a for a in \
                        uncut_a_ingredients if a not in on_cutting_board_uncut_a_ingredients]
                    # Continue cutting
                    if on_cutting_board_uncut_a_ingredients:
                        max_progress = max(
                            a.progress for a in on_cutting_board_uncut_a_ingredients
                        )
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda a: (a.x, a.y), 
                                list(filter(
                                    lambda a: a.progress == max_progress,
                                    on_cutting_board_uncut_a_ingredients
                                ))
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE, 
                                    nearest_path['direction']
                                )
                    # Get uncut a from table
                    elif not_on_cutting_board_uncut_a_ingredients:
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda a: (a.x, a.y),
                                not_on_cutting_board_uncut_a_ingredients
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                    # Get a from box
                    else:
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                ingredient_boxes[game_constants.INGREDIENT_A_NAME].x,
                                ingredient_boxes[game_constants.INGREDIENT_A_NAME].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE, 
                                    nearest_path['direction']
                                )
                # Put uncut a on cutting board
                else:
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_A_NAME and \
                                not own_chef.held_item.processes_done:
                            left_side_empty_cutting_boards = list(filter(
                                lambda cutting_board: not cutting_board.content and \
                                    cutting_board.x < constants.PASSING_TABLE_X,
                                self.current_game_info['cutting_boards']    
                            ))
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                list(map(
                                    lambda cutting_board: (cutting_board.x, cutting_board.y),
                                    left_side_empty_cutting_boards
                                ))
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT, 
                                        nearest_path['direction']
                                    )
                                
            elif action == constants.ACTION_MIX_A_AND_C:
                left_side_bowls = list(filter(
                    lambda bowl: bowl.x <= constants.PASSING_TABLE_X, 
                    self.current_game_info['bowls']
                ))
                cut_a_ingredients = list(filter(
                    lambda ingredient: \
                        ingredient.name == game_constants.INGREDIENT_A_NAME and \
                        ingredient.processes_done,
                    unbound_ingredients
                ))
                left_side_c_ingredients = list(filter(
                    lambda ingredient: \
                        ingredient.name == game_constants.INGREDIENT_C_NAME and \
                        ingredient.x <= constants.PASSING_TABLE_X,
                    unbound_ingredients
                ))
                if not own_chef.held_item:
                    not_mixed_full_bowls = list(filter(
                        lambda bowl: len(bowl.contents) == 2 and not bowl.is_mixed and \
                            bowl.x < constants.PASSING_TABLE_X,
                        self.current_game_info['bowls']
                    ))
                    not_mixed_not_on_mixer_full_bowls = [
                        bowl for bowl in not_mixed_full_bowls if bowl not in on_mixer_bowls
                    ]
                    # Get not mixed full bowl from table
                    if not_mixed_not_on_mixer_full_bowls:
                        max_progress = max(
                            bowl.progress for bowl in not_mixed_not_on_mixer_full_bowls
                        )
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda bowl: (bowl.x, bowl.y),
                                list(filter(
                                    lambda bowl: bowl.progress == max_progress,
                                    not_mixed_not_on_mixer_full_bowls
                                ))
                            ))
                        )
                    # Get ingredient
                    else:
                        candidate_bowls = list(filter(
                            lambda bowl: len(bowl.contents) < 2,
                            left_side_bowls
                        ))
                        if candidate_bowls:
                            max_progress = max(bowl.progress for bowl in candidate_bowls)
                            if max_progress > 0:
                                candidate_bowls = list(filter(
                                    lambda candidate_bowl: \
                                        candidate_bowl.progress == max_progress,
                                    candidate_bowls
                                ))
                            one_content_candidate_bowls = list(filter(
                                lambda candidate_bowl: len(candidate_bowl.contents) == 1,
                                candidate_bowls
                            ))
                            candidate_destinations = []
                            if one_content_candidate_bowls:
                                contain_a_candidate_bowls = list(filter(
                                    lambda candidate_bowl: candidate_bowl.contents[0].name == \
                                        game_constants.INGREDIENT_A_NAME,
                                    one_content_candidate_bowls
                                ))
                                contain_c_candidate_bowls = list(filter(
                                    lambda candidate_bowl: candidate_bowl.contents[0].name == \
                                        game_constants.INGREDIENT_C_NAME,
                                    one_content_candidate_bowls
                                ))
                                if contain_a_candidate_bowls:
                                    candidate_destinations += list(map(
                                        lambda c: (c.x, c.y),
                                        left_side_c_ingredients, 
                                    ))
                                if contain_c_candidate_bowls:
                                    candidate_destinations += list(map(
                                        lambda a: (a.x, a.y),
                                        cut_a_ingredients
                                    ))
                            else:
                                if cut_a_ingredients and left_side_c_ingredients:
                                    candidate_destinations = list(map(
                                        lambda ingredient: (ingredient.x, ingredient.y),
                                        cut_a_ingredients + left_side_c_ingredients
                                    ))
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                candidate_destinations
                            )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK, 
                                nearest_path['direction']
                            )
                else:
                    # Put bowl on empty mixer
                    if isinstance(own_chef.held_item, Bowl):
                        empty_mixers = list(filter(
                            lambda mixer: not mixer.content, 
                            self.current_game_info['mixers']
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda mixer: (mixer.x, mixer.y), empty_mixers))
                        )
                    elif isinstance(own_chef.held_item, Ingredient):
                        empty_bowls = list(filter(
                            lambda bowl: not bowl.contents,
                            left_side_bowls
                        ))
                        # Put a on most progressed bowl
                        if own_chef.held_item.name == game_constants.INGREDIENT_A_NAME and \
                                own_chef.held_item.processes_done:
                            only_contain_c_bowls = list(filter(
                                lambda bowl: len(bowl.contents) == 1 and list(filter(
                                    lambda content: \
                                        content.name == game_constants.INGREDIENT_C_NAME, 
                                    bowl.contents
                                )), 
                                left_side_bowls
                            ))
                            if only_contain_c_bowls:
                                max_progress = max(
                                    bowl.progress for bowl in only_contain_c_bowls
                                )
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda bowl: (bowl.x, bowl.y),
                                        list(filter(
                                            lambda bowl: bowl.progress == max_progress,
                                            only_contain_c_bowls
                                        ))
                                    ))
                                )
                            elif left_side_c_ingredients:
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(lambda bowl: (bowl.x, bowl.y), empty_bowls))
                                )
                        # Put c on most progressed bowl
                        elif own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            only_contain_a_bowls = list(filter(
                                lambda bowl: len(bowl.contents) == 1 and list(filter(
                                    lambda content: \
                                        content.name == game_constants.INGREDIENT_A_NAME, 
                                    bowl.contents
                                )),
                                left_side_bowls
                            ))
                            if only_contain_a_bowls:
                                max_progress = max(
                                    bowl.progress for bowl in only_contain_a_bowls
                                )
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda bowl: (bowl.x, bowl.y),
                                        list(filter(
                                            lambda bowl: bowl.progress == max_progress,
                                            only_contain_a_bowls
                                        ))
                                    ))
                                )
                            elif cut_a_ingredients:
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(lambda bowl: (bowl.x, bowl.y), empty_bowls))
                                )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PUT, 
                                nearest_path['direction']
                            )

            elif action == constants.ACTION_PASS_MIXED_BOWL:
                if not own_chef.held_item:
                    # Get mixed bowl
                    unpassed_mixed_bowl = list(filter(
                        lambda bowl: bowl.x < constants.PASSING_TABLE_X and bowl.is_mixed,
                        self.current_game_info['bowls']
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda bowl: (bowl.x, bowl.y), unpassed_mixed_bowl))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Pass mixed bowl
                    if isinstance(own_chef.held_item, Bowl):
                        if own_chef.held_item.is_mixed:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_passing_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_PASS_CLEAN_PLATE:
                if not own_chef.held_item:
                    # Get clean plate
                    left_side_clean_plate = list(filter(
                        lambda plate: plate.x < constants.PASSING_TABLE_X and \
                            not plate.is_dirty,
                        self.current_game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda plate: (plate.x, plate.y), left_side_clean_plate))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Pass clean plate
                    if isinstance(own_chef.held_item, Plate):
                        if not own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_passing_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )  

            elif action == constants.ACTION_WASH_PLATE:
                if not own_chef.held_item:
                    if self.current_game_info['sink'].dirty_plates:
                        # Use sink
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                self.current_game_info['sink'].x,
                                self.current_game_info['sink'].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE,
                                    nearest_path['direction']
                                )
                    else:
                        # Get dirty plates
                        left_side_dirty_plates = list(filter(
                            lambda plate: plate.x <= constants.PASSING_TABLE_X and \
                                plate.is_dirty,
                            self.current_game_info['plates']
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda plate: (plate.x, plate.y), left_side_dirty_plates))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    if isinstance(own_chef.held_item, Plate):
                        #  Put dirty plates into sink
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                self.current_game_info['sink'].x,
                                self.current_game_info['sink'].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )

            elif action == constants.ACTION_PUT_ASIDE_A:
                if not own_chef.held_item:
                    # Get cut a from cutting board
                    if on_cutting_board_a_ingredients:
                        on_cutting_board_cut_a_ingredients = list(filter(
                            lambda a: a.processes_done,
                            on_cutting_board_a_ingredients
                        ))
                        nearest_path == self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda a: (a.x, a.y),
                                on_cutting_board_cut_a_ingredients
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    # Put a on side table
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_A_NAME and \
                                own_chef.held_item.processes_done:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_left_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_PUT_ASIDE_C:
                if not own_chef.held_item:
                    # Get c from passing table
                    on_passing_table_c = list(filter(
                        lambda ingredient: ingredient.name == \
                            game_constants.INGREDIENT_C_NAME and \
                            ingredient.x == constants.PASSING_TABLE_X,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda c: (c.x, c.y), on_passing_table_c))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Put c on side table
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_left_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PUT_ASIDE_MIXED_BOWL:
                if not own_chef.held_item:
                    # Get most progressed on mixer bowl
                    if on_mixer_bowls:
                        mixed_on_mixer_bowls = list(filter(
                            lambda on_mixer_bowl: on_mixer_bowl.is_mixed,
                            on_mixer_bowls
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda bowl: (bowl.x, bowl.y),
                                mixed_on_mixer_bowls
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    # Put bowl on side table
                    if isinstance(own_chef.held_item, Bowl):
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_left_side_table_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )

            elif action == constants.ACTION_PUT_ASIDE_DIRTY_PLATE:
                if not own_chef.held_item:
                    # Get dirty plate from passing table
                    on_passing_table_dirty_plates = list(filter(
                        lambda plate: plate.x == constants.PASSING_TABLE_X and plate.is_dirty,
                        self.current_game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(
                            lambda plate: (plate.x, plate.y),
                            on_passing_table_dirty_plates
                        ))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Put dirty plate on side table
                    if isinstance(own_chef.held_item, Plate):
                        if own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_left_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_THROW_AWAY_A:
                if not own_chef.held_item:
                    # Get unprogressed a
                    unprogressed_a_ingredients = list(filter(
                        lambda ingredient: ingredient.progress == 0 and \
                            ingredient.name == game_constants.INGREDIENT_A_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda a: (a.x, a.y), unprogressed_a_ingredients))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Throw away unprogressed a
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_A_NAME and \
                                own_chef.held_item.progress == 0:
                            nearest_path = self.__a_star(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                (
                                    self.current_game_info['garbage_bin'].x,
                                    self.current_game_info['garbage_bin'].y
                                )
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_THROW_AWAY_C:
                if not own_chef.held_item:
                    # Get c
                    left_side_c = list(filter(
                        lambda ingredient: ingredient.x <= constants.PASSING_TABLE_X and \
                            ingredient.name == game_constants.INGREDIENT_C_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda c: (c.x, c.y), left_side_c))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Throw aweay c
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            nearest_path = self.__a_star(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                (
                                    self.current_game_info['garbage_bin'].x,
                                    self.current_game_info['garbage_bin'].y
                                )
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

        elif self.__side == constants.SIDE_RIGHT:
            on_cutting_board_b_ingredients = []
            for cutting_board in self.current_game_info['cutting_boards']:        
                on_cutting_board_b_ingredients += list(filter(
                    lambda ingredient: ingredient.x == cutting_board.x and \
                        ingredient.y == cutting_board.y and ingredient.name == \
                        game_constants.INGREDIENT_B_NAME,
                    unbound_ingredients
                ))
            on_stove_cookable_containers = []
            for stove in self.current_game_info['stoves']:
                on_stove_cookable_containers += list(filter(
                    lambda cookable_container: cookable_container.x == stove.x and \
                        cookable_container.y == stove.y,
                    self.current_game_info['cookable_containers']
                ))
            empty_right_side_table_positions = list(map(
                lambda table: (table.x, table.y),
                list(filter(
                    lambda table: table.x > constants.PASSING_TABLE_X and not table.content,
                    self.current_game_info['tables']
                ))
            ))
            empty_stove_positions = list(map(
                lambda stove: (stove.x, stove.y),
                list(filter(
                    lambda stove: not stove.content,
                    self.current_game_info['stoves']
                ))
            ))
            empty_cookable_container_positions = list(map(
                lambda cookable_container: (cookable_container.x, cookable_container.y),
                list(filter(
                    lambda cookable_container: not cookable_container.contents,
                    self.current_game_info['cookable_containers']
                ))
            ))
            right_side_empty_clean_plate_positions = list(map(
                lambda plate: (plate.x, plate.y),
                list(filter(
                    lambda plate: len(plate.contents) == 0 and not plate.is_dirty and \
                        plate.x >= constants.PASSING_TABLE_X ,
                    self.current_game_info['plates']                       
                ))
            ))
            submission_counter_positions = list(map(
                lambda submission_counter: (submission_counter.x , submission_counter.y),
                self.current_game_info['submission_counters']
            ))

            if action == constants.ACTION_CUT_B:
                if not own_chef.held_item:
                    uncut_b_ingredients = list(filter(
                        lambda ingredient:
                            ingredient.name == game_constants.INGREDIENT_B_NAME and \
                            not ingredient.processes_done,
                        unbound_ingredients
                    ))
                    on_cutting_board_uncut_b_ingredients = list(filter(
                        lambda on_cutting_board_b: not on_cutting_board_b.processes_done,
                        on_cutting_board_b_ingredients
                    ))
                    not_on_cutting_board_uncut_b_ingredients = [b for b in \
                        uncut_b_ingredients if b not in on_cutting_board_uncut_b_ingredients]
                    # Continue cutting
                    if on_cutting_board_uncut_b_ingredients:
                        max_progress = max(
                            b.progress for b in on_cutting_board_uncut_b_ingredients
                        )
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda b: (b.x, b.y), 
                                list(filter(
                                    lambda b: b.progress == max_progress,
                                    on_cutting_board_uncut_b_ingredients
                                ))
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE, 
                                    nearest_path['direction']
                                )
                    # Get uncut b from table
                    elif not_on_cutting_board_uncut_b_ingredients:
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda b: (b.x, b.y),
                                not_on_cutting_board_uncut_b_ingredients
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                    # Get b from box
                    else:
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                ingredient_boxes[game_constants.INGREDIENT_B_NAME].x,
                                ingredient_boxes[game_constants.INGREDIENT_B_NAME].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE, 
                                    nearest_path['direction']
                                )
                # Put uncut b on cutting board
                else:
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME and \
                                not own_chef.held_item.processes_done:
                            right_side_empty_cutting_boards = list(filter(
                                lambda cutting_board: not cutting_board.content and \
                                    cutting_board.x > constants.PASSING_TABLE_X,
                                self.current_game_info['cutting_boards']    
                            ))
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                list(map(
                                    lambda cutting_board: (cutting_board.x, cutting_board.y),
                                    right_side_empty_cutting_boards
                                ))
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT, 
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PASS_C:
                if not own_chef.held_item:
                    # Get c
                    right_side_c_ingredients = list(filter(
                        lambda ingredient: \
                            ingredient.name == game_constants.INGREDIENT_C_NAME and \
                            ingredient.x > constants.PASSING_TABLE_X,
                        unbound_ingredients
                    ))
                    if right_side_c_ingredients:
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda c: (c.x, c.y),
                                right_side_c_ingredients
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                    else:
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                ingredient_boxes[game_constants.INGREDIENT_C_NAME].x,
                                ingredient_boxes[game_constants.INGREDIENT_C_NAME].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_USE,
                                    nearest_path['direction']
                                )
                else:
                    # Pass c
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_passing_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PASS_DIRTY_PLATE:
                if not own_chef.held_item:
                    # Get dirty plate
                    if self.current_game_info['return_counter'].content:
                        nearest_path = self.__a_star(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            (
                                self.current_game_info['return_counter'].x, 
                                self.current_game_info['return_counter'].y
                            )
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    # Pass dirty plate
                    if isinstance(own_chef.held_item, Plate):
                        if own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_passing_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_COOK_MIXED_BOWL:
                if not own_chef.held_item:
                    not_cooked_contain_mix_cookable_containers = list(filter(
                        lambda cookable_container: len(cookable_container.contents) == 2 and \
                            not cookable_container.is_cooked,
                        self.current_game_info['cookable_containers']
                    ))
                    not_cooked_not_on_stove_contain_mix_cookable_containers = [
                        cookable_container for cookable_container in \
                        not_cooked_contain_mix_cookable_containers if cookable_container \
                        not in on_stove_cookable_containers
                    ]
                    # Get not cooked cookable container that contains mix from table
                    if not_cooked_not_on_stove_contain_mix_cookable_containers:
                        max_progress = max(cookable_container.progress for \
                            cookable_container in \
                            not_cooked_not_on_stove_contain_mix_cookable_containers)
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda cookable_container: (
                                    cookable_container.x,
                                    cookable_container.y
                                ),
                                list(filter(
                                    lambda cookable_container: \
                                        cookable_container.progress == max_progress,
                                    not_cooked_not_on_stove_contain_mix_cookable_containers
                                ))
                            ))
                        )
                    # Get mixed bowl
                    else:
                        right_side_mixed_bowls = list(filter(
                            lambda bowl: bowl.is_mixed and \
                                bowl.x >= constants.PASSING_TABLE_X,
                            self.current_game_info['bowls']
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda bowl: (bowl.x, bowl.y), right_side_mixed_bowls))
                        )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Put cookable container on empty stove
                    if isinstance(own_chef.held_item, CookableContainer):
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_stove_positions
                        )
                    elif isinstance(own_chef.held_item, Bowl):
                        # Put bowl into cookable container
                        if own_chef.held_item.is_mixed:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_cookable_container_positions
                            )
                        # Return empty bowl
                        else:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_passing_table_positions
                            )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PUT,
                                nearest_path['direction']
                            )
                            
            elif action == constants.ACTION_COOK_B:
                if not own_chef.held_item:
                    not_cooked_contain_b_cookable_containers = list(filter(
                        lambda cookable_container: len(cookable_container.contents) == 1 and \
                            not cookable_container.is_cooked,
                        self.current_game_info['cookable_containers']
                    ))
                    not_cooked_not_on_stove_contain_b_cookable_containers = [
                        cookable_container for cookable_container in \
                        not_cooked_contain_b_cookable_containers if cookable_container \
                        not in on_stove_cookable_containers
                    ]
                    # Get cooking container that contains b from table
                    if not_cooked_not_on_stove_contain_b_cookable_containers:
                        max_progress = max(cookable_container.progress for \
                            cookable_container in \
                            not_cooked_not_on_stove_contain_b_cookable_containers)
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda cookable_container: (
                                    cookable_container.x,
                                    cookable_container.y
                                ),
                                list(filter(
                                    lambda cookable_container: \
                                        cookable_container.progress == max_progress,
                                    not_cooked_not_on_stove_contain_b_cookable_containers
                                ))
                            ))
                        )
                    # Get cut b
                    else:
                        cut_b_ingredients = list(filter(
                            lambda ingredient: \
                                ingredient.name == game_constants.INGREDIENT_B_NAME and \
                                ingredient.processes_done,
                            unbound_ingredients
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda b: (b.x, b.y), cut_b_ingredients))
                        )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK, 
                                nearest_path['direction']
                            )
                else:
                    # Put cookable container on empty stove
                    if isinstance(own_chef.held_item, CookableContainer):
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_stove_positions
                        )
                    # Put cut b into empty cookable container
                    elif isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME and \
                                own_chef.held_item.processes_done:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_cookable_container_positions
                            )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PUT, 
                                nearest_path['direction']
                            )
            
            elif action == constants.ACTION_PLATE_MIX:
                contain_mix_cooked_cookable_container = list(filter(
                    lambda cookable_container: cookable_container.is_cooked and \
                        len(cookable_container.contents) == 2,
                    self.current_game_info['cookable_containers']
                ))
                if contain_mix_cooked_cookable_container:
                    if not own_chef.held_item:
                        # Get empty clean plate
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            right_side_empty_clean_plate_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                    else:
                        # Plate mix
                        if isinstance(own_chef.held_item, Plate):
                            if not own_chef.held_item.is_dirty:
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda cookable_container: (
                                            cookable_container.x,
                                            cookable_container.y
                                        ), 
                                        contain_mix_cooked_cookable_container
                                    ))
                                )
                                if nearest_path:
                                    if nearest_path['distance'] == 0:
                                        return "%s %s" % (
                                            game_constants.ACTION_PUT,
                                            nearest_path['direction']
                                        )
            
            elif action == constants.ACTION_PLATE_B:
                contain_b_cooked_cookable_container = list(filter(
                    lambda cookable_container: cookable_container.is_cooked and \
                        len(cookable_container.contents) == 1,
                    self.current_game_info['cookable_containers']
                ))
                if contain_b_cooked_cookable_container:
                    if not own_chef.held_item:
                        # Get empty clean plate
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            right_side_empty_clean_plate_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                    else:
                        # Plate b
                        if isinstance(own_chef.held_item, Plate):
                            if not own_chef.held_item.is_dirty:
                                nearest_path = self.__get_nearest_path(
                                    self.current_game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda cookable_container: (
                                            cookable_container.x,
                                            cookable_container.y
                                        ),
                                        contain_b_cooked_cookable_container
                                    ))
                                )
                                if nearest_path:
                                    if nearest_path['distance'] == 0:
                                        return "%s %s" % (
                                            game_constants.ACTION_PUT,
                                            nearest_path['direction']
                                        )

            elif action == constants.ACTION_SUBMIT_MIX:
                if not own_chef.held_item:
                    # Get plate that contains mix
                    contain_mix_plates = list(filter(
                        lambda plate: len(plate.contents) == 2 and not plate.is_dirty,
                        self.current_game_info['plates'] 
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda plate: (plate.x, plate.y), contain_mix_plates))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Submit plate that contains mix
                    if isinstance(own_chef.held_item, Plate):
                        if len(own_chef.held_item.contents) == 2 and \
                                not own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                submission_counter_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_SUBMIT_B:
                if not own_chef.held_item:
                    # Get plate that contains b
                    contain_b_plates = list(filter(
                        lambda plate: len(plate.contents) == 1 and not plate.is_dirty,
                        self.current_game_info['plates'] 
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda plate: (plate.x, plate.y), contain_b_plates))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Submit plate that contains b
                    if isinstance(own_chef.held_item, Plate):
                        if len(own_chef.held_item.contents) == 1 and \
                                not own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                submission_counter_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_PUT_ASIDE_B:
                if not own_chef.held_item:
                    # Get cut b from cutting board
                    if on_cutting_board_b_ingredients:
                        on_cutting_board_cut_b_ingredients = list(filter(
                            lambda b: b.processes_done,
                            on_cutting_board_b_ingredients
                        ))
                        nearest_path == self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda b: (b.x, b.y),
                                on_cutting_board_cut_b_ingredients
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    # Put b on side table
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME and \
                                own_chef.held_item.processes_done:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_right_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_PUT_ASIDE_MIXED_BOWL:
                if not own_chef.held_item:
                    # Get mixed bowl from passing table
                    on_passing_table_mixed_bowl = list(filter(
                        lambda bowl: bowl.is_mixed and bowl.x == constants.PASSING_TABLE_X,
                        self.current_game_info['bowls']
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda bowl: (bowl.x, bowl.y), on_passing_table_mixed_bowl))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Put mixed bowl on side table
                    if isinstance(own_chef.held_item, Bowl):
                        if own_chef.held_item.is_mixed:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_right_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PUT_ASIDE_COOKED_CONTAINER:
                if not own_chef.held_item:
                    # Get cooked on stove cookable container
                    if on_stove_cookable_containers:
                        cooked_on_stove_cookable_containers = list(filter(
                            lambda on_stove_cookable_container: \
                                on_stove_cookable_container.is_cooked,
                            on_stove_cookable_containers
                        ))
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda cookable_container: (
                                    cookable_container.x,
                                    cookable_container.y
                                ),
                                cooked_on_stove_cookable_containers
                            ))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PICK,
                                    nearest_path['direction']
                                )
                else:
                    # Put cookable container on side table
                    if isinstance(own_chef.held_item, CookableContainer):
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_right_side_table_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )

            elif action == constants.ACTION_PUT_ASIDE_PLATED_MIX:
                if isinstance(own_chef.held_item, Plate):
                    if len(own_chef.held_item.contents) == 2 and \
                            not own_chef.held_item.is_dirty:
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_right_side_table_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )
            
            elif action == constants.ACTION_PUT_ASIDE_PLATED_B:
                if isinstance(own_chef.held_item, Plate):
                     if len(own_chef.held_item.contents) == 1 and \
                            not own_chef.held_item.is_dirty:
                        nearest_path = self.__get_nearest_path(
                            self.current_game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_right_side_table_positions
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )

            elif action == constants.ACTION_PUT_ASIDE_CLEAN_PLATE:
                if not own_chef.held_item:
                    # Get clean plate from passing table
                    on_passing_table_clean_plate = list(filter(
                        lambda plate: plate.x == constants.PASSING_TABLE_X and \
                            not plate.is_dirty,
                        self.current_game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(
                            lambda plate: (plate.x, plate.y),
                            on_passing_table_clean_plate
                        ))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    if isinstance(own_chef.held_item, Plate):
                        if len(own_chef.held_item.contents) == 0 and \
                                not own_chef.held_item.is_dirty:
                            nearest_path = self.__get_nearest_path(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_right_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_THROW_AWAY_B:
                if not own_chef.held_item:
                    # Get unprogressed b
                    unprogressed_b_ingredients = list(filter(
                        lambda ingredient: ingredient.progress == 0 and \
                            ingredient.name == game_constants.INGREDIENT_B_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        self.current_game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda b: (b.x, b.y), unprogressed_b_ingredients))
                    )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Throw away unprogressed b
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME and \
                                own_chef.held_item.progress == 0:
                            nearest_path = self.__a_star(
                                self.current_game_info['map'],
                                (own_chef.x, own_chef.y),
                                (
                                    self.current_game_info['garbage_bin'].x,
                                    self.current_game_info['garbage_bin'].y
                                )
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

        if nearest_path:
            return "%s %s" % (
                game_constants.ACTION_DASH if nearest_path['should_dash'] else \
                    game_constants.ACTION_WALK,
                nearest_path['direction']
            )
        else:
            return "do nothing"
    

    def remember(self, state, action, reward, next_state, done):
        pass


    def act(self):
        actions_sort_by_priority_descending = []
        right_side_clean_plates = list(filter(
            lambda plate: plate.x >= constants.PASSING_TABLE_X and not plate.is_dirty,
            self.current_game_info['plates']
        ))
        if self.__side == constants.SIDE_LEFT:
            if len(right_side_clean_plates) <= 2:
                actions_sort_by_priority_descending = [
                    constants.ACTION_PUT_ASIDE_MIXED_BOWL,
                    constants.ACTION_PASS_CLEAN_PLATE,
                    constants.ACTION_WASH_PLATE,
                    constants.ACTION_PASS_MIXED_BOWL,
                    constants.ACTION_MIX_A_AND_C,
                    constants.ACTION_CUT_A,
                ]
            else:
                actions_sort_by_priority_descending = [
                    constants.ACTION_PASS_MIXED_BOWL,
                    constants.ACTION_PASS_CLEAN_PLATE,
                    constants.ACTION_MIX_A_AND_C,
                    constants.ACTION_WASH_PLATE,
                    constants.ACTION_CUT_A,
                    constants.ACTION_PUT_ASIDE_MIXED_BOWL
                ]

            actions_sort_by_priority_descending += [
                constants.ACTION_PUT_ASIDE_DIRTY_PLATE,
                constants.ACTION_PUT_ASIDE_EMPTY_BOWL,
                constants.ACTION_PUT_ASIDE_C,
                constants.ACTION_PUT_ASIDE_A,
                constants.ACTION_THROW_AWAY_A,
                constants.ACTION_THROW_AWAY_C
            ]

        else:
            if len(right_side_clean_plates) <= 2:
                if self.current_game_info['current_orders'][0].name == \
                        game_constants.ORDER_A_NAME:
                    actions_sort_by_priority_descending = [
                        constants.ACTION_PLATE_MIX,
                        constants.ACTION_PUT_ASIDE_PLATED_MIX,
                        constants.ACTION_PLATE_B,
                        constants.ACTION_PUT_ASIDE_PLATED_B,
                        constants.ACTION_PUT_ASIDE_COOKED_CONTAINER,
                        constants.ACTION_PASS_DIRTY_PLATE,
                        constants.ACTION_SUBMIT_MIX,
                        constants.ACTION_COOK_MIXED_BOWL,
                        constants.ACTION_PASS_C
                    ]
                else:
                    actions_sort_by_priority_descending = [
                        constants.ACTION_PLATE_B,
                        constants.ACTION_PUT_ASIDE_PLATED_B,
                        constants.ACTION_PLATE_MIX,
                        constants.ACTION_PUT_ASIDE_PLATED_MIX,
                        constants.ACTION_PUT_ASIDE_COOKED_CONTAINER,
                        constants.ACTION_PASS_DIRTY_PLATE,
                        constants.ACTION_SUBMIT_B,
                        constants.ACTION_COOK_B,
                        constants.ACTION_CUT_B
                    ]
            else:
                if self.current_game_info['current_orders'][0].name == \
                        game_constants.ORDER_A_NAME:
                    actions_sort_by_priority_descending = [
                        constants.ACTION_SUBMIT_MIX,
                        constants.ACTION_PLATE_MIX,
                        constants.ACTION_PLATE_B,
                        constants.ACTION_PUT_ASIDE_PLATED_B,
                        constants.ACTION_PUT_ASIDE_PLATED_MIX,
                        constants.ACTION_PUT_ASIDE_COOKED_CONTAINER,
                        constants.ACTION_COOK_MIXED_BOWL,
                        constants.ACTION_PASS_C,
                        constants.ACTION_PASS_DIRTY_PLATE
                    ]
                else:
                    actions_sort_by_priority_descending = [
                        constants.ACTION_SUBMIT_B,
                        constants.ACTION_PLATE_B,
                        constants.ACTION_PLATE_MIX,
                        constants.ACTION_PUT_ASIDE_PLATED_MIX,
                        constants.ACTION_PUT_ASIDE_PLATED_B,
                        constants.ACTION_PUT_ASIDE_COOKED_CONTAINER,
                        constants.ACTION_COOK_B,
                        constants.ACTION_CUT_B,
                        constants.ACTION_PASS_DIRTY_PLATE
                    ]
            
            actions_sort_by_priority_descending += [
                constants.ACTION_PUT_ASIDE_CLEAN_PLATE,
                constants.ACTION_PUT_ASIDE_MIXED_BOWL,
            ]

            if self.current_game_info['current_orders'][0].name == \
                    game_constants.ORDER_A_NAME:
                actions_sort_by_priority_descending += [
                    constants.ACTION_COOK_B,
                    constants.ACTION_CUT_B,
                ]
            else:
                actions_sort_by_priority_descending += [
                    constants.ACTION_COOK_MIXED_BOWL,
                    constants.ACTION_PASS_C,
                ]

            actions_sort_by_priority_descending += [
                constants.ACTION_PUT_ASIDE_B,
                constants.ACTION_THROW_AWAY_B
            ]

        left_side_c = list(filter(
            lambda ingredient: ingredient.name == game_constants.INGREDIENT_C_NAME and \
                ingredient.x <= constants.PASSING_TABLE_X,
            self.current_game_info['ingredients'] 
        ))
        for action in actions_sort_by_priority_descending:
            if action == constants.ACTION_PASS_C and len(left_side_c) >= 2:
                continue
            self.current_action = constants.LEFT_SIDE_ACTION_CHOICES.index(action) if \
                self.__side == constants.SIDE_LEFT else \
                constants.RIGHT_SIDE_ACTION_CHOICES.index(action)
            game_action = self.translate_to_game_action()
            if game_action != "do nothing": return
        self.current_action = 0


    def replay(self, batch_size):
        pass
    

    def load(self, episode):
        pass

    
    def save(self, episode):
        pass