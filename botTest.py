import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

import random, datetime
from pathlib import Path

import pygame
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE
from modules.managers.gamemodes import *
from modules.env import GunGameEnv
from modules.agent import Mario
import random
from typing import Callable, Tuple

import gym
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch import distributions

# must be < 0.5
SECONDS = 0.017

episodes = 10

# Load pygame basics to keep it from getting upset
pygame.init()
pygame.display.set_caption("M@rio+")
pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

# Initalize game env (unique to AI bot training)
env = GunGameEnv()

save_dir = Path("checkpoints") / datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir.mkdir(parents=True)

checkpoint = None
mario = Mario(
    # 6 features for each player, 5 features for each of 8 bullets
    state_dim=(52),
    action_dim=env.action_qty,
    save_dir=save_dir,
    checkpoint=checkpoint,
)


def main():
    for e in range(episodes):
        state = env.reset()

        # get action set info
        action_set = env.action_set
        action_qty = env.action_qty

        gameOver = False

        # While game is not won perform steps
        while not gameOver:
            # Select Rand Actions
            actions = [action_set[random.randint(0, action_qty - 1)] for _ in range(2)]

            # Step with actions and report
            state, rewards, done = env.step(actions)

            # Prints out state, actions, and rewards when rewards are > 0 for debugging
            if rewards[0] > 0 or rewards[1] > 0:
                print("\n\nSTATE OBS:")
                print("Mario: ", state[0])
                print("Luigi: ", state[1])
                print("Bullets: ", state[2])

                print("\nPLAYER ACTIONS:")
                print("Mario: ", actions[0])
                print("Luigi: ", actions[1])

                print("\nPLAYER REWARDS:")
                print("Mario: ", rewards[0])
                print("Luigi: ", rewards[1])

                print("\nMario health: ", env.game._players[0]._lives)
                print("Luigi health: ", env.game._players[1]._lives)

                print(f"\nEpisode {e}")

            gameOver = done


if __name__ == "__main__":
    main()
