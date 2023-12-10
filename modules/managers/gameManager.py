from ast import Str
import os

from modules.managers.soundManager import SoundManager
from .basicManager import BasicManager
from ..gameObjects.drawable import Drawable
from ..gameObjects.backgrounds import *
from ..gameObjects.vector2D import Vector2
from ..gameObjects.player import Player
from ..gameObjects.enemy import Enemy, Turtle
from ..UI.screenInfo import SCREEN_SIZE
from .gamemodes import *
from pygame.joystick import Joystick
import pygame
from ..utils.actions import Actions
import numpy as np


class GameManager(BasicManager):
    WORLD_SIZE = None

    BLOCKS_OFFSETS = {
        "G": (2, 0),  # Ground
        "L": (0, 0),  # Leaves
        "<": (1, 0),  # End Leaves Right
        ">": (0, 1),  # End Leaves Left
        "W": (3, 0),  # Wall Brick
        "S": (2, 1),  # Stud Brick]
        "Z": (7, 0),  # Scafold beam
    }

    def __init__(
        self,
        screenSize: Vector2,
        mode: str,
        levelFile: str,
        joysticks: "list[Joystick]",
        render_screen=True,
    ):
        self._screenSize = screenSize
        self._levelFile = levelFile
        self._mode = mode
        self._joysticks = joysticks

        # Allow for running program without music/visual displays
        if render_screen:
            # Start playing music
            if self._mode in [BATTLE, BATTLE_AI]:
                SoundManager.getInstance().playBattleMusic()
            elif self._mode == SINGLE_PLAYER:
                SoundManager.getInstance().playMusic("marioOriginal.mp3")
            elif self._mode == TWO_PLAYER:
                SoundManager.getInstance().playMusic("marioRemix.mp3")

            # Set backhround Image
            backgroundImage = (
                "battleBackground.png"
                if mode in [BATTLE, BATTLE_AI]
                else "background.png"
            )
            self._background = EfficientBackground(
                self._screenSize, backgroundImage, parallax=0
            )

        # Lists to hold all elements
        self._blocks: list[Drawable] = []
        self._decor: list[Drawable] = []
        self._enemies: list[Enemy] = []
        self._players: list[Player] = []
        self._end: Drawable = None
        self._gameOver = False
        self._winner: Str = ""

        # Open map file, set world/tile sizes
        file = open(os.path.join("resources", "levels", self._levelFile))
        fileCharacters = [[y for y in x] for x in file.read().split("\n")]
        tileSize = 16

        GameManager.WORLD_SIZE = Vector2(
            len(fileCharacters[0]) * tileSize, len(fileCharacters) * tileSize
        )

        # Scan world file, fill in elements lists
        for row in range(len(fileCharacters)):
            for col in range(len(fileCharacters[row])):
                elemChar = fileCharacters[row][col]

                # Interactive block
                if elemChar in self.BLOCKS_OFFSETS.keys():
                    self._blocks.append(
                        Drawable(
                            "blocks.png",
                            Vector2(col * tileSize, row * tileSize),
                            self.BLOCKS_OFFSETS[elemChar],
                        )
                    )

                # Background Block
                elif elemChar == "B":
                    self._decor.append(
                        Drawable(
                            "blocks.png",
                            Vector2(col * tileSize, row * tileSize),
                            (1, 1),
                        )
                    )

                # Gumba
                elif elemChar == "E":
                    self._enemies.append(
                        Enemy("enemies.png", Vector2(col * tileSize, row * tileSize))
                    )

                # Turtle
                elif elemChar == "T":
                    self._enemies.append(
                        Turtle(Vector2(col * tileSize, row * tileSize))
                    )

                # Flag
                elif elemChar == "F":
                    self._end = Drawable(
                        "flagPost.png", Vector2(col * tileSize, row * tileSize)
                    )

                # Player 1
                elif elemChar == "1":
                    # Make p1 a bot ONLY when screen is not displayed
                    if not render_screen:
                        self._players.append(
                            Player(
                                "mario.png",
                                Vector2(col * tileSize, row * tileSize),
                                None,
                                hasGun=True,
                                isBot=True,
                            )
                        )
                    # Usually p1 is a human player
                    else:
                        self._players.append(
                            Player(
                                "mario.png",
                                Vector2(col * tileSize, row * tileSize),
                                self._joysticks[0]
                                if len(self._joysticks) >= 1
                                else None,
                                hasGun=(self._mode in [BATTLE, BATTLE_AI]),
                            )
                        )

                # Player 2
                elif elemChar == "2" and self._mode not in [SINGLE_PLAYER]:
                    # Make p2 a bot if AI mode enabled
                    if self._mode == BATTLE_AI:
                        self._players.append(
                            Player(
                                "luigi.png",
                                Vector2(col * tileSize, row * tileSize),
                                None,
                                hasGun=True,
                                isBot=True,
                                isGame=True
                            )
                        )

                    # Otherwise, p2 will also be human player
                    else:
                        self._players.append(
                            Player(
                                "luigi.png",
                                Vector2(col * tileSize, row * tileSize),
                                self._joysticks[1]
                                if len(self._joysticks) == 2
                                else None,
                                hasGun=(self._mode == BATTLE),
                            )
                        )

        if self._mode in [BATTLE, BATTLE_AI]:
            for player in self._players:
                player.setSpeed(100)
                player.setJump(120, 0.3)

    def draw(self, drawSurf: pygame.surface.Surface, whichPlayer=None):
        # Draw everything
        self._background.draw(drawSurf, whichPlayer)

        for decor in self._decor:
            decor.draw(drawSurf, whichPlayer)
        for block in self._blocks:
            block.draw(drawSurf, whichPlayer)

        if self._end:
            self._end.draw(drawSurf, whichPlayer)
        for enemy in self._enemies:
            enemy.draw(drawSurf, whichPlayer)

        # Draw player compenents
        for player in self._players:
            # TODO Lol why is this if a thing
            if player._imageName == "mario.png":
                player.draw(drawSurf, whichPlayer, drawCollision=False)
            else:
                player.draw(drawSurf, whichPlayer, drawCollision=False)

            # Player guns
            if player._currentGun != None:
                player._currentGun.draw(drawSurf, whichPlayer)
                player.drawStats(drawSurf)
            # Gun bullets
            for bullet in player.getBullets():
                bullet.draw(drawSurf, whichPlayer)

    # Used for bot control during Battle_AI
    def updateBot(self):
        if not self._gameOver:
            state = self.getState()
            mario_state = np.array(state[0])
            luigi_state = np.array(state[1])
            bullets_state = np.array(state[2]).flatten()
            state = np.concatenate((mario_state, luigi_state, bullets_state))
            self._players[1].updateBot(state=state)

    # Specifically for self-play Bot training
    def updateBots(self, actions):
        if not self._gameOver:
            state = self.getState()
            mario_state = np.array(state[0])
            luigi_state = np.array(state[1])
            bullets_state = np.array(state[2]).flatten()
            state = np.concatenate((mario_state, luigi_state, bullets_state))
            self._players[0].updateBot(state=state, action=actions[0])
            self._players[1].updateBot(state=state, action=actions[1])

    # Hand player moves, for human players
    def handleEvent(self, event):
        if not self._gameOver:
            for player in self._players:
                if not player._isBot:
                    player.handleEvent(event)

    def update(self, seconds):
        # Test get state method
        # print(f"Reward: {self.getState()}")

        # Record health for reward calculation
        if self._mode == BATTLE_AI:
            # Confirm identity
            for player in self._players:
                if player._imageName == "mario.png":
                    initialHealth_mario = player._lives
                else:
                    initialHealth_luigi = player._lives

        # Split screen updates
        for player in self._players:
            whichPlayer = (
                None
                if self._mode in [SINGLE_PLAYER, BATTLE, BATTLE_AI]
                else self._players.index(player)
            )
            Drawable.updateOffset(
                player, SCREEN_SIZE, GameManager.WORLD_SIZE, whichPlayer=whichPlayer
            )

        # Update enemies/detect collision with player
        for player in self._players:
            self._winner = player.updateCollisions(
                self._blocks, self._end
            )  # Dectects if won for each player

            if self._winner != None:
                self._gameOver = True
                return

        # Update enemies/detect collision with player
        for enemy in self._enemies:
            if type(enemy) == Turtle:
                enemy.updateCollisions(self._players, self._blocks, self._enemies)

            else:
                enemy.updateCollisions(self._players, self._blocks)

        for player in self._players:
            for bullet in player.getBullets():
                bullet.detectCollision(self._players)

        # let others update based on the amount of time elapsed
        if seconds < 0.5:
            for player in self._players:
                if player._hasGun:
                    for bullet in player.getBullets():
                        if bullet._isDead:
                            for gun in player._guns:
                                if bullet in gun._bullets:
                                    gun._bullets.remove(bullet)
                        bullet.update(seconds)

                if player._isDead:
                    self._gameOver = True
                    SoundManager.getInstance().stopMusic()

                    if self._mode in [TWO_PLAYER, BATTLE, BATTLE_AI]:
                        index = (
                            self._players.index(player) + 1
                        ) % 2  # Gets index of other player
                        self._winner = self._players[index]._imageName

                        # Return large positive reward for winning, large negative for losing
                        if self._winner == "mario.png":
                            return (100, -100)
                        else:
                            return (-100, 100)

                    return

                player.update(seconds, GameManager.WORLD_SIZE)

                if player._hasGun:
                    player._currentGun.update(seconds)

            for enemy in self._enemies:
                if enemy._isDead:
                    self._enemies.remove(enemy)
                    pass

                enemy.update(seconds, GameManager.WORLD_SIZE)

        # Calculate Reward based on health
        if self._mode == BATTLE_AI:
            # Confirm using idenity
            for player in self._players:
                if player._imageName == "mario.png":
                    finalHealth_mario = player._lives
                else:
                    finalHealth_luigi = player._lives

            reward_mario = (
                finalHealth_mario
                - initialHealth_mario
                + initialHealth_luigi
                - finalHealth_luigi
            )
            reward_luigi = (
                finalHealth_luigi
                - initialHealth_luigi
                + initialHealth_mario
                - finalHealth_mario
            )
            # print(f"\nReward Mario: {finalHealth_mario}, {initialHealth_mario}")
            # print(f"\nReward Luigi: {finalHealth_luigi}, {initialHealth_luigi}")

            return (reward_mario, reward_luigi)

    def updateMovement(self):
        for player in self._players:
            player.updateMovement()

    def isGameOver(self):
        return self._gameOver

    def isWon(self):
        return self._winner

    def getPlayers(self):
        return self._players

    def getState(self):
        """Gets state for RL agent, returns list of bullet states, the bot state, and the player state as a tuple"""

        bulletsState = [[0.0, 0.0, 0.0, 0.0, 0.0] for _ in range(8)]
        b_indx = 0
        for player in self._players:
            if player._hasGun:
                for bullet in player.getBullets():
                    bulletsState[b_indx] = [
                        float(bullet._velocity[0]),
                        float(bullet._velocity[1]),
                        float(bullet._position[0]),
                        float(bullet._position[1]),
                        float(bullet._timeToLive),
                    ]
                    b_indx += 1

        # Store player state info (velocity, vertical speed, )
        luigiState, marioState = None, None

        for player in self._players:
            gun_type = 0 if player._currentGun._imageName == "bazooka.png" else 1

            if player._imageName == "mario.png":
                marioState = (
                    float(player._velocity[0]),
                    float(player._velocity[1]),
                    float(player._position[0]),
                    float(player._position[1]),
                    float(player._lives),
                    float(gun_type),
                )  # player._jSpeed, player._jumpTimer,
            elif player._imageName == "luigi.png":
                luigiState = (
                    float(player._velocity[0]),
                    float(player._velocity[1]),
                    float(player._position[0]),
                    float(player._position[1]),
                    float(player._lives),
                    float(gun_type),
                )  # player._jSpeed, player._jumpTimer,

        return (marioState, luigiState, bulletsState)
