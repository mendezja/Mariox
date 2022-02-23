
from tkinter.font import BOLD
from .basicManager import BasicManager
from ..gameObjects.drawable import Drawable
from ..gameObjects.backgrounds import *
from ..gameObjects.vector2D import Vector2
from ..gameObjects.player import Player
from ..gameObjects.enemy import Enemy
from ..UI.screenInfo import SCREEN_SIZE
from .gamemodes import *
from pygame.joystick import Joystick


class GameManager(BasicManager):

    WORLD_SIZE = Vector2(2624, 240)

    def __init__(self, screenSize: Vector2, mode: str, joysticks: 'list[Joystick]'):
        self._mode = mode
        self._joysticks = joysticks
        self._players: list[Player] = []
        if mode == SINGLE_PLAYER:
            if len(joysticks) >= 1:
                self._players.append(
                    Player("mario.png", Vector2(10, GameManager.WORLD_SIZE.y - 48), joysticks[0]))
            else:
                print("Need one joystick")
        elif mode == TWO_PLAYER:
            if len(joysticks) == 2:
                self._players = [Player("mario.png", Vector2(10, GameManager.WORLD_SIZE.y - 48), joysticks[x])
                                 for x in range(2)]
            else:
                print("Need two joysticks")

        self._floor = [Drawable("brick.png", Vector2(x, SCREEN_SIZE.y - 32))
                       for x in range(0, GameManager.WORLD_SIZE.x, 16)]
        self._background = EfficientBackground(
            screenSize, "background.png", parallax=0)
        self._enemies = [Enemy("enemies.png",  list(
            GameManager.WORLD_SIZE//x)) for x in range(2, 16, 2)]

    def draw(self, drawSurf: pygame.surface.Surface, whichPlayer=None):

        # Draw everything
        self._background.draw(drawSurf, whichPlayer)
        for floor in self._floor:
            floor.draw(drawSurf, whichPlayer)
        for player in self._players:
            player.draw(drawSurf, whichPlayer)
        for enemy in self._enemies:
            enemy.draw(drawSurf, whichPlayer)

    def handleEvent(self, event):
        for player in self._players:
            player.handleEvent(event)

    def update(self, seconds) -> bool:
        # Update everything
        for player in self._players:
            whichPlayer = None if len(
                self._players) == 1 else self._players.index(player)
            Drawable.updateOffset(
                player, SCREEN_SIZE, GameManager.WORLD_SIZE, whichPlayer=whichPlayer)

        # Detect the floor collision
        for floor in self._floor:
            for player in self._players:
                clipRect = player.getCollisionRect().clip(floor.getCollisionRect())

                if clipRect.width > 0:
                    player.collideGround(clipRect.height)
                    break

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            for player in self._players:
                playerClipRect = enemy.getCollisionRect().clip(player.getCollisionRect())
                # enemyClipRect = mario.getCollisionRect().clip(enemy.getCollisionRect())

                if playerClipRect.width > 0:
                    # print (mario._state.getState(), ": ",playerClipRect.height, ": ",playerClipRect.width )
                    # TODO fix bug where if both players jump on the same enemy at the same time it crashes
                    if player._state.getState() == "falling" and playerClipRect.height <= playerClipRect.width:
                        self._enemies.remove(enemy)
                        pass
                    else:
                        player.kill()
                        return False

                for floor in self._floor:
                    clipRect = enemy.getCollisionRect().clip(floor.getCollisionRect())

                    if clipRect.width > 0:
                        enemy.collideGround(clipRect.height)
                        break

        # let others update based on the amount of time elapsed
        if seconds < 0.05:

            for player in self._players:
                player.update(seconds, GameManager.WORLD_SIZE)

            for enemy in self._enemies:
                enemy.update(seconds, GameManager.WORLD_SIZE)

        return True

    def updateMovement(self):
        for player in self._players:
            player.updateMovement()
