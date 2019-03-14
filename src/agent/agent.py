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
        self.__name = name
        self.__side = side
        self.__memory = deque(maxlen=constants.MEMORY_MAX_LENGTH)
        self.__epsilon = constants.INITIAL_EPSILON
        self.__model = Sequential()

    def __translate_to_state(self, game_info, blackboard_recent_writings):
        state = []
        
        # Add remaining time
        state.append(game_info['remaining_time'])
        
        # Add current orders
        tracked_order_count = 0
        for current_order in game_info['current_orders']:
            """
            Encode order name:
                column 1: is a
                column 2: is b
            """
            if current_order.name == game_constants.INGREDIENT_A_NAME:
                state.append(1)
                state.append(0)
            elif current_order.name == game_constants.INGREDIENT_B_NAME:
                state.append(0)
                state.append(1)
            state.append(current_order.remaining_time)
            tracked_order_count + 1
        # Add padding for empty orders
        for __ in range(constants.SHOULD_TRACK_ORDER_COUNT - tracked_order_count):
            state.append(0)
            state.append(0)
            state.append(0)

        ingredients = game_info['ingredients']
        own_chef = game_info['chefs'][int(self.__name[-1:]) - 1]

        # Add bowls
        for bowl in game_info['bowls']:
            """
            Encode bowl contents:
                column 1: contain 'a'
                column 2: contain 'c'
            """
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                bowl.contents
            )):
                state.append(1)
            else:
                state.append(0)
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_C_NAME,
                bowl.contents
            )):
                state.append(1)
            else:
                state.append(0)
            """
            Encode bowl positions:
                column 1: being carried by self
                column 2: on mixer
                column 3: on passing table
                column 4: on side table
                all 0 means being carried by other
            """
            if bowl.x == own_chef.x and bowl.y == own_chef.y:
                state.append(1)
                state.append(0)
                state.append(0)
                state.append(0)
            elif list(filter(
                lambda mixer: mixer.x == bowl.x and mixer.y == bowl.y,
                game_info['mixers']
            )):
                state.append(0)
                state.append(1)
                state.append(0)
                state.append(0)
            elif bowl.x == constants.PASSING_TABLE_X:
                state.append(0)
                state.append(0)
                state.append(1)
                state.append(0)
            elif list(filter(
                lambda table: table.x == bowl.x and table.y == bowl.y,
                game_info['tables']
            )):
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(1)
            else:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
            state.append(1 if bowl.x < constants.PASSING_TABLE_X else 0)
            state.append(bowl.progress)

            # Filter out ingredients that are in bowl
            for content in bowl.contents:
                ingredients.remove(content)
            
        # Add cookable containers
        for cookable_container in game_info['cookable_containers']:
            """
            Encode cookable container contents:
                column 1: contain 'a'
                column 2: contain 'b'
            """
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                bowl.contents
            )):
                state.append(1)
            else:
                state.append(0)
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_B_NAME,
                bowl.contents
            )):
                state.append(1)
            else:
                state.append(0)
            """
            Encode bowl positions:
                column 1: being carried by self
                column 2: on stove
                column 3: on side table
                all 0 means being carried by other
            """
            if cookable_container.x == own_chef.x and cookable_container.y == own_chef.y:
                state.append(1)
                state.append(0)
                state.append(0)
            elif list(filter(
                lambda mixer: mixer.x == bowl.x and mixer.y == bowl.y,
                game_info['stoves']
            )):
                state.append(0)
                state.append(1)
                state.append(0)
            elif list(filter(
                lambda table: table.x == bowl.x and table.y == bowl.y,
                game_info['tables']
            )):
                state.append(0)
                state.append(0)
                state.append(1)
            else:
                state.append(0)
                state.append(0)
                state.append(0)
            state.append(cookable_container.progress)

            # Filter out ingredients that are in cookable container
            for content in cookable_container.contents:
                ingredients.remove(content)

        # Add plates
        for plate in game_info['plates']:
            """
            Encode plate contents:
                column 1: contain 'a'
                column 2: contain 'b'
            """
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                plate.contents
            )):
                state.append(1)
            else:
                state.append(0)
            if list(filter(
                lambda ingredient: ingredient.name == game_constants.INGREDIENT_B_NAME,
                plate.contents
            )):
                state.append(1)
            else:
                state.append(0)
            """
            Encode plate position:
                column 1: being carried by self
                column 2: on passing table
                column 3: on submission
                column 4: on return
                column 5: on sink
                all 0 means being carried by other
            """
            return_counter = game_info['return_counter']
            sink = game_info['sink']
            if plate.x == own_chef.x and plate.y == own_chef.y:
                state.append(1)
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
            if plate.x == constants.PASSING_TABLE_X:
                state.append(0)
                state.append(1)
                state.append(0)
                state.append(0)
                state.append(0)
            elif plate.x == -1 and plate.y == -1:
                state.append(0)
                state.append(0)
                state.append(1)
                state.append(0)
                state.append(0)
            elif plate.x == return_counter.x and plate.y == return_counter.y:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(1)
                state.append(0)
            elif plate.x == sink.x and plate.y == sink.y:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(1)
            else:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
            state.append(1 if plate.is_dirty else 0)

            # Filter out ingredients that are in plate
            for content in plate.contents:
                ingredients.remove(content)

        # Add ingredients
        ingredient_states = np.zeros(22)
        for ingredient in game_info['ingredients']:
            """
            Encode ingredient counts
            column 1-8: 'a' counts
            column 9-16: 'b' counts
            column 17-22: 'c' counts
            
            column 1-4 & 9-12: not cut
            column 5-8 & 13-16: cut

            column 1, 5, 9, 13: being carried by self
            column 2, 6, 10, 14: on table
            column 3, 7, 11, 15: on cutting board
            column 4, 8, 12, 16: being carried by other

            column 17: being carried by self
            column 18: on passing table
            column 19: on left side table
            column 20: on right side table
            column 21: being carried by other on left side
            column 22: being carried by other on right side
            """
            to_be_modified_state_idx = 0
            if ingredient.name != game_constants.INGREDIENT_C_NAME:
                # Check if name is 'a' or 'b'
                if ingredient.name == game_constants.INGREDIENT_B_NAME:
                    to_be_modified_state_idx += 8
                # Check if cut
                if ingredient.processes_done:
                    to_be_modified_state_idx += 4
                # Check if on table, on cutting board, or being carried
                if ingredient.x == own_chef.x and ingredient.y == own_chef.y:
                    pass
                elif list(filter(
                    lambda table: table.x == ingredient.x and table.y == ingredient.y,
                    game_info['tables']
                )):
                    to_be_modified_state_idx += 1
                elif list(filter(
                    lambda cutting_board: cutting_board.x == ingredient.x and \
                        cutting_board.y == ingredient.y,
                    game_info['cutting_boards']
                )):
                    to_be_modified_state_idx += 2
                else:
                    to_be_modified_state_idx += 3
            elif ingredient.name == game_constants.INGREDIENT_C_NAME:
                to_be_modified_state_idx += 12
                # Check if not being carried by self
                if ingredient.x != own_chef.x or ingredient.y != own_chef.y:
                    # Check if not on table
                    if not list(filter(
                        lambda table: table.x == ingredient.x and table.y == ingredient.y,
                        game_info['tables']
                    )):
                        to_be_modified_state_idx += 2
                    # Check on which side
                    if ingredient.x < constants.PASSING_TABLE_X:
                        to_be_modified_state_idx += 1
                    elif ingredient.x > constants.PASSING_TABLE_X:
                        to_be_modified_state_idx += 2
                        
            ingredient_states[to_be_modified_state_idx] += 1    
        
        for ingredient_state in ingredient_states:
            state.append(ingredient_state)

        # Add other agents action
        for __, blackboard_recent_writing in blackboard_recent_writings.items():
            action_idx = constants.ALL_ACTION_CHOICES.index(blackboard_recent_writing)
            for idx in range(len(constants.ALL_ACTION_CHOICES)):
                state.append(1 if idx == action_idx else 0)

        state = np.reshape(state, [1, constants.STATE_SIZE])
        state = np.ones((1, constants.STATE_SIZE))

        return state


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
        
        map_width = len(current_map[0])
        map_height = len(current_map)

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
                        distance += 1
                    else:
                        found = True
                path = { 'distance': distance }

                if distance > 0:
                    x_direction = current[0] - origin[0]
                    y_direction = current[1] - origin[1]
                else:
                    x_direction = current[0] - destination[0]
                    y_direction = current[1] - destination[1]

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

            # Add walkable to neighbors
            if not current_map[current[1] - 1][current[0] - 1].content:
                neighbors.append((current[0] - 1, current[1] - 1))
            if not current_map[current[1] - 1][current[0]].content:
                neighbors.append((current[0], current[1] - 1))
            if not current_map[current[1] - 1][current[0] + 1].content:
                neighbors.append((current[0] + 1, current[1] - 1))
            if not current_map[current[1]][current[0] - 1].content:
                neighbors.append((current[0] - 1, current[1]))
            if not current_map[current[1]][current[0] + 1].content:
                neighbors.append((current[0] + 1, current[1]))
            if not current_map[current[1] + 1][current[0] - 1].content:
                neighbors.append((current[0] - 1, current[1] + 1))
            if not current_map[current[1] + 1][current[0]].content:
                neighbors.append((current[0], current[1] + 1))
            if not current_map[current[1] + 1][current[0] + 1].content:
                neighbors.append((current[0] + 1, current[1] + 1))

            # Add dashable to neighbors
            dash_distance = game_constants.DASH_DISTANCE
            while current[0] - dash_distance < 0 or current[1] - dash_distance < 0:
                dash_distance -= 1
            while dash_distance > 1 and \
                    current_map[current[1] - dash_distance][current[0] - dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] - dash_distance, current[1] - dash_distance))

            dash_distance = game_constants.DASH_DISTANCE
            while current[1] - dash_distance < 0:
                dash_distance -= 1
            while dash_distance > 1 and current_map[current[1] - dash_distance][current[0]]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0], current[1] - dash_distance))

            dash_distance = game_constants.DASH_DISTANCE
            while current[0] + dash_distance >= map_width or current[1] - dash_distance < 0:
                dash_distance -= 1
            while dash_distance > 1 and \
                    current_map[current[1] - dash_distance][current[0] + dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] + dash_distance, current[1] - dash_distance))

            dash_distance = game_constants.DASH_DISTANCE
            while current[0] - dash_distance < 0:
                dash_distance -= 1
            while dash_distance > 1 and current_map[current[1]][current[0] - dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] - dash_distance, current[1]))

            dash_distance = game_constants.DASH_DISTANCE
            while current[0] + dash_distance >= map_width:
                dash_distance -= 1
            while dash_distance > 1 and current_map[current[1]][current[0] + dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] + dash_distance, current[1]))

            dash_distance = game_constants.DASH_DISTANCE
            while current[0] - dash_distance < 0 or current[1] + dash_distance >= map_height:
                dash_distance -= 1
            while dash_distance > 1 and \
                    current_map[current[1] + dash_distance][current[0] - dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] - dash_distance, current[1] + dash_distance))

            dash_distance = game_constants.DASH_DISTANCE
            while current[1] + dash_distance >= map_height:
                dash_distance -= 1
            while dash_distance > 1 and current_map[current[1] - dash_distance][current[0]]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0], current[1] - dash_distance))

            dash_distance = game_constants.DASH_DISTANCE
            while current[0] + dash_distance >= map_width or \
                    current[1] + dash_distance >= map_height:
                dash_distance -= 1
            while dash_distance > 1 and \
                    current_map[current[1] + dash_distance][current[0] + dash_distance]:
                dash_distance -= 1
            if dash_distance > 1:
                neighbors.append((current[0] + dash_distance, current[1] + dash_distance))

            for neighbor in neighbors:
                if not neighbor in closed_set:
                    if not neighbor in open_set:
                        open_set.append(neighbor)
                    elif g_score[current] + 1 >= g_score[neighbor]:
                        continue
                    came_from[neighbor] = current
                    g_score[neighbor] = g_score[current] + 1
                    f_score[neighbor] = g_score[neighbor] + \
                        abs(destination[0] - neighbor[0]) + \
                        abs(destination[1] - neighbor[1])
    

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


    def __translate_action_to_game_action(self, action, game_info):
        own_chef = game_info['chefs'][int(self.__name[-1:]) - 1]

        bound_ingredients = []
        for container in game_info['chefs'] + \
                game_info['bowls'] + \
                game_info['cookable_containers'] + \
                game_info['plates']:
            bound_ingredients += list(filter(
                lambda ingredient: ingredient.x == container.x and \
                    ingredient.y == container.y,
                game_info['ingredients']
            ))
        unbound_ingredients = [ingredient for ingredient in game_info['ingredients'] \
            if ingredient not in bound_ingredients]

        ingredient_boxes = {}
        for ingredient_box in game_info['ingredient_boxes']:
            ingredient_boxes[ingredient_box.name.lower()] = ingredient_box

        empty_passing_table_positions = list(map(
            lambda table: (table.x, table.y),
            list(filter(
                lambda table: table.x == constants.PASSING_TABLE_X and not table.content,
                game_info['tables']
            ))
        ))

        nearest_path = None
        if self.__side == constants.SIDE_LEFT:
            on_cutting_board_a_ingredients = []
            for cutting_board in game_info['cutting_boards']:        
                on_cutting_board_b_ingredients += list(filter(
                    lambda ingredient: ingredient.x == cutting_board.x and \
                        ingredient.y == cutting_board.y and ingredient.name == \
                        game_constants.INGREDIENT_A_NAME,
                    unbound_ingredients
                ))
            on_mixer_bowls = []
            for mixer in game_info['mixers']:
                on_mixer_bowls += list(filter(
                    lambda bowl: bowl.x == mixer.x and bowl.y == mixer.y,
                    game_info['bowls']
                ))
            empty_left_side_table_positions = list(map(
                lambda table: (table.x, table.y),
                list(filter(
                    lambda table: table.x < constants.PASSING_TABLE_X and not table.content,
                    game_info['tables']
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
                            game_info['map'],
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
                            game_info['map'],
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
                            game_info['map'],
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
                                game_info['cutting_boards']    
                            ))
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
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
                    game_info['bowls']
                ))
                if not own_chef.held_item:
                    not_mixed_full_bowls = list(filter(
                        lambda bowl: len(bowl.contents) == 2 and not bowl.is_mixed and \
                            bowl.x < constants.PASSING_TABLE_X,
                        game_info['bowls']
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
                            game_info['map'],
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
                            cut_a_ingredients = list(filter(
                                lambda ingredient: \
                                    ingredient.name == game_constants.INGREDIENT_A_NAME and \
                                    ingredient.processes_done,
                                unbound_ingredients
                            ))
                            left_side_c_ingredients = list(filter(
                                lambda ingredient: \
                                    ingredient.name == game_constants.INGREDIENT_C_NAME and \
                                    ingredient.x < constants.PASSING_TABLE_X,
                                unbound_ingredients
                            ))
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
                                        lambda a: (a.x, a.y), 
                                        cut_a_ingredients
                                    ))
                                if contain_c_candidate_bowls:
                                    candidate_destinations += list(map(
                                        lambda c: (c.x, c.y),
                                        left_side_c_ingredients
                                    ))
                            else:
                                candidate_destinations = list(map(
                                    lambda ingredient: (ingredient.x, ingredient.y),
                                    cut_a_ingredients + left_side_c_ingredients
                                ))
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
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
                            game_info['mixers']
                        ))
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
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
                                    game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda bowl: (bowl.x, bowl.y),
                                        list(filter(
                                            lambda bowl: bowl.progress == max_progress,
                                            only_contain_c_bowls
                                        ))
                                    ))
                                )
                            else:
                                nearest_path = self.__get_nearest_path(
                                    game_info['map'],
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
                                    game_info['map'],
                                    (own_chef.x, own_chef.y),
                                    list(map(
                                        lambda bowl: (bowl.x, bowl.y),
                                        list(filter(
                                            lambda bowl: bowl.progress == max_progress,
                                            only_contain_a_bowls
                                        ))
                                    ))
                                )
                            else:
                                nearest_path = self.__get_nearest_path(
                                    game_info['map'],
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
                        game_info['bowls']
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                game_info['map'],
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
                        lambda plate: plate.x < constants.PASSING_TABLE_X and not plate.is_dirty,
                        game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                game_info['map'],
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
                    if game_info['sink'].dirty_plates:
                        # Use sink
                        nearest_path = self.__a_star(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            (game_info['sink'].x, game_info['sink'].y)
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
                            lambda plate: plate.x <= constants.PASSING_TABLE_X and plate.is_dirty,
                            game_info['plates']
                        ))
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda plate: (plate.x, plate.y), left_side_dirty_plates))
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )
                else:
                    if isinstance(own_chef.held_item, Plate):
                        #  Put dirty plates into sink
                        nearest_path = self.__a_star(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            (game_info['sink'].x, game_info['sink'].y)
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )

            elif action == constants.ACTION_PUT_ASIDE_A:
                if not own_chef.held_item:
                    # Get a from cutting board
                    if on_cutting_board_a_ingredients:
                        max_progress = max(
                            b.progress for b in on_cutting_board_a_ingredients
                        )
                        nearest_path == self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda a: (a.x, a.y), list(filter(
                                lambda a: a.progress == max_progress,
                                on_cutting_board_a_ingredients
                            ))))
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
                        if own_chef.held_item.name == game_constants.INGREDIENT_A_NAME:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
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
                        game_info['map'],
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
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_left_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PUT_ASIDE_MIXING_BOWL:
                if not own_chef.held_item:
                    # Get most progressed on mixer bowl
                    if on_mixer_bowls:
                        max_progress = max(bowl.progress for bowl in on_mixer_bowls)
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda bowl: (bowl.x, bowl.y),
                                list(filter(
                                    lambda bowl: bowl.progress == max_progress,
                                    on_mixer_bowls
                                ))
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
                            game_info['map'],
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
                        game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda plate: (plate.x, plate.y), on_passing_table_dirty_plates))
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
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_left_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.THROW_AWAY_A:
                if not own_chef.held_item:
                    # Get unprogressed a
                    unprogressed_a_ingredients = list(filter(
                        lambda ingredient: ingredient.progress == 0 and \
                            ingredient.name == game_constants.INGREDIENT_A_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                (game_info['garbage_bin'].x, game_info['garbage_bin'].y)
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.THROW_AWAY_C:
                if not own_chef.held_item:
                    # Get c from passing table
                    left_side_c = list(filter(
                        lambda ingredient: ingredient.x <= constants.PASSING_TABLE_X and \
                            ingredient.name == game_constants.INGREDIENT_C_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            nearest_path = self.__a_star(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                (game_info['garbage_bin'].x, game_info['garbage_bin'].y)
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

        elif self.__side == constants.SIDE_RIGHT:
            on_cutting_board_b_ingredients = []
            for cutting_board in game_info['cutting_boards']:        
                on_cutting_board_b_ingredients += list(filter(
                    lambda ingredient: ingredient.x == cutting_board.x and \
                        ingredient.y == cutting_board.y and ingredient.name == \
                        game_constants.INGREDIENT_B_NAME,
                    unbound_ingredients
                ))
            on_stove_cookable_containers = []
            for stove in game_info['stoves']:
                on_stove_cookable_containers += list(filter(
                    lambda cookable_container: cookable_container.x == stove.x and \
                        cookable_container.y == stove.y,
                    game_info['cookable_containers']
                ))
            empty_right_side_table_positions = list(map(
                lambda table: (table.x, table.y),
                list(filter(
                    lambda table: table.x > constants.PASSING_TABLE_X and not table.content,
                    game_info['tables']
                ))
            ))
            empty_stove_positions = list(map(
                lambda stove: (stove.x, stove.y),
                list(filter(
                    lambda stove: not stove.content,
                    game_info['stoves']
                ))
            ))
            empty_cookable_container_positions = list(map(
                lambda cookable_container: (cookable_container.x, cookable_container.y),
                list(filter(
                    lambda cookable_container: not cookable_container.contents,
                    game_info['cookable_containers']
                ))
            ))
            right_side_empty_clean_plate_positions = list(map(
                lambda plate: (plate.x, plate.y),
                list(filter(
                    lambda plate: len(plate.contents) == 0 and plate.is_clean and \
                        plate.x >= constants.PASSING_TABLE_X ,
                    game_info['plates']                       
                ))
            ))
            submission_counter_positions = list(map(
                lambda submission_counter: (submission_counter.x , submission_counter.y),
                game_info['submission_counters']
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
                            game_info['map'],
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
                            game_info['map']
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
                            game_info['map'],
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
                                game_info['cutting_boards']    
                            ))
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
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
                    nearest_path = self.__a_star(
                        game_info['map'],
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
                                game_info['map'],
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
                    nearest_path = self.__a_star(
                        game_info['map'],
                        (own_chef.x, own_chef.y),
                        (game_info['return_counter'].x, game_info['return_counter'].y)
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
                                game_info['map'],
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
                        game_info['cookable_containers']
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
                            game_info['map'],
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
                            game_info['bowls']
                        ))
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
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
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_stove_positions
                        )
                    elif isinstance(own_chef.held_item, Bowl):
                        if own_chef.held_item.is_mixed:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_cookable_container_positions
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
                        game_info['cookable_containers']
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
                            game_info['map'],
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
                            game_info['map'],
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
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            empty_stove_positions
                        )
                    # Put cut b into empty cookable container
                    elif isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME and \
                                own_chef.held_item.processes_done:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_cookable_container_positions
                            )
                    if nearest_path:
                        if nearest_path['distance'] == 0:
                            return "%s %s" % (
                                game_constants.ACTION_PUT, 
                                nearest_path['direction']
                            )
            
            elif action == consants.ACTION_PLATE_MIX:
                if not own_chef.held_item:
                    # Get empty clean plate
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                        contain_mix_cooked_cookable_container = list(filter(
                            lambda cookable_container: cookable_container.is_cooked and \
                                len(cookable_container.contents) == 2,
                            game_info['cookable_containers']
                        ))
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            contain_mix_cooked_cookable_container
                        )
                        if nearest_path:
                            if nearest_path['distance'] == 0:
                                return "%s %s" % (
                                    game_constants.ACTION_PUT,
                                    nearest_path['direction']
                                )
            
            elif action == constants.ACTION_PLATE_B:
                if not own_chef.held_item:
                    # Get empty clean plate
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                        contain_b_cooked_cookable_container = list(filter(
                            lambda cookable_container: cookable_container.is_cooked and \
                                len(cookable_container.contents) == 1
                        ))
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            contain_b_cooked_cookable_container
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
                        lambda plate: len(plate.contents == 2) and plate.is_clean,
                        game_info['plates'] 
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                own_chef.held_item.is_clean:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                submission_counter_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] = =0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_SUBMIT_B:
                if not own_chef.held_item:
                    # Get plate that contains b
                    contain_b_plates = list(filter(
                        lambda plate: len(plate.contents == 1) and plate.is_clean,
                        game_info['plates'] 
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                own_chef.held_item.is_clean:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                submission_counter_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] = =0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.ACTION_PUT_ASIDE_B:
                if not own_chef.held_item:
                    # Get b from cutting board
                    if on_cutting_board_b_ingredients:
                        max_progress = max(
                            b.progress for b in on_cutting_board_b_ingredients
                        )
                        nearest_path == self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(lambda b: (b.x, b.y), list(filter(
                                lambda b: b.progress == max_progress,
                                on_cutting_board_b_ingredients
                            ))))
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
                        if own_chef.held_item.name == game_constants.INGREDIENT_B_NAME:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
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
                        game_info['bowls']
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(lambda bowl: (bowl.x, bowl.y), on_passing_table_mixed_bowl))
                    )
                    if nearest_path:
                        if nearest_path['distance'] = =0:
                            return "%s %s" % (
                                game_constants.ACTION_PICK,
                                nearest_path['direction']
                            )
                else:
                    # Put mixed bowl on side table
                    if isinstance(own_chef.held_item, Bowl):
                        if own_chef.held_item.is_mixed:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_right_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.ACTION_PUT_ASIDE_COOKABLE_CONTAINER:
                if not own_chef.held_item:
                    # Get most progressed on stove cookable container
                    if on_stove_cookable_containers:
                        max_progress = max(cookable_container.progress for cookable_container in \
                            on_stove_cookable_containers)
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
                            (own_chef.x, own_chef.y),
                            list(map(
                                lambda cookable_container: (
                                    cookable_container.x,
                                    cookable_container.y
                                ),
                                list(filter(
                                    lambda cookable_container: cookable.container.progress == \
                                        max_progress,
                                    on_stove_cookable_containers
                                ))
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
                            game_info['map'],
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
                            own_chef.held_item.is_clean:
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
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
                            own_chef.held_item.is_clean:
                        nearest_path = self.__get_nearest_path(
                            game_info['map'],
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
                        lambda plate: plate.x == game_constants.PASSING_TABLE_X and \
                            plate.is_clean,
                        game_info['plates']
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                own_chef.held_item.is_clean:
                            nearest_path = self.__get_nearest_path(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                empty_right_side_table_positions
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )

            elif action == constants.THROW_AWAY_B:
                if not own_chef.held_item:
                    # Get unprogressed b
                    unprogressed_b_ingredients = list(filter(
                        lambda ingredient: ingredient.progress == 0 and \
                            ingredient.name == game_constants.INGREDIENT_B_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                (game_info['garbage_bin'].x, game_info['garbage_bin'].y)
                            )
                            if nearest_path:
                                if nearest_path['distance'] == 0:
                                    return "%s %s" % (
                                        game_constants.ACTION_PUT,
                                        nearest_path['direction']
                                    )
            
            elif action == constants.THROW_AWAY_C:
                if not own_chef.held_item:
                    # Get c from passing table
                    on_passing_table_c = list(filter(
                        lambda ingredient: ingredient.x == constants.PASSING_TABLE_X and \
                            ingredient.name == game_constants.INGREDIENT_C_NAME,
                        unbound_ingredients
                    ))
                    nearest_path = self.__get_nearest_path(
                        game_info['map'],
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
                    if isinstance(own_chef.held_item, Ingredient):
                        if own_chef.held_item.name == game_constants.INGREDIENT_C_NAME:
                            nearest_path = self.__a_star(
                                game_info['map'],
                                (own_chef.x, own_chef.y),
                                (game_info['garbage_bin'].x, game_info['garbage_bin'].y)
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


    def build_model(self, graph):
        with graph.as_default():
            self.__model.add(Dense(53, input_dim=constants.STATE_SIZE, activation='relu'))
            self.__model.add(Dense(
                len(constants.LEFT_SIDE_ACTION_CHOICES) if self.__side == constants.SIDE_LEFT 
                    else len(constants.RIGHT_SIDE_ACTION_CHOICES), 
                activation='linear'
            ))

            self.__model.compile(loss='mse', optimizer=Adam(lr=constants.LEARNING_RATE))
    

    def remember(self, state, action, reward, next_state, done):
        self.__memory.append((state, action, reward, next_state, done))


    def act(self, game_info, blackboard_recent_writings):
        action_idx = None
        if np.random.rand() <= self.__epsilon:
            action_idx = random.randrange(len(constants.LEFT_SIDE_ACTION_CHOICES) if 
                self.__side == constants.SIDE_LEFT else 
                len(constants.RIGHT_SIDE_ACTION_CHOICES))
        else:
            act_values = self.__model.predict(self.__translate_to_state(
                game_info, 
                blackboard_recent_writings
            ))
            action_idx = np.argmax(act_values[0])
        return self.__translate_action_to_game_action(
            constants.LEFT_SIDE_ACTION_CHOICES[action_idx] if \
                self.__side == constants.SIDE_LEFT else \
                constants.RIGHT_SIDE_ACTION_CHOICES[action_idx],
            game_info
        )


    def replay(self, batch_size):
        minibatch = random.sample(self.__memory, batch_size)

        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + constants.GAMMA * 
                    np.amax(self.__model.predict(next_state)[0]))
            target_f = self.__model.predict(state)
            target_f[0][action] = target

            self.__model.fit(state, target_f, epochs=1, verbose=0)

        if self.__epsilon > constants.MINIMUM_EPSILON:
            self.__epsilon *= constants.EPSILON_DECAY
    

    def load(self):
        self.__model.load_weights(self.__name)

    
    def save(self):
        self.__model.save_weights(self.__name)
