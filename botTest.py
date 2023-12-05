
import pygame  
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE 
from modules.managers.gamemodes import *
from modules.env import GunGameEnv
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

def main():

    # Load pygame basics to keep it from getting upset 
    pygame.init()
    pygame.display.set_caption("M@rio+")
    pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

    # Initalize game env (unique to AI bot training)
    env = GunGameEnv()

    # get action set info
    action_set = env.action_set
    action_qty = env.action_qty

    # While game is not won perform steps
    while not env.done:

        # Select Rand Actions
        actions = [action_set[random.randint(0,action_qty-1)] for _ in range(2)]

        # Step with actions and report
        state, rewards, done = env.step(actions)
        
    
if __name__ == "__main__":
    main()
