
import time
import os
from modules.gameObjects.bullet import Bullet
from .vector2D import Vector2
from .mobile import Mobile
from .animated import Animated
from .drawable import Drawable, BasicState
from ..managers.soundManager import SoundManager
from ..managers.gamemodes import ACTIONS
import pygame
from pygame.event import Event
from pygame.joystick import Joystick
from .items import BasicItemManager, RectBarItem
from typing import List

UPDATE_SCRIPT = False


class Player(Mobile):
    def __init__(self, imageName: str, position: Vector2, joystick: Joystick = None, hasGun=False, isBot=False):
        super().__init__(imageName, position)
        self._killSound = "mario_die.wav"

        self._isBot = isBot

        self._hasGun = hasGun
        self._lives = 100 if hasGun == True else 1
        self._joystick = joystick
        self._jumpTime = .05
        self._vSpeed = 50
        self._jSpeed = 80*(1.4)

        self._pressedLeft = False
        self._pressedRight = False
        self._pressedUp = False

        self._nFrames = 2
        self._framesPerSecond = 2

        if self._hasGun: 
            self._guns = [Gun("bazooka.png",self), Gun("ak47.png", self)]
            self._gunNum = 1
            self._currentGun = self._guns[0]
        else:
            self._currentGun = None

        if self._isBot and not UPDATE_SCRIPT:
            f = open(os.path.join("resources", "bot_script", 'moves.txt'),"r" ) 
            self.moves = [line.rstrip('\n') for line in f]
            self.step = 0
            # print(self.moves)

        if not self._isBot and UPDATE_SCRIPT: open(os.path.join("resources", "bot_script", 'moves.txt'), "w").close()
          

        self._stats = BasicItemManager()
        self._stats.addItem("health",
                          RectBarItem(pygame.Rect(0,0,50,10),
                                      initialValue=100,
                                      maxValue=100,
                                      backgroundColor=(0,0,0), position = (10,18) if imageName == "mario.png" else (180,18)))


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
            "dead": 1  
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

    def updateBot(self, action=None): 

        # If bot is CPU, select next move in script
        if not action and self._isBot and not UPDATE_SCRIPT: 
            # Select next action in moves script
            try:
                action = self.moves[self.step]
            except: 
                action = None

            self.step += 1
     
        # Map action str to int
        # Confirm it is valid action - set to None otherwise
        if action in list(ACTIONS.keys()):
                action = int(action) 
        else:
                action = None 

        
        # Act according to action
        if action == 0:
            self._state.manageState("jump", self)
        
        elif action == 1:
            self._state.manageState("left", self)
           
        elif action == 2:
            self._state.manageState("right", self)

        elif self._hasGun:
            if action == 3:
                self._currentGun.addBullets(self._position) 
            elif action == 4:           
                self._currentGun = self._guns[1]
            elif action == 5:
                self._currentGun = self._guns[0]
        
        elif action == 6:
            self._pressedUp = False
            self._state.manageState("fall", self)

        elif action == 7:
            self._pressedRight = False
            self._state.manageState("stopright", self)

        elif action == 8:
            self._pressedLeft = False
            self._state.manageState("stopleft", self)

        elif action == None:
            pass

        else: 
            raise Exception("Invalid Action: " + str(action))
        
        # Match Player speed using None, if updating script
        if UPDATE_SCRIPT and self._isBot:
            file1 = open(os.path.join("resources", "bot_script", 'moves.txt'), 'a')
            file1.write(str (None)+ '\n')
            file1.close()


    def handleEvent(self, event: Event):

        # check control inputs: keyboard and Joystick

        eventAction = None
        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                self._pressedUp = True
                self._state.manageState("jump", self) 
                eventAction = 0

            elif event.key == pygame.K_LEFT:
                self._state.manageState("left", self)
                eventAction= 1

            elif event.key == pygame.K_RIGHT:
                self._state.manageState("right", self)
                eventAction = 2

            elif event.key == pygame.K_SPACE and self._hasGun:
                self._currentGun.addBullets(self._position)
                eventAction = 3
                
            elif event.key == pygame.K_2 and self._hasGun:
                self._currentGun = self._guns[1]
                eventAction = 4
            elif event.key == pygame.K_1 and self._hasGun:
                self._currentGun = self._guns[0]
                eventAction = 5

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_UP:
                self._state.manageState("fall", self)
                eventAction = 6

            elif event.key == pygame.K_LEFT:
                self._state.manageState("stopleft", self)
                eventAction= 7

            elif event.key == pygame.K_RIGHT:
                self._state.manageState("stopright", self)
                eventAction = 8
        # print eventAction)
        if UPDATE_SCRIPT and not self._isBot:
            file1 = open(os.path.join("resources", "bot_script", 'moves.txt'), 'a')
            file1.write(str (eventAction)+ '\n')
            file1.close()

        # Joystick
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 2 and event.instance_id == self._joystick.get_id():
                self._pressedUp = True
                self._state.manageState("jump", self)

            elif event.button == 5 and event.instance_id == self._joystick.get_id() and self._hasGun:
                self._currentGun.addBullets(self._position)
            elif event.button == 4 and event.instance_id == self._joystick.get_id() and self._hasGun:
                self._gunNum +=1
                self._currentGun = self._guns[self._gunNum %2]

            

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

        if self._isBot:
            pass
        else:
            pressed = pygame.key.get_pressed() 

            if not pressed[pygame.K_UP]:  # and not self._pressedUp:
                self._state.manageState("fall", self)
            if not pressed[pygame.K_LEFT]:  # and not self._pressedLeft:
                self._state.manageState("stopleft", self)
            if not pressed[pygame.K_RIGHT]:  # and not self._pressedRight:
                self._state.manageState("stopright", self)

    
    
    def updateCollisions(self, blocks: 'list[Drawable]', end: Drawable):
        if self._isDead:
            return
        pRect = self.getCollisionRect()

        # Dectect if won for each player
        if end != None:
           
            if pRect.clip(end.getCollisionRect()).width > 0:
                self.collideWall(0)
                return str(self._imageName)

        # Detect Gravity for each block
        hasFloor = False

        for block in blocks:
            clipRect = pRect.clip(block.getCollisionRect())

            if clipRect.width >= clipRect.height and clipRect.width > 2:  # check virtical collide
                if clipRect.height > block.getSize()[1]//3:
                    hasFloor = self.collideGround(clipRect.height*2)
                else:
                    hasFloor = self.collideGround(clipRect.height)
                break

            elif clipRect.width < clipRect.height and clipRect.width > 1:  # check for horizontal collide
                if clipRect.width < block.getSize()[0]//3:
                    self.collideWall(clipRect.width+2)
                else:
                    self.collideWall(clipRect.width)
                break

            elif (pRect.move(0, 1)).colliderect(block.getCollisionRect()):  # Check for ground
                hasFloor = True
                break

        if not hasFloor:
            self.fall()
        else:
            self.collideGround(0)

    def getBullets(self):
        totalBullets: List[Bullet] = []
        if self._hasGun:
            for gun in self._guns:
                totalBullets += gun.getBullets()
        return totalBullets
        
    def kill(self, bullet: Bullet = None):
        if bullet:
            bullet.setDead()
            #TODO add explosion
            SoundManager.getInstance().playSound("explosion.wav")
        if self._lives > 5:
            if  bullet._type == "AK":
                self._stats.decreaseItem("health", 5)
                self._lives -= 5
            elif bullet._type == "BILL":
                self._stats.decreaseItem("health", 20)
                self._lives -= 20

            if self._lives < 1:
                super().kill()
        
        else:
            super().kill()
            
    def getLives(self):
        return self._lives

    def setSpeed(self, speed):
        self._vSpeed = speed

    def setJump(self, speed, jtime):
        self._jSpeed = speed
        self._jumpTime = jtime
    def drawStats(self, drawSurf):
      self._stats.draw(drawSurf)



