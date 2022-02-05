
   
class BasicState(object):
   def __init__(self, facing="none"):
      self._facing = facing
      
   def getFacing(self):
      return self._facing

   def _setFacing(self, direction):
      self._facing = direction


      
class KirbyState(object):
   def __init__(self, state="falling"):
      self._state = state
      
      self._movement = {
         "left" : False,
         "right" : False
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

   def manageState(self, action, kirby):
      if action in self._movement.keys():
         if self._movement[action] == False:
            self._movement[action] = True
            if self._state == "standing":
               kirby.transitionState("walking")
         
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
               kirby.transitionState(self._state)
      
      elif action == "jump" and self._state == "standing":
         self._state = "jumping"
         kirby.transitionState(self._state)
         
      elif action == "fall" and self._state != "falling":
         self._state = "falling"
         kirby.transitionState(self._state)
         
      elif action == "ground" and self._state == "falling":
         
         self._state = "standing"
         
         if self.isMoving():
            kirby.transitionState("walking")
         else:
            kirby.transitionState(self._state)            

   def getState(self):
      return self._state
   
