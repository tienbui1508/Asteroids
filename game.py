import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from game_state import START_KEYS, GameState
from logger import log_event
from player import Player
from shot import Shot
from ui import (
    GAME_OVER_LINES,
    GAME_OVER_PROMPT,
    GAME_OVER_TITLE,
    WELCOME_LINES,
    WELCOME_PROMPT,
    WELCOME_TITLE,
    draw_hud,
    draw_message_screen,
)


class Game:
    """Owns sprite groups, score, and high-level play flow."""

    def __init__(self) -> None:
        self.state = GameState.WELCOME
        self.score = 0

        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        Asteroid.containers = (self.updatable, self.drawable, self.asteroids)
        AsteroidField.containers = (self.updatable,)
        Player.containers = (self.updatable, self.drawable)
        Shot.containers = (self.updatable, self.drawable, self.shots)

        self.asteroid_field = AsteroidField()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def reset(self) -> None:
        for sprite in list(self.asteroids):
            sprite.kill()
        for sprite in list(self.shots):
            sprite.kill()

        self.player.position.update(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.rotation = 0
        self.player.shoot_cooldown_timer = 0
        self.asteroid_field.spawn_timer = 0.0
        self.score = 0

    def start_playing(self) -> None:
        self.reset()
        self.state = GameState.PLAYING

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the app should quit."""
        if event.type == pygame.QUIT:
            return True

        if (
            event.type == pygame.KEYDOWN
            and event.key in START_KEYS
            and self.state in (GameState.WELCOME, GameState.GAME_OVER)
        ):
            self.start_playing()

        return False

    def update(self, dt: float) -> None:
        if self.state != GameState.PLAYING:
            return

        self.updatable.update(dt)
        self._handle_collisions()

    def _handle_collisions(self) -> None:
        for asteroid in self.asteroids:
            for shot in self.shots:
                if not shot.collides_with(asteroid):
                    continue

                log_event("asteroid_shot")
                # Award a flat point per asteroid hit (simpler scoring).
                self.score += 1
                shot.kill()
                asteroid.split()

            if self.player.collides_with(asteroid):
                log_event("player_hit")
                self.state = GameState.GAME_OVER
                return

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == GameState.WELCOME:
            draw_message_screen(
                screen, WELCOME_TITLE, WELCOME_LINES, WELCOME_PROMPT
            )
            return

        screen.fill("black")
        for sprite in self.drawable:
            sprite.draw(screen)

        if self.state == GameState.PLAYING:
            draw_hud(screen, self.score)
        else:
            draw_message_screen(
                screen,
                GAME_OVER_TITLE,
                GAME_OVER_LINES + [f"Final score: {self.score}"],
                GAME_OVER_PROMPT,
                clear_background=False,
            )
