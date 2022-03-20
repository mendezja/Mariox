from ast import Str
import os

from modules.managers.soundManager import SoundManager
from .basicManager import BasicManager
from ..gameObjects.drawable import Drawable
from ..gameObjects.backgrounds import *
from ..gameObjects.vector2D import Vector2
from ..gameObjects.player import Player
from ..gameObjects.enemy import Enemy, Turtle
from ..UI.screenInfo import SCREEN_SIZE
from .gamemodes import *
from pygame.joystick import Joystick
import pygame


class GameManager(BasicManager):

    WORLD_SIZE = None

    BLOCKS_OFFSETS = {"G": (2, 0),  # Ground
                      "L": (0, 0),  # Leaves
                      "<": (1, 0),  # End Leaves Right
                      ">": (0, 1),  # End Leaves Left
                      "W": (3, 0),  # Wall Brick
                      "S": (2, 1)  # Stud Brick
                      }

    def __init__(self, screenSize: Vector2, mode: str, levelFile: str, joysticks: 'list[Joystick]'):
        self._screenSize = screenSize
        self._levelFile = levelFile
        self._mode = mode
        self._joysticks = joysticks

        # Start playing music
        SoundManager.getInstance().playMusic("marioremix.mp3")

        self._blocks: list[Drawable] = []
        self._decor: list[Drawable] = []
        self._enemies: list[Enemy] = []
        self._players: list[Player] = []
        self._end: Drawable = None
        self._gameOver = False
        self._winner: Str = ""  # gameWon = False

        backgroundImage = "battleBackground.jpeg" if mode in [
            BATTLE] else "background.png"
        self._background = EfficientBackground(
            self._screenSize, backgroundImage, parallax=0)

        file = open(os.path.join("resources", "levels", self._levelFile))
        fileCharacters = [[y for y in x]
                          for x in file.read().split("\n")]
        tileSize = 16

        GameManager.WORLD_SIZE = Vector2(len(fileCharacters[0]) * tileSize,
                                         len(fileCharacters) * tileSize)

        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                elemChar = fileCharacters[row][col]

                if elemChar in self.BLOCKS_OFFSETS.keys():  # physics bound blocks
                    self._blocks.append(Drawable("blocks.png", Vector2(
                        col*tileSize, row*tileSize), self.BLOCKS_OFFSETS[elemChar]))
                elif elemChar == "B":  # non-physics blocks
                    self._decor.append(Drawable("blocks.png", Vector2(
                        col*tileSize, row*tileSize), (1, 1)))
                elif elemChar == "E":  # enemies
                    self._enemies.append(
                        Enemy("enemies.png",  Vector2(col*tileSize, row*tileSize)))
                elif elemChar == "T":
                    self._enemies.append(
                        Turtle(Vector2(col*tileSize, row*tileSize)))

                elif elemChar == "F":  # Flag
                    self._end = Drawable("flagPost.png", Vector2(
                        col*tileSize, row*tileSize))

                elif elemChar == "1":  # player 1
                    self._players.append(Player("mario.png", Vector2(
                        col*tileSize, row*tileSize), self._joysticks[0] if len(self._joysticks) >= 1 else None, hasGun=(self._mode == BATTLE)))

                elif elemChar == "2" and self._mode in [TWO_PLAYER, BATTLE]:
                    self._players.append(Player("luigi.png", Vector2(
                        col*tileSize, row*tileSize), self._joysticks[1] if len(self._joysticks) == 2 else None, hasGun=(self._mode == BATTLE)))

    def draw(self, drawSurf: pygame.surface.Surface, whichPlayer=None):

        # Draw everything

        self._background.draw(drawSurf, whichPlayer)

        for decor in self._decor:
            decor.draw(drawSurf, whichPlayer)
        for block in self._blocks:
            block.draw(drawSurf, whichPlayer)

        if self._end:
            self._end.draw(drawSurf, whichPlayer)
        for enemy in self._enemies:
            enemy.draw(drawSurf, whichPlayer)
           # pygame.draw.rect(drawSurf,(0,0,0), enemy.getCollisionRect())
        for player in self._players:
            player.draw(drawSurf, whichPlayer, drawCollision=False)
            for bullet in player.getBullets():
                bullet.draw(drawSurf, whichPlayer)

    def handleEvent(self, event):
        if not self._gameOver:
            for player in self._players:
                player.handleEvent(event)

    def update(self, seconds):
        # Update everything

        for player in self._players:

            whichPlayer = None if self._mode in [
                SINGLE_PLAYER, BATTLE] else self._players.index(player)
            Drawable.updateOffset(
                player, SCREEN_SIZE, GameManager.WORLD_SIZE, whichPlayer=whichPlayer)

        # Update enemies/detect collision with player
        for player in self._players:
            self._winner = player.updateCollisions(self._blocks, self._end)
            # pRect = self.getCollisionRect()

        # # Dectect if won for each player
        # if end != None:
        #     if pRect.clip(end.getCollisionRect()).width > 0:
        #         self.updateMovement()
        #         return str(self._imageName)

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            if type(enemy) == Turtle:
                enemy.updateCollisions(
                    self._players, self._blocks, self._enemies)

            else:
                enemy.updateCollisions(self._players, self._blocks)

        for player in self._players:
            for bullet in player.getBullets():
                bullet.detectCollision(self._players)

        # let others update based on the amount of time elapsed
        if seconds < 0.05:

            for player in self._players:
                for bullet in player.getBullets():
                    if bullet._isDead:
                        player._bullets.remove(bullet)
                    bullet.update(seconds)
                if player._isDead:
                    if self._mode in [TWO_PLAYER, BATTLE]:
                        index = (self._players.index(player) +
                                 1) % 2  # Gets index of other player
                        self._winner = self._players[index]._imageName
                        # TODO show correct winner
                    self._gameOver = True
                    SoundManager.getInstance().stopMusic()
                    return

                player.update(seconds, GameManager.WORLD_SIZE)

            for enemy in self._enemies:
                if enemy._isDead:
                    self._enemies.remove(enemy)
                    pass

                enemy.update(seconds, GameManager.WORLD_SIZE)

    def updateMovement(self):
        for player in self._players:
            player.updateMovement()

    def isGameOver(self):
        return self._gameOver

    def isWon(self):
        return self._winner
