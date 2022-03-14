
from modules.managers.soundManager import SoundManager
from .vector2D import Vector2
from .mobile import Mobile

import pygame
from pygame.event import Event
from pygame.joystick import Joystick


class Player(Mobile):
    def __init__(self, imageName: str, position: Vector2, joystick: Joystick = None):
        super().__init__(imageName, position)
        self._joystick = joystick
        self._jumpTime = .05
        self._vSpeed = 50
        self._jSpeed = 80*(1.3)
        

        self._pressedLeft = False
        self._pressedRight = False
        self._pressedUp = False

        self._nFrames = 2
        self._framesPerSecond = 2

        self._nFramesList = {
            "walking": 2,
            "falling": 1,
            "jumping": 6,
            "standing": 1,
            "dead": 0
        }

        self._rowList = {
            "walking": 0,
            "jumping": 2,
            "falling": 2,
            "standing": 3,
            "dead": 1  # delay when switching from left/right walking, based on acceleration
        }

        self._framesPerSecondList = {
            "walking": 8,
            "standing": 1,
            "jumping": 1,
            "falling": 8,
            "dead": 1  # will likely depend on acceleration
        }

        self._state._lastFacing = "right"
        self.transitionState("falling")

    def updateVelocity(self, seconds):
        super().updateVelocity(seconds)

        if self._state.getState() == "jumping":
            self._velocity.y = -self._jSpeed
            self._velocity.x *= .5
            self._jumpTimer -= seconds
            if self._jumpTimer < 0:
                self._state.manageState("fall", self)

    def startFalling(self):
        self._state.manageState("falling", self)

   

    def handleEvent(self, event: Event):
        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                self._state.manageState("jump", self)

            elif event.key == pygame.K_LEFT:
                self._state.manageState("left", self)

            elif event.key == pygame.K_RIGHT:
                self._state.manageState("right", self)

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_UP:
                self._state.manageState("fall", self)

            elif event.key == pygame.K_LEFT:
                self._state.manageState("stopleft", self)

            elif event.key == pygame.K_RIGHT:
                self._state.manageState("stopright", self)

        # Joystick
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 2 and event.instance_id == self._joystick.get_id():
                self._pressedUp = True
                self._state.manageState("jump", self)

        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 0:
                self._pressedUp = False
                self._state.manageState("fall", self)

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0 and event.instance_id == self._joystick.get_id():
                if abs(event.value) < 0.1:
                    self._pressedLeft = False
                    self._pressedRight = False
                    self._state.manageState("stopleft", self)
                    self._state.manageState("stopright", self)
                elif event.value < 0:
                    self._pressedLeft = True
                    self._state.manageState("left", self)
                    self._state.manageState("stopright", self)
                elif event.value > 0:
                    self._pressedRight = True
                    self._state.manageState("right", self)
                    self._state.manageState("stopleft", self)

    def updateMovement(self):

        pressed = pygame.key.get_pressed()

        if not pressed[pygame.K_UP]:# and not self._pressedUp:
            self._state.manageState("fall", self)
        if not pressed[pygame.K_LEFT]:# and not self._pressedLeft:
            self._state.manageState("stopleft", self)
        if not pressed[pygame.K_RIGHT]: # and not self._pressedRight:
            self._state.manageState("stopright", self)
        

    def collideGround(self, yClip):
       # print("collide")
      
        if self._velocity.y < 0: 
            
            self._state.manageState("fall", self)
            self._velocity.y *= -1
            self._position.y += yClip

            return False

        else:
            self._state.manageState("ground", self)
            self._position.y -= yClip
            return True

    

    def collideWall(self, xClip):
        self._state.manageState("ground", self)
        if self._state._movement["left"] == True:
            self._state.manageState("stopleft", self)
            #self._state.manageState("right", self)
            self._position.x += xClip

        elif self._state._movement["right"] == True:
            self._state.manageState("stopright", self)
            #self._state.manageState("left", self)
            self._position.x -= xClip

    def kill(self):
        SoundManager.getInstance().playSound("mario_die.wav")
        super().kill()
