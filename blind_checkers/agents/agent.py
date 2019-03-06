""" AI for checkers.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

from abc import ABC
from abc import abstractmethod


class Agent(ABC):
    @abstractmethod
    def __init__(self, base_name, player, rule):
        if player == 1:
            name = base_name + '-Dark'
        else:
            assert(player == -1)
            name = base_name + '-Light'
        self.name = name
        self.player = player
        self.rule = rule

    @abstractmethod
    def act(self, obs, moves, info):
        pass

    @abstractmethod
    def consume(self, rew):
        pass

    def __str__(self):
        return self.name
