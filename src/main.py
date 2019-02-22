import os
import time

from osbrain import run_nameserver
from osbrain import run_agent

import tensorflow as tf

from world import World
from blackboard_system import BlackboardSystem
from agent.agent import Agent

actions = {}

MESSAGE_TYPE_READ = 'read'
MESSAGE_TYPE_WRITE = 'write'

def chef_handler(agent, state):
    agent.log_info('Received game state, requesting blackboard writings')
    blackboard_message = {}
    blackboard_message['sender'] = agent.name
    blackboard_message['type'] = MESSAGE_TYPE_READ
    agent.send('blackboard', blackboard_message)
    blackboard_recent_writings = agent.recv('blackboard')
    agent.log_info(blackboard_recent_writings)

    global actions
    undercooked_message = {}
    undercooked_message['sender'] = agent.name
    if actions[agent.name]: 
        undercooked_message['action'] = actions[agent.name].pop(0)
    else:
        undercooked_message['action'] = 'idle'

    blackboard_message['type'] = MESSAGE_TYPE_WRITE
    blackboard_message['plan'] = 'do something'
    agent.send('blackboard', blackboard_message)
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
      return agent.blackboard_system.write(message['sender'], message['plan'])

def dummy_handler(agent, message):
    pass

if __name__ == '__main__':

    level_name = 'level_1'
    number_of_chefs = 4
    with open('action_sets/action_set_1') as infile:
        actions['chef_1'] = [line.rstrip() for line in infile.readlines()]
    with open('action_sets/action_set_4') as infile:
        actions['chef_4'] = [line.rstrip() for line in infile.readlines()]

    # Setup agents
    ns = run_nameserver()
    undercooked = run_agent('undercooked')
    chef_1 = run_agent('chef_1')
    chef_2 = run_agent('chef_2')
    chef_3 = run_agent('chef_3')
    chef_4 = run_agent('chef_4')
    blackboard = run_agent('blackboard')

    # Connect chefs to Undercooked
    undercooked_addr = undercooked.bind('SYNC_PUB', alias='undercooked', handler=game_handler)
    chef_1.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    # chef_2.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    # chef_3.connect(undercooked_addr, alias='undercooked', handler=chef_handler)
    chef_4.connect(undercooked_addr, alias='undercooked', handler=chef_handler)

    # Connect chefs to Blackboard System
    blackboard_addr = blackboard.bind('REP', alias='blackboard', handler=blackboard_handler)
    chef_1.connect(blackboard_addr, alias='blackboard')
    # chef_2.connect(blackboard_addr, alias='blackboard')
    # chef_3.connect(blackboard_addr, alias='blackboard')
    chef_4.connect(blackboard_addr, alias='blackboard')
    
    # Setup Undercooked world
    world = World()
    world.load_level(level_name, number_of_chefs)
    undercooked.world = world

    # Setup BlackBoard system
    blackboard_system = BlackboardSystem(number_of_chefs)
    blackboard.blackboard_system = blackboard_system

    # Setup Chef agents
    graph = tf.get_default_graph()
    chef_1.agent = Agent('chef_1')
    chef_1.agent.build_model(graph)
    # chef_2.agent = Agent('chef_2')
    # chef_2.agent.build_model(graph)
    # chef_3.agent = Agent('chef_3')
    # chef_3.agent.build_model(graph)
    # chef_4.agent = Agent('chef_4')
    # chef_4.agent.build_model(graph)

    while world.remaining_time > 0:
        # os.system('clear')
        world = undercooked.world
        world.simulate()
        undercooked.world = world
        undercooked.send('undercooked', undercooked.world.map)
        time.sleep(1)
        undercooked.world.print_current_map()
        undercooked.world.print_current_orders()
        print('Obtained reward:', undercooked.world.obtained_reward)
        undercooked.world.print_chefs()
        undercooked.world.print_ingredients()
        undercooked.world.print_containers()
        undercooked.world.print_sinks()
        undercooked.world.print_plates()

    # ns.shutdown()