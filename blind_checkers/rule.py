""" Stores basic rules for checkers
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np


class Rule(object):
    def __init__(self, args):
        self.board_size = args['board_size'] if 'board_size' in args else 10
        self.sight = args['sight'] if 'sight' in args else 1
        self.king_sight = args['king_sight'] if 'king_sight' in args else 2
        # self.range = args['range'] if 'range' in args else 1
        self.king_range = args['king_range'] if 'king_range' in args else 2
        self.force_capture = args['force_capture'] if 'force_capture' in args else True
        self.backward_capture = args['backward_capture'] if 'backward_capture' in args else True
