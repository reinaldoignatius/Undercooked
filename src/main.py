import time

from osbrain import run_nameserver
from osbrain import run_agent

from world import World

def chef_handler(agent, state):
    agent.log_info('Received game state')
    global actions
    message = {}
    message['sender'] = agent.name
    message['action'] = actions.pop(0)
    agent.send('undercooked', message, handler=dummy_handler)

def game_handler(agent, message):
    agent.log_info('Execute action: %s %s' % (message['sender'], message['action']))
    global world
    world.handle_action(message['sender'], message['action'])
    world.print_current_map()

def dummy_handler(agent, message):
    pass

if __name__ == '__main__':

    # setup world
    world = World()
    level_name = 'level_1'
    number_of_players = 4
    world.load_map(level_name, number_of_players)

    with open('action_sets/action_set_1') as infile:
        actions = [line.rstrip() for line in infile.readlines()]

    ns = run_nameserver()
    undercooked = run_agent('undercooked')
    chef_1 = run_agent('chef_1')
    chef_2 = run_agent('chef_2')
    chef_3 = run_agent('chef_3')
    chef_4 = run_agent('chef_4')

    addr = undercooked.bind('SYNC_PUB', alias='undercooked', handler=game_handler)
    chef_1.connect(addr, alias='undercooked', handler=chef_handler)
    # chef_2.connect(addr, alias='undercooked', handler=chef_handler)
    # chef_3.connect(addr, alias='undercooked', handler=get_game_state)
    # chef_4.connect(addr, alias='undercooked', handler=get_game_state)

    for i in range(len(actions)):
        undercooked.send('undercooked', world.map)

    ns.shutdown()