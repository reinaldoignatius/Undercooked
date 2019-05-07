import sys
from . import constants
from agent.agent import Agent
from agent.greedy_agent import Agent as GreedyAgent

def init_handler(agent, __):
    if len(sys.argv) > 1:
        if sys.argv[1] == 'greedy':
            agent.agent = GreedyAgent(agent.name, constants.SIDE_LEFT if \
            agent.name[-1:] == '1' or agent.name[-1:] == '3' else \
            constants.SIDE_RIGHT)
            agent.log_info('Greedy agent initiated')
        elif sys.argv[1] == 'load':
            agent.agent = Agent(agent.name, constants.SIDE_LEFT if \
                agent.name[-1:] == '1' or agent.name[-1:] == '3' else \
                constants.SIDE_RIGHT)
            episode = int(sys.argv[2])
            agent.agent.load(episode)
            agent.agent.is_learning = False
            agent.log_info('Loaded agent from episode %d' % episode)

    else:
        agent.agent = Agent(agent.name, constants.SIDE_LEFT if \
            agent.name[-1:] == '1' or agent.name[-1:] == '3' else \
            constants.SIDE_RIGHT)
        agent.log_info('Learning agent initiated')

def action_handler(agent, game_info):
    # agent.log_info('Received game info, requesting blackboard writings')
    
    agent.send('blackboard', {
        'sender': agent.name,
        'type': constants.BLACKBOARD_MESSAGE_TYPE_READ
    })
    blackboard_recent_writings = agent.recv('blackboard')
    # agent.log_info('Received blackboard writings, choosing action')

    last_game_info = agent.agent.current_game_info
    last_state = agent.agent.current_state
    agent.agent.current_game_info = game_info  
    agent.agent.current_state = agent.agent.translate_to_state(
        game_info,
        blackboard_recent_writings
    )

    if agent.agent.is_learning and last_game_info:
        reward = (game_info['obtained_reward'] - last_game_info['obtained_reward']) * \
            constants.REWARD_MULTIPLIER
        reward -= constants.IDLE_PENALTY if agent.agent.current_action == 0 else 0
        agent.agent.remember(
            last_state,
            agent.agent.current_action,
            reward,
            agent.agent.current_state,
            False
        )

    agent.agent.act()

    undercooked_message = {
      'sender': agent.name,
      'action': agent.agent.translate_to_game_action()
    }

    agent.send('blackboard', {
        'sender': agent.name,
        'type': constants.BLACKBOARD_MESSAGE_TYPE_WRITE,
        'plan': agent.agent.current_action
    })
    agent.recv('blackboard')
    # agent.log_info('Wrote to blackboard')
    agent.send('undercooked', undercooked_message, handler=__dummy_handler)
    # agent.log_info('Sent action to Undercooked')

def reset_handler(agent, __):
    agent.agent.current_game_info = {}

def finish_handler(agent, message):
    if agent.agent.is_learning:
        game_info = message['game_info']
        reward = (game_info['obtained_reward'] - agent.agent.current_game_info['obtained_reward']) \
            * constants.REWARD_MULTIPLIER
        reward = -constants.EARLY_FINISH_PENALTY if game_info['remaining_time'] > 0 else 0
            
        agent.log_info('Received game info, requesting blackboard writings')
        
        agent.send('blackboard', {
            'sender': agent.name,
            'type': constants.BLACKBOARD_MESSAGE_TYPE_READ
        })
        blackboard_recent_writings = agent.recv('blackboard')

        agent.agent.remember(
            agent.agent.current_state,
            agent.agent.current_action,
            reward - (constants.IDLE_PENALTY if agent.agent.current_action == 0 else 0),
            agent.agent.translate_to_state(
                game_info,
                blackboard_recent_writings
            ),
            True
        )

        if len(agent.agent.memory) > constants.BATCH_SIZE:
            agent.agent.replay(constants.BATCH_SIZE)
            agent.log_info('Replayed memory')

        if message['episode'] % constants.EPISODES_CHECKPOINT == 0:
            agent.agent.save(message['episode'])
            agent.log_info('Save model')

def __dummy_handler(agent, __):
    pass
