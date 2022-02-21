
from tkinter.font import BOLD
from .basicManager import BasicManager
from ..gameObjects.drawable import Drawable
from ..gameObjects.backgrounds import *
from ..gameObjects.vector2D import Vector2
from ..gameObjects.player import Player
from ..gameObjects.enemy import Enemy
from ..UI.screenInfo import SCREEN_SIZE


class GameManager(BasicManager):

    WORLD_SIZE = Vector2(2624, 240)

    def __init__(self, screenSize):
        self._player = Player("mario.png", Vector2(0, 0))
        # self._floor = Floor(GameManager.WORLD_SIZE.x,
        #                     GameManager.WORLD_SIZE.y-32)
        self._floor = [Drawable("brick.png", Vector2(x, SCREEN_SIZE.y - 32))
                       for x in range(0, GameManager.WORLD_SIZE.x, 16)]
        self._background = EfficientBackground(
            screenSize, "background.png", parallax=0)
        self._enemies = [Enemy("enemies.png",  list(
            GameManager.WORLD_SIZE//x)) for x in range(2, 16, 2)]

    def draw(self, drawSurf: pygame.surface.Surface):

        # Draw everything
        self._background.draw(drawSurf)
        for floor in self._floor:
            floor.draw(drawSurf)
        self._player.draw(drawSurf)
        for enemy in self._enemies:
            enemy.draw(drawSurf)

    def handleEvent(self, event):
        self._player.handleEvent(event)

    def update(self, seconds) -> bool:
        # Update everything
        Drawable.updateOffset(self._player, SCREEN_SIZE,
                              GameManager.WORLD_SIZE)

        # Detect the floor collision
        for floor in self._floor:
            clipRect = self._player.getCollisionRect().clip(floor.getCollisionRect())

            if clipRect.width > 0:
                self._player.collideGround(clipRect.height)
                break

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            playerClipRect = enemy.getCollisionRect().clip(self._player.getCollisionRect())
            #enemyClipRect = mario.getCollisionRect().clip(enemy.getCollisionRect())

            if playerClipRect.width > 0:
               # print (mario._state.getState(), ": ",playerClipRect.height, ": ",playerClipRect.width )
                if self._player._state.getState() == "falling" and playerClipRect.height <= playerClipRect.width:
                    self._enemies.remove(enemy)
                    #print("enemy merked")
                    pass
                else:
                    self._player.kill()
                    return False

            for floor in self._floor:
                clipRect = enemy.getCollisionRect().clip(floor.getCollisionRect())

                if clipRect.width > 0:
                    enemy.collideGround(clipRect.height)
                    break

        # let others update based on the amount of time elapsed
        if seconds < 0.05:

            self._player.update(seconds, GameManager.WORLD_SIZE)

            for enemy in self._enemies:
                enemy.update(seconds, GameManager.WORLD_SIZE)

        return True

    def updateMovement(self):
        self._player.updateMovement()
