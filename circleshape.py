import pygame

from constants import PLAYFIELD_BOTTOM, PLAYFIELD_TOP, SCREEN_WIDTH


class CircleShape(pygame.sprite.Sprite):
    """Base sprite for circular game objects with optional screen wrap."""

    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        raise NotImplementedError

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def collides_with(self, other: "CircleShape") -> bool:
        distance = self.position.distance_to(other.position)
        return distance < self.radius + other.radius

    def wrap_position(self) -> None:
        min_x = self.radius
        max_x = SCREEN_WIDTH - self.radius
        min_y = PLAYFIELD_TOP + self.radius
        max_y = PLAYFIELD_BOTTOM - self.radius

        if self.position.x < min_x:
            self.position.x = max_x
        elif self.position.x > max_x:
            self.position.x = min_x

        if self.position.y < min_y:
            self.position.y = max_y
        elif self.position.y > max_y:
            self.position.y = min_y
