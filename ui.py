import pygame

from constants import (
    COLOR_FOREGROUND,
    HUD_BAR_BG_COLOR,
    HUD_BAR_HEIGHT,
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
GAME_OVER_OVERLAY_ALPHA = 170


def format_games_played_line(count: int) -> str:
    return f"Games played worldwide: {count:,}"


def touch_controls_toggle_rect(*, hit_padding: int = 0) -> pygame.Rect:
    top = (HUD_BAR_HEIGHT - TOUCH_CONTROLS_TOGGLE_HEIGHT) // 2
    rect = pygame.Rect(
        SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_MARGIN - TOUCH_CONTROLS_TOGGLE_WIDTH,
        top,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


def _welcome_vertical_layout(
    body_lines: list[str],
    *,
    games_played_line: str,
    player_name_line: str,
    prompt: str,
) -> tuple[float, pygame.Rect]:
    """Compute top Y and SET NAME button rect for a vertically centered welcome block."""
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 32)
    body_font = pygame.font.Font(None, 36)
    prompt_font = pygame.font.Font(None, 40)

    rows: list[tuple[int, int]] = [
        (title_font.get_height(), 14),
        (subtitle_font.get_height(), 18),
    ]
    for line in body_lines:
        if line:
            rows.append((body_font.get_height(), 12))
        else:
            rows.append((0, 10))
    rows.append((body_font.get_height(), 18))
    rows.append((prompt_font.get_height(), 36))
    rows.append((TOUCH_CONTROLS_TOGGLE_HEIGHT, 0))

    total = sum(height + gap for height, gap in rows)
    y = (SCREEN_HEIGHT - total) / 2
    start_y = y

    button_rect = pygame.Rect(0, 0, 0, 0)
    for height, gap in rows:
        if height == TOUCH_CONTROLS_TOGGLE_HEIGHT:
            button_rect = pygame.Rect(
                (SCREEN_WIDTH - TOUCH_CONTROLS_TOGGLE_WIDTH) / 2,
                y,
                TOUCH_CONTROLS_TOGGLE_WIDTH,
                TOUCH_CONTROLS_TOGGLE_HEIGHT,
            )
            break
        y += height + gap

    return start_y, button_rect


def welcome_set_name_button_rect(
    body_lines: list[str],
    *,
    games_played_line: str,
    player_name_line: str,
    prompt: str,
    hit_padding: int = 0,
) -> pygame.Rect:
    _, rect = _welcome_vertical_layout(
        body_lines,
        games_played_line=games_played_line,
        player_name_line=player_name_line,
        prompt=prompt,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


def draw_welcome_screen(
    screen: pygame.Surface,
    *,
    games_played_line: str,
    body_lines: list[str],
    player_name_line: str,
    prompt: str,
) -> pygame.Rect:
    """Draw welcome content centered vertically. Returns the SET NAME button rect."""
    screen.fill("black")

    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 32)
    body_font = pygame.font.Font(None, 36)
    prompt_font = pygame.font.Font(None, 40)

    start_y, button_rect = _welcome_vertical_layout(
        body_lines,
        games_played_line=games_played_line,
        player_name_line=player_name_line,
        prompt=prompt,
    )

    y = start_y
    center_x = SCREEN_WIDTH / 2

    def blit_line(surface: pygame.Surface, gap: int) -> None:
        nonlocal y
        rect = surface.get_rect(midtop=(center_x, y))
        screen.blit(surface, rect)
        y = rect.bottom + gap

    blit_line(title_font.render(WELCOME_TITLE, True, COLOR_FOREGROUND), 14)
    blit_line(subtitle_font.render(games_played_line, True, COLOR_FOREGROUND), 18)

    for line in body_lines:
        if not line:
            y += 10
            continue
        blit_line(body_font.render(line, True, COLOR_FOREGROUND), 12)

    blit_line(body_font.render(player_name_line, True, COLOR_FOREGROUND), 18)
    blit_line(prompt_font.render(prompt, True, COLOR_FOREGROUND), 48)

    draw_set_name_button(screen, button_rect)
    return button_rect


def fullscreen_toggle_rect(*, hit_padding: int = 0) -> pygame.Rect:
    top = (HUD_BAR_HEIGHT - TOUCH_CONTROLS_TOGGLE_HEIGHT) // 2
    rect = pygame.Rect(
        SCREEN_WIDTH
        - TOUCH_CONTROLS_TOGGLE_MARGIN
        - TOUCH_CONTROLS_TOGGLE_WIDTH
        - TOUCH_CONTROLS_TOGGLE_MARGIN
        - TOUCH_CONTROLS_TOGGLE_WIDTH,
        top,
        TOUCH_CONTROLS_TOGGLE_WIDTH,
        TOUCH_CONTROLS_TOGGLE_HEIGHT,
    )
    if hit_padding:
        rect = rect.inflate(hit_padding * 2, hit_padding * 2)
    return rect


def draw_dim_overlay(
    screen: pygame.Surface, *, alpha: int = GAME_OVER_OVERLAY_ALPHA
) -> None:
    """Darken the game scene so menu text stays readable on top."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))


def draw_message_screen(
    screen: pygame.Surface,
    title: str,
    body_lines: list[str],
    prompt: str,
    *,
    subtitle: str | None = None,
    clear_background: bool = True,
) -> None:
    if clear_background:
        screen.fill("black")

    title_font = pygame.font.Font(None, 72)
    body_font = pygame.font.Font(None, 36)
    subtitle_font = pygame.font.Font(None, 32)
    prompt_font = pygame.font.Font(None, 40)

    title_surface = title_font.render(title, True, COLOR_FOREGROUND)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
    screen.blit(title_surface, title_rect)

    body_top = title_rect.bottom + 16
    if subtitle:
        subtitle_surface = subtitle_font.render(subtitle, True, COLOR_FOREGROUND)
        subtitle_rect = subtitle_surface.get_rect(
            midtop=(SCREEN_WIDTH / 2, body_top)
        )
        screen.blit(subtitle_surface, subtitle_rect)
        body_top = subtitle_rect.bottom + 20

    prompt_surface = prompt_font.render(prompt, True, COLOR_FOREGROUND)
    prompt_rect = prompt_surface.get_rect(
        midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 44)
    )
    body_bottom = prompt_rect.top - 28

    non_empty = [line for line in body_lines if line]
    if non_empty:
        slot_height = (body_bottom - body_top) / len(non_empty)
        slot_height = max(22, min(40, slot_height))
    else:
        slot_height = 36

    y = body_top
    for line in body_lines:
        if not line:
            y += slot_height * 0.35
            continue
        text_surface = body_font.render(line, True, COLOR_FOREGROUND)
        text_rect = text_surface.get_rect(midtop=(SCREEN_WIDTH / 2, y))
        screen.blit(text_surface, text_rect)
        y += slot_height

    screen.blit(prompt_surface, prompt_rect)


def draw_game_over_screen(
    screen: pygame.Surface,
    *,
    title: str,
    games_played_line: str,
    summary_lines: list[str],
    prompt: str,
    leaderboard_lines: list[str],
) -> None:
    """Game over: summary + prompt higher; leaderboard uses the lower screen."""
    title_font = pygame.font.Font(None, 72)
    body_font = pygame.font.Font(None, 36)
    subtitle_font = pygame.font.Font(None, 32)
    prompt_font = pygame.font.Font(None, 40)

    title_surface = title_font.render(title, True, COLOR_FOREGROUND)
    title_rect = title_surface.get_rect(
        center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.14)
    )
    screen.blit(title_surface, title_rect)

    stats_surface = subtitle_font.render(games_played_line, True, COLOR_FOREGROUND)
    stats_rect = stats_surface.get_rect(midtop=(SCREEN_WIDTH / 2, title_rect.bottom + 12))
    screen.blit(stats_surface, stats_rect)

    y = stats_rect.bottom + 20
    line_gap = 36
    for line in summary_lines:
        if not line:
            y += line_gap * 0.4
            continue
        text_surface = body_font.render(line, True, COLOR_FOREGROUND)
        text_rect = text_surface.get_rect(midtop=(SCREEN_WIDTH / 2, y))
        screen.blit(text_surface, text_rect)
        y = text_rect.bottom + 12

    prompt_surface = prompt_font.render(prompt, True, COLOR_FOREGROUND)
    prompt_rect = prompt_surface.get_rect(midtop=(SCREEN_WIDTH / 2, y + 8))
    screen.blit(prompt_surface, prompt_rect)

    leaderboard_top = prompt_rect.bottom + 40
    leaderboard_bottom = SCREEN_HEIGHT - 32
    entries = [line for line in leaderboard_lines if line]
    if not entries:
        return

    slot_height = (leaderboard_bottom - leaderboard_top) / len(entries)
    slot_height = max(24, min(36, slot_height))

    y = leaderboard_top
    for line in entries:
        text_surface = body_font.render(line, True, COLOR_FOREGROUND)
        text_rect = text_surface.get_rect(midtop=(SCREEN_WIDTH / 2, y))
        screen.blit(text_surface, text_rect)
        y += slot_height


def draw_hud(screen: pygame.Surface, score: int, player_name: str) -> None:
    # Keep a dedicated top row for status and controls so gameplay stays visible.
    hud_bg = pygame.Surface((SCREEN_WIDTH, HUD_BAR_HEIGHT), pygame.SRCALPHA)
    hud_bg.fill(HUD_BAR_BG_COLOR)
    screen.blit(hud_bg, (0, 0))

    font = pygame.font.Font(None, 34)
    status_label = font.render(
        f"Player: {player_name}   Score: {score}", True, COLOR_FOREGROUND
    )
    status_rect = status_label.get_rect(midleft=(16, HUD_BAR_HEIGHT // 2))
    screen.blit(status_label, status_rect)


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


def draw_set_name_button(screen: pygame.Surface, rect: pygame.Rect) -> None:
    font = pygame.font.Font(None, 28)
    label = font.render("SET NAME", True, TOUCH_CONTROL_TEXT_COLOR)
    pygame.draw.rect(screen, TOUCH_CONTROLS_TOGGLE_BG_COLOR, rect, border_radius=8)
    pygame.draw.rect(
        screen,
        TOUCH_CONTROLS_TOGGLE_BORDER_COLOR,
        rect,
        width=2,
        border_radius=8,
    )
    screen.blit(label, label.get_rect(center=rect.center))
