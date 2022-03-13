import os
from tkinter.font import BOLD
from .basicManager import BasicManager
from ..gameObjects.drawable import Drawable
from ..gameObjects.backgrounds import *
from ..gameObjects.vector2D import Vector2
from ..gameObjects.player import Player
from ..gameObjects.enemy import Enemy
from ..UI.screenInfo import SCREEN_SIZE
from .gamemodes import *
from pygame.joystick import Joystick

from pygame import Rect

class GameManager(BasicManager):

    WORLD_SIZE = Vector2(2624, 240)
    
    BLOCKS_OFFSETS = {"G":(2,0), # Ground
                    "L": (0,0), # Leaves
                    "<": (1,0), # End Leaves Right
                    ">": (0,1), # End Leaves Left
                    "W": (3,0), # Wall Brick
                    "S": (2,1)  # Stud Brick
                    }

    def __init__(self, screenSize: Vector2, mode: str, levelFile: str, joysticks: 'list[Joystick]'):
        self._screenSize = screenSize
        self._levelFile = levelFile
        self._mode = mode
        self._joysticks = joysticks
        self._blocks: list[Drawable] = []
        self._decor: list[Drawable] = []
        self._enemies: list [Enemy] = []
        self._players: list[Player] = []
        self._end: Drawable
        self._gameOver = False
        self._WINNER: String = None#gameWon = False
       
        self._background = EfficientBackground(
            self._screenSize, "background.png", parallax=0)

        file = open(os.path.join("resources", "levels", self._levelFile))
        fileCharacters = [[y for y in x] \
                          for x in file.read().split("\n")]
        tileSize = 16

        self._worldSize = Vector2(len(fileCharacters[0]) * tileSize,
                                    len(fileCharacters) * tileSize)

        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                elemChar = fileCharacters[row][col]
                if elemChar in self.BLOCKS_OFFSETS.keys(): #physics bound blocks
                    self._blocks.append(Drawable("blocks.png", Vector2(col*tileSize, row*tileSize), self.BLOCKS_OFFSETS[elemChar]))
                elif elemChar == "B": #non-physics blocks
                    self._decor.append(Drawable("blocks.png", Vector2(col*tileSize, row*tileSize), (1,1)))
                elif elemChar == "E": #enemies
                    self._enemies.append(Enemy("enemies.png",  Vector2(col*tileSize, row*tileSize) ))
                
                elif elemChar == "F": # Flag
                    self._end = Drawable("flagPost.png", Vector2(col*tileSize, row*tileSize))

                elif elemChar == "P": #player
                    if len(self._joysticks) >= 1 and self._mode == SINGLE_PLAYER:
                        self._players.append(Player("mario.png", Vector2(col*tileSize, row*tileSize), self._joysticks[0]))
                    elif self._mode == TWO_PLAYER:
                        self._players.append(Player("mario.png", Vector2(col*tileSize, row*tileSize), self._joysticks[0] if len(self._joysticks) == 2 else None))#,Vector2(10, GameManager.WORLD_SIZE.y - 48)
                        self._players.append(Player("luigi.png", Vector2(col*tileSize, row*tileSize), self._joysticks[1] if len(self._joysticks) == 2 else None))
                    else:
                        #print("Please insert joystick")
                        self._players.append(Player("mario.png", Vector2(col*tileSize, row*tileSize) )) # edited for testing 


    def draw(self, drawSurf: pygame.surface.Surface, whichPlayer=None):

        # Draw everything
       # nameText = Text(Vector2(10, 10),)

        self._background.draw(drawSurf, whichPlayer)

        for decor in self._decor: 
            decor.draw(drawSurf, whichPlayer)
        for block in self._blocks:
            block.draw(drawSurf, whichPlayer)

        self._end.draw(drawSurf, whichPlayer)
        for enemy in self._enemies:
            enemy.draw(drawSurf, whichPlayer)      
        for player in self._players:
            player.draw(drawSurf, whichPlayer)

    def handleEvent(self, event):
        if not self._gameOver:
            for player in self._players:
                player.handleEvent(event)

    def update(self, seconds):
        '''Return false if player dies'''
        # Update everything
        
        for player in self._players:

            whichPlayer = None if len(
                self._players) == 1 else self._players.index(player)
            Drawable.updateOffset(
                player, SCREEN_SIZE, GameManager.WORLD_SIZE, whichPlayer=whichPlayer)


        
        for player in self._players:
            if player._isDead:
                continue

            pRect = player.getCollisionRect()
            # Dectect if won for each player
            if pRect.clip(self._end.getCollisionRect()).width > 0:
                player.updateMovement()
                #self._gameWon = True
                self._WINNER = str(player._imageName)
                return
                print(player, "won")
                pass
            # Detect Gravity for each block
            hasFloor = False
            
            for block in self._blocks:
                clipRect = pRect.clip(block.getCollisionRect())

                if clipRect.width >= clipRect.height and clipRect.width > 0: # check virtical collide                     
                    hasFloor = player.collideGround(clipRect.height)
                    break
                elif clipRect.width < clipRect.height: # check for horizontal collide
                    player.collideWall(clipRect.width)
                    #break
                elif (pRect.move(0, 1)).colliderect(block.getCollisionRect()): # Check for ground
                    hasFloor = True
                    break
    
            if not hasFloor:
                player.fall()#updateMovement()

        

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            if enemy._isDead:
                continue

            eRect = enemy.getCollisionRect()

            for player in self._players:
                playerClipRect = eRect.clip(player.getCollisionRect())
                # enemyClipRect = mario.getCollisionRect().clip(enemy.getCollisionRect())

                if playerClipRect.width > 0:
                    # print (mario._state.getState(), ": ",playerClipRect.height, ": ",playerClipRect.width )
                    if player._velocity.y > 0  and playerClipRect.height <= playerClipRect.width:
                        enemy.kill()
                        #self._enemies.remove(enemy)
                        break
                    else:
                        player.kill()
                        #self._gameOver = True
                        return
            
            hasFloor = False
            
            for block in self._blocks:
                clipRect = eRect.clip(block.getCollisionRect())

                if  clipRect.width > 0:  # check virtical collide   clipRect.width > clipRect.height and
                    enemy.collideGround(clipRect.height)
                    hasFloor = True
                    break
                elif clipRect.width < clipRect.height: # check for horizontal collide
                    enemy.collideWall(clipRect.width)
                    break
                elif (eRect.move(0, 1)).colliderect(block.getCollisionRect()): # check for ground
                    hasFloor = True
                    break
    
            if not hasFloor:
                enemy.updateMovement()
                    

        # let others update based on the amount of time elapsed
        if seconds < 0.05:

            for player in self._players:
                print (player._isDead)
                if player._isDead:
                    self._gameOver = True
                    
                    return

                player.update(seconds, GameManager.WORLD_SIZE)

            for enemy in self._enemies:
                if enemy._isDead:
                    self._enemies.remove(enemy)
                    pass

                enemy.update(seconds, GameManager.WORLD_SIZE)

    def updateMovement(self):
        for player in self._players:
            player.updateMovement()

    def isGameOver(self):
        return self._gameOver

    def isWon(self):
        return self._WINNER