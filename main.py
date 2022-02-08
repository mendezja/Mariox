
import pygame
import os
from modules.vector2D import Vector2
from modules.drawable import Drawable
from modules.player import Player

WORLD_SIZE = Vector2(2624, 240)
SCREEN_SIZE = Vector2(WORLD_SIZE.y, WORLD_SIZE.y)
SCALE = 4
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

    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(
        x) for x in range(2)]

    players: list[Player] = []
    players.append(Player("mario.png", SCREEN_SIZE // 2, joysticks[0]))
    # players.append(Player("mario.png", SCREEN_SIZE // 2, joysticks[1]))

    # Make a game clock for nice, smooth animations
    gameClock = pygame.time.Clock()

    # define a variable to control the main loop
    RUNNING = True

    # main loop
    while RUNNING:

        # Draw everything
        # drawSurface.fill((92,148,252))
        background.draw(drawSurface)

        for floor in floorTiles:
            floor.draw(drawSurface)

        for player in players:
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

            for player in players:
                player.handleEvent(event)

        # Update everything
        for player in players:
            Drawable.updateOffset(player, SCREEN_SIZE, WORLD_SIZE)

        # Detect the floor collision
        for floor in floorTiles:
            for player in players:
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

            for player in players:
                player.update(seconds)


if __name__ == "__main__":
    main()
