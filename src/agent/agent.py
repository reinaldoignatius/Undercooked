import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from . import constants


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


    def act(self, state):
        if np.random.rand() <= self.__epsilon:
            return random.randrange(constants.ACTION_SIZE)
        act_values = self.__model.predict(state)
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
