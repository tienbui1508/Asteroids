import pygame
from pathlib import Path

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    HIGH_SCORES_FILE,
    PLAYER_NAME_MAX_LENGTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOUCH_CONTROLS_TOGGLE_HEIGHT,
    TOUCH_CONTROLS_TOGGLE_MARGIN,
    TOUCH_CONTROLS_TOGGLE_WIDTH,
)
from game_state import START_KEYS, GameState
from logger import log_event
from high_scores import record_high_score
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
        self.player_name = "NoobPlayer"
        self.player_name_input = ""
        self.high_scores = []
        self._has_recorded_high_score = False
        self._high_scores_path = Path(__file__).with_name(HIGH_SCORES_FILE)

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
        self._has_recorded_high_score = False
        self.high_scores = []
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

    def _confirm_player_name(self) -> None:
        sanitized = self.player_name_input.strip()
        self.player_name = sanitized if sanitized else "NoobPlayer"
        # Keep the input in sync so the UI reflects the chosen name.
        self.player_name_input = self.player_name

    def _handle_welcome_keydown(self, event: pygame.event.Event) -> None:
        # Confirm name and start
        if event.key in START_KEYS:
            self._confirm_player_name()
            self.start_playing()
            return

        if event.key == pygame.K_BACKSPACE:
            self.player_name_input = self.player_name_input[:-1]
            return

        if event.key == pygame.K_ESCAPE:
            self.player_name_input = ""
            return

        # Pygame provides the typed character in `event.unicode`.
        ch = getattr(event, "unicode", "")
        if not isinstance(ch, str) or len(ch) != 1:
            return

        # Keep it simple: allow letters/digits and '-'/'_' only.
        if not (ch.isalnum() or ch in ("-", "_")):
            return

        if len(self.player_name_input) >= PLAYER_NAME_MAX_LENGTH:
            return

        self.player_name_input += ch

    def _record_high_score_if_needed(self) -> None:
        if self._has_recorded_high_score:
            return
        self._has_recorded_high_score = True

        # Record using the confirmed player name.
        scores = record_high_score(
            self._high_scores_path, player_name=self.player_name, score=self.score
        )
        self.high_scores = scores.top()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the app should quit."""
        if event.type == pygame.QUIT:
            return True

        if self.state == GameState.WELCOME:
            if event.type == pygame.KEYDOWN:
                self._handle_welcome_keydown(event)
            elif self._menu_tap(event):
                self._confirm_player_name()
                self.start_playing()
            return False

        if self.state == GameState.GAME_OVER:
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
                self._record_high_score_if_needed()
                return

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == GameState.WELCOME:
            display_input = self.player_name_input + "_"
            draw_message_screen(
                screen,
                WELCOME_TITLE,
                WELCOME_LINES + [f"Player name: {display_input}"],
                WELCOME_PROMPT,
            )
            return

        screen.fill("black")
        for sprite in self.drawable:
            sprite.draw(screen)

        if self.state == GameState.PLAYING:
            draw_hud(screen, self.score, self.player_name)
            draw_touch_controls_toggle(screen, self.touch_controls.enabled)
            self.touch_controls.draw(screen)
        else:
            high_score_lines: list[str] = []
            if self.high_scores:
                for i, entry in enumerate(self.high_scores, start=1):
                    high_score_lines.append(f"{i}. {entry['name']} - {entry['score']}")
            else:
                high_score_lines = ["No saved high scores yet."]

            draw_message_screen(
                screen,
                GAME_OVER_TITLE,
                GAME_OVER_LINES
                + [f"Player: {self.player_name}", f"Final score: {self.score}", ""]
                + ["High scores:"] + high_score_lines,
                GAME_OVER_PROMPT,
                clear_background=False,
            )
