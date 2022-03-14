from .vector2D import Vector2
from .mobile import Mobile
from .player import Player
from .drawable import Drawable
from ..managers.frameManager import FrameManager
from ..managers.soundManager import SoundManager

import pygame
from pygame.event import Event


class Enemy(Mobile):

    def __init__(self, enemyName: str, position: Vector2, offset=None, isSmart: bool = False):
        super().__init__(enemyName, position, offset)
        self._killSound = "mario_stomp.wav"
        self._jumpTime = 0.01
        self._vSpeed = 50
        self._jSpeed = 100
        self._isSmart = isSmart

        self._nFrames = 2
        self._framesPerSecond = 2

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

    def updateCollisions(self, players: 'list[Player]', blocks: 'list[Drawable]'):
        if self._isDead:
            return

        eRect = self.getCollisionRect()

        for player in players:
            playerClipRect = eRect.clip(player.getCollisionRect())

            if playerClipRect.width > 0:
                if player._velocity.y > 0 and playerClipRect.height <= playerClipRect.width:
                    self.kill()
                    break
                else:
                    player.kill()
                    self._gameOver = True
                    SoundManager.getInstance().stopMusic()

                    return

            hasFloor = False

        for block in blocks:
            clipRect = eRect.clip(block.getCollisionRect())
            if clipRect.width > 0:
                # check virtical collide   clipRect.width > clipRect.height and
                if self._velocity.y > 0 and clipRect.width > clipRect.height:
                    self.collideGround(clipRect.height)
                    hasFloor = True
                    break
                elif clipRect.width < clipRect.height:  # check for horizontal collide
                    self.collideWall(clipRect.width)
                    break
            elif (eRect.move(0, 1)).colliderect(block.getCollisionRect()):  # check for ground
                hasFloor = True
                break

        if not hasFloor:
            self.fall()
