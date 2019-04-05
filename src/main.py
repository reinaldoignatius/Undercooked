import os
import time

from osbrain import run_nameserver
from osbrain import run_agent

import tensorflow as tf

from world import World
from blackboard_system import BlackboardSystem
from agent.agent import Agent
from agent import constants as agent_constants

actions = {}

MESSAGE_TYPE_READ = 'read'
MESSAGE_TYPE_WRITE = 'write'

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

    # global actions
    # undercooked_message = {}
    # undercooked_message['sender'] = agent.name
    # if actions[agent.name]: 
    #     undercooked_message['action'] = actions[agent.name].pop(0)
    # else:
    #     undercooked_message['action'] = 'idle'

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

def game_handler(agent, message):
    agent.log_info('Execute action: %s %s' % (message['sender'], message['action']))
    agent.world.handle_action(message['sender'], message['action'])

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

def dummy_handler(agent, message):
    pass

def remember_last_state(agent, reward, current_game_info, blackboard_system):
    agent.remember(
        agent.current_state,
        agent.current_action,
        reward - (agent_constants.IDLE_PENALTY if agent.current_action == 0 else 0),
        agent.translate_to_state(
            current_game_info,
            blackboard_system.read_recent_writings(agent.name)
        ),
        True
    )

if __name__ == '__main__':

    level_name = 'level_1'
    number_of_chefs = 4
    # with open('action_sets/action_set_1') as infile:
    #     actions['chef_1'] = [line.rstrip() for line in infile.readlines()]
    # with open('action_sets/action_set_4') as infile:
    #     actions['chef_4'] = [line.rstrip() for line in infile.readlines()]

    # Setup agents
    ns = run_nameserver()
    undercooked = run_agent('undercooked')
    chef_1 = run_agent('chef_1')
    chef_2 = run_agent('chef_2')
    chef_3 = run_agent('chef_3')
    chef_4 = run_agent('chef_4')
    blackboard = run_agent('blackboard')

    # Connect chefs to Undercooked
    undercooked_addr = undercooked.bind(
        'SYNC_PUB',
        alias='undercooked',
        handler=game_handler
    )
    chef_1.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    chef_2.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    chef_3.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    chef_4.connect(undercooked_addr, alias='undercooked', handler=chef_handler)

    # Connect chefs to Blackboard System
    blackboard_addr = blackboard.bind('REP', alias='blackboard', handler=blackboard_handler)
    chef_1.connect(blackboard_addr, alias='blackboard')
    chef_2.connect(blackboard_addr, alias='blackboard')
    chef_3.connect(blackboard_addr, alias='blackboard')
    chef_4.connect(blackboard_addr, alias='blackboard')

    # Setup Chef agents
    chef_1.agent = Agent('chef_1', agent_constants.SIDE_LEFT, tf.Graph())
    chef_2.agent = Agent('chef_2', agent_constants.SIDE_RIGHT, tf.Graph())
    chef_3.agent = Agent('chef_3', agent_constants.SIDE_LEFT, tf.Graph())
    chef_4.agent = Agent('chef_4', agent_constants.SIDE_RIGHT, tf.Graph())

    for episode in range(agent_constants.EPISODES_COUNT):
        # Setup Undercooked world
        world = World()
        world.load_level(level_name, number_of_chefs)
        undercooked.world = world

        # Setup BlackBoard system
        blackboard_system = BlackboardSystem(number_of_chefs)
        blackboard.blackboard_system = blackboard_system

        chef_1.agent.current_game_info = {}
        chef_2.agent.current_game_info = {}
        chef_3.agent.current_game_info = {}
        chef_4.agent.current_game_info = {}

        while not world.is_done:
            # os.system('clear')
            world.print_all_game_info()
            undercooked.world = world
            undercooked.send('undercooked', world.get_all_game_info())
            time.sleep(0.5)
            world = undercooked.world
            world.simulate()

        current_game_info = world.get_all_game_info()
        
        print('Episode: %d, Score: %d, Epsilon: %f' % (
            episode,
            current_game_info['obtained_reward'],
            chef_1.agent.epsilon
        ))

        reward = current_game_info['obtained_reward'] - \
            chef_1.agent.current_game_info['obtained_reward']
        reward = -agent_constants.EARLY_FINISH_PENALTY if world.remaining_time > 0 else 0
        
        remember_last_state(
            chef_1.agent,
            reward,
            current_game_info,
            blackboard.blackboard_system
        )
        remember_last_state(
            chef_2.agent,
            reward,
            current_game_info,
            blackboard.blackboard_system
        )
        remember_last_state(
            chef_3.agent,
            reward,
            current_game_info,
            blackboard.blackboard_system
        )
        remember_last_state(
            chef_4.agent,
            reward,
            current_game_info,
            blackboard.blackboard_system
        )

        if len(chef_1.agent.memory) > agent_constants.BATCH_SIZE:
            chef_1.agent.replay(agent_constants.BATCH_SIZE)
            chef_2.agent.replay(agent_constants.BATCH_SIZE)
            chef_3.agent.replay(agent_constants.BATCH_SIZE)
            chef_4.agent.replay(agent_constants.BATCH_SIZE)

        if episode % agent_constants.EPISODES_CHECKPOINT == 0:
            chef_1.agent.save(episode)
            chef_2.agent.save(episode)
            chef_3.agent.save(episode)
            chef_4.agent.save(episode)

    ns.shutdown()