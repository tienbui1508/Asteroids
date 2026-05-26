import asyncio

import pygame

from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from game import Game
from logger import log_state


async def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()

    game = Game()
    dt = 0.0

    while True:
        log_state()

        for event in pygame.event.get():
            if game.handle_event(event):
                return

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

        dt = clock.tick(FPS) / 1000
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
