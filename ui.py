import pygame

from constants import COLOR_FOREGROUND, SCREEN_HEIGHT, SCREEN_WIDTH

WELCOME_TITLE = "ASTEROIDS"
WELCOME_LINES = [
    "W / S : thrust forward and backward",
    "A / D : rotate",
    "SPACE : shoot",
    "Destroy asteroids. Don't get hit.",
]
WELCOME_PROMPT = "Press ENTER to play"

GAME_OVER_TITLE = "GAME OVER"
GAME_OVER_LINES = ["You were hit by an asteroid."]
GAME_OVER_PROMPT = "Press ENTER to play again"


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
