""" Checkers constants.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')  # resources directory

# Rule constants
BOARD_SIZE = 10  # board size
SIGHT = 2  # sight of man
KING_SIGHT = 2  # sight of king
KING_RANGE = 2  # attack range of king
FORCE_CAPTURE = True  # mandatory capture rule
BACKWARD_CAPTURE = True  # backward capture rule

# Board constants
EMPTY = 0  # encoding of empty space
DARK = 1  # encoding of dark man
LIGHT = -1  # encoding of light man
DARK_KING = 2  # encoding of dark king
LIGHT_KING = -2  # encoding of light king
BLIND = 3  # encoding of invisible space

# Graphics constants
CAPTION = 'Blind Checkers'  # title of the pygame program
WINDOW_SIZE = 800  # window size of pygame
IMAGE_BOARD = os.path.join(RESOURCES_DIR, 'board.png')  # board image
IMAGE_DARK = os.path.join(RESOURCES_DIR, 'dark_man.png')  # dark man image
IMAGE_DARK_KING = os.path.join(RESOURCES_DIR, 'dark_king.png')  # dark king image
IMAGE_LIGHT = os.path.join(RESOURCES_DIR, 'light_man.png')  # light man image
IMAGE_LIGHT_KING = os.path.join(RESOURCES_DIR, 'light_king.png')  # light king image
FONT = os.path.join(RESOURCES_DIR, 'font.ttf')  # font
COLOR_HIGH = (160, 190, 255)  # color for highlighting
COLOR_BACKGROUND1 = (241, 235, 217)  # color for board
COLOR_BACKGROUND2 = (234, 184, 82)  # color for board
COLOR_DARK = (48, 48, 48)  # color for dark man
COLOR_LIGHT = (247, 247, 247)  # color for light man
COLOR_KING = (255, 215, 0)  # color for king
COLOR_BLIND = (0, 0, 0)  # color for invisible space
COLOR_FONT = (255, 0, 0)  # color of font
COLOR_FONT_SHADOW = (127, 127, 127)  # color of shadow of font
FONT_SIZE = 56  # font size
BLUR_AMOUNT = 5.  # blur the screen when print the text. (1. means no blur)
PIECE_RATIO_IMAGE = 1.05  # piece ratio relative to each board space, when using image.
PIECE_RATIO_DRAW = 0.95  # piece ratio relative to each board space, when not using image.
FPS = 60  # maximum frames per second.

# Game constants
DRAW_MOVE_COUNT = 40 * 2  # with this moves without capturing, it becomes draw.
MIN_VISUALIZE_TIME = 0.1  # minimum time to visualize each board.
PRINT_TIME = 1.  # time duration to print the text (when game is started or ended.)

# Main constants
REPEAT_EPISODES = True
VISUALIZE = True
VISUALIZE_TYPE = 'light'  # one of 'dark', 'light', 'both', and 'no-blind'.
AGENT_DARK = 'Greedy'  # one of 'Human', 'Random', 'Greedy'.
AGENT_LIGHT = 'Human'  # one of 'Human', 'Random', 'Greedy'.