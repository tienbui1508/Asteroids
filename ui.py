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
WELCOME_PROMPT = "Type name then press ENTER (or tap)"

GAME_OVER_TITLE = "GAME OVER"
GAME_OVER_LINES = ["You were hit by an asteroid."]
GAME_OVER_PROMPT = "Press ENTER or tap to play again"

TOUCH_CONTROLS_TOGGLE_HIT_PADDING = 12


def touch_controls_toggle_rect(*, hit_padding: int = 0) -> pygame.Rect:
    rect = pygame.Rect(
        SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_MARGIN - TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_MARGIN,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


def set_name_button_rect(*, hit_padding: int = 0) -> pygame.Rect:
    rect = pygame.Rect(
        (SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_WIDTH) / 2,
        SCREEN_HEIGHT - SCREEN_HEIGHT / 4 + 56,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


def fullscreen_toggle_rect(*, hit_padding: int = 0) -> pygame.Rect:
    rect = pygame.Rect(
        SCREEN_WIDTH
        - TOUCH_CONTROLS_TOGGLE_MARGIN
        - TOUCH_CONTROLS_TOGGLE_WIDTH
        - TOUCH_CONTROLS_TOGGLE_MARGIN
        - TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_MARGIN,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


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


def draw_hud(screen: pygame.Surface, score: int, player_name: str) -> None:
    font = pygame.font.Font(None, 36)
    name_label = font.render(f"{player_name}", True, COLOR_FOREGROUND)
    screen.blit(name_label, (16, 16))

    score_label = font.render(f"Score: {score}", True, COLOR_FOREGROUND)
    screen.blit(score_label, (16, 16 + 40))


def draw_touch_controls_toggle(screen: pygame.Surface, enabled: bool) -> None:
    font = pygame.font.Font(None, 28)
    label = font.render(
        f"TOUCH: {'ON' if enabled else 'OFF'}",
        True,
        TOUCH_CONTROL_TEXT_COLOR,
    )
    rect = touch_controls_toggle_rect()
    pygame.draw.rect(screen, TOUCH_CONTROLS_TOGGLE_BG_COLOR, rect, border_radius=8)
    pygame.draw.rect(
        screen,
        TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
        rect,
        width=2,
        border_radius=8,
    )
    screen.blit(label, label.get_rect(center=rect.center))


def draw_fullscreen_toggle(screen: pygame.Surface) -> None:
    font = pygame.font.Font(None, 28)
    label = font.render("FULLSCREEN", True, TOUCH_CONTROL_TEXT_COLOR)
    rect = fullscreen_toggle_rect()
    pygame.draw.rect(screen, TOUCH_CONTROLS_TOGGLE_BG_COLOR, rect, border_radius=8)
    pygame.draw.rect(
        screen,
        TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
        rect,
        width=2,
        border_radius=8,
    )
    screen.blit(label, label.get_rect(center=rect.center))


def draw_set_name_button(screen: pygame.Surface) -> None:
    font = pygame.font.Font(None, 28)
    label = font.render("SET NAME", True, TOUCH_CONTROL_TEXT_COLOR)
    rect = set_name_button_rect()
    pygame.draw.rect(screen, TOUCH_CONTROLS_TOGGLE_BG_COLOR, rect, border_radius=8)
    pygame.draw.rect(
        screen,
        TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
        rect,
        width=2,
        border_radius=8,
    )
    screen.blit(label, label.get_rect(center=rect.center))
