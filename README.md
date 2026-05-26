# Asteroids

Classic Asteroids built with Python and Pygame, playable in the browser via [pygbag](https://pygame-web.github.io/) and deployed to GitHub Pages.

**[Play live demo](https://tienbui1508.github.io/Asteroids/)**

## Motivation

This project started as Boot.dev’s [Build Asteroids using Python and Pygame](https://www.boot.dev/courses/build-asteroids-python) guided project. I’m extending it into an ongoing portfolio piece—added features, cleaner structure, a playable web build, and GitHub Pages deploy so anyone can try it without installing Python.

Goals along the way:

- Practice and learn
- Ship something shareable: readable code, live demo, and automated deploy on push to `main`

## Quick Start

**Play in the browser:** open the [live demo](https://tienbui1508.github.io/Asteroids/) — no install required.

**Run on your machine** (Python 3.13+, [uv](https://docs.astral.sh/uv/) recommended):

```bash
git clone https://github.com/tienbui1508/Asteroids.git
cd Asteroids
uv sync
uv run python main.py
```

**Local browser build** (same stack as GitHub Pages):

```bash
uv run pygbag main.py
```

Open the URL printed in the terminal (usually `http://localhost:8000`).

## Usage

### Game flow

1. **Welcome screen** — read the controls, press **Enter** to start.
2. **Playing** — destroy asteroids; each hit adds **1** point. Avoid collisions.
3. **Game over** — press **Enter** to play again (world resets, score returns to 0).

### Controls

| Key | Action |
|-----|--------|
| W / S or ↑ / ↓ | Thrust forward / backward |
| A / D or ← / → | Rotate |
| Space | Shoot |
| Enter | Start or restart after game over |
| Touch (web / mobile) | Joystick (bottom-left) to fly; FIRE (bottom-right) to shoot |
| Tap | Start or restart on welcome / game over screens |

### Features

- Vector-style ship controls (thrust, rotate, shoot)
- Asteroids spawn from screen edges and split when hit
- Screen wrap for the player and asteroids; shots despawn off-screen
- Score HUD and final score on game over
- Global **games played** counter (Supabase + local fallback), shown on welcome and game over
- Welcome screen, game over, and restart flow

## Project structure

```
main.py          Entry point and game loop
game.py          Game state, collisions, score
game_state.py    State enum and menu keys
ui.py            Menus and HUD rendering
player.py        Player ship
touch_controls.py On-screen joystick and fire button
asteroid.py      Asteroids and splitting
asteroidfield.py Spawner
shot.py          Projectiles
circleshape.py   Shared sprite base (collision, wrap)
constants.py     Tuning values
logger.py        Boot.dev telemetry (optional local logs)
```

## Tech stack

- Python 3.13
- Pygame 2.6
- pygbag (WebAssembly build for GitHub Pages)
- GitHub Actions — build and deploy on push to `main`

## Development notes

- Game logic lives in `Game` (`game.py`); `main.py` only runs the async loop.
- Sprite groups use Pygame’s container pattern (`Class.containers = (...)`).
- `game_state.jsonl` / `game_events.jsonl` are written by `logger.py` for course telemetry and are gitignored.
- For the global games-played counter, run `supabase_stats.sql` once in the Supabase SQL editor.
- For the shared high-score leaderboard, run `supabase_high_scores.sql` once in the Supabase SQL editor.
- Configure the Supabase client in `constants.py`:

```python
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_ANON_KEY = "<anon-public-key>"
SUPABASE_HIGH_SCORES_TABLE = "asteroids_high_scores"
```

## Acknowledgments

Core gameplay and project structure come from Boot.dev’s [Build Asteroids using Python and Pygame](https://www.boot.dev/courses/build-asteroids-python) guided project.

Beyond the course, I’ve added (and am still adding) features such as welcome and game-over flows, scoring, screen wrap, arrow-key controls, refactored modules (`game.py`, `ui.py`, `game_state.py`), the pygbag web build, and GitHub Pages deployment. This repository is a work in progress—not a finished fork of the course alone.

## Contributing

This is primarily a learning and portfolio repo, but feedback and small improvements are welcome.

1. **Fork** the repository and create a branch from `main`.
2. **Make focused changes** — one logical change per commit (gameplay vs docs vs deploy).
3. **Test locally** — `uv run python main.py` and, if you touch the web build, `uv run pygbag main.py`.
4. **Open a pull request** with a short description of what changed and why.

Please avoid drive-by refactors or unrelated changes. If you plan something larger (new modes, multiplayer, etc.), open an issue first so we can align on scope.
