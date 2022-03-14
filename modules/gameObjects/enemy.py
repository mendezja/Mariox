from .vector2D import Vector2
from .mobile import Mobile
from ..managers.frameManager import FrameManager

import pygame
from pygame.event import Event

from ..managers.soundManager import SoundManager

class Enemy(Mobile):

    def __init__(self, enemyName: str, position: Vector2, offset = None):
        super().__init__(enemyName, position, offset)

        self._jumpTime = 0.01
        self._vSpeed = 50
        self._jSpeed = 100

        self._nFrames = 2
        self._framesPerSecond = 2

        #self._isDead = False

        self._nFramesList = {
            "walking": 2,
            "falling": 1,
            "standing": 1,
            "dead": 1
        }

        self._rowList = {
            "walking": 0,
            "falling": 0,
            "standing": 0,
            "dead": 1
        }

        self._framesPerSecondList = {
            "walking": 8,
            "falling": 8,
            "standing": 1,
            "dead": 1
        }

        #self._state = EnemyState()
        self.transitionState("falling")

    def collideGround(self, yClip):
        super().collideGround(yClip)

        self._state.manageState(self._state.getFacing(), self)
    def collideWall(self, xClip):
        super().collideWall(xClip)
        self._velocity.x *= -1

        if self._state.getFacing() == "right":
            self._state.manageState("left", self)
            
        else:
            self._state.manageState("right", self)
        self.transitionState("falling")
    
    def kill(self):
        SoundManager.getInstance().playSound("mario_stomp.wav")
        print("killed enemy")
        super().kill()
