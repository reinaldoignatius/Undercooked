EPISODES_COUNT = 1
EPISODES_CHECKPOINT = 5

MEMORY_MAX_LENGTH = 2800

BATCH_SIZE = 3

GAMMA = 0.95

INITIAL_EPSILON = 1.0
EPSILON_DECAY = 0.995
MINIMUM_EPSILON = 0.01

LEARNING_RATE = 0.001

IDLE_PENALTY = 10
EARLY_FINISH_PENALTY = 1000

STATE_SIZE = 176

SHOULD_TRACK_ORDER_COUNT = 4

PASSING_TABLE_X = 9

ACTION_CUT_A = 'cut a'
ACTION_CUT_B = 'cut b'
ACTION_MIX_A_AND_C = 'mix a and c'
ACTION_PASS_C = 'pass c'
ACTION_PASS_MIXED_BOWL = 'pass mixed bowl'
ACTION_PASS_DIRTY_PLATE = 'pass dirty plate'
ACTION_PASS_CLEAN_PLATE = 'pass clean plate'
ACTION_COOK_B = 'cook b'
ACTION_COOK_MIXED_BOWL = 'cook mixed bowl'
ACTION_PLATE_MIX = 'plate mix'
ACTION_PLATE_B = 'plate b'
ACTION_SUBMIT_MIX = 'submit mix'
ACTION_SUBMIT_B = 'submit b'
ACTION_WASH_PLATE = 'wash plate'
ACTION_PUT_ASIDE_A = 'put aside a'
ACTION_PUT_ASIDE_B = 'put aside b'
ACTION_PUT_ASIDE_C = 'put aside c'
ACTION_PUT_ASIDE_EMPTY_BOWL = 'put aside empty bowl'
ACTION_PUT_ASIDE_MIXED_BOWL = 'put aside mixed bowl'
ACTION_PUT_ASIDE_PLATED_MIX = 'put aside plated mix'
ACTION_PUT_ASIDE_PLATED_B = 'put aside plated b'
ACTION_PUT_ASIDE_DIRTY_PLATE = 'put aside dirty plate'
ACTION_PUT_ASIDE_CLEAN_PLATE = 'put aside clean plate'
ACTION_PUT_ASIDE_COOKED_CONTAINER = 'put aside cooked container'
ACTION_THROW_AWAY_A = 'throw away a'
ACTION_THROW_AWAY_B = 'throw away b'
ACTION_THROW_AWAY_C = 'throw away c'

SIDE_LEFT = 'left'
SIDE_RIGHT = 'right'

LEFT_SIDE_ACTION_CHOICES = [
    ACTION_CUT_A,
    ACTION_MIX_A_AND_C,
    ACTION_PASS_MIXED_BOWL,
    ACTION_PASS_CLEAN_PLATE,
    ACTION_WASH_PLATE,
    ACTION_PUT_ASIDE_A,
    ACTION_PUT_ASIDE_C,
    ACTION_PUT_ASIDE_MIXED_BOWL,
    ACTION_PUT_ASIDE_EMPTY_BOWL,
    ACTION_PUT_ASIDE_DIRTY_PLATE,
    ACTION_THROW_AWAY_A,
]

RIGHT_SIDE_ACTION_CHOICES = [
    ACTION_CUT_B,
    ACTION_PASS_C,
    ACTION_PASS_DIRTY_PLATE,
    ACTION_COOK_MIXED_BOWL,
    ACTION_COOK_B,
    ACTION_PLATE_MIX,
    ACTION_PLATE_B,
    ACTION_SUBMIT_MIX,
    ACTION_SUBMIT_B,
    ACTION_PUT_ASIDE_B,
    ACTION_PUT_ASIDE_C,
    ACTION_PUT_ASIDE_MIXED_BOWL,
    ACTION_PUT_ASIDE_COOKED_CONTAINER,
    ACTION_PUT_ASIDE_PLATED_MIX,
    ACTION_PUT_ASIDE_PLATED_B,
    ACTION_PUT_ASIDE_CLEAN_PLATE,
    ACTION_THROW_AWAY_B,
    ACTION_THROW_AWAY_C
]

ALL_ACTION_CHOICES = LEFT_SIDE_ACTION_CHOICES + \
    list(set(RIGHT_SIDE_ACTION_CHOICES) - set(LEFT_SIDE_ACTION_CHOICES))
