
from modules.managers.soundManager import SoundManager
from .animated import Animated
from .vector2D import Vector2
from ..managers.frameManager import FrameManager

import pygame
from pygame.event import Event
from pygame.joystick import Joystick

class Mobile(Animated):
    def __init__(self, imageName, position, offset=None):
        super().__init__(imageName, position, offset)
        self._killSound = None
        self._velocity = Vector2(0, 0)
        self._jumpTimer = 0
        self._jSpeed = 0
        self._vSpeed = 0
        self._jumpTime = 0
        self._nFramesList: dict[str, int] = {}
        self._rowList: dict[str, int] = {}
        self._framesPerSecondList: dict[str, int] = {}
        self._state = MobileState()
        self._isDead = False

        self._row = 0

    def update(self, seconds, boundaries):
        self.updateVelocity(seconds)
        self.updatePosition(seconds, boundaries)


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

        if self._state.getState() == "standing":
            self._velocity.y = 0
        elif self._state.getState() == "falling":
            self._velocity.y += self._jSpeed * seconds*1.2
        

    def updatePosition(self, seconds, boundaries):
        '''Helper method for update'''
        newPosition = self.getPosition() + self._velocity * seconds

        if newPosition.x < 0 or newPosition.x > boundaries.x - self.getSize()[0]:
            newPosition = self.getPosition() #+ self._velocity * seconds
        if  newPosition.y > boundaries.y - self.getSize()[1]:#newPosition.y < 0 or
            self.kill() 
        else:
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

    
    def collideGround(self, yClip):
        if self._velocity.y < 0:   
            self._state.manageState("fall", self)
            self._velocity.y *= -.8
            self._position.y += yClip
            return False

        else:
            self._state.manageState("ground", self)
            self._position.y -= yClip
            return True
    
    def collideWall(self, xClip):
        
        if self._state._movement["left"] == True:
            self._state.manageState("stopleft", self)
            self._position.x += xClip

        elif self._state._movement["right"] == True:
            self._state.manageState("stopright", self)
            self._position.x -= xClip

        self._state.manageState("ground", self)
    
    def fall (self): #to be used when gravity is needed
        self._state.manageState("fall", self)   

    
    def kill(self):
        self._isDead = True
        self._state.manageState("dead", self)
        if self._killSound != None:
            SoundManager.getInstance().playSound(self._killSound)




class MobileState(object):
    def __init__(self, state="falling"):
        self._state = state

        self._movement = {
            "left": False,
            "right": False
        }

        self._lastFacing = "left"

    def isMoving(self):
        return True in self._movement.values()

    def isGrounded(self):
        return self._state == "walking" or self._state == "standing"

    def getFacing(self):
        if self._movement["left"] == True:
            self._lastFacing = "left"
        elif self._movement["right"] == True:
            self._lastFacing = "right"

        return self._lastFacing

    def manageState(self, action: str, player: Mobile):
        if action in self._movement.keys():
            if self._movement[action] == False:
                self._movement[action] = True
                if self._state == "standing":
                     player.transitionState("walking")

        elif action == "dead":
            self._state = "dead"
            player.transitionState(self._state)
            #player.transitionState("falling")

        elif action.startswith("stop") and action[4:] in self._movement.keys():
            direction = action[4:]
            if self._movement[direction] == True:
                self._movement[direction] = False
                allStop = True
                for move in self._movement.keys():
                    if self._movement[move] == True:
                        allStop = False
                        break

                if allStop and self._state not in ["falling", "jumping"]:
                    player.transitionState(self._state)

        elif action == "jump" and self._state == "standing":
            SoundManager.getInstance().playSound("mario_jump.wav")
            self._state = "jumping"
            player.transitionState(self._state)

        elif action == "fall" and self._state != "falling":
            self._state = "falling"
            player.transitionState(self._state)

        elif action == "ground" and self._state == "falling":

            self._state = "standing"

            if self.isMoving():
                player.transitionState("walking")
            else:
                player.transitionState(self._state)


    def getState(self):
        return self._state
