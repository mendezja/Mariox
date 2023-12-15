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
from modules.rl.agent import Agent
from modules.rl.metrics import MetricLogger
import random
from typing import Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch import distributions

# must be < 0.5
SECONDS = 0.017

episodes = 1000

# Load pygame basics to keep it from getting upset
pygame.init()
pygame.display.set_caption("M@rio+")
pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

# Initalize game env (unique to AI bot training)
env = GunGameEnv()

save_dir_mario = Path("checkpoints/mario") / datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir_mario.mkdir(parents=True)
save_dir_luigi = Path("checkpoints/luigi") / datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
save_dir_luigi.mkdir(parents=True)

logger_mario = MetricLogger(save_dir_mario)
logger_luigi = MetricLogger(save_dir_luigi)

# Load checkpoint if available, change path to most recent
MOST_RECENT_CHECKPOINT_MARIO = ""
MOST_RECENT_CHECKPOINT_LUIGI = ""
# MOST_RECENT_CHECKPOINT = "NONE"
checkpoint_mario = (
    Path(MOST_RECENT_CHECKPOINT_MARIO)
    if os.path.exists(MOST_RECENT_CHECKPOINT_MARIO)
    else None
)
checkpoint_luigi = (
    Path(MOST_RECENT_CHECKPOINT_MARIO)
    if os.path.exists(MOST_RECENT_CHECKPOINT_MARIO)
    else None
)

mario = Agent(
    # 6 features for each player, 5 features for each of 8 bullets
    state_dim=(52),
    action_dim=env.action_qty,
    save_dir=save_dir_mario,
    checkpoint=checkpoint_mario,
    isGame = False
)

luigi = Agent(
    # 6 features for each player, 5 features for each of 8 bullets
    state_dim=(52),
    action_dim=env.action_qty,
    save_dir=save_dir_luigi,
    checkpoint=checkpoint_luigi,
    isGame = False
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
            # mario_action = action_set[mario.act(state)]
            luigi_action = action_set[luigi.act(state)]
            mario_action = action_set[random.randint(0, action_qty - 1)]
            actions = [mario_action, luigi_action]

            # Step with actions for both players and report
            next_state, rewards, done = env.step(actions)
            
            # mario_reward = rewards[0]
            luigi_reward = rewards[1]

            # Remember
            # mario.cache(state, next_state, mario_action, mario_reward, done)
            luigi.cache(state, next_state, luigi_action, luigi_reward, done)

            # Learn
            # q_mario, loss_mario = mario.learn()
            q_luigi, loss_luigi = luigi.learn()

            # Log
            # logger_mario.log_step(mario_reward, q_mario, loss_mario)
            logger_luigi.log_step(luigi_reward, q_luigi, loss_luigi)
            
            # Update next state
            state = next_state


            gameOver = done
        
        # logger_mario.log_episode()
        logger_luigi.log_episode()

        if e % 10 == 0:
            # logger_mario.record(episode=e, epsilon=mario.exploration_rate, step=mario.curr_step)
            logger_luigi.record(episode=e, epsilon=luigi.exploration_rate, step=luigi.curr_step)



if __name__ == "__main__":
    main()
