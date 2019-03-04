""" Greedy AI. You SHOULD beat this AI!
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
from ..Random.agent import RandomAgent


class GreedyAgent(Agent):
    def __init__(self, player, rule, future_count=4, num_simulation=5):
        if player == 1:
            name = 'Greedy_Dark'
        else:
            assert(player == -1)
            name = 'Greedy_Light'
        self.future_count = future_count
        self.num_simulation = num_simulation
        self.sub_agent = RandomAgent(1, rule) # no player specified.
        super(GreedyAgent, self).__init__(name, player, rule)

    def compute_reward(self, last_player, rew):
        r = 0.
        if self.player == last_player:
            r += float(rew['capture_man']) * 1.
            r += float(rew['capture_king']) * 5.
            r += float(rew['promotion']) * 3.
            r += float(rew['win']) * 100.
            r += float(rew['draw']) * 0.  # no point for draw
        else:
            assert(self.player == -last_player)
            r -= float(rew['capture_man']) * 1.
            r -= float(rew['capture_king']) * 5.
            r -= float(rew['promotion']) * 3.
            r -= float(rew['win']) * 100.
            r -= float(rew['draw']) * 0.  # no point for draw
        return r

    def act(self, obs, moves, info):
        scores = []
        actions = []
        for from_pos, legal_moves in moves:
            for to_pos in legal_moves:
                score = 0.
                for _ in range(self.num_simulation):
                    matrix = np.copy(obs)
                    matrix[matrix == BLIND] = EMPTY
                    temp_board = Board(self.rule, matrix)
                    temp_env = Checkers(self.rule, board=temp_board)
                    temp_env.player = self.player
                    temp_env.move_count = info['move-count']
                    action = (from_pos, to_pos)
                    for _ in range(self.future_count):
                        last_player = temp_env.player
                        _, temp_obs, temp_moves, temp_rew, temp_done, temp_info = temp_env.step(action)
                        score += self.compute_reward(last_player, temp_rew)
                        if temp_done > 0:
                            break
                        action = self.sub_agent.act(temp_obs, temp_moves, temp_info)
                    del temp_env
                    del temp_board
                score /= self.num_simulation
                scores.append(score)
                actions.append((from_pos, to_pos))
        scores = np.array(scores)
        max_indices = np.where(scores == np.max(scores))[0]
        random_index = int(np.random.random_sample() * len(max_indices))
        max_index = max_indices[random_index]
        max_action = actions[max_index]
        return max_action

    def consume(self, rew):
        pass
