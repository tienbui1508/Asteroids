import pygame

from circleshape import CircleShape
from constants import COLOR_FOREGROUND, LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH


class Shot(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen, COLOR_FOREGROUND, self.position, self.radius, width=LINE_WIDTH
        )

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        if self.is_off_screen():
            self.kill()

    def is_off_screen(self) -> bool:
        return (
            self.position.x < -self.radius
            or self.position.x > SCREEN_WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > SCREEN_HEIGHT + self.radius
        )
