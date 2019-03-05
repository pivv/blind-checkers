""" Stores basic rules for checkers
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

from .constants import *


class Board(object):
    def __init__(self, rule, matrix=None):
        self.rule = rule
        if matrix is None:
            self.matrix = self.init_board()
        else:
            self.matrix = matrix

    def init_board(self):
        # initialize squares and place them in matrix
        matrix = np.zeros((self.rule.board_size, self.rule.board_size), dtype='int')
        for x in range(self.rule.board_size):
            for y in range(self.rule.board_size):
                if ((x % 2 != 0) and (y % 2 == 0)) or ((x % 2 == 0) and (y % 2 != 0)):
                    if y < (self.rule.board_size - 1) // 2:
                        matrix[y, x] = DARK
                    elif y >= self.rule.board_size - (self.rule.board_size - 1) // 2:
                        matrix[y, x] = LIGHT
        self.matrix = matrix
        return matrix

    def flip_pos(self, pos):
        x, y = pos
        return (self.rule.board_size-1-x, self.rule.board_size-1-y)

    def flip_legal_moves(self, legal_moves):
        flipped_legal_moves = []
        for pos in legal_moves:
            flipped_legal_moves.append(self.flip_pos(pos))
        return flipped_legal_moves

    def flip_moves(self, moves):
        flipped_moves = []
        for pos, legal_moves in moves:
            flipped_moves.append((self.flip_pos(pos), self.flip_legal_moves(legal_moves)))
        return flipped_moves

    def blind_board(self, player, flip=False): # player == 1 : DARK, player == -1 : LIGHT
        blind = np.ones((self.rule.board_size, self.rule.board_size), dtype='bool')
        ys, xs = np.where(player * self.matrix > 0)
        for x, y in zip(xs, ys):
            if abs(self.matrix[y, x]) == DARK:
                ystart = max(y-self.rule.sight, 0)
                yend = min(y+self.rule.sight+1, self.rule.board_size)
                xstart = max(x-self.rule.sight, 0)
                xend = min(x+self.rule.sight+1, self.rule.board_size)
                blind[ystart:yend, xstart:xend] = False
                if self.rule.sight == 1: # additional process to capture
                    if 0 <= (y+2*player) < self.rule.board_size:
                        if x-2 >= 0 and player * self.matrix[y+player, x-1] < 0: # opponent at (y+player, x-1)
                            blind[y+2*player, x-2] = False
                        if x+2 < self.rule.board_size and player * self.matrix[y+player, x+1] < 0: # opponent at (y+player, x+1)
                            blind[y+2*player, x+2] = False
                    if self.rule.backward_capture and (0 <= (y-2*player) < self.rule.board_size):
                        if x-2 >= 0 and player * self.matrix[y-player, x-1] < 0: # opponent at (y-player, x-1)
                            blind[y-2*player, x-2] = False
                        if x+2 < self.rule.board_size and player * self.matrix[y-player, x+1] < 0: # opponent at (y-player, x+1)
                            blind[y-2*player, x+2] = False

            elif abs(self.matrix[y, x]) == DARK_KING:
                ystart = max(y-self.rule.king_sight, 0)
                yend = min(y+self.rule.king_sight+1, self.rule.board_size)
                xstart = max(x-self.rule.king_sight, 0)
                xend = min(x+self.rule.king_sight+1, self.rule.board_size)
                blind[ystart:yend, xstart:xend] = False
                sight_moves = self.get_sight_moves((x, y)) # For king, we use sight_moves function for easy implementation.
                for pos in sight_moves:
                    blind[pos[1], pos[0]] = False
        matrix = np.copy(self.matrix)
        if player == -1 and flip:
            matrix = -matrix[::-1, ::-1]
            blind = blind[::-1, ::-1]
        matrix[blind] = BLIND
        return matrix

    def move_index_to_move(self, player, pos, move_index):
        x, y = pos
        if move_index == 0:
            return (x+player, y+player)
        elif move_index == 1:
            return (x-player, y+player)
        elif move_index == 2:
            return (x+player, y-player)
        else:
            assert(move_index == 3)
            return (x-player, y-player)

    def move_index_to_capture_available(self, player, pos, move_index, attack_range):
        move = pos
        capture_flag = False
        for irange in range(attack_range+1):
            if not capture_flag and irange == attack_range: # cannot go
                break
            move = self.move_index_to_move(player, move, move_index)
            x, y = move
            if not self.on_board(move):
                break
            if self.matrix[y, x] == EMPTY:
                if capture_flag:
                    return True
            elif player * self.matrix[y, x] > 0 or abs(self.matrix[y, x]) == DARK_DEAD:  # same team or dead
                break
            else:
                assert(player * self.matrix[y, x] < 0) # opponents
                if capture_flag:
                    break
                else:
                    capture_flag = True
        return False

    def capture_available(self, player):
        ys, xs = np.where(np.bitwise_and(player * self.matrix > 0, np.fabs(self.matrix) != DARK_DEAD))
        for x, y in zip(xs, ys):
            pos = (x, y)
            if abs(self.matrix[y, x]) == DARK:
                attack_range = 1
            else:
                assert(abs(self.matrix[y, x]) == DARK_KING)
                attack_range = self.rule.king_range
            if self.move_index_to_capture_available(player, pos, 0, attack_range):
                return True
            if self.move_index_to_capture_available(player, pos, 1, attack_range):
                return True
            if (abs(self.matrix[y, x]) == DARK and self.rule.backward_capture) or abs(self.matrix[y, x]) == DARK_KING:
                if self.move_index_to_capture_available(player, pos, 2, attack_range):
                    return True
                if self.move_index_to_capture_available(player, pos, 3, attack_range):
                    return True
        return False

    def move_index_to_sight_moves(self, player, pos, move_index, attack_range):
        sight_moves = []
        move = pos
        capture_flag = False
        break_flag = False
        for irange in range(attack_range+1):
            if (break_flag or not capture_flag) and irange == attack_range: # cannot go
                break
            move = self.move_index_to_move(player, move, move_index)
            x, y = move
            if not self.on_board(move):
                break
            sight_moves.append(move)
            if player * self.matrix[y, x] > 0 or abs(self.matrix[y, x]) == DARK_DEAD:  # same team or dead
                break_flag = True
            elif player * self.matrix[y, x] < 0:  # opponents
                if capture_flag:
                    break_flag = True
                else:
                    capture_flag = True
        return sight_moves

    def get_sight_moves(self, pos):
        x, y = pos
        # We only call this function for king!
        assert(abs(self.matrix[y, x]) == DARK_KING)
        player = np.sign(self.matrix[y, x])
        attack_range = self.rule.king_range
        sight_moves = []
        for move_index in range(4):
            sight_moves += self.move_index_to_sight_moves(player, pos, move_index, attack_range)
        return sight_moves

    def move_index_to_legal_moves(self, player, pos, move_index, attack_range, hop):
        legal_moves = []
        move = pos
        capture_flag = False
        for irange in range(attack_range+1):
            if not capture_flag and irange == attack_range: # cannot go
                break
            move = self.move_index_to_move(player, move, move_index)
            x, y = move
            if not self.on_board(move):
                break
            if self.matrix[y, x] == EMPTY:
                if not hop or capture_flag:
                    legal_moves.append(move)
            elif player * self.matrix[y, x] > 0 or abs(self.matrix[y, x]) == DARK_DEAD:  # same team or dead
                break
            else:
                assert(player * self.matrix[y, x] < 0) # opponents
                if capture_flag:
                    break
                else:
                    capture_flag = True
        return legal_moves

    def get_legal_moves(self, pos, hop=False):
        """
        Returns a list of legal move locations from a given set of coordinates (x, y) on the board.
        If that location is empty, then legal_moves() returns an empty list.
        """

        x, y = pos
        if self.matrix[y, x] == EMPTY:
            return []
        player = np.sign(self.matrix[y, x])
        if abs(self.matrix[y, x]) == DARK:
            attack_range = 1
        else:
            assert(abs(self.matrix[y, x]) == DARK_KING)
            attack_range = self.rule.king_range
        legal_moves = []
        legal_moves += self.move_index_to_legal_moves(player, pos, 0, attack_range, hop)
        legal_moves += self.move_index_to_legal_moves(player, pos, 1, attack_range, hop)
        if abs(self.matrix[y, x]) == DARK and self.rule.backward_capture:
            legal_moves += self.move_index_to_legal_moves(player, pos, 2, attack_range, True)
            legal_moves += self.move_index_to_legal_moves(player, pos, 3, attack_range, True)
        elif abs(self.matrix[y, x]) == DARK_KING:
            legal_moves += self.move_index_to_legal_moves(player, pos, 2, attack_range, hop)
            legal_moves += self.move_index_to_legal_moves(player, pos, 3, attack_range, hop)
        return legal_moves

    def get_all_legal_moves(self, player, hop=False, selected_pos=None):
        if self.rule.force_capture and self.capture_available(player):
            hop = True
        ys, xs = np.where(np.bitwise_and(player * self.matrix > 0, np.fabs(self.matrix) != DARK_DEAD))
        moves = []
        for x, y in zip(xs, ys):
            pos = (x, y)
            if selected_pos is None or pos == selected_pos:
                legal_moves = self.get_legal_moves(pos, hop)
                if len(legal_moves) > 0:
                    moves.append((pos, legal_moves))
        return moves

    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from (from_x, from_y) to (to_x, to_y).
        """

        from_x, from_y = from_pos
        to_x, to_y = to_pos
        self.matrix[to_y, to_x] = self.matrix[from_y, from_x]
        assert(abs(to_x - from_x) == abs(to_y - from_y))
        range_x = np.arange(from_x, to_x, int(to_x > from_x) * 2 - 1)
        range_y = np.arange(from_y, to_y, int(to_y > from_y) * 2 - 1)
        self.matrix[from_y, from_x] = EMPTY
        move_spaces = self.matrix[range_y, range_x]
        capture_man = False
        capture_king = False
        if np.all(move_spaces == EMPTY):
            hop = False
        else:
            if np.any(np.fabs(move_spaces) == DARK):
                capture_man = True
            else:
                assert(np.any(np.fabs(move_spaces) == DARK_KING))
                capture_king = True
            move_spaces = np.sign(move_spaces) * DARK_DEAD
            self.matrix[range_y, range_x] = move_spaces
            hop = True
        return hop, capture_man, capture_king

    def remove_dead_pieces(self):
        self.matrix[np.fabs(self.matrix) == DARK_DEAD] = EMPTY
        return self.matrix

    def on_board(self, pos):
        x, y = pos
        return (0 <= x < self.rule.board_size) and (0 <= y < self.rule.board_size)

    def promote(self, pos):
        x, y = pos
        if self.matrix[y, x] == DARK and y == self.rule.board_size-1:
            self.matrix[y, x] = DARK_KING
            return True
        elif self.matrix[y, x] == LIGHT and y == 0:
            self.matrix[y, x] = LIGHT_KING
            return True
        return False
