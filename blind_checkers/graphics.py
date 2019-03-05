""" Implement checkers UI using pygame.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np

import pygame

from .constants import *


class Graphics(object):
    def __init__(self, rule):
        pygame.init()
        pygame.font.init()

        self.caption = CAPTION
        self.rule = rule

        self.clock = pygame.time.Clock()

        self.window_size = WINDOW_SIZE
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))

        self.square_size = self.window_size // self.rule.board_size
        try:
            self.background = pygame.image.load(IMAGE_BOARD)
            self.background = pygame.transform.scale(self.background, (self.window_size, self.window_size))
        except:
            self.background = self.acquire_background()

        try:
            self.piece_size = int(self.square_size * PIECE_RATIO_IMAGE)
            self.dark_piece = pygame.image.load(IMAGE_DARK).convert_alpha()
            self.dark_piece = pygame.transform.scale(self.dark_piece, (self.piece_size, self.piece_size))
            self.dark_king_piece = pygame.image.load(IMAGE_DARK_KING).convert_alpha()
            self.dark_king_piece = pygame.transform.scale(self.dark_king_piece, (self.piece_size, self.piece_size))
            self.light_piece = pygame.image.load(IMAGE_LIGHT).convert_alpha()
            self.light_piece = pygame.transform.scale(self.light_piece, (self.piece_size, self.piece_size))
            self.light_king_piece = pygame.image.load(IMAGE_LIGHT_KING).convert_alpha()
            self.light_king_piece = pygame.transform.scale(self.light_king_piece, (self.piece_size, self.piece_size))
        except:
            self.piece_size = int(self.square_size * PIECE_RATIO_DRAW)
            self.dark_piece = self.acquire_piece(1, False)
            self.dark_king_piece = self.acquire_piece(1, True)
            self.light_piece = self.acquire_piece(-1, False)
            self.light_king_piece = self.acquire_piece(-1, True)

        try:
            self.font = FONT
            test_font = pygame.font.Font(self.font, 10)  # test font
            del test_font
        except:
            self.font = 'freesansbold.ttf'

        self.setup_window()

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def setup_window(self):
        """
        This initializes the window and sets the caption at the top.
        """
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(self.caption)

    def close_window(self):
        pygame.quit()

    def update_display(self, matrix, pos, legal_moves, all_poses):
        """
        This updates the current display.
        """
        self.screen.blit(self.background, (0,0))

        self.draw_blind_squares(matrix)
        self.highlight_squares(None, all_poses, COLOR_HIGH2)
        self.highlight_squares(pos, legal_moves, COLOR_HIGH)
        self.draw_board_pieces(matrix)

        pygame.display.update()
        self.clock.tick(FPS)

    def acquire_background(self):
        surface = pygame.Surface((self.window_size, self.window_size))
        for x in range(self.rule.board_size):
            for y in range(self.rule.board_size):
                if (x+y) % 2 == 0:
                    pygame.draw.rect(surface, COLOR_BACKGROUND1,
                        (x * self.square_size, y * self.square_size, self.square_size, self.square_size))
                else:
                    pygame.draw.rect(surface, COLOR_BACKGROUND2,
                        (x * self.square_size, y * self.square_size, self.square_size, self.square_size))
        return surface

    def acquire_piece(self, player, king):
        surface = pygame.Surface((self.piece_size, self.piece_size), pygame.SRCALPHA, 32)
        if player == 1:
            pygame.draw.circle(surface, COLOR_DARK, (self.piece_size//2, self.piece_size//2), self.piece_size//2)
        else:
            assert(player == -1)
            pygame.draw.circle(surface, COLOR_LIGHT, (self.piece_size//2, self.piece_size//2), self.piece_size//2)
        if king:
            pygame.draw.circle(surface, COLOR_KING, (self.piece_size//2, self.piece_size//2), self.piece_size//4)
        return surface

    def draw_blind_squares(self, matrix):
        ys, xs = np.where(matrix == BLIND)
        for x, y in zip(xs, ys):
            pygame.draw.rect(self.screen, COLOR_BLIND,
                (x * self.square_size, y * self.square_size, self.square_size, self.square_size))

    def draw_board_pieces(self, matrix):
        """
        Takes a board object and draws all of its pieces to the display
        """
        ys, xs = np.where(np.bitwise_and(matrix != 0, matrix != BLIND))
        for y, x in zip(ys, xs):
            if matrix[y, x] == DARK:
                self.screen.blit(self.dark_piece, self.piece_coords((x, y)))
            elif matrix[y, x] == LIGHT:
                self.screen.blit(self.light_piece, self.piece_coords((x, y)))
            elif matrix[y, x] == DARK_KING:
                self.screen.blit(self.dark_king_piece, self.piece_coords((x, y)))
            elif matrix[y, x] == LIGHT_KING:
                self.screen.blit(self.light_king_piece, self.piece_coords((x, y)))
            elif matrix[y, x] == DARK_DEAD:
                self.blit_alpha(self.screen, self.dark_piece, self.piece_coords((x, y)), DEAD_OPACITY)
            elif matrix[y, x] == LIGHT_DEAD:
                self.blit_alpha(self.screen, self.light_piece, self.piece_coords((x, y)), DEAD_OPACITY)

    def piece_coords(self, board_coords):
        pixel_coords = self.pixel_coords(board_coords)
        return (pixel_coords[0] - self.piece_size//2, pixel_coords[1] - self.piece_size//2)

    def pixel_coords(self, board_coords):
        """
        Takes in a tuple of board coordinates (x, y)
        and returns the pixel coordinates of the center of the square at that location.
        """
        return (board_coords[0] * self.square_size + self.square_size//2,
            board_coords[1] * self.square_size + self.square_size//2)

    def board_coords(self, pos):
        """
        Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
        """
        pixel_x, pixel_y = pos
        return (pixel_x // self.square_size, pixel_y // self.square_size)

    def highlight_squares(self, origin, squares, color):
        """
        Squares is a list of board coordinates.
        highlight_squares highlights them.
        """
        if squares is not None:
            for square in squares:
                pygame.draw.rect(self.screen, color,
                    (square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))

        if origin is not None:
            pygame.draw.rect(self.screen, color,
                (origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

    def blur(self, amt):
        """
        Blur the given surface by the given 'amount'.  Only values 1 and greater
        are valid.  Value 1 = no blur.
        """
        if amt < 1.0:
            raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s." % amt)
        surface = self.screen
        scale = 1.0 / float(amt)
        surf_size = surface.get_size()
        scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
        surface = pygame.transform.smoothscale(surface, scale_size)
        surface = pygame.transform.smoothscale(surface, surf_size)
        self.screen.blit(surface, (0, 0))

        pygame.display.update()
        self.clock.tick(FPS)

    def draw_message(self, message, font_size=None, color=None):
        """
        Draws message to the screen.
        """
        if font_size is None:
            font_size = FONT_SIZE
        if color is None:
            color = COLOR_FONT
        shadow_offset = 1 + (font_size // 15)
        font_obj = pygame.font.Font(self.font, font_size)
        shadow_surface_obj = font_obj.render(message, True, COLOR_FONT_SHADOW)
        text_surface_obj = font_obj.render(message, True, color)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (self.window_size // 2, self.window_size // 2)
        self.blur(BLUR_AMOUNT)
        self.screen.blit(shadow_surface_obj, text_rect_obj.move(shadow_offset, shadow_offset))
        self.screen.blit(text_surface_obj, text_rect_obj)

        pygame.display.update()
        self.clock.tick(FPS)
