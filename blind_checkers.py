""" Main loop
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import time

import datetime

from blind_checkers.constants import *
from blind_checkers.rule import Rule
from blind_checkers.board import Board
from blind_checkers.graphics import Graphics
from blind_checkers.game import Checkers

#from blind_checkers.agents.Random.agent import RandomAgent
#from blind_checkers.agents.Greedy.agent import GreedyAgent
#from blind_checkers.agents.Human.agent import HumanAgent

# Import all agents.
# We use this UNCLEAR way to import since arbitrary students can make their own agent in their own folder,
# and then the code to import all of them gets messy.
agent_root = 'blind_checkers/agents/'
agent_paths = []
for agent_dir, _, agent_name_with_exts in os.walk(agent_root):
    if agent_dir == agent_root:
        continue
    for agent_name_with_ext in agent_name_with_exts:
        agent_name = os.path.splitext(agent_name_with_ext)[0]
        if agent_name == 'agent':
            agent_module = agent_dir.replace('/', '.') + '.' + agent_name
            module = __import__(agent_module, globals(), locals(), ['*'])
            for k in dir(module):
                if k != '__name__':
                    locals()[k] = getattr(module, k)


def log_pdn(_log_dir, _pdn, _dark_name, _light_name, _round_number, _player, _done):
    dark_result_symbol, light_result_symbol = '*', '*'
    if _done > 0:  # game is ended.
        if _done == 2:  # draw
            dark_result_symbol, light_result_symbol = 'D', 'D'
        else:
            assert(_done == 1)  # victory
            if _player == 1:
                dark_result_symbol, light_result_symbol = 'W', 'L'
            else:
                dark_result_symbol, light_result_symbol = 'L', 'W'
    log_name = 'round_{}_{}({})_vs_{}({}).txt'.format(str(_round_number).zfill(5),
        _dark_name, dark_result_symbol, _light_name, light_result_symbol)
    with open(os.path.join(_log_dir, log_name), 'w') as f:
        f.write(_pdn)


def replay(_env, _pdn):
    _dark_name, _light_name, _round_number, _player, _matrix, _actions = _env.decode_pdn(_pdn)

    _player, _obs, _moves, _info = _env.reset(_player, _matrix)
    _done = 0

    _env.print("Round {}".format(_round_number), font_size=72)
    _env.print("{}\nvs\n{}".format(_dark_name, _light_name), font_size=56)
    _env.print("Game Start!", font_size=72)

    # Main loop.
    for _action in _actions:
        if _player == 1:
            current_name = _dark_name
        else:
            assert(_player == -1)
            current_name = _light_name

        _player, _obs, _moves, _rew, _done, _info = _env.step(_action)
        _env.render()

        if _done > 0:  # game is ended.
            if _done == 2:  # draw
                _env.print("Draw", font_size=56)
            else:
                assert(_done == 1)
                _env.print("{} Win".format(current_name), font_size=56)

    return _player, _done


def arena(_env, _agent_dark, _agent_light, _round_number=1, _log_dir='./'):
    _player, _obs, _moves, _info = _env.reset()
    _env.reset_pdn(_agent_dark.name, _agent_light.name, _round_number)
    _done = 0

    _env.print("Round {}".format(_round_number), font_size=72)
    _env.print("{}\nvs\n{}".format(_agent_dark, _agent_light), font_size=56)
    _env.print("Game Start!", font_size=72)

    # Main loop.
    while _done == 0:
        if _player == 1:
            current_agent = _agent_dark
        else:
            assert(_player == -1)
            current_agent = _agent_light

        start_time = time.time()
        _action = current_agent.act(_obs, _moves, _info)
        end_time = time.time()
        if current_agent.name[:5] != 'Human' and end_time - start_time > ACTION_TIMEOUT:  # timeout, using random agent
            timeout_agent = RandomAgent(current_agent.player, current_agent.rule)
            _action = timeout_agent.act(_obs, _moves, _info)
        _player, _obs, _moves, _rew, _done, _info = _env.step(_action)
        _env.step_pdn()
        current_agent.consume(_rew)

        _env.render()

        if _done > 0:  # game is ended.
            if _done == 2:  # draw
                _env.print("Draw", font_size=56)
            else:
                assert(_done == 1)
                _env.print("{} Win".format(current_agent), font_size=56)

    log_pdn(_log_dir, _env.get_pdn(), _agent_dark.name, _agent_light.name, _round_number, _player, _done)

    return _player, _done


if __name__ == '__main__':
    # Set rules.
    rule = Rule({
        'board_size': BOARD_SIZE,
        'sight': SIGHT,
        'king_sight': KING_SIGHT,
        'king_range': KING_RANGE,
        'force_capture': FORCE_CAPTURE,
        'backward_capture': BACKWARD_CAPTURE
        })

    # Load graphics.
    graphics = Graphics(rule) if VISUALIZE else None

    # agent_dark = HumanAgent(1, rule, graphics)
    # agent_light = GreedyAgent(-1, rule)

    env = Checkers(rule, graphics=graphics, visualize=VISUALIZE, visualize_type=VISUALIZE_TYPE)
    base_log_dir = './logs/'
    log_dir = os.path.join(base_log_dir, f"{datetime.datetime.now():%Y%m%d%H%M%S}")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if PLAY_MODE == 'match':
        if AGENT_DARK == 'Human':
            agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule, graphics)
        else:
            agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule)
        if AGENT_LIGHT == 'Human':
            agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule, graphics)
        else:
            agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule)

        round_number, dark_win_count, light_win_count, draw_count = 0, 0, 0, 0
        while True:
            round_number += 1
            player, done = arena(env, agent_dark, agent_light, round_number, log_dir)

            if not REPEAT_EPISODES:
                break
            else:  # print records
                if done == 2:  # draw
                    draw_count += 1
                else:
                    assert(done == 1)  # victory
                    if player == 1:
                        dark_win_count += 1
                    else:
                        light_win_count += 1
                env.print("Light : Dark : Draw\n{} : {} : {}".format(light_win_count, dark_win_count, draw_count), font_size=56)

        del agent_dark
        del agent_light

    elif PLAY_MODE == 'league':  # implementation of league matches
        env.visualize_type = 'no-blind'  # Force the type of visualization to observer mode.
        assert('Human' not in LEAGUE_AGENTS)  # AI league is implemented.
        record_table = np.zeros((len(LEAGUE_AGENTS), len(LEAGUE_AGENTS)), dtype='int')
        round_number = 0
        for iagent_dark, AGENT_DARK in enumerate(LEAGUE_AGENTS):
            for iagent_light, AGENT_LIGHT in enumerate(LEAGUE_AGENTS):
                if iagent_dark == iagent_light:  # same player
                    continue
                agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule)
                agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule)

                round_number += 1
                player, done = arena(env, agent_dark, agent_light, round_number, log_dir)

                if done == 2:  # draw
                    record_table[iagent_dark, iagent_light] = 2  # 2 for draw
                else:
                    assert(done == 1)  # victory
                    record_table[iagent_dark, iagent_light] = player  # who wins?

                del agent_dark
                del agent_light

        # Final points
        points = np.zeros((len(LEAGUE_AGENTS),), dtype='int')
        for iagent in range(len(LEAGUE_AGENTS)):
            points[iagent] = (3 * (np.sum(record_table[iagent, :] == 1) + np.sum(record_table[:, iagent] == -1)) +  # 3 point for win
                0 * (np.sum(record_table[iagent, :] == -1) + np.sum(record_table[:, iagent] == 1)) +  # 0 point for lose
                1 * (np.sum(record_table[iagent, :] == 2) + np.sum(record_table[:, iagent] == 2)))  # 1 point for draw
        sorted_agents = [LEAGUE_AGENTS[iagent] for iagent in np.argsort(np.argsort(-points))]

        # This is the function for scoring the term project, so use built-in print function.
        print(record_table)
        print(points)
        print(sorted_agents)

    elif PLAY_MODE == 'replay':  # replay mode
        pdn_path = os.path.join(base_log_dir, REPLAY_NAME)
        with open(pdn_path, 'r') as f:
            pdn = f.read()
        player, done = replay(env, pdn)

    else:
        raise ValueError('Invalid play mode: %s.' % PLAY_MODE)

    env.close()
