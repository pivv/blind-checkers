""" Main loop
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import time

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


def arena(_env, _agent_dark, _agent_light):
    player, obs, moves, info = _env.reset()
    _env.print("{}\nvs\n{}".format(_agent_dark, _agent_light), font_size=56)
    _env.print("Game Start!", font_size=72)
    done = 0

    # Main loop.
    while done == 0:
        if player == 1:
            current_agent = _agent_dark
        else:
            assert(player == -1)
            current_agent = _agent_light

        action = current_agent.act(obs, moves, info)
        player, obs, moves, rew, done, info = _env.step(action)
        current_agent.consume(rew)

        _env.render()

        if done > 0:  # game is ended.
            if done == 2:  # draw
                _env.print("Draw", font_size=56)
            else:
                assert(done == 1)
                _env.print("{} Win".format(current_agent), font_size=56)

    return player, done


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

    if not LEAGUE:
        if AGENT_DARK == 'Human':
            agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule, graphics)
        else:
            agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule)
        if AGENT_LIGHT == 'Human':
            agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule, graphics)
        else:
            agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule)

        dark_win_count, light_win_count, draw_count = 0, 0, 0
        while True:
            player, done = arena(env, agent_dark, agent_light)

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
                env.print("Dark : Light : Draw\n{} : {} : {}".format(dark_win_count, light_win_count, draw_count), font_size=56)

    else:  # implementation of league matches
        env.visualize_type = 'no-blind'  # Force the type of visualization to observer mode.
        assert('Human' not in LEAGUE_AGENTS)  # AI league is implemented.
        record_table = np.zeros((len(LEAGUE_AGENTS), len(LEAGUE_AGENTS)), dtype='int')
        for iagent_dark, AGENT_DARK in enumerate(LEAGUE_AGENTS):
            for iagent_light, AGENT_LIGHT in enumerate(LEAGUE_AGENTS):
                if iagent_dark == iagent_light:  # same player
                    continue
                agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule)
                agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule)
                player, done = arena(env, agent_dark, agent_light)
                if done == 2:  # draw
                    record_table[iagent_dark, iagent_light] = 2  # 2 for draw
                else:
                    assert(done == 1)  # victory
                    record_table[iagent_dark, iagent_light] = player  # who wins?

        # Final points
        points = np.zeros((len(LEAGUE_AGENTS),), dtype='int')
        for iagent in range(len(LEAGUE_AGENTS)):
            points[iagent] = (3 * (np.sum(record_table[iagent, :] == 1) + np.sum(record_table[:, iagent] == -1)) +  # 3 point for win
                0 * (np.sum(record_table[iagent, :] == -1) + np.sum(record_table[:, iagent] == 1)) +  # 0 point for lose
                1 * (np.sum(record_table[iagent, :] == 2) + np.sum(record_table[:, iagent] == 2)))  # 1 point for draw
        sorted_agents = [LEAGUE_AGENTS[iagent] for iagent in np.argsort(np.argsort(-points))]
        print(record_table)
        print(points)
        print(sorted_agents)

    env.close()
