import pygame
import time
import os
from modules.vector2D import Vector2
from modules.drawable import Drawable
from modules.playerJoysticks import Player
from modules.enemy import Enemy

WORLD_SIZE = Vector2(2624, 240)
SCREEN_SIZE = Vector2(WORLD_SIZE.y * 2, WORLD_SIZE.y * 2)
SCALE = 1.5
UPSCALED_SCREEN_SIZE = SCREEN_SIZE * SCALE


def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo

    pygame.display.set_caption("Physics")

    mainSurface = pygame.Surface(
        (SCREEN_SIZE.x, SCREEN_SIZE.y))  # main surface
    screen = pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE))  # main screen

    drawSurfaces: list[pygame.Surface] = []
    drawSurfaces.append(pygame.Surface(
        (SCREEN_SIZE.x, SCREEN_SIZE.y//2)))
    drawSurfaces.append(pygame.Surface(
        (SCREEN_SIZE.x, SCREEN_SIZE.y//2)))

    backgrounds: list[Drawable] = []
    backgrounds.append(Drawable("background.png", (0, 0)))
    backgrounds.append(Drawable("background.png", (0, 0)))

    floorTiles: list[Drawable] = []

    for x in range(0, WORLD_SIZE.x, 16):
        floorTiles.append(
            Drawable("brick.png", Vector2(x, WORLD_SIZE.y - 32)))

    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(
        x) for x in range(2)]

    players: list[Player] = []
    players.append(Player("mario.png", (15, WORLD_SIZE.y - 48), joysticks[0]))
    players.append(Player("luigi.png", (35,200), joysticks[1]))

    enemies: list [Enemy] = [Enemy("enemies.png", list(WORLD_SIZE//x)) for x in range (2,16,2)]

    # Make a game clock for nice, smooth animations
    gameClock = pygame.time.Clock()

    # define a variable to control the main loop
    RUNNING = True

    # main loop
    while RUNNING:

        # Drawing two separate screens
        for player in players:
            index = players.index(player)  # 0 or 1
            drawSurface = drawSurfaces[index]

            Drawable.updateOffset(player, SCREEN_SIZE,
                                  WORLD_SIZE, whichPlayer=index)

            backgrounds[index].draw(
                drawSurface, index)
            # Draw everything
            # drawSurface.fill((92,148,252))

            for floor in floorTiles:
                floor.draw(drawSurface, index)

            for enemy in enemies:
                enemy.draw(drawSurface, index)


            players[0].draw(drawSurface, index)
            players[1].draw(drawSurface, index)

            mainSurface.blit(drawSurface, (0, 0 if index ==
                             0 else SCREEN_SIZE.y // 2))

        pygame.transform.scale(mainSurface, list(
            UPSCALED_SCREEN_SIZE), screen)

        # Update everything

        # Flip the display to the monitor
        pygame.display.flip()

        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT or ESCAPE is pressed
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # change the value to False, to exit the main loop
                RUNNING = False

            for player in players:
                index = players.index(player)  # 0 or 1
                player.handleEvent(event)

        # Detect the floor collision
        for floor in floorTiles:
            for player in players:
                clipRect = player.getCollisionRect().clip(floor.getCollisionRect())

                if clipRect.width > 0:
                    player.collideGround(clipRect.height)
                    break

        # Update enemies/detect collision with player
        for enemy in enemies:
            for player in players:
                playerClipRect = enemy.getCollisionRect().clip(player.getCollisionRect())
                #enemyClipRect = mario.getCollisionRect().clip(enemy.getCollisionRect())

                if playerClipRect.width > 0:
                # print (mario._state.getState(), ": ",playerClipRect.height, ": ",playerClipRect.width )
                    if player._state.getState() == "falling" and playerClipRect.height <= playerClipRect.width:
                        enemies.remove(enemy)
                        #print("enemy merked")
                        pass
                    else:
                        player.kill()
                        time.sleep(2)
                        RUNNING = False
                
                for floor in floorTiles:
                    clipRect = enemy.getCollisionRect().clip(floor.getCollisionRect())

                    if clipRect.width > 0:
                        enemy.collideGround(clipRect.height)
                        break

        # Let our game clock tick at 60 fps
        gameClock.tick(60)

        # Get some time in seconds
        seconds = gameClock.get_time() / 1000

        # let others update based on the amount of time elapsed

        if seconds < 0.05:

            for player in players:
                player.update(seconds)
            
            for enemy in enemies:
                enemy.update(seconds)


if __name__ == "__main__":
    main()
