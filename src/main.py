import os
import time

from osbrain import run_nameserver
from osbrain import run_agent

from world import World
from blackboard_system import BlackboardSystem
from agent.agent import Agent
from agent import constants as agent_constants

UNDERCOOKED_ALIAS = 'undercooked'
BLACKBOARD_ALIAS = 'blackboard'
INIT_ALIAS = 'init'
RESET_ALIAS = 'reset'
FINISH_ALIAS = 'finish'
SAVE_ALIAS = 'save'

CHEF_1_NAME = 'chef_1'
CHEF_2_NAME = 'chef_2'
CHEF_3_NAME = 'chef_3'
CHEF_4_NAME = 'chef_4'

MESSAGE_TYPE_READ = 'read'
MESSAGE_TYPE_WRITE = 'write'

def init_handler(agent, __):
    agent.agent = Agent(agent.name, agent_constants.SIDE_LEFT if \
        agent.name[-1:] == '1' or agent.name[-1:] == '3' else \
        agent_constants.SIDE_RIGHT)
    agent.log_info('Agent initiated')

def chef_handler(agent, game_info):
    agent.log_info('Received game info, requesting blackboard writings')
    
    agent.send('blackboard', {
        'sender': agent.name,
        'type': MESSAGE_TYPE_READ
    })
    blackboard_recent_writings = agent.recv('blackboard')

    last_game_info = agent.agent.current_game_info
    last_state = agent.agent.current_state
    agent.agent.current_game_info = game_info  
    agent.agent.current_state = agent.agent.translate_to_state(
        game_info,
        blackboard_recent_writings
    )

    if last_game_info:
        reward = game_info['obtained_reward'] - last_game_info['obtained_reward']
        reward -= agent_constants.IDLE_PENALTY if agent.agent.current_action == 0 else 0
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
        'type': MESSAGE_TYPE_WRITE,
        'plan': agent.agent.current_action
    })
    agent.recv('blackboard')
    agent.log_info('Wrote to blackboard')
    agent.send('undercooked', undercooked_message, handler=dummy_handler)
    agent.log_info('Sent action to Undercooked')

def blackboard_handler(agent, message):
    if (message['type'] == 'read'):
        return agent.blackboard_system.read_recent_writings(message['sender'])
    else:
        agent.log_info('Wrote: %s %s' % (
            message['sender'],
            agent_constants.LEFT_SIDE_ACTION_CHOICES[message['plan']] if \
                message['sender'][-1:] == '1' or message['sender'][-1:] == '3' else \
                agent_constants.RIGHT_SIDE_ACTION_CHOICES[message['plan']]
        ))
        return agent.blackboard_system.write(message['sender'], message['plan'])

def game_handler(agent, message):
    agent.log_info('Execute action: %s %s' % (message['sender'], message['action']))
    agent.world.handle_action(message['sender'], message['action'])

def reset_handler(agent, __):
    agent.agent.current_game_info = {}

def finish_handler(agent, game_info):
    reward = game_info['obtained_reward'] - agent.agent.current_game_info['obtained_reward']
    reward = -agent_constants.EARLY_FINISH_PENALTY if game_info['remaining_time'] > 0 else 0
        
    agent.log_info('Received game info, requesting blackboard writings')
    
    agent.send('blackboard', {
        'sender': agent.name,
        'type': MESSAGE_TYPE_READ
    })
    blackboard_recent_writings = agent.recv('blackboard')

    agent.agent.remember(
        agent.agent.current_state,
        agent.agent.current_action,
        reward - (agent_constants.IDLE_PENALTY if agent.agent.current_action == 0 else 0),
        agent.agent.translate_to_state(
            game_info,
            blackboard_recent_writings
        ),
        True
    )

    if len(agent.agent.memory) > agent_constants.BATCH_SIZE:
        agent.agent.replay(agent_constants.BATCH_SIZE)

def save_handler(agent, episode):
    agent.agent.save(episode)
    agent.log_info('Save model')

def dummy_handler(agent, __):
    pass

if __name__ == '__main__':

    level_name = 'level_1'
    number_of_chefs = 4
    # Setup agents
    ns = run_nameserver()
    undercooked = run_agent(UNDERCOOKED_ALIAS)
    chefs = {
        CHEF_1_NAME: run_agent(CHEF_1_NAME),
        CHEF_2_NAME: run_agent(CHEF_2_NAME),
        CHEF_3_NAME: run_agent(CHEF_3_NAME),
        CHEF_4_NAME: run_agent(CHEF_4_NAME)
    }
    blackboard = run_agent(BLACKBOARD_ALIAS)

    # Connect agents
    init_addr = undercooked.bind('PUB', alias=INIT_ALIAS)
    undercooked_addr = undercooked.bind(
        'SYNC_PUB',
        alias=UNDERCOOKED_ALIAS,
        handler=game_handler
    )
    blackboard_addr = blackboard.bind(
        'REP',
        alias=BLACKBOARD_ALIAS,
        handler=blackboard_handler
    )
    reset_addr = undercooked.bind('PUB', alias=RESET_ALIAS)
    finish_addr = undercooked.bind('PUB', alias=FINISH_ALIAS)
    save_addr = undercooked.bind('PUB', alias=SAVE_ALIAS)
    for name, chef in chefs.items():
        chef.connect(init_addr, alias=INIT_ALIAS, handler=init_handler)
        chef.connect(undercooked_addr, alias=UNDERCOOKED_ALIAS, handler=chef_handler)
        chef.connect(blackboard_addr, alias=BLACKBOARD_ALIAS)
        chef.connect(reset_addr, alias=RESET_ALIAS, handler=reset_handler)
        chef.connect(finish_addr, alias=FINISH_ALIAS, handler=finish_handler)
        chef.connect(save_addr, alias=SAVE_ALIAS, handler=save_handler)

    undercooked.send(INIT_ALIAS, None)
    time.sleep(1)

    for episode in range(agent_constants.EPISODES_COUNT):
        # Setup Undercooked world
        world = World()
        world.load_level(level_name, number_of_chefs)
        undercooked.world = world

        # Setup BlackBoard system
        blackboard_system = BlackboardSystem(number_of_chefs)
        blackboard.blackboard_system = blackboard_system

        undercooked.send(RESET_ALIAS, None)

        while not world.is_done:
            # os.system('clear')
            # world.print_all_game_info()
            undercooked.world = world
            undercooked.send(UNDERCOOKED_ALIAS, world.get_all_game_info())
            time.sleep(0.5)
            world = undercooked.world
            world.simulate()

        print('Episode: %d, Score: %d' % (
            episode,
            world.get_all_game_info()['obtained_reward'],
        ))

        undercooked.send(FINISH_ALIAS, world.get_all_game_info())
        time.sleep(10)

        if episode % agent_constants.EPISODES_CHECKPOINT == 0:
            undercooked.send(SAVE_ALIAS, episode)
            time.sleep(1)

    ns.shutdown()