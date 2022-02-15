
import pygame
import os
from modules.vector2D import Vector2
from modules.drawable import Drawable
from modules.player import Player

WORLD_SIZE = Vector2(2624, 240)
SCREEN_SIZE = Vector2(WORLD_SIZE.y, WORLD_SIZE.y)
SCALE = 3
UPSCALED_SCREEN_SIZE = SCREEN_SIZE * SCALE


def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo

    pygame.display.set_caption("Physics")

    screen = pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE))

    drawSurface = pygame.Surface(list(SCREEN_SIZE))

    background = Drawable("background.png", (0, 0))

    floorTiles: list[Drawable] = []

    for x in range(0, WORLD_SIZE.x, 16):
        floorTiles.append(
            Drawable("brick.png", Vector2(x, SCREEN_SIZE.y - 32)))

    player = Player("mario.png", SCREEN_SIZE // 2)

    # Make a game clock for nice, smooth animations
    gameClock = pygame.time.Clock()

    # define a variable to control the main loop
    RUNNING = True

    # main loop
    while RUNNING:

        # Draw everything
        background.draw(drawSurface)

        for floor in floorTiles:
            floor.draw(drawSurface)

        player.draw(drawSurface)

        pygame.transform.scale(drawSurface, list(UPSCALED_SCREEN_SIZE), screen)

        # Flip the display to the monitor
        pygame.display.flip()

        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT or ESCAPE is pressed
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # change the value to False, to exit the main loop
                RUNNING = False

            player.handleEvent(event)

        # Update everything
        Drawable.updateOffset(player, SCREEN_SIZE, WORLD_SIZE)

        # Detect the floor collision
        for floor in floorTiles:
            clipRect = player.getCollisionRect().clip(floor.getCollisionRect())

            if clipRect.width > 0:
                player.collideGround(clipRect.height)
                break

        # Let our game clock tick at 60 fps
        gameClock.tick(60)

        # Get some time in seconds
        seconds = gameClock.get_time() / 1000

        # let others update based on the amount of time elapsed

        if seconds < 0.05:

            player.update(seconds)


if __name__ == "__main__":
    main()
