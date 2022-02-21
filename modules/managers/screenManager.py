from .basicManager import BasicManager
from .gameManager import GameManager
from ..UI.items import Text
from ..UI.displays import *
from ..gameObjects.vector2D import Vector2
from ..UI.screenInfo import SCREEN_SIZE
import pygame


class ScreenManager(BasicManager):

    def __init__(self):
        super().__init__()
        self._game = GameManager(SCREEN_SIZE)
        self._state = ScreenState()
        self._pausedText = Text(Vector2(0, 0), "Paused")

        size = self._pausedText.getSize()
        midPointX = SCREEN_SIZE.x // 2 - size[0] // 2
        midPointY = SCREEN_SIZE.y // 2 - size[1] // 2

        self._pausedText.setPosition(Vector2(midPointX, midPointY))

        self._mainMenu = CursorMenu("background.png", fontName="default8")
        self._mainMenu.addOption("start", "Start Game",
                                 SCREEN_SIZE // 2 - Vector2(0, 50),
                                 center="both")
        self._mainMenu.addOption("exit", "Exit Game",
                                 SCREEN_SIZE // 2 + Vector2(0, 50),
                                 center="both")

    def draw(self, drawSurf):
        if self._state == "game":
            self._game.draw(drawSurf)

            if self._state.isPaused():
                self._pausedText.draw(drawSurf)

        elif self._state == "mainMenu":
            self._mainMenu.draw(drawSurf)

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

                if choice == "start":
                    self._state.manageState("startGame", self)
                elif choice == "exit":
                    return "exit"

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

        elif action in ["cursor", "event", "hoverclick"] and self._state != "mainMenu":
            self._state = "mainMenu"
            screenManager.setMainMenu(action)
            screenManager.transitionState(self._state)

    def __eq__(self, other):
        return self._state == other

    def isPaused(self):
        return self._paused
