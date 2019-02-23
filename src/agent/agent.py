import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from . import constants
import constants as game_constants

class Agent():

    def __init__(self, name):
        self.__name = name
        self.__memory = deque(maxlen=constants.MEMORY_MAX_LENGTH)
        self.__epsilon = constants.INITIAL_EPSILON
        
        self.__model = Sequential()


    def build_model(self, graph):
        with graph.as_default():
            self.__model.add(Dense(45, input_dim=constants.STATE_SIZE, activation='relu'))
            self.__model.add(Dense(constants.ACTION_SIZE, activation='linear'))

            self.__model.compile(loss='mse', optimizer=Adam(lr=constants.LEARNING_RATE))
    

    def remember(self, state, action, reward, next_state, done):
        self.__memory.append((state, action, reward, next_state, done))


    def __translate_to_state(self, game_info, blackboard_recent_writings):
        state = []
        
        # Add remaining time
        state.append(game_info['remaining_time'])
        
        # Add current orders
        tracked_order_count = 0
        for current_order in game_info['current_orders']:
            """
            Encode order name:
                1 if a
                0 if b
            """
            state.append(1 if current_order =='a' else 0)
            state.append(current_order.time)
            tracked_order_count + 1
        # Add padding for empty orders
        for __ in range(constants.SHOULD_TRACK_ORDER_COUNT - tracked_order_count):
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
            if filter(lambda ingredient: ingredient.name == 'a', bowl.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == 'c', bowl.contents):
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
            if filter(lambda mixer: mixer.x == bowl.x and mixer.y == bowl.y, game_info['mixers']):
                state.append(1)
                state.append(0)
                state.append(0)
            elif bowl.x == constants.PASSING_TABLE_X:
                state.append(0)
                state.append(1)
                state.append(0)
            elif filter(lambda table: table.x == bowl.x and table.y == bowl.y, game_info['tables']):
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
            if filter(lambda ingredient: ingredient.name == 'a', bowl.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == 'b', bowl.contents):
                state.append(1)
            else:
                state.append(0)
            """
            Encode bowl positions:
                column 1: on stove
                column 2: on side table
                all 0 means being carried
            """
            if filter(lambda mixer: mixer.x == bowl.x and mixer.y == bowl.y, game_info['stoves']):
                state.append(1)
                state.append(0)
            elif filter(lambda table: table.x == bowl.x and table.y == bowl.y, game_info['tables']):
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
            if filter(lambda ingredient: ingredient.name == 'a', plate.contents):
                state.append(1)
            else:
                state.append(0)
            if filter(lambda ingredient: ingredient.name == 'b', plate.contents):
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
        ingredient_state = np.zeros(17)
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
            if ingredient.name != 'c':
                # Check if name is 'a' or 'b'
                if ingredient.name == 'b':
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
            elif ingredient.name == 'c':
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

        return state


    def act(self, game_info, blackboard_recent_writings):
        state = self.__translate_to_state(game_info, blackboard_recent_writings)
        print(state)
        if np.random.rand() <= self.__epsilon:
            return random.randrange(constants.ACTION_SIZE)
        act_values = self.__model.predict(self.__translate_to_state(game_info, blackboard_recent_writings))
        return np.argmax(act_values[0])


    def replay(self, batch_size):
        minibatch = random.sample(self.__memory, batch_size)

        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + constants.GAMMA * np.amax(self.__model.predict(next_state)[0]))
            target_f = self.__model.predict(state)
            target_f[0][action] = target

            self.__model.fit(state, target_f, epochs=1, verbose=0)

        if self.__epsilon > constants.MINIMUM_EPSILON:
            self.__epsilon *= constants.EPSILON_DECAY
    

    def load(self):
        self.__model.load_weights(self.__name)

    
    def save(self):
        self.__model.save_weights(self.__name)
