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

    def __init__(self, screenSize: Vector2, mode: str, levelFile: str, joysticks: 'list[Joystick]'):
        self._screenSize = screenSize
        self._levelFile = levelFile
        self._mode = mode
        self._joysticks = joysticks

        
        

    def load(self):
        self._floor: list[Drawable] = []
        self._wall: list[Drawable] = []
        self._enemies: list [Enemy] = []
        self._players: list[Player] = []
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
                if fileCharacters[row][col] == "G": #ground
                    self._floor.append(Drawable("blocks.png", Vector2(col*tileSize, row*tileSize), (2,0)))
                elif fileCharacters[row][col] == "W": #ground
                    self._wall.append(Drawable("blocks.png", Vector2(col*tileSize, row*tileSize), (3,0)))
                elif fileCharacters[row][col] == "E": #enemies
                    self._enemies.append(Enemy("enemies.png",  Vector2(col*tileSize, row*tileSize) ))
                elif fileCharacters[row][col] == "P": #player
                    if len(self._joysticks) >= 1 and self._mode == SINGLE_PLAYER:
                        self._players.append(Player("mario.png", Vector2(col*tileSize, row*tileSize), self._joysticks[0]))
                    elif self._mode == TWO_PLAYER:
                        #self._players.append(Player("mario.png", Vector2(10, GameManager.WORLD_SIZE.y - 48)))
                        #self._players.append(Player("luigi.png", Vector2(10, GameManager.WORLD_SIZE.y - 48)))
                        print("player 2 ")
                        self._players = [(Player("mario.png", Vector2(10, GameManager.WORLD_SIZE.y -48), (self._joysticks[x] if len(self._joysticks) == 2 else None))) for x in range(2)]
                    else:
                        #print("Please insert joystick")
                        self._players.append(Player("mario.png", Vector2(col*tileSize, row*tileSize) )) # edited for testing

            

    


    def draw(self, drawSurf: pygame.surface.Surface, whichPlayer=None):

        # Draw everything
        self._background.draw(drawSurf, whichPlayer)

        for floor in self._floor:
            floor.draw(drawSurf, whichPlayer)
        for player in self._players:
            player.draw(drawSurf, whichPlayer)
        for enemy in self._enemies:
            enemy.draw(drawSurf, whichPlayer)
        for wall in self._wall: 
            wall.draw(drawSurf, whichPlayer)

    def handleEvent(self, event):
        for player in self._players:
            player.handleEvent(event)

    def update(self, seconds) -> bool:
        # Update everything
        for player in self._players:
            whichPlayer = None if len(
                self._players) == 1 else self._players.index(player)
            Drawable.updateOffset(
                player, SCREEN_SIZE, GameManager.WORLD_SIZE, whichPlayer=whichPlayer)


        for player in self._players:
            pRect = player.getCollisionRect()
            hasFloor = False
            
            for floor in self._floor:
                clipRect = pRect.clip(floor.getCollisionRect())

                if clipRect.width > 0 :
                    player.collideGround(clipRect.height)
                    hasFloor = True
                    break
                elif (pRect.move(0, 1)).colliderect(floor.getCollisionRect()):
                    hasFloor = True
                    break
                

            for wall in self._wall:
                clipRect = pRect.clip(wall.getCollisionRect())

                if clipRect.height > 0 and clipRect.width >= clipRect.height:
                    player.collideGround(clipRect.height)
                    hasFloor = True
                    break
                elif (pRect.move(0, 1)).colliderect(wall.getCollisionRect()):
                    hasFloor = True
                    break
                    
        
            if not hasFloor:
                player.updateMovement()

        # Detect the brick collision
        for floor in self._wall:
            for player in self._players:
                clipRect = player.getCollisionRect().clip(floor.getCollisionRect())
                clipRect2 = (player.getCollisionRect().move(0,-1)).clip(floor.getCollisionRect())

                if clipRect.height > 0 and clipRect.width >= clipRect.height:
                    player.collideGround(clipRect.height)
                    break
                elif clipRect.width > 0 and clipRect.width <= clipRect.height:
                    player.collideWall(clipRect.width)
                    break
        
                
        

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            for player in self._players:
                playerClipRect = enemy.getCollisionRect().clip(player.getCollisionRect())
                # enemyClipRect = mario.getCollisionRect().clip(enemy.getCollisionRect())

                if playerClipRect.width > 0:
                    # print (mario._state.getState(), ": ",playerClipRect.height, ": ",playerClipRect.width )
                    # TODO fix bug where if both players jump on the same enemy at the same time it crashes
                    if player._state.getState() == "falling" and playerClipRect.height <= playerClipRect.width:
                        self._enemies.remove(enemy)
                        pass
                    else:
                        player.kill()
                        return False

            for floor in self._floor:
                clipRect = enemy.getCollisionRect().clip(floor.getCollisionRect())

                if clipRect.width > 0:
                    enemy.collideGround(clipRect.height)
                    break
                
            for floor in self._wall:
                clipRect = enemy.getCollisionRect().clip(floor.getCollisionRect())

                if clipRect.height > 0 and clipRect.width >= clipRect.height:
                    enemy.collideGround(clipRect.height)
                    break
                elif clipRect.width > 0 and clipRect.width <= clipRect.height:
                    enemy.collideWall(clipRect.width)
                    break

        # let others update based on the amount of time elapsed
        if seconds < 0.05:

            for player in self._players:
                player.update(seconds, GameManager.WORLD_SIZE)

            for enemy in self._enemies:
                enemy.update(seconds, GameManager.WORLD_SIZE)

        return True

    def updateMovement(self):
        for player in self._players:
            player.updateMovement()

