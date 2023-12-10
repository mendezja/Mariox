import pygame
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE
from modules.managers.gamemodes import *
import numpy as np

# must be < 0.5
SECONDS = 0.017


class GunGameEnv:
    def __init__(self) -> None:
        self.game = GameManager(
            SCREEN_SIZE, BATTLE_AI, "battleWorld3.txt", [], render_screen=False
        )
        self.action_set = list(ACTIONS.keys())
        self.action_qty = len(self.action_set)
        self.state = self.game.getState()
        self.done = False

    def step(self, actions):
        self.game.updateBots(actions)

        rewards = self.game.update(SECONDS)

        self.state = self.game.getState()

        # print("Mario: ", mario_state)
        # print("Luigi: ", luigi_state)
        # print("Bullets: ", bullets_state)

        done = False
        if self.game.isWon():
            done = True

        return self.state, rewards, done

    def reset(self):
        self.game = GameManager(
            SCREEN_SIZE, BATTLE_AI, "battleWorld3.txt", [], render_screen=False
        )
        self.state = self.game.getState()

        self.done = False
        return self.state
