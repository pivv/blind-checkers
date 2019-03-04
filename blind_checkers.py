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
                locals()[k] = getattr(module, k)

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

# Load agents.
if AGENT_DARK == 'Human':
    agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule, graphics)
else:
    agent_dark = globals()[AGENT_DARK + 'Agent'](1, rule)

if AGENT_LIGHT == 'Human':
    agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule, graphics)
else:
    agent_light = globals()[AGENT_LIGHT + 'Agent'](-1, rule)

# Main loop.
env = Checkers(rule, graphics=graphics, visualize=VISUALIZE, visualize_type=VISUALIZE_TYPE)

player, obs, moves, info = env.reset()
env.print("Game Start", font_size=72)
done = 0

while done == 0:
    if player == 1:
        current_agent = agent_dark
    else:
        assert(player == -1)
        current_agent = agent_light

    action = current_agent.act(obs, moves, info)
    player, obs, moves, rew, done, info = env.step(action)
    current_agent.consume(rew)

    env.render()

    if done > 0: # game is ended.
        if done == 2: # draw
            env.print("Draw", font_size=72)
        else:
            assert(done == 1)
            env.print("{} Win".format(current_agent), font_size=56)
        if REPEAT_EPISODES:
            player, obs, moves, info = env.reset()
            env.print("Game Start", font_size=72)
            done = 0

env.close()
