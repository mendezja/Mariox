from pygame.joystick import Joystick
from .basicManager import BasicManager
from .gameManager import GameManager
from ..UI.items import Text
from ..UI.displays import *
from ..gameObjects.vector2D import Vector2
from ..UI.screenInfo import SCREEN_SIZE
import pygame
from .gamemodes import *


class ScreenManager(BasicManager):

    def __init__(self, joysticks: 'list[Joystick]'):
        super().__init__()
        self._game = None
        self._state = ScreenState()
        self._pausedText = Text(Vector2(0, 0), "Paused")
        self._joysticks = joysticks

        size = self._pausedText.getSize()
        midPointX = SCREEN_SIZE.x // 2 - size[0] // 2
        midPointY = SCREEN_SIZE.y // 2 - size[1] // 2

        self._pausedText.setPosition(Vector2(midPointX, midPointY))

        self._mainMenu = CursorMenu("background.png", fontName="default8")
        self._mainMenu.addOption(START_SINGLE_PLAYER, "Single-Player",
                                 SCREEN_SIZE // 2 - Vector2(0, 50),
                                 center="both")
        self._mainMenu.addOption(START_TWO_PLAYER, "Two-Player",
                                 SCREEN_SIZE // 2,
                                 center="both")
        self._mainMenu.addOption(EXIT, "Exit Game",
                                 SCREEN_SIZE // 2 + Vector2(0, 50),
                                 center="both")

    def draw(self, mainSurface: pygame.Surface):
        if self._state == "game":

            if self._game._mode == SINGLE_PLAYER:
                self._game.draw(mainSurface)
            elif self._game._mode == TWO_PLAYER:
                drawSurfaces: list[pygame.Surface] = [pygame.Surface(
                    (SCREEN_SIZE.x, SCREEN_SIZE.y//2)) for x in range(2)]
                self._game.draw(drawSurfaces[0], 0)
                self._game.draw(drawSurfaces[1], 1)
                mainSurface.blit(drawSurfaces[0], (0, 0))
                mainSurface.blit(drawSurfaces[1], (0, SCREEN_SIZE.y // 2))

            if self._state.isPaused():
                self._pausedText.draw(
                    mainSurface, noOffset=True)

        elif self._state == "mainMenu":
            self._mainMenu.draw(mainSurface)

    def handleEvent(self, event):
        # Handle screen-changing events first
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._state.manageState("pause", self)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self._state.manageState("mainMenu", self)
        else:
            if self._state == "game" and not self._state.isPaused():
                self._game.handleEvent(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self._currentMenu = 0
                    elif event.key == pygame.K_2:
                        self._currentMenu = 1
                    elif event.key == pygame.K_3:
                        self._currentMenu = 2
            elif self._state == "mainMenu":
                choice = self._mainMenu.handleEvent(event)

                if choice == START_SINGLE_PLAYER:
                    if len(self._joysticks) >= 1:
                        self._game = GameManager(
                            SCREEN_SIZE, SINGLE_PLAYER, self._joysticks)
                        self._state.manageState("startGame", self)
                    else:
                        print("Need one joystick")
                elif choice == START_TWO_PLAYER:
                    if len(self._joysticks) == 2:
                        self._game = GameManager(
                            SCREEN_SIZE, TWO_PLAYER, self._joysticks)
                        self._state.manageState("startGame", self)
                    else:
                        print("Need two joysticks")
                elif choice == EXIT:
                    return EXIT

    def update(self, seconds):
        if self._state == "game" and not self._state.isPaused():
            self._game.update(seconds)
        elif self._state == "mainMenu":
            self._mainMenu.update(seconds)

    # Prevents player from constantly walking if the direction arrow
    #  is released when the game isn't playing

    def transitionState(self, state):
        if state == "game":
            self._game.updateMovement()


class ScreenState(object):
    def __init__(self, state="mainMenu"):
        self._state = state
        self._paused = False

    def manageState(self, action, screenManager: ScreenManager):
        if action == "pause" and self._state == "game":
            self._paused = not self._paused
            screenManager.transitionState(self._state)

        elif action == "mainMenu" and not self._paused and self._state != "mainMenu":
            self._state = "mainMenu"
            screenManager.transitionState(self._state)

        elif action == "startGame" and self._state != "game":
            self._state = "game"
            screenManager.transitionState(self._state)

        elif action == "cursor" and self._state != "mainMenu":
            self._state = "mainMenu"
            screenManager.transitionState(self._state)

    def __eq__(self, other):
        return self._state == other

    def isPaused(self):
        return self._paused
