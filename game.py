import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOUCH_CONTROLS_TOGGLE_HEIGHT,
    TOUCH_CONTROLS_TOGGLE_MARGIN,
    TOUCH_CONTROLS_TOGGLE_WIDTH,
)
from game_state import START_KEYS, GameState
from logger import log_event
from player import Player
from shot import Shot
from touch_controls import TouchControls
from ui import (
    GAME_OVER_LINES,
    GAME_OVER_PROMPT,
    GAME_OVER_TITLE,
    WELCOME_LINES,
    WELCOME_PROMPT,
    WELCOME_TITLE,
    draw_hud,
    draw_message_screen,
    draw_touch_controls_toggle,
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
        self.touch_controls = TouchControls(enabled=False)
        self.player.touch_controls = self.touch_controls

    def reset(self) -> None:
        for sprite in list(self.asteroids):
            sprite.kill()
        for sprite in list(self.shots):
            sprite.kill()

        self.player.position.update(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.rotation = 0
        self.player.shoot_cooldown_timer = 0
        self.player.color = "green"
        self.asteroid_field.spawn_timer = 0.0
        self.score = 0

    def start_playing(self) -> None:
        self.reset()
        self.state = GameState.PLAYING

    def _menu_tap(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.FINGERDOWN:
            return True
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def _event_pos(self, event: pygame.event.Event) -> pygame.Vector2 | None:
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            return pygame.Vector2(event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            if getattr(event, "button", 0) == 1:
                return pygame.Vector2(event.pos)
        return None

    def _touch_toggle_tap(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.FINGERDOWN and not (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):
            return False

        pos = self._event_pos(event)
        if pos is None:
            return False

        rect = pygame.Rect(
            SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_MARGIN - TOUCH_CONTROLS_TOGGLE_WIDTH,
            TOUCH_CONTROLS_TOGGLE_MARGIN,
            TOUCH_CONTROLS_TOGGLE_WIDTH,
            TOUCH_CONTROLS_TOGGLE_HEIGHT,
        )
        return rect.collidepoint(pos.x, pos.y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the app should quit."""
        if event.type == pygame.QUIT:
            return True

        if self.state in (GameState.WELCOME, GameState.GAME_OVER):
            if event.type == pygame.KEYDOWN and event.key in START_KEYS:
                self.start_playing()
            elif self._menu_tap(event):
                self.start_playing()
            return False

        if self.state == GameState.PLAYING:
            if self._touch_toggle_tap(event):
                self.touch_controls.set_enabled(not self.touch_controls.enabled)
            else:
                self.touch_controls.handle_event(event)

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
                self.player.color = "red"
                self.touch_controls.reset()
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
            draw_touch_controls_toggle(screen, self.touch_controls.enabled)
            self.touch_controls.draw(screen)
        else:
            draw_message_screen(
                screen,
                GAME_OVER_TITLE,
                GAME_OVER_LINES + [f"Final score: {self.score}"],
                GAME_OVER_PROMPT,
                clear_background=False,
            )
