from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from . import constants

def create_model(side):
    model = Sequential()
    model.add(Dense(53, input_dim=constants.STATE_SIZE, activation='relu'))
    model.add(Dense(
        len(constants.LEFT_SIDE_ACTION_CHOICES) if side == constants.SIDE_LEFT 
            else len(constants.RIGHT_SIDE_ACTION_CHOICES), 
        activation='linear'
    ))
    model.compile(loss='mse', optimizer=Adam(lr=constants.LEARNING_RATE))

    return model