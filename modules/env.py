import pygame
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE
from modules.managers.gamemodes import *


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
        print("\nPLAYER ACTIONS:")
        print("Mario: ", actions[0])
        print("Luigi: ", actions[1])
        self.game.updateBots(actions)

        rewards = self.game.update(SECONDS)
        print("\nPLAYER REWARDS:")
        print("Mario: ", rewards[0])
        print("Luigi: ", rewards[1])

        self.state = self.game.getState()
        print("\n\nSTATE OBS:")
        print("Mario: ", self.state[0])
        print("Luigi: ", self.state[1])
        print("Bullets: ", self.state[2])
        done = self.game.isWon()
        return self.state, rewards, done

    def reset(self):
        self.game = GameManager(
            SCREEN_SIZE, BATTLE_AI, "battleWorld3.txt", [], render_screen=False
        )
        self.state = self.game.getState()
        self.done = False
        return self.state
