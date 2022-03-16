from pygame import Rect
from modules.gameObjects.animated import Animated
from modules.gameObjects.drawable import BasicState
from modules.gameObjects.vector2D import Vector2


class Bullet(Animated):
    def __init__(self, position, direction):
        super().__init__("bulletbill.png", position +
                         Vector2((16 if direction == "right" else -28), -8))
        self._state = BasicState(direction)
        self._velocity = Vector2(70, 0)
        self._timeToLive = 3
        self._isDead = False

        self._row = 0
        self._nFrames = 5
        self._framesPerSecond = 10

        self._nFramesList = {
            "flying": 5
        }

        self._rowList = {
            "flying": 0
        }

        self._framesPerSecondList = {
            "flying": 5
        }

    def update(self, seconds):
        super().update(seconds)
        self.updatePosition(seconds)
        self._timeToLive -= seconds
        if self._timeToLive < 0:
            self._isDead = True

    def updatePosition(self, seconds):
        '''Helper method for update'''
        self._position += self._velocity * seconds * \
            (-1 if self._state.getFacing() == "left" else 1)

    def detectCollision(self, players):
        for player in players:
            if player.getCollisionRect().clip(self.getCollisionRect()).width > 0:
                player.kill()
                return player
