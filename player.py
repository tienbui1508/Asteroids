import pygame

from circleshape import CircleShape
from constants import (
    COLOR_FOREGROUND,
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SHOT_RADIUS,
)
from shot import Shot
from touch_controls import TouchControls, TouchMovement


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, radius=PLAYER_RADIUS)
        self.rotation = 0.0
        self.shoot_cooldown_timer = 0.0
        self.color = "green"
        self.touch_controls: TouchControls | None = None

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(
            screen, self.color, self.triangle(), width=LINE_WIDTH
        )

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        if self.touch_controls is not None and self.touch_controls.joystick_active:
            movement = self.touch_controls.movement
            if movement is not None:
                self._update_from_touch(dt, movement)
        else:
            self._update_from_keyboard(dt)

        if self.touch_controls is not None and self.touch_controls.shooting:
            self.shoot()
        elif pygame.key.get_pressed()[pygame.K_SPACE]:
            self.shoot()

        self.shoot_cooldown_timer -= dt

    def _update_from_touch(self, dt: float, movement: TouchMovement) -> None:
        if movement.heading is not None:
            self.rotation = movement.heading
        if movement.thrust > 0:
            # Match keyboard: once thrust is engaged, move at full speed.
            self.move(dt)

    def _update_from_keyboard(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-dt)

    def move(self, dt: float, *, speed_scale: float = 1.0) -> None:
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += direction * PLAYER_SPEED * dt * speed_scale
        self.wrap_position()

    def shoot(self) -> None:
        if self.shoot_cooldown_timer > 0:
            return

        self.shoot_cooldown_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
        shot.velocity = (
            pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        )
