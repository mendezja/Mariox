import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

import random, datetime
from pathlib import Path

import pygame
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE
from modules.managers.gamemodes import *
from modules.rl.env import GunGameEnv
from modules.rl.agent import Mario
from modules.rl.metrics import MetricLogger
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

episodes = 100

# Load pygame basics to keep it from getting upset
pygame.init()
pygame.display.set_caption("M@rio+")
pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

# Initalize game env (unique to AI bot training)
env = GunGameEnv()

save_dir = Path("checkpoints/mario") / datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir.mkdir(parents=True)

logger = MetricLogger(save_dir)

# Load checkpoint if available, change path to most recent
MOST_RECENT_CHECKPOINT = "checkpoints/mario/2023-12-09T10-55-06/mario_net_40.chkpt"
checkpoint = (
    Path(MOST_RECENT_CHECKPOINT)
    if os.path.exists(MOST_RECENT_CHECKPOINT)
    else None
)

print(checkpoint)

mario = Mario(
    # 6 features for each player, 5 features for each of 8 bullets
    state_dim=(52),
    action_dim=env.action_qty,
    save_dir=save_dir,
    checkpoint=checkpoint,
)

def main():
    for e in range(1, episodes + 1):
        print(f"Episode {e}")
        state = env.reset()

        # get action set info
        action_set = env.action_set
        action_qty = env.action_qty

        gameOver = False

        # While game is not won perform steps
        while not gameOver:

            # Select Rand Actions
            # actions = [action_set[random.randint(0, action_qty - 1)] for _ in range(2)]

            # Run agent on the state
            mario_action = action_set[mario.act(state)]
            luigi_action = action_set[random.randint(0, action_qty - 1)]
            actions = [mario_action, luigi_action]

            # Step with actions for both players and report
            next_state, rewards, done = env.step(actions)
            mario_reward = rewards[0]

            # Remember
            mario.cache(state, next_state, mario_action, mario_reward, done)

            # Learn
            q, loss = mario.learn()

            # Log
            logger.log_step(mario_reward, loss, q)
            
            # Update next state
            state = next_state


            gameOver = done
        
        logger.log_episode()

        if e % 10 == 0:
            logger.record(episode=e, epsilon=mario.exploration_rate, step=mario.curr_step)



if __name__ == "__main__":
    main()
