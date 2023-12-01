
import pygame
from pygame.joystick import Joystick
import os
from modules.managers.screenManager import ScreenManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE


def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo
    pygame.display.set_caption("M@rio+")
    # Initialize sounds
    pygame.mixer.init()
    pygame.mixer.music.load("./resources/music/marioremix.mp3")

    screen = pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE))

    drawSurface = pygame.Surface(list(SCREEN_SIZE))

    # Initialize joysticks
    joysticks: list[Joystick] = []
    try:
        pygame.joystick.init()
        try:
            joysticks.append(Joystick(0))
            joysticks.append(Joystick(1))
        except:
            print("one joystick")
    except:
        print("no joysticks")

    screenManager = ScreenManager(joysticks)

    # Make a game clock for nice, smooth animations
    gameClock = pygame.time.Clock()

    RUNNING = True 
    
    while RUNNING:

        screenManager.draw(drawSurface)

        pygame.transform.scale(drawSurface, list(UPSCALED_SCREEN_SIZE), screen)

        # Flip the display to the monitor
        pygame.display.flip()

        # event handling, gets all event from the eventqueue
        # if event in pygame.event.get():
        for event in pygame.event.get():
            # only do something if the event is of type QUIT or ESCAPE is pressed
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # change the value to False, to exit the main loop
                RUNNING = False
                break

            result = screenManager.handleEvent(event)

            if result == "exit":
                RUNNING = False
                break

        screenManager.handelBot()


        # Let our game clock tick at 60 fps
        gameClock.tick(60)

        # Get some time in seconds
        seconds = min(0.5, gameClock.get_time() / 1000)
     
        screenManager.update(seconds)



if __name__ == "__main__":
    main()
