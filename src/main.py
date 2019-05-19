import os
import time
import math

from osbrain import run_nameserver
from osbrain import run_agent

from world import World
from blackboard_system import BlackboardSystem
from agent import constants as agent_constants
from agent import handlers as agent_handlers

UNDERCOOKED_ALIAS = 'undercooked'
BLACKBOARD_ALIAS = 'blackboard'
INIT_ALIAS = 'init'
RESET_ALIAS = 'reset'
FINISH_ALIAS = 'finish'

CHEF_1_NAME = 'chef_1'
CHEF_2_NAME = 'chef_2'
CHEF_3_NAME = 'chef_3'
CHEF_4_NAME = 'chef_4'

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
    for name, chef in chefs.items():
        chef.connect(init_addr, alias=INIT_ALIAS, handler=agent_handlers.init_handler)
        chef.connect(
            undercooked_addr,
            alias=UNDERCOOKED_ALIAS,
            handler=agent_handlers.action_handler
        )
        chef.connect(blackboard_addr, alias=BLACKBOARD_ALIAS)
        chef.connect(reset_addr, alias=RESET_ALIAS, handler=agent_handlers.reset_handler)
        chef.connect(finish_addr, alias=FINISH_ALIAS, handler=agent_handlers.finish_handler)

    undercooked.send(INIT_ALIAS, None)
    time.sleep(1)

    min_score = math.inf
    max_score = 0
    total_score = 0
    min_submited_a = math.inf
    max_submited_a = 0
    total_submited_a = 0
    min_submited_b = math.inf
    max_submited_b = 0
    total_submited_b = 0
    min_remaining_time = math.inf
    max_remaining_time = 0
    total_remaining_time = 0
    min_multiplier = math.inf
    max_multiplier = 0
    total_multiplier = 0

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
            world.print_all_game_info()
            undercooked.world = world
            undercooked.send(UNDERCOOKED_ALIAS, world.get_all_game_info())
            time.sleep(0.2)
            world = undercooked.world
            world.simulate()

        score = world.get_all_game_info()['obtained_reward']
        if score < min_score:
            min_score = score
        if score > max_score:
            max_score = score
        total_score += score
        print('Episode: %d, Score: %d, Max multiplier: %d' % (
            episode + 1,
            score,
            world.max_multiplier
        ))

        if world.submited_a_count < min_submited_a:
            min_submited_a = world.submited_a_count
        if world.submited_a_count > max_submited_a:
            max_submited_a = world.submited_a_count            
        total_submited_a += world.submited_a_count

        if world.submited_b_count < min_submited_b:
            min_submited_b = world.submited_b_count
        if world.submited_b_count > max_submited_b:
            max_submited_b = world.submited_b_count
        total_submited_b += world.submited_b_count
        print("Submited a: %d, Submited b: %d" %(
            world.submited_a_count,
            world.submited_b_count
        ))

        remaining_time = world.get_all_game_info()['remaining_time']
        if remaining_time < min_remaining_time:
            min_remaining_time = remaining_time
        if remaining_time > max_remaining_time:
            max_remaining_time = remaining_time
        total_remaining_time += remaining_time

        if world.max_multiplier < min_multiplier:
            min_multiplier = world.max_multiplier
        if world.max_multiplier > max_multiplier:
            max_multiplier = world.max_multiplier
        total_multiplier += world.max_multiplier

        undercooked.send(FINISH_ALIAS, {
            'game_info': world.get_all_game_info(),
            'episode': episode + 1
        })
        time.sleep(10)

    print("Score min: %d, max: %d, total: %d" % (
        min_score,
        max_score,
        total_score
    ))
    print("Submited a min: %d, max: %d, total: %d" % (
        min_submited_a,
        max_submited_a,
        total_submited_a
    ))
    print("Submited b min: %d, max: %d, total: %d" % (
        min_submited_b,
        max_submited_b,
        total_submited_b
    ))
    print("Time min: %d, max: %d, total: %d" % (
        min_remaining_time,
        max_remaining_time,
        total_remaining_time
    ))
    print("Multiplier min: 5d, maax: 5d, total: %d" % (
        min_multiplier,
        max_multiplier,
        total_remaining_time
    ))

    ns.shutdown()
