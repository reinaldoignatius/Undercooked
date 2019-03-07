import random
import math
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from . import constants
import constants as game_constants

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

        # Add bowls
        for bowl in game_info['bowls']:
            """
            Encode bowl contents:
                column 1: contain 'a'
                column 2: contain 'c'
            """
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                    bowl.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_C_NAME,
                    bowl.contents):
                state.append(1)
            else:
                state.append(0)
            """
            Encode bowl positions:
                column 1: on mixer
                column 2: on passing table
                column 3: on side table
                all 0 means being carried
            """
            if filter(lambda mixer: mixer.x == bowl.x and mixer.y == bowl.y,
                    game_info['mixers']):
                state.append(1)
                state.append(0)
                state.append(0)
            elif bowl.x == constants.PASSING_TABLE_X:
                state.append(0)
                state.append(1)
                state.append(0)
            elif filter(lambda table: table.x == bowl.x and table.y == bowl.y,
                    game_info['tables']):
                state.append(0)
                state.append(0)
                state.append(1)
            else:
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
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                    bowl.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_B_NAME,
                    bowl.contents):
                state.append(1)
            else:
                state.append(0)
            """
            Encode bowl positions:
                column 1: on stove
                column 2: on side table
                all 0 means being carried
            """
            if filter(lambda mixer: mixer.x == bowl.x and 
                mixer.y == bowl.y, game_info['stoves']):
                state.append(1)
                state.append(0)
            elif filter(lambda table: table.x == bowl.x and 
                table.y == bowl.y, game_info['tables']):
                state.append(0)
                state.append(1)
            else:
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
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME,
                    plate.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == game_constants.INGREDIENT_B_NAME,
                    plate.contents):
                state.append(1)
            else:
                state.append(0)
            """
            Encode plate position:
                column 1: on passing table
                column 2: on submission
                column 3: on return
                column 4: on sink
                all 0 means being carried
            """
            return_counter = game_info['return_counter']
            sink = game_info['sink']
            if plate.x == constants.PASSING_TABLE_X:
                state.append(1)
                state.append(0)
                state.append(0)
                state.append(0)
            elif plate.x == -1 and plate.y == -1:
                state.append(0)
                state.append(1)
                state.append(0)
                state.append(0)
            elif plate.x == return_counter.x and plate.y == return_counter.y:
                state.append(0)
                state.append(0)
                state.append(1)
                state.append(0)
            elif plate.x == sink.x and plate.y == sink.y:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(1)
            else:
                state.append(0)
                state.append(0)
                state.append(0)
                state.append(0)
            state.append(1 if plate.is_dirty else 0)

            # Filter out ingredients that are in plate
            for content in plate.contents:
                ingredients.remove(content)

        # Add ingredients
        ingredient_states = np.zeros(17)
        for ingredient in game_info['ingredients']:
            """
            Encode ingredient counts
            column 1-6: 'a' counts
            column 7-12: 'b' counts
            column 13-17: 'c' counts
            
            column 1-3 & 7-9: not cut
            column 4-6 & 10-12: cut

            column 1, 4, 7, 10: on table
            column 2, 5, 8, 11: on cutting board
            column 3, 8, 9, 12: being carried

            column 13: on passing table
            column 14: on left side table
            column 15: on right side table
            column 16: being carried on left side
            column 17: being carried on right side
            """
            to_be_modified_state_idx = 0
            if ingredient.name != game_constants.INGREDIENT_C_NAME:
                # Check if name is 'a' or 'b'
                if ingredient.name == game_constants.INGREDIENT_B_NAME:
                    to_be_modified_state_idx += 6
                # Check if cut
                if game_constants.PROCESS_CUT in ingredient.processes_done:
                    to_be_modified_state_idx += 3
                # Check if on table, on cutting board, or being carried
                if filter(lambda table: table.x == ingredient.x and 
                    table.y == ingredient.y, game_info['tables']):
                    pass
                elif filter(lambda cutting_board: cutting_board.x == ingredient.x and 
                    cutting_board.y == ingredient.y, game_info['cutting_boards']):
                    to_be_modified_state_idx += 1
                else:
                    to_be_modified_state_idx += 2
            elif ingredient.name == game_constants.INGREDIENT_C_NAME:
                # Check if on table
                if filter(lambda table: table.x == ingredient.x and 
                    table.y == ingredient.y, game_info['tables']):
                    to_be_modified_state_idx += 13
                else:
                    to_be_modified_state_idx += 15
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


    def __a_star(self, map, origin, destination):
        closed_set = []
        open_set = [(origin.x, origin.y)]
        came_from = {}
        
        g_score = {}
        f_score = {}
        for row in map:
            for col in row:
                g_score[(col, row)] = math.inf        
                f_score[(col, row)] = math.inf
        g_score[(origin.x, origin.y)] = 0
        f_score[(origin.x, origin.y)] = abs(destination.x - origin.x) + \
            abs(destination.y - origin.y)

        while not open_set:
            current = min(
                { open_key: f_score[open_key] for open_key in open_set }, 
                key=f_score.get
            )
            if current[0] - 1 == destination.x and current[1] - 1 == destination.y or \
                    current[0] - 1 == destination.x and current[1] == destination.y or \
                    current[0] - 1 == destination.x and current[1] + 1 == destination.y or \
                    current[0] == destination.x and current[1] - 1 == destination.y or \
                    current[0] == destination.x and current[1] + 1 == destination.y or \
                    current[0] + 1 == destination.x and current[1] - 1 == destination.y or \
                    current[0] + 1 == destination.x and current[1] == destination.y or \
                    current[0] + 1 == destination.x and current[1] + 1 == destination.y:
                while current in came_from:
                    current = came_from[current]
                path = { 'distance': len(came_from) }

                x_direction = current.x - origin.x
                y_direction = current.y - origin.y
                if x_direction == -1 and y_direction == -1:
                    path['direction'] = game_constants.DIRECTION_UPPER_LEFT
                elif x_direction == 0 and y_direction == -1:
                    path['direction'] = game_constants.DIRECTION_UP
                elif x_direction == 1 and y_direction == -1:
                    path['direction'] = game_constants.DIRECTION_UPPER_RIGHT
                elif x_direction == -1 and y_direction == 0:
                    path['direction'] == game_constants.DIRECTION_LEFT
                elif x_direction == 1 and y_direction == 0:
                    path['direction'] == game_constants.DIRECTION_RIGHT
                elif x_direction == -1 and y_direction == 1:
                    path['direction'] == game_constants.DIRECTION_LOWER_LEFT
                elif x_direction == 0 and y_direction == 1:
                    path['direction'] == game_constants.DIRECTION_DOWN
                elif x_direction == 1 and y_direction == 1:
                    path['direction'] == game_constants.DIRECTION_LOWER_RIGHT
                
                return path
            
            open_set.remove(current)
            closed_set.remove(current)

            neighbors = []
            if not map[current[0] - 1][current[1] - 1].content:
                neighbors.append((current[0] - 1, current[1] - 1))
            if not map[current[0] - 1][current[1]].content:
                neighbors.append((current[0] - 1, current[1]))
            if not map[current[0] - 1][current[1] + 1].content:
                neighbors.append((current[0] - 1, current[1] + 1))
            if not map[current[0]][current[1] - 1].content:
                neighbors.append((current[0], current[1] - 1))
            if not map[current[0]][current[1] + 1].content:
                neighbors.append((current[0], current[1] + 1))
            if not map[current[0] + 1][current[1] - 1].content:
                neighbors.append((current[0] + 1, current[1] - 1))
            if not map[current[0] + 1][current[1]].content:
                neighbors.append((current[0] + 1, current[1]))
            if not map[current[0] + 1][current[1] + 1].content:
                neighbors.append((current[0] + 1, current[1] + 1))
            
            for neighbor in neighbors:
                if not neighbor in closed_set:
                    if not neighbor in open_set:
                        open_set.append(neighbor)
                    elif g_score[current] + 1 < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = g_score[current] + 1
                        f_score[neighbor] = g_score[neighbor] + \
                            abs(destination.x - neighbor[0]) + \
                            abs(destination.y - neighbor[1])
    

    def __get_closest_path(self, map, origin, destinations):
        chosen_path = None
        for destination in destinations:
            if not chosen_path:
                chosen_path = self.__a_star(map, origin, destination)
            else:
                candidate_path = self.__a_star(map, origin, destination)
                if candidate_path['distance'] < chosen_path['distance']:
                    chosen_path = candidate_path
        return chosen_path


    def __translate_action_to_game_action(self, action_idx, game_info):
        own_chef = game_info['chefs'][int(self.__name[-1:]) - 1]

        not_held_ingredients = game_info['ingredients']
        for chef in game_info['chefs']:
            not_held_ingredients = filter(
                lambda ingredient: ingredient.x == chef.x and ingredient.y == chef.y,
                not_held_ingredients
            )

        a_ingredients = filter(
            lambda ingredient: ingredient.name == game_constants.INGREDIENT_A_NAME, 
            not_held_ingredients
        )
        b_ingredients = filter(
            lambda ingredient: ingredient.name == game_constants.INGREDIENT_B_NAME,
            not_held_ingredients
        )
        c_ingredients = filter(
            lambda ingredient: ingredient.name == game_constants.INGREDIENT_C_NAME,
            not_held_ingredients
        )

        uncut_a_ingredients = filter(
            lambda a_ingredient: not a_ingredient.processes_done, a_ingredients)
        uncut_b_ingredients = filter(
            lambda b_ingredient: not b_ingredient.processes_done, b_ingredients)

        uncut_a_ingredients_on_cutting_board = []
        uncut_b_ingredients_on_cutting_board = []
        for cutting_board in game_info['cutting_boards']:        
            uncut_a_ingredients_on_cutting_board += filter(
                lambda uncut_a: uncut_a.x == cutting_board.x and uncut_a.y == cutting_board.y,
                uncut_a_ingredients
            )
            uncut_a_ingredients_on_cutting_board += filter(
                lambda uncut_b: uncut_b.x == cutting_board.x and uncut_b.y == cutting_board.y,
                uncut_b_ingredients
            )

        uncut_a_ingredients_not_on_cutting_board = [a for a in uncut_a_ingredients \
            if a not in uncut_a_ingredients_on_cutting_board]
        uncut_b_ingredients_not_on_cutting_board = [b for b in uncut_b_ingredients \
            if b not in uncut_b_ingredients_on_cutting_board]

        if self.__side == constants.SIDE_LEFT:
            if action_idx == 0: # Cut a
                if not own_chef.held_item:
                    closest_path = self.__get_closest_path(
                        game_info['map'],
                        (own_chef.x, own_chef.y),
                        list(map(
                            lambda a: (a.x, a.y), 
                            uncut_a_ingredients_on_cutting_board if \
                                uncut_a_ingredients_on_cutting_board else \
                                uncut_a_ingredients_not_on_cutting_board
                        ))
                    )
                    if closest_path['distance'] == 0:
                        return "%s %s" % (
                            game_constants.ACTION_USE, 
                            closest_path['direction']
                        )
                    return "%s %s" % (
                        game_constants.ACTION_WALK,
                        closest_path['direction']
                    )
            elif action_idx == 1: # Mix a and c
        else:
            pass


    def build_model(self, graph):
        with graph.as_default():
            self.__model.add(Dense(51, input_dim=constants.STATE_SIZE, activation='relu'))
            self.__model.add(Dense(
                len(constants.LEFT_SIDE_ACTION_CHOICES) if self.__side == constants.SIDE_LEFT 
                    else len(constants.RIGHT_SIDE_ACTION_CHOICES), 
                activation='linear'
            ))

            self.__model.compile(loss='mse', optimizer=Adam(lr=constants.LEARNING_RATE))
    

    def remember(self, state, action, reward, next_state, done):
        self.__memory.append((state, action, reward, next_state, done))


    def act(self, game_info, blackboard_recent_writings):
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
        return self.__translate_action_to_game_action(action_idx, game_info)


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
