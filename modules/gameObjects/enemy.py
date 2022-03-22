from .vector2D import Vector2
from .mobile import Mobile, MobileState
from .player import Player
from .drawable import Drawable
from ..managers.frameManager import FrameManager
from ..managers.soundManager import SoundManager

import pygame
from pygame.event import Event


class Enemy(Mobile):

    def __init__(self, enemyName: str, position: Vector2, offset=None):
        super().__init__(enemyName, position, offset)
        self._killSound = "mario_stomp.wav"
        self._jumpTime = 0.01
        self._vSpeed = 50
        self._jSpeed = 100

        self._nFrames = 2
        self._framesPerSecond = 2

        self._nFramesList = {
            "walking": 2,
            "falling": 1,
            "standing": 1,
            "jumping": 6,
            "dead": 1
        }

        self._rowList = {
            "walking": 0,
            "falling": 0,
            "standing": 1,
            "jumping": 1,
            "dead": 1
        }

        self._framesPerSecondList = {
            "walking": 8,
            "falling": 1,
            "standing": 1,
            "jumping": 1,
            "dead": 1
        }
        self._state = MobileState()
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

        self.transitionState("walking")

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
                elif clipRect.width < clipRect.height and clipRect.width > 0:  # check for horizontal collide
                    self.collideWall(clipRect.width)
                    break
            elif (eRect.move(0, 1)).colliderect(block.getCollisionRect()):  # check for ground
                hasFloor = True
                break

        if not hasFloor:
            self.fall()


class Turtle(Enemy):
    def __init__(self, position: Vector2, offset=None):
        super().__init__("turtle.png", position, offset)
        self._state = MobileState()

        self._nFramesList.update({"sliding": 1})
        self._rowList.update({"sliding": 1})
        self._framesPerSecondList.update({"sliding": 1})

    def collideWall(self, xClip):
        super().collideWall(xClip)

        if self._state.getState() == "sliding":
            self.transitionState("sliding")

    def updateCollisions(self, players: 'list[Player]', blocks: 'list[Drawable]', enemies: 'list[Enemy]'):
        if self._isDead:
            return

        eRect = self.getCollisionRect()

        for player in players:
            playerClipRect = eRect.clip(player.getCollisionRect())

            if playerClipRect.width > 0:
                if player._velocity.y > 0 and playerClipRect.height//2 <= playerClipRect.width:
                    if self._state.getState() != "slidng":
                        self._state.manageState("hide", self)

                        player._state.manageState("ground", self)
                        player._state.manageState("jump", self)

                    else:
                        self._vSpeed = 0

                else:
                    player.kill()
                    self._gameOver = True
                    SoundManager.getInstance().stopMusic()
                    return

        if self._state.getState() == "sliding":
            for other in enemies:
                otherClipRect = eRect.clip(other.getCollisionRect())

                if otherClipRect.width > 0 and other != self:
                    other.kill()
                    pass

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
            if not self._state.getState() == "sliding":

                self.collideWall(0)
            else:

                self._velocity.y = 50
                return


# class TurtleState(MobileState):
#     def __init__(self, state="falling"):
#         super().__init__(state)

#     def manageState(self, action: str, enemy: Mobile):
#         super().manageState(action, enemy )
#         if action == "hide":
#             self._state = "sliding"
#             enemy._vSpeed = 200

#             enemy.transitionState(self._state)
