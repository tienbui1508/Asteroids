import asyncio

import pygame
from asteroid import Asteroid
from constants import *
from logger import log_state
from player import Player
from asteroidfield import AsteroidField
from logger import log_event
from shot import Shot

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock =pygame.time.Clock()

    dt = 0.0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()

    Asteroid.containers = (updatable, drawable, asteroids)
    AsteroidField.containers = (updatable)
    asteroid_field = AsteroidField()

    Player.containers = (updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    shots = pygame.sprite.Group()
    Shot.containers = (updatable, drawable, shots)

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid in asteroids:
            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    asteroid.split()
            if player.collides_with(asteroid):
                log_event("player_hit")
                print("Game over!")
                return

        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        pygame.display.flip()

        dt = clock.tick(60) / 1000
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
