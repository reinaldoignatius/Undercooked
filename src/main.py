import os
import time

from osbrain import run_nameserver
from osbrain import run_agent

from world import World

actions = {}

def chef_handler(agent, state):
    agent.log_info('Received game state')
    global actions
    message = {}
    message['sender'] = agent.name
    if actions[agent.name]: 
        message['action'] = actions[agent.name].pop(0)
    else:
        message['action'] = 'do nothing'
    agent.send('undercooked', message, handler=dummy_handler)

def game_handler(agent, message):
    agent.log_info('Execute action: %s %s' % (message['sender'], message['action']))
    agent.world.handle_action(message['sender'], message['action'])

def dummy_handler(agent, message):
    pass

if __name__ == '__main__':

    level_name = 'level_1'
    number_of_players = 4
    with open('action_sets/action_set_1') as infile:
        actions['chef_1'] = [line.rstrip() for line in infile.readlines()]
    with open('action_sets/action_set_4') as infile:
        actions['chef_4'] = [line.rstrip() for line in infile.readlines()]

    ns = run_nameserver()
    undercooked = run_agent('undercooked')
    chef_1 = run_agent('chef_1')
    chef_2 = run_agent('chef_2')
    chef_3 = run_agent('chef_3')
    chef_4 = run_agent('chef_4')

    addr = undercooked.bind('SYNC_PUB', alias='undercooked', handler=game_handler)
    chef_1.connect(addr, alias='undercooked', handler=chef_handler)
    # chef_2.connect(addr, alias='undercooked', handler=chef_handler)
    # chef_3.connect(addr, alias='undercooked', handler=chef_handler)
    chef_4.connect(addr, alias='undercooked', handler=chef_handler)

    # setup world
    world = World()
    world.load_level(level_name, number_of_players)
    undercooked.world = world

    for i in range(len(actions['chef_1'])):
        # os.system('clear')
        world = undercooked.world
        world.simulate()
        undercooked.world = world
        undercooked.send('undercooked', undercooked.world.map)
        time.sleep(0.1)
        undercooked.world.print_current_map()
        undercooked.world.print_current_orders()
        print('Obtained reward:', undercooked.world.obtained_reward)
        undercooked.world.print_chefs()
        undercooked.world.print_ingredients()
        undercooked.world.print_containers()
        undercooked.world.print_sinks()
        undercooked.world.print_plates()

    ns.shutdown()