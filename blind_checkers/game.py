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

import datetime


class Checkers(object):
    """
    The main game control.
    """

    def __init__(self, rule, board=None, graphics=None, visualize=False, visualize_type='no-blind'):
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
        self.prev_player = -1
        self.done = 0
        self.selected_pos = None # a board location.
        self.hop = False
        self.prev_hop = False
        self.capture_man = False
        self.capture_king = False
        self.promotion = False
        self.turn_count = 0
        self.move_count = 0
        self.last_matrices = []
        self.from_pos, self.to_pos = None, None
        self.visualize_time = time.time()

        self.fen_string = ''
        self.init_pdn_string = ''
        self.pdn_string = ''

        self.moves = None

    def reset(self, player=-1, matrix=None):
        self.player = player
        self.prev_player = player
        self.done = 0
        self.selected_pos = None # a board location.
        self.hop = False
        self.prev_hop = False
        self.capture_man = False
        self.capture_king = False
        self.promotion = False
        self.turn_count = 0
        self.move_count = 0
        self.last_matrices = []
        self.from_pos, self.to_pos = None, None
        self.visualize_time = time.time()

        self.fen_string = ''
        self.init_pdn_string = ''
        self.pdn_string = ''

        if matrix is None:
            self.board.init_board()
        else:
            self.board.matrix[:, :] = matrix[:, :]
        self.render_once()

        self.moves = self.get_valid_moves()

        player = self.player
        obs = self.board.blind_board(self.player)
        moves = self.moves
        info = {'prev-obs': [], 'move-count': self.move_count}
        return player, obs, moves, info

    def end_turn(self):
        """
        End the turn. Switches the current player.
        end_turn() also checks for and game and resets a lot of class attributes.
        """
        self.board.remove_dead_pieces()
        self.promotion = self.board.promote(self.to_pos)
        self.player = -self.player
        if self.player == -1:
            self.turn_count += 1

        if self.capture_man or self.capture_king:  # or self.promotion:  # No reset for promotion.
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
        self.prev_player, self.prev_hop = self.player, self.hop

        if self.moves is not None:
            if not (from_pos in [pos for pos, _ in self.moves]):  # error
                self.close()
                raise ValueError('Invalid action.')
            _, legal_moves = self.moves[[pos for pos, _ in self.moves].index(from_pos)]
            if not to_pos in legal_moves:  # error
                self.close()
                raise ValueError('Invalid action.')

        # update
        last_matrix = self.board.blind_board(-self.player)
        self.last_matrices.append(last_matrix)

        self.hop, self.capture_man, self.capture_king = self.board.move_piece(from_pos, to_pos)
        if not self.hop or self.board.get_legal_moves(to_pos, self.hop) == []:
            self.selected_pos = None
            prev_obs = self.last_matrices
            self.last_matrices = []
            self.end_turn()
        else:
            self.selected_pos = to_pos
            prev_obs = []

        self.moves = self.get_valid_moves()
        self.done = self.check_for_endgame(self.moves)

        player = self.player
        obs = self.board.blind_board(self.player)
        moves = self.moves
        done = self.done
        if done > 0:
            self.player = -self.player  # victory player (or draw player) remains.
            player = -player
        rew = {'capture-man': self.capture_man,
            'capture-king': self.capture_king,
            'win': done == 1,
            'draw': done == 2,
            'promotion': self.promotion}
        info = {'prev-obs': prev_obs, 'move-count': self.move_count}
        return player, obs, moves, rew, done, info

    def render_once(self):
        if self.visualize:
            if self.visualize_type == 'dark':
                self.graphics.update_display(self.board.blind_board(1), None, [], None)
            elif self.visualize_type == 'light':
                self.graphics.update_display(self.board.blind_board(-1), None, [], None)
            elif self.visualize_type == 'both':
                self.graphics.update_display(self.board.blind_board(self.player), None, [], None)
            else:
                assert(self.visualize_type == 'no-blind')
                if self.from_pos is not None:
                    self.graphics.update_display(self.board.matrix, self.from_pos, [self.to_pos], None)
                else:
                    self.graphics.update_display(self.board.matrix, None, [], None)

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
            self.render_once()
            self.graphics.draw_message(message, font_size, color)
            start_time = time.time()
            elapsed_time = 0.
            while elapsed_time < self.print_time:
                self.event_loop()
                end_time = time.time()
                elapsed_time = end_time - start_time
            self.visualize_time = time.time()
        else:
            print(message)

    def step_pdn(self):
        from_board_number = self.board.pos_to_board_number(self.from_pos)
        to_board_number = self.board.pos_to_board_number(self.to_pos)
        if self.prev_player == -1 and not self.prev_hop:  # new turn
            self.pdn_string += '%d. ' % (self.turn_count + 1)
        if not self.prev_hop:
            if self.capture_man or self.capture_king:
                self.pdn_string += '%dx%d' % (from_board_number, to_board_number)
            else:
                self.pdn_string += '%d-%d' % (from_board_number, to_board_number)
        else:
            if self.capture_man or self.capture_king:
                self.pdn_string += 'x%d' % to_board_number
            else:
                self.pdn_string += 'x%d' % to_board_number
        if not self.hop:
            self.pdn_string += ' '
        if self.done > 0:
            if self.done == 2:  # draw
                self.pdn_string += '1/2-1/2'
                self.init_pdn_string += '[Result "1/2-1/2"]\n'
            else:
                assert(self.done == 1)  # victory
                if self.prev_player == 1:
                    self.pdn_string += '0-1'
                    self.init_pdn_string += '[Result "0-1"]\n'
                else:
                    self.pdn_string += '1-0'
                    self.init_pdn_string += '[Result "1-0"]\n'
            self.init_pdn_string += '[GameType "20"]\n'
            self.init_pdn_string += self.fen_string
        return self.pdn_string

    def decode_fen(self, fen_string):
        fen_string_refined = fen_string.split('"')[1]
        fen_string_split = fen_string_refined.split(':')
        if fen_string_split[0].strip() == 'B':
            player = 1
        else:
            assert(fen_string_split[0].strip() == 'W')
            player = -1
        matrix = EMPTY * np.ones((self.rule.board_size, self.rule.board_size), dtype='int')
        assert(fen_string_split[1][0] == 'W')
        light_strings = fen_string_split[1][1:].split(',')
        for light_string in light_strings:
            light_string = light_string.strip()
            if light_string[0] == 'K':
                pos = self.board.board_number_to_pos(int(light_string[1:]))
                matrix[pos[1], pos[0]] = LIGHT_KING
            else:
                pos = self.board.board_number_to_pos(int(light_string))
                matrix[pos[1], pos[0]] = LIGHT
        assert(fen_string_split[2][0] == 'B')
        dark_strings = fen_string_split[2][1:].split(',')
        for dark_string in dark_strings:
            dark_string = dark_string.strip()
            if dark_string[0] == 'K':
                pos = self.board.board_number_to_pos(int(dark_string[1:]))
                matrix[pos[1], pos[0]] = DARK_KING
            else:
                pos = self.board.board_number_to_pos(int(dark_string))
                matrix[pos[1], pos[0]] = DARK
        return player, matrix

    def decode_pdn(self, pdn_string):
        pdn_string_split = pdn_string.splitlines()
        dark_name, light_name, round_number, player, matrix, actions = '', '', 1, -1, None, []
        for pdn_string_sub in pdn_string_split[:-1]:  # last is main pdn string
            if pdn_string_sub[:6] == '[White':  # light name
                light_name = pdn_string_sub.split('"')[1]
            elif pdn_string_sub[:6] == '[Black':  # dark name
                dark_name = pdn_string_sub.split('"')[1]
            elif pdn_string_sub[:6] == '[Round':  # round
                round_number = int(pdn_string_sub.split('"')[1])
            elif pdn_string_sub[:4] == '[FEN':  # fen
                player, matrix = self.decode_fen(pdn_string_sub)
        pdn_string = pdn_string_split[-1]
        pdn_string_split = pdn_string.split()
        for pdn_string_sub in pdn_string_split[:-1]:  # last is for result
            poses = None
            if '-' in pdn_string_sub:
                poses = [self.board.board_number_to_pos(int(s)) for s in pdn_string_sub.split('-')]
            elif 'x' in pdn_string_sub:
                poses = [self.board.board_number_to_pos(int(s)) for s in pdn_string_sub.split('x')]
            if poses is not None:
                for from_pos, to_pos in zip(poses[:-1], poses[1:]):
                    actions.append((from_pos, to_pos))
        return dark_name, light_name, round_number, player, matrix, actions

    def reset_pdn(self, dark_name=None, light_name=None, round_number=1, acquire_fen=False):
        self.init_pdn_string += '[Event ""]\n'
        self.init_pdn_string += '[Site ""]\n'
        self.init_pdn_string += '[Round "%d"]\n' % round_number
        self.init_pdn_string += '[Date "%s"]\n' % f"{datetime.datetime.now():%Y.%m.%d}"
        self.init_pdn_string += '[White "%s"]\n' % light_name
        self.init_pdn_string += '[Black "%s"]\n' % dark_name
        if acquire_fen:
            self.fen_string = self.get_fen()

    def get_pdn(self):
        return self.init_pdn_string + self.pdn_string

    def get_fen(self):
        assert(not self.hop)  # not in middle of capturing
        fen_string = '[FEN "'
        if self.player == 1:
            fen_string += 'B:'
        else:
            fen_string += 'W:'
        fen_string += 'W'
        ys, xs = np.where(self.board.matrix < 0)
        for x, y in zip(xs, ys):
            board_number = self.board.pos_to_board_number((x, y))
            if self.board.matrix[y, x] == LIGHT:
                fen_string += '%d,' % board_number
            else:
                assert(self.board.matrix[y, x] == LIGHT_KING)
                fen_string += 'K%d,' % board_number
        fen_string = fen_string[:-1]
        fen_string += ':B'
        ys, xs = np.where(self.board.matrix > 0)
        for x, y in zip(xs, ys):
            board_number = self.board.pos_to_board_number((x, y))
            if self.board.matrix[y, x] == DARK:
                fen_string += '%d,' % board_number
            else:
                assert(self.board.matrix[y, x] == DARK_KING)
                fen_string += 'K%d,' % board_number
        fen_string = fen_string[:-1]
        fen_string += '"]\n'
        return fen_string
