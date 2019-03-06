""" Human AI(?).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import time

import pygame
import pygame.locals

from ...constants import *
from ...board import Board
from ...game import Checkers
from ..agent import Agent


class HumanAgent(Agent):
    def __init__(self, player, rule, graphics):
        base_name = 'Human'
        self.graphics = graphics
        super(HumanAgent, self).__init__(base_name, player, rule)

    def act(self, obs, moves, info):
        matrix = obs
        pos_to_legal_moves = dict(moves)
        self.selected_pos = None
        self.selected_legal_moves = []
        self.all_poses = [pos for pos, _ in moves]
        if len(moves) == 1:
            self.selected_pos, self.selected_legal_moves = moves[0]
        while True:
            action = self.event_loop(pos_to_legal_moves)
            self.update(matrix)
            if action is not None:
                return action

    def update(self, matrix):
        """Calls on the graphics class to update the game display."""
        self.graphics.update_display(matrix, self.selected_pos, self.selected_legal_moves, self.all_poses)

    def event_loop(self, pos_to_legal_moves):
        """
        The event loop. This is where events are triggered
        (like a mouse click) and then effect the game state.
        """

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                self.graphics.close_window()
                sys.exit()
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
                if self.mouse_pos in pos_to_legal_moves:
                    self.selected_pos = self.mouse_pos
                    self.selected_legal_moves = pos_to_legal_moves[self.selected_pos]
                elif self.selected_pos != None and self.mouse_pos in pos_to_legal_moves[self.selected_pos]:
                    from_pos = self.selected_pos
                    to_pos = self.mouse_pos
                    return (from_pos, to_pos)
        return None

    def consume(self, rew):
        pass
