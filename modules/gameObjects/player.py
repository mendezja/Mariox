
import time
from modules.gameObjects.bullet import Bullet
from .vector2D import Vector2
from .mobile import Mobile
from .animated import Animated
from .drawable import Drawable, BasicState
from ..managers.soundManager import SoundManager
import pygame
from pygame.event import Event
from pygame.joystick import Joystick


class Player(Mobile):
    def __init__(self, imageName: str, position: Vector2, joystick: Joystick = None, hasGun=False):
        super().__init__(imageName, position)
        self._killSound = "mario_die.wav"

        self._hasGun = hasGun
        self._bullets: list[Bullet] = []
        self._lastShot = time.clock_gettime(0)
        self._bulletSpeed = 70
        self._lives = 3 if hasGun == True else 1
        self._joystick = joystick
        self._jumpTime = .06
        self._vSpeed = 50
        self._jSpeed = 80*(1.4)

        self._pressedLeft = False
        self._pressedRight = False
        self._pressedUp = False

        self._nFrames = 2
        self._framesPerSecond = 2

        if self._hasGun:
            # self._image.
            self._gun = Gun("bazooka.png",self)#Drawable("bazooka.png", position + self._gunOffset)
        else:
            self._gun = None


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

    def handleEvent(self, event: Event):
        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                self._state.manageState("jump", self)

            elif event.key == pygame.K_LEFT:
                self._state.manageState("left", self)

            elif event.key == pygame.K_RIGHT:
                self._state.manageState("right", self)

            elif event.key == pygame.K_SPACE and self._hasGun:
                if len(self._bullets) < 5:
                    self._bullets.append(
                        Bullet(self._position, self._state._lastFacing))

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
            elif event.button == 5 and event.instance_id == self._joystick.get_id() and self._hasGun:

                if time.clock_gettime(0) - self._lastShot > 1:
                    self._bullets.append(
                        Bullet(self._position, self._state._lastFacing, self._bulletSpeed))
                    self._lastShot = time.clock_gettime(0)

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
                self.updateMovement()
                return str(self._imageName)

        # Detect Gravity for each block
        hasFloor = False
        #TODO delata
        for block in blocks:

            clipRect = pRect.clip(block.getCollisionRect())

            if clipRect.width >= clipRect.height and clipRect.width > 0:  # check virtical collide
                hasFloor = self.collideGround(clipRect.height)
                break
            elif clipRect.width < clipRect.height:  # check for horizontal collide
                self.collideWall(clipRect.width)
                break
            elif (pRect.move(0, 1)).colliderect(block.getCollisionRect()):  # Check for ground
                hasFloor = True
                break

        if not hasFloor:
            self.fall()

    def getBullets(self):
        return self._bullets
        
    def kill(self, bullet: Bullet = None):
        if bullet:
            bullet.setDead()
        SoundManager.getInstance().playSound("explosion.wav")
        if self._lives > 1:
            self._lives -= 1
        else:
            super().kill()

    def getLives(self):
        return self._lives

    def setSpeed(self, speed):
        self._vSpeed = speed

    def setJump(self, speed, jtime):
        self._jSpeed = speed
        self._jumpTime = jtime



class Gun(Animated):
    _GUN_OFFSET = Vector2(0,0)#(-12,6)
    def __init__(self, imageName: str, player: Player):
        super().__init__(imageName, player.getPosition() + Gun._GUN_OFFSET)
        self._owner = player
        # center = self._image.width//2 + self._image.height//2
        self._state = BasicState(player._state.getFacing())

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
        self._position = self._owner.getPosition() + Gun._GUN_OFFSET
