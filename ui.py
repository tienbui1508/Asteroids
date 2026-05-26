import pygame

from constants import (
    COLOR_FOREGROUND,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
    TOUCH_CONTROLS_TOGGLE_BG_COLOR,
    TOUCH_CONTROLS_TOGGLE_HEIGHT,
    TOUCH_CONTROLS_TOGGLE_MARGIN,
    TOUCH_CONTROLS_TOGGLE_WIDTH,
    TOUCH_CONTROL_TEXT_COLOR,
)

WELCOME_TITLE = "ASTEROIDS"
WELCOME_LINES = [
    "W / S : thrust forward and backward",
    "A / D : rotate",
    "SPACE : shoot",
    "Touch: joystick to fly, FIRE to shoot",
    "Destroy asteroids. Don't get hit.",
]
WELCOME_PROMPT = "Press ENTER or tap to play"

GAME_OVER_TITLE = "GAME OVER"
GAME_OVER_LINES = ["You were hit by an asteroid."]
GAME_OVER_PROMPT = "Press ENTER or tap to play again"


def draw_message_screen(
    screen: pygame.Surface,
    title: str,
    body_lines: list[str],
    prompt: str,
    *,
    clear_background: bool = True,
) -> None:
    if clear_background:
        screen.fill("black")

    title_font = pygame.font.Font(None, 72)
    body_font = pygame.font.Font(None, 36)
    prompt_font = pygame.font.Font(None, 40)

    title_surface = title_font.render(title, True, COLOR_FOREGROUND)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
    screen.blit(title_surface, title_rect)

    y = title_rect.bottom + 40
    for line in body_lines:
        text_surface = body_font.render(line, True, COLOR_FOREGROUND)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y))
        screen.blit(text_surface, text_rect)
        y = text_rect.bottom + 12

    prompt_surface = prompt_font.render(prompt, True, COLOR_FOREGROUND)
    prompt_rect = prompt_surface.get_rect(
        center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - SCREEN_HEIGHT / 4)
    )
    screen.blit(prompt_surface, prompt_rect)


def draw_hud(screen: pygame.Surface, score: int) -> None:
    font = pygame.font.Font(None, 36)
    label = font.render(f"Score: {score}", True, COLOR_FOREGROUND)
    screen.blit(label, (16, 16))


def draw_touch_controls_toggle(screen: pygame.Surface, enabled: bool) -> None:
    font = pygame.font.Font(None, 28)
    label = font.render(
        f"TOUCH: {'ON' if enabled else 'OFF'}",
        True,
        TOUCH_CONTROL_TEXT_COLOR,
    )
    rect = pygame.Rect(
        SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_MARGIN - TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_MARGIN,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    pygame.draw.rect(screen, TOUCH_CONTROLS_TOGGLE_BG_COLOR, rect, border_radius=8)
    pygame.draw.rect(
        screen,
        TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
        rect,
        width=2,
        border_radius=8,
    )
    screen.blit(label, label.get_rect(center=rect.center))
