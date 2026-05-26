from enum import Enum, auto

import pygame


class GameState(Enum):
    WELCOME = auto()
    PLAYING = auto()
    GAME_OVER = auto()


START_KEYS = frozenset({pygame.K_RETURN, pygame.K_KP_ENTER})
