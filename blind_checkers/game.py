""" Main environment of checkers game.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import time

from .constants import *
from .board import Board
from .graphics import Graphics

import pygame
import pygame.locals


class Checkers(object):
    """
    The main game control.
    """

    def __init__(self, rule, board=None, graphics = None, visualize=False, visualize_type='no-blind'):
        self.rule = rule

        if board is None:
            self.board = Board(rule)
        else:
            self.board = board
        self.draw_move_count = DRAW_MOVE_COUNT

        self.visualize = visualize
        self.graphics = None
        if self.visualize:
            if graphics is None:
                self.graphics = Graphics(rule)
            else:
                self.graphics = graphics
        # visualize_type is one of 'dark', 'light', 'both', 'no-blind'
        self.visualize_type = visualize_type
        self.min_visualize_time = MIN_VISUALIZE_TIME
        self.print_time = PRINT_TIME

        self.player = -1
        self.selected_pos = None # a board location.
        self.hop = False
        self.capture = False
        self.promotion = False
        self.move_count = 0
        self.last_matrices = []
        self.from_pos, self.to_pos = None, None
        self.visualize_time = time.time()

    def reset(self):
        self.player = -1
        self.selected_pos = None # a board location.
        self.hop = False
        self.capture = False
        self.promotion = False
        self.move_count = 0
        self.last_matrices = []
        self.from_pos, self.to_pos = None, None
        self.visualize_time = time.time()

        self.board.init_board()
        self.render_once()

        player = self.player
        obs = self.board.blind_board(self.player)
        moves = self.get_valid_moves()
        info = {'prev-obs': [], 'move-count': self.move_count}
        return player, obs, moves, info

    def end_turn(self):
        """
        End the turn. Switches the current player.
        end_turn() also checks for and game and resets a lot of class attributes.
        """
        self.board.remove_dead_pieces()
        self.player = -self.player

        if self.capture:  # or self.promotion:  # No reset for promotion.
            self.move_count = 0
        else:
            self.move_count += 1
        self.selected_pos = None
        self.hop = False

    def get_valid_moves(self):
        return self.board.get_all_legal_moves(self.player, self.hop, self.selected_pos)

    def check_for_endgame(self, moves=None):
        """
        Checks to see if a player has run out of moves or pieces.
        """
        if self.move_count == self.draw_move_count:
            return 2
        if moves is None:
            moves = self.get_valid_moves()
        for pos, legal_moves in moves:
            if len(legal_moves) > 0:
                return 0
        return 1

    def step(self, action):
        """obs, rew, done, info = env.step(action)"""
        from_pos, to_pos = action
        self.from_pos, self.to_pos = from_pos, to_pos
        from_x, from_y = from_pos
        to_x, to_y = to_pos

        # update
        last_matrix = self.board.blind_board(-self.player)
        self.last_matrices.append(last_matrix)
        if not (self.player * self.board.matrix[from_y, from_x] > 0 and
            (self.selected_pos is None or self.selected_pos == from_pos) and
            to_pos in self.board.get_legal_moves(from_pos, self.hop)): # error
            self.close()
            raise ValueError('Invalid action.')
        self.hop, self.capture, self.promotion, rew = self.board.move_piece(from_pos, to_pos)
        if not self.hop or self.board.get_legal_moves(to_pos, self.hop) == []:
            self.selected_pos = None
            prev_obs = self.last_matrices
            self.last_matrices = []
            self.end_turn()
        else:
            self.selected_pos = to_pos
            prev_obs = []

        player = self.player
        obs = self.board.blind_board(self.player)
        moves = self.get_valid_moves()
        done = self.check_for_endgame(moves)
        if done > 0:
            self.player = -self.player  # victory player (or draw player) remains.
            player = -player
        rew['win'] = done == 1
        rew['draw'] = done == 2
        info = {'prev-obs': prev_obs, 'move-count': self.move_count}
        return player, obs, moves, rew, done, info

    def render_once(self):
        if self.visualize:
            if self.visualize_type == 'dark':
                self.graphics.update_display(self.board.blind_board(1), None, [])
            elif self.visualize_type == 'light':
                self.graphics.update_display(self.board.blind_board(-1), None, [])
            elif self.visualize_type == 'both':
                self.graphics.update_display(self.board.blind_board(self.player), None, [])
            else:
                assert(self.visualize_type == 'no-blind')
                if self.from_pos is not None:
                    self.graphics.update_display(self.board.matrix, self.from_pos, [self.to_pos])
                else:
                    self.graphics.update_display(self.board.matrix, None, [])

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                self.graphics.close_window()
                sys.exit()

    def render(self):
        if self.visualize:
            elapsed_time = 0.
            while elapsed_time < self.min_visualize_time:
                self.event_loop()
                end_time = time.time()
                elapsed_time = end_time - self.visualize_time
            self.render_once()
            self.visualize_time = time.time()

    def close(self):
        if self.visualize:
            self.graphics.close_window()

    def print(self, message, font_size=None, color=None):
        if self.visualize:
            self.graphics.draw_message(message, font_size, color)
        else:
            print(message)
        start_time = time.time()
        elapsed_time = 0.
        while elapsed_time < self.print_time:
            self.event_loop()
            end_time = time.time()
            elapsed_time = end_time - start_time
        self.visualize_time = time.time()

