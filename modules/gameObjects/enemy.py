from .vector2D import Vector2
from .mobile import Mobile
from ..managers.frameManager import FrameManager

import pygame
from pygame.event import Event

from ..managers.soundManager import SoundManager

class Enemy(Mobile):

    def __init__(self, enemyName: str, position: Vector2):
        super().__init__(enemyName, position)

        self._jumpTime = 0.01
        self._vSpeed = 50
        self._jSpeed = 100

        self._nFrames = 2
        self._framesPerSecond = 2

        self._isDead = False

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

        self._state = EnemyState()
        
        self.transitionState("falling")
        #self._state.manageState("left", self)

    def updateVelocity(self, seconds):
        super().updateVelocity(seconds)

        if self._state.getState() == "standing":
            self._velocity.y = 0
        elif self._state.getState() == "falling":
            self._velocity.y += self._jSpeed * seconds
        elif self._state.getState() == "dying":
            self._velocity = Vector2(0, 0)

    def collideGround(self, yClip):
        #print("you fucking dumbass")
        self._position.y -= yClip
        self._state.manageState("ground", self)
        
        self._state.manageState("left", self)
        
    
    def collideWall(self, xClip):
        #self._state.manageState("ground", self)
        
        if self._state._movement["left"] == True:
            self._state.manageState("stopleft", self)
            self._state.manageState("right", self)
            self._position.x += xClip

        elif self._state._movement["right"] == True:
            self._state.manageState("stopright", self)
            self._state.manageState("left", self)
            self._position.x -= xClip
            
            
    def kill(self):
        SoundManager.getInstance().playSound("mario_stomp.wav")
        self._state.manageState("dead", self)
        self._isDead = True

    def updateMovement(self):
        pressed = pygame.key.get_pressed()

        if not pressed[pygame.K_UP]:
            self._state.manageState("fall", self)
        if not pressed[pygame.K_LEFT]:
            self._state.manageState("stopleft", self)
        if not pressed[pygame.K_RIGHT]:
            self._state.manageState("stopright", self)


class EnemyState(object):
    def __init__(self, state="falling"):
        self._state = state

        self._movement = {
            "left": False,
            "right": False
        }

        self._lastFacing = "right"

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


    def manageState(self, action: str, enemy: Enemy):

        # if action in self._movement.keys():
        #     if self._movement[action] == False:
        #         self._movement[self._lastFacing] = False
        #         self._movement[action] = True
        #         self._lastFacing = action

        #         if self._state == "standing":
                    
        #             enemy.transitionState("walking")

        if action in self._movement.keys():
            if self._movement[action] == False:
                self._movement[action] = True
                if self._state == "standing":
                    enemy.transitionState("walking")

        elif action.startswith("stop") and action[4:] in self._movement.keys():
            direction = action[4:]
            if self._movement[direction] == True:
                self._movement[direction] = False
                allStop = True
                for move in self._movement.keys():
                    if self._movement[move] == True:
                        allStop = False
                        break

                if allStop and self._state not in ["falling"]:
                    enemy.transitionState(self._state)

        elif action == "fall" and self._state != "falling":
            self._state = "falling"
            enemy.transitionState(self._state)

        elif action == "ground" and self._state == "falling":

            self._state = "standing"
            

            if self.isMoving():
                enemy.transitionState("walking")
            else:
                enemy.transitionState(self._state)

    def getState(self):
        return self._state
