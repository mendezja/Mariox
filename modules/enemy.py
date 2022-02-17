from .mobile import Mobile
from .frameManager import FrameManager

import pygame
from pygame.event import Event


class Enemy(Mobile):

   _ENEMY_ROWS = { "gTurtle": 1,
                  "rTurtle": 2,
                    "gumba": 6}
   _ENEMY_SIZES = { "gTurtle": (10,10),
                  "rTurtle": (10,10),
                    "gumba": (10,10)}

   def __init__(self, enemyName, position, enemy):
      super().__init__(enemyName, position, (0,Enemy._ENEMY_ROWS[enemy]))
      
      self._jumpTime = 0.01
      self._vSpeed = 50
      self._jSpeed = 100
      print(FrameManager._FM._FRAME_SIZES[enemyName])
      FrameManager._FM._FRAME_SIZES[enemyName] = Enemy._ENEMY_SIZES[enemy]

      self._nFrames = 2
      self._framesPerSecond = 2
      self._row = Enemy._ENEMY_ROWS[enemy]
      
      
      #self._image = FrameManager.getInstance().getFrame(self._imageName, offset)
      
    #   self._enemyTypeRow = {
    #       "turtle": 1,
    #       "redTurtle": 2,
    #       "mushroom": 3
    #   }

      self._nFramesList = {
         "walking": 2,
         "falling": 1,
         "jumping": 6,
         "standing": 1,
         "dying": 1
      }

      self._columnsList = {
         "walking": 0,
         "falling": 2,
         "standing": 1,
         "dying": 1 
      }

      self._framesPerSecondList = {
         "walking": 8,
         "falling": 8,
         "standing": 1,
         "dying": 1

      }

      self._state = EnemyState()
      self.transitionState("falling")

   def updateVelocity(self, seconds):
       super().updateVelocity(seconds)

       if self._state.getState() == "standing":
            self._velocity.y = 0
       elif self._state.getState() == "falling":
            self._velocity.y += self._jSpeed * seconds
       elif self._state.getState() == "dying":
            self._velocity = Vector2(0,0)
   
       
   def collideGround(self, yClip):
      self._state.manageState("left",self)
      self._state.manageState("ground", self)
      self._position.y -= yClip
   

  
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
