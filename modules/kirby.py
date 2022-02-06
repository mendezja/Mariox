from .mobile import Mobile

import pygame

class Kirby(Mobile):
   def __init__(self, position):
      super().__init__("kirby.png", position)
      
      self._jumpTime = 0.5
      self._vSpeed = 50
      self._jSpeed = 100
      
      self._nFrames = 2
      self._framesPerSecond = 2
      
      self._nFramesList = {
         "walking" : 4,
         "falling" : 4,
         "jumping" : 1,
         "standing" : 2
      }
      
      self._rowList = {
         "walking" : 1,
         "jumping" : 2,
         "falling" : 4,
         "standing" : 0
      }
      
      self._framesPerSecondList = {
         "walking" : 8,
         "standing" : 2,
         "jumping" : 1,
         "falling" : 8
      }
      
      self._state = KirbyState()      
      
      self.transitionState("falling")
   
   def handleEvent(self, event: pygame.event.Event):
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
   
   def collideGround(self, yClip):
      self._state.manageState("ground", self)
      self._position.y -= yClip
   
  
   
      
   