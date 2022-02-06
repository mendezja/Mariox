
from .animated import Animated
from .vector2D import Vector2
from .frameManager import FrameManager


class Mobile(Animated):
    def __init__(self, imageName, position):
        super().__init__(imageName, position)
        self._velocity = Vector2(0, 0)
        self._jumpTimer = 0
        self._jSpeed = 0
        self._vSpeed = 0
        self._jumpTime = 0
        self._nFramesList: dict[str, int] = {}
        self._rowList: dict[str, int] = {}
        self._framesPerSecondList: dict[str, int] = {}
        self._state = MobileState()

    def update(self, seconds):
        self.updateVelocity(seconds)
        self.updatePosition(seconds)

    def updateVelocity(self, seconds):
        '''Helper method for update'''
        super().update(seconds)

        if self._state.isMoving():

            if self._state._movement["left"]:
                self._velocity.x = -self._vSpeed
            elif self._state._movement["right"]:
                self._velocity.x = self._vSpeed
        else:
            self._velocity.x = 0

    def updatePosition(self, seconds):
        '''Helper method for update'''
        newPosition = self.getPosition() + self._velocity * seconds

        self.setPosition(newPosition)

    def transitionState(self, state):

        if state == "jumping":
            self._jumpTimer = self._jumpTime

        self._nFrames = self._nFramesList[state]
        self._frame = 0
        self._row = self._rowList[state]
        self._framesPerSecond = self._framesPerSecondList[state]
        self._animationTimer = 0
        self.setImage(FrameManager.getInstance().getFrame(
            self._imageName, (self._frame, self._row)))


class MobileState(object):
    def __init__(self, state="falling"):
        self._state = state

        self._movement = {
            "left": False,
            "right": False
        }

        self._lastFacing = "right"

    def isMoving(self):
        return True in self._movement.values()

    def getFacing(self):
        if self._movement["left"] == True:
            self._lastFacing = "left"
        elif self._movement["right"] == True:
            self._lastFacing = "right"

        return self._lastFacing

    def getState(self):
        return self._state
