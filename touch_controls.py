"""On-screen joystick and fire button for touch and mouse (pygbag / mobile)."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from constants import (
    COLOR_FOREGROUND,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOUCH_CONTROL_MARGIN,
    TOUCH_CONTROL_COLOR,
    TOUCH_FIRE_BUTTON_SIZE,
    TOUCH_JOYSTICK_DEAD_ZONE,
    TOUCH_JOYSTICK_KNOB_RADIUS,
    TOUCH_JOYSTICK_RADIUS,
    TOUCH_CONTROL_TEXT_COLOR,
)
from input_coords import is_synthetic_mouse, pointer_position

MOUSE_POINTER_ID = -1


@dataclass(frozen=True)
class TouchMovement:
    heading: float | None
    thrust: float


class TouchControls:
    def __init__(self, *, enabled: bool = False) -> None:
        margin = TOUCH_CONTROL_MARGIN
        radius = TOUCH_JOYSTICK_RADIUS
        self.joystick_center = pygame.Vector2(
            margin + radius, SCREEN_HEIGHT - margin - radius
        )
        self.joystick_radius = radius
        fire_size = TOUCH_FIRE_BUTTON_SIZE
        self.fire_rect = pygame.Rect(
            SCREEN_WIDTH - margin - fire_size,
            SCREEN_HEIGHT - margin - fire_size,
            fire_size,
            fire_size,
        )

        self._joystick_pointer: int | None = None
        self._joystick_offset = pygame.Vector2(0, 0)
        self._fire_pointer: int | None = None
        self.enabled = enabled

    def reset(self) -> None:
        self._joystick_pointer = None
        self._joystick_offset.update(0, 0)
        self._fire_pointer = None

    def set_enabled(self, enabled: bool) -> None:
        if not enabled:
            self.reset()
        self.enabled = enabled

    @property
    def joystick_active(self) -> bool:
        return self.enabled and self._joystick_pointer is not None

    @property
    def movement(self) -> TouchMovement | None:
        if not self.enabled:
            return None
        if not self.joystick_active:
            return None

        offset = self._joystick_offset
        distance = offset.length()
        dead = self.joystick_radius * TOUCH_JOYSTICK_DEAD_ZONE
        heading = None
        if distance > 0:
            heading = pygame.Vector2(0, 1).angle_to(offset)
        thrust = 0.0
        if distance >= dead:
            thrust = min(1.0, distance / self.joystick_radius)
        return TouchMovement(heading=heading, thrust=thrust)

    @property
    def shooting(self) -> bool:
        return self.enabled and self._fire_pointer is not None

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return

        if event.type == pygame.FINGERDOWN:
            self._on_press(event.finger_id, pointer_position(event))
        elif event.type == pygame.FINGERMOTION:
            pos = pointer_position(event)
            if pos is not None:
                self._on_motion(event.finger_id, pos)
        elif event.type == pygame.FINGERUP:
            self._on_release(event.finger_id)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (0, 1):
            if is_synthetic_mouse(event):
                return
            pos = pointer_position(event)
            if pos is not None:
                self._on_press(MOUSE_POINTER_ID, pos)
        elif event.type == pygame.MOUSEMOTION and any(event.buttons):
            if is_synthetic_mouse(event):
                return
            if self._joystick_pointer == MOUSE_POINTER_ID:
                pos = pointer_position(event)
                if pos is not None:
                    self._on_motion(MOUSE_POINTER_ID, pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button in (0, 1):
            if is_synthetic_mouse(event):
                return
            self._on_release(MOUSE_POINTER_ID)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.enabled:
            return

        pygame.draw.circle(
            screen,
            TOUCH_CONTROL_COLOR,
            self.joystick_center,
            self.joystick_radius,
            width=LINE_WIDTH,
        )
        knob_center = self.joystick_center + self._joystick_offset
        pygame.draw.circle(
            screen,
            TOUCH_CONTROL_COLOR,
            knob_center,
            TOUCH_JOYSTICK_KNOB_RADIUS,
            width=LINE_WIDTH,
        )
        pygame.draw.rect(
            screen, TOUCH_CONTROL_COLOR, self.fire_rect, width=LINE_WIDTH
        )
        font = pygame.font.Font(None, 36)
        label = font.render("FIRE", True, TOUCH_CONTROL_TEXT_COLOR)
        label_rect = label.get_rect(center=self.fire_rect.center)
        screen.blit(label, label_rect)

    def _on_press(self, pointer_id: int, pos: pygame.Vector2) -> None:
        if self._joystick_pointer is None and self._in_joystick_zone(pos):
            self._joystick_pointer = pointer_id
            self._set_joystick_offset(pos)
            return

        if self._fire_pointer is None and self.fire_rect.collidepoint(pos):
            self._fire_pointer = pointer_id

    def _on_motion(self, pointer_id: int, pos: pygame.Vector2) -> None:
        if pointer_id == self._joystick_pointer:
            self._set_joystick_offset(pos)

    def _on_release(self, pointer_id: int) -> None:
        if pointer_id == self._joystick_pointer:
            self._joystick_pointer = None
            self._joystick_offset.update(0, 0)
        if pointer_id == self._fire_pointer:
            self._fire_pointer = None

    def _in_joystick_zone(self, pos: pygame.Vector2) -> bool:
        return pos.distance_to(self.joystick_center) <= self.joystick_radius * 1.5

    def _set_joystick_offset(self, pos: pygame.Vector2) -> None:
        offset = pos - self.joystick_center
        distance = offset.length()
        if distance > self.joystick_radius and distance > 0:
            offset = offset * (self.joystick_radius / distance)
        self._joystick_offset = offset
