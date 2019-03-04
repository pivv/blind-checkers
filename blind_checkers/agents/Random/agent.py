""" Random AI.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import time

from ...constants import *
from ...board import Board
from ...game import Checkers
from ..agent import Agent


class RandomAgent(Agent):
    def __init__(self, player, rule):
        if player == 1:
            name = 'Random_Dark'
        else:
            assert(player == -1)
            name = 'Random_Light'
        super(RandomAgent, self).__init__(name, player, rule)

    def act(self, obs, moves, info):
        random_index1 = int(np.random.random_sample() * len(moves))
        from_pos, legal_moves = moves[random_index1]
        assert(len(legal_moves) > 0)
        random_index2 = int(np.random.random_sample() * len(legal_moves))
        to_pos = legal_moves[random_index2]
        return (from_pos, to_pos)

    def consume(self, rew):
        pass