class Gun(Animated):
    _GUN_OFFSET = Vector2(-12,-10)
    _bullet_names = {"ak47.png": "akBullet.png",
                    "bazooka.png": "bulletbill.png"
                    }
    _bullet_speeds = {"ak47.png": 140,
                    "bazooka.png": 70
                    }
    

    def __init__(self, imageName: str, player: Player):
        super().__init__(imageName, player.getPosition() + Gun._GUN_OFFSET)
        self._owner = player
        
        self._state = BasicState(player._state.getFacing())
        self._center = Vector2(self.getSize()[0]//2 , self.getSize()[1]//2)
        self._offset = Gun._GUN_OFFSET + self._center 
        self.updateOffset()

        self._bullets: list[Bullet] = []
        self._lastShot = time.clock_gettime(0)
        self._bulletSpeed = Gun._bullet_speeds[imageName]
        self._bulletName = Gun._bullet_names[imageName]
        

        self._row = 0
        self._nFrames = 1
        self._framesPerSecond = 1


        self._nFramesList = {
            "shooting": 1,
            "flipping": 1
        }

        self._rowList = {
            "shooting": 1,
            "flipping": 1
        }

        self._framesPerSecondList = {
            "shooting": 1,
            "flipping": 1
        }

    def update(self, seconds):
        super().update(seconds)
        self.updatePosition(seconds)

    def updatePosition(self, seconds):
        '''Helper method for update'''
        self._state._setFacing(self._owner._state.getFacing())
        self.updateOffset()
        self._position =  self._owner._position + self._offset

    def updateOffset(self):
        if self._owner._state.getFacing() == "left":
            self._offset.x = Gun._GUN_OFFSET.x - (self._center.x //2)
        if self._owner._state.getFacing() == "right":
            self._offset.x = Gun._GUN_OFFSET.x + (self._center.x )
    
    def getBullets(self):
        return self._bullets

    def addBullets(self, position):
        newPosition = position + Vector2(self._owner.getSize()[0], self._owner.getSize()[1]//2)
        if self._imageName == "ak47.png":
            self.addAkBullets(newPosition)
        elif self._imageName == "bazooka.png":
            self.addBazooBullet(newPosition)

    def addAkBullets(self,position):
        if len(self._bullets) < 3:
            self._bullets.append(
                        Bullet(self._bulletName, position, self._state.getFacing(), self._bulletSpeed))

    def addBazooBullet(self,position):
        if len (self._bullets) < 1: 
            if time.clock_gettime(0) - self._lastShot > 1:
                        self._bullets.append(
                            Bullet(self._bulletName, position, self._state.getFacing(), self._bulletSpeed))
                        self._lastShot = time.clock_gettime(0)