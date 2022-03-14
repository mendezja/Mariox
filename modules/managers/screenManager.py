from pygame.joystick import Joystick
from .basicManager import BasicManager
from .gameManager import GameManager
from ..UI.items import Text
from ..UI.displays import *
from ..gameObjects.vector2D import Vector2
from ..UI.screenInfo import SCREEN_SIZE
import pygame
from .gamemodes import *
from .soundManager import SoundManager
import time

class ScreenManager(BasicManager):

    RETURN_TO_MAIN = "returnToMain"

    def __init__(self, joysticks: 'list[Joystick]'):
        super().__init__()
        self._game = None
        self._state = ScreenState()
        self._pausedText = Text(Vector2(0, 0), "Paused")
        self._gameOverText = Text(Vector2(0, 0), "Game Over")
        self._gameWonText = Text(Vector2(0, 0), "Winner")
        self._joysticks = joysticks

        pausedTextSize = self._pausedText.getSize()
        midPointX = SCREEN_SIZE.x // 2 - pausedTextSize[0] // 2
        midPointY = SCREEN_SIZE.y // 2 - pausedTextSize[1] // 2

        self._pausedText.setPosition(Vector2(midPointX, midPointY))

        # Create Main Menu
        self._mainMenu = CursorMenu("menuBackground.png", fontName="default8")
        self._mainMenu.addOption(START_SINGLE_PLAYER, "Single-Player",
                                 SCREEN_SIZE // 2 + Vector2(0, 20),
                                 center="both")
        self._mainMenu.addOption(START_TWO_PLAYER, "Two-Player",
                                 SCREEN_SIZE // 2 + Vector2(0, 40),
                                 center="both")
        self._mainMenu.addOption(EXIT, "Exit Game",
                                 SCREEN_SIZE // 2 + Vector2(0, 60),
                                 center="both")
        self._mainMenu.setCursor(START_SINGLE_PLAYER)

        # Positon text for end menu
        gameOverTextSize = self._gameOverText.getSize()
        self._gameOverText.setPosition(
            SCREEN_SIZE // 2 - Vector2(gameOverTextSize[0]//2, gameOverTextSize[1]//2 + 50))
        
        
        # Create Game Over Menu
        self._gameOverMenu = CursorMenu("gameOver.png", fontName="default8")
        self._gameOverMenu.addOption(ScreenManager.RETURN_TO_MAIN, "Return to Main Menu", SCREEN_SIZE // 2 + Vector2(0, 50),
                                     center="both")
        self._gameOverMenu.addOption(EXIT, "Quit",
                                     SCREEN_SIZE // 2 + Vector2(0, 80),
                                     center="both")
        self._gameOverMenu.setCursor(ScreenManager.RETURN_TO_MAIN)
    
    

        # Create Game Won Menu
        self._gameWonMenu = CursorMenu("gameOver.png", fontName="default8")
        self._gameWonMenu.addOption(ScreenManager.RETURN_TO_MAIN, "Return to Main Menu", SCREEN_SIZE // 2 + Vector2(0, 50),
                                     center="both")
        self._gameWonMenu.addOption(EXIT, "Quit",
                                     SCREEN_SIZE // 2 + Vector2(0, 80),
                                     center="both")
        self._gameWonMenu.setCursor(ScreenManager.RETURN_TO_MAIN)

    def draw(self, mainSurface: pygame.Surface):
        if self._state == ScreenState.state["GAME"]:

            if self._game._mode == SINGLE_PLAYER:
                self._game.draw(mainSurface)
            elif self._game._mode == TWO_PLAYER:
                drawSurfaces: list[pygame.Surface] = [pygame.Surface(
                    (SCREEN_SIZE.x, SCREEN_SIZE.y//2)) for x in range(2)]
                self._game.draw(drawSurfaces[0], 0)
                self._game.draw(drawSurfaces[1], 1)
                mainSurface.blit(drawSurfaces[0], (0, 0))
                mainSurface.blit(drawSurfaces[1], (0, SCREEN_SIZE.y // 2))

                pygame.draw.line(mainSurface, (0,0,0), (0, SCREEN_SIZE.y//2), (SCREEN_SIZE.x ,SCREEN_SIZE.y//2), 2)

            if self._state.isPaused():
                self._pausedText.draw(
                    mainSurface, noOffset=True)

        elif self._state == ScreenState.state["MAIN_MENU"]:
            self._mainMenu.draw(mainSurface)

        elif self._state == ScreenState.state["GAME_OVER_MENU"]:
            self._gameOverMenu.draw(mainSurface)
            self._gameOverText.draw(mainSurface, noOffset=True)

        elif self._state == ScreenState.state["GAME_WON_MENU"]:
            self._gameWonMenu.draw(mainSurface)
            self._gameWonText.draw(mainSurface, noOffset=True)

    def handleEvent(self, event):
        # Handle screen-changing events first
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._state.manageState(ScreenState.actions["PAUSE"], self)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self._state.manageState(ScreenState.actions["MAIN_MENU"], self)
        else:
            if self._state == ScreenState.state["GAME"] and not self._state.isPaused():
                self._game.handleEvent(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self._currentMenu = 0
                    elif event.key == pygame.K_2:
                        self._currentMenu = 1
                    elif event.key == pygame.K_3:
                        self._currentMenu = 2
                if self._game.isGameOver():   
                    self._state.manageState(
                        ScreenState.actions["GAME_OVER"], self)
                elif self._game.isWon() != None:
                    # If two player change text
                    if self._game._mode == TWO_PLAYER:
                        winner = (self._game.isWon())[0:-4]
                        self._gameWonText = Text(Vector2(0, 0), (winner.upper()+" Wins" ))
                    # Update text Position 
                    gameWonTextSize = self._gameWonText.getSize()
                    self._gameWonText.setPosition(
                        SCREEN_SIZE // 2 - Vector2(gameWonTextSize[0]//2, gameWonTextSize[1]//2 + 50))
                    self._state.manageState(ScreenState.actions["GAME_WON"],self)
              

            elif self._state == ScreenState.state["MAIN_MENU"]:
                choice = self._mainMenu.handleEvent(event)
                if choice == START_SINGLE_PLAYER:
                    self._game = GameManager(
                        SCREEN_SIZE, SINGLE_PLAYER, "world1.txt", self._joysticks)

                    self._state.manageState(
                        ScreenState.actions["START_GAME"], self)
                elif choice == START_TWO_PLAYER:
                    self._game = GameManager(
                        SCREEN_SIZE, TWO_PLAYER,"world1.txt", self._joysticks)
                    self._state.manageState(
                        ScreenState.actions["START_GAME"], self)
                elif choice == EXIT:
                    return EXIT
            elif self._state == ScreenState.state["GAME_OVER_MENU"]:
                choice = self._gameOverMenu.handleEvent(event)
                if choice == ScreenManager.RETURN_TO_MAIN:
                    self._state.manageState(
                        ScreenState.actions["MAIN_MENU"], self)
                elif choice == EXIT:
                    return EXIT
            elif self._state == ScreenState.state["GAME_WON_MENU"]:
                choice = self._gameWonMenu.handleEvent(event)
                if choice == ScreenManager.RETURN_TO_MAIN:
                    self._state.manageState(
                        ScreenState.actions["MAIN_MENU"], self)
                elif choice == EXIT:
                    return EXIT

    def update(self, seconds):
        if self._state == ScreenState.state["GAME"] and not self._state.isPaused():
            self._game.update(seconds)
            if self._game.isGameOver():
                self._state.manageState(ScreenState.actions["GAME_OVER"], self)
        elif self._state == ScreenState.state["MAIN_MENU"]:
            self._mainMenu.update(seconds)
        elif self._state == ScreenState.state["GAME_OVER_MENU"]:
            self._gameOverMenu.update(seconds)
        elif self._state == ScreenState.state["GAME_WON_MENU"]:
            self._gameWonMenu.update(seconds)

    # Prevents player from constantly walking if the direction arrow
    #  is released when the game isn't playing

    def transitionState(self, state):
        if state == ScreenState.state["GAME"]:
            self._game.updateMovement()
        


class ScreenState(object):
    # actions
    actions = {
        "PAUSE": "pause",
        "MAIN_MENU": "mainMenu",
        "START_GAME": "startGame",
        "CURSOR": "cursor",
        "GAME_OVER": "gameOver",
        "GAME_WON": "gameWon"
    }

    # state
    state = {
        "GAME": "game",
        "MAIN_MENU": "mainMenu",
        "GAME_OVER_MENU": "gameOverMenu",
        "GAME_WON_MENU": "gameWonMenu"
    }

    def __init__(self, state=state["MAIN_MENU"]):
        self._state = state
        self._paused = False

    def manageState(self, action: str, screenManager: 'ScreenManager'):
        if action == ScreenState.actions["PAUSE"] and self._state == ScreenState.state["GAME"]:
            self._paused = not self._paused
            screenManager.transitionState(self._state)
            if self._paused:
                SoundManager.getInstance().playSound("pause.wav")
                SoundManager.getInstance().pauseMusic()
            else:
                SoundManager.getInstance().unpauseMusic()

        elif action == ScreenState.actions["MAIN_MENU"] and not self._paused and self._state != ScreenState.state["MAIN_MENU"]:
            self._state = ScreenState.state["MAIN_MENU"]
            screenManager.transitionState(self._state)

        elif action == ScreenState.actions["START_GAME"] and self._state != ScreenState.state["GAME"]:
            self._state = ScreenState.state["GAME"]
            screenManager.transitionState(self._state)

        elif action == ScreenState.actions["CURSOR"] and self._state != ScreenState.state["MAIN_MENU"]:
            self._state = ScreenState.state["MAIN_MENU"]
            screenManager.transitionState(self._state)

        elif action == ScreenState.actions["GAME_OVER"] and self._state == ScreenState.state["GAME"]:
            self._state = ScreenState.state["GAME_OVER_MENU"]
            time.sleep(1)
            screenManager.transitionState(self._state)
        

        elif action == ScreenState.actions["GAME_WON"] and self._state == ScreenState.state["GAME"]:
            self._state = ScreenState.state["GAME_WON_MENU"]
            time.sleep(1)
            screenManager.transitionState(self._state)

            
    def __eq__(self, other):
        return self._state == other

    def isPaused(self):
        return self._paused
