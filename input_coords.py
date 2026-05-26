"""Map browser pointer events to game surface coordinates."""

from __future__ import annotations

import sys

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH

# Chrome device emulation (and real touch) often emits FINGERDOWN then a synthetic
# MOUSEBUTTONDOWN for the same tap. Handling both toggles touch controls twice.
_SYNTHETIC_MOUSE_MS = 80
_last_finger_down_ms = -1_000_000


def is_web() -> bool:
    return sys.platform == "emscripten"


def note_finger_down() -> None:
    global _last_finger_down_ms
    _last_finger_down_ms = pygame.time.get_ticks()


def is_synthetic_mouse(event: pygame.event.Event) -> bool:
    if not is_web():
        return False
    if event.type not in (
        pygame.MOUSEBUTTONDOWN,
        pygame.MOUSEBUTTONUP,
        pygame.MOUSEMOTION,
    ):
        return False
    return pygame.time.get_ticks() - _last_finger_down_ms < _SYNTHETIC_MOUSE_MS


def _surface_size() -> tuple[int, int]:
    surface = pygame.display.get_surface()
    if surface is None:
        return SCREEN_WIDTH, SCREEN_HEIGHT
    return surface.get_size()


def _scale_to_surface(x: float, y: float) -> pygame.Vector2:
    sw, sh = _surface_size()
    if not is_web():
        return pygame.Vector2(x, y)

    try:
        ww, wh = pygame.display.get_window_size()
    except pygame.error:
        return pygame.Vector2(x, y)

    if ww > 0 and wh > 0 and (ww != sw or wh != sh):
        return pygame.Vector2(x * sw / ww, y * sh / wh)
    return pygame.Vector2(x, y)


def finger_position(event: pygame.event.Event) -> pygame.Vector2:
    sw, sh = _surface_size()
    x = float(event.x)
    y = float(event.y)
    # Pygame finger coords are normalized 0..1; some web builds send pixels instead.
    if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
        return pygame.Vector2(x * sw, y * sh)
    return _scale_to_surface(x, y)


def pointer_position(event: pygame.event.Event) -> pygame.Vector2 | None:
    if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
        if event.type == pygame.FINGERDOWN:
            note_finger_down()
        return finger_position(event)

    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        if is_synthetic_mouse(event):
            return None
        if event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
        else:
            if getattr(event, "button", 0) not in (0, 1):
                return None
            pos = pygame.mouse.get_pos()
        return _scale_to_surface(pos[0], pos[1])

    return None


def is_primary_pointer_down(event: pygame.event.Event) -> bool:
    if event.type == pygame.FINGERDOWN:
        return True
    if event.type == pygame.MOUSEBUTTONDOWN:
        if is_synthetic_mouse(event):
            return False
        return getattr(event, "button", 0) in (0, 1)
    return False
