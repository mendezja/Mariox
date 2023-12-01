
import pygame  
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE 
from modules.managers.gamemodes import *

# must be < 0.5
SECONDS = 0.017

def main():

    # Load pygame basics to keep it from getting upset 
    pygame.init()
    pygame.display.set_caption("M@rio+")
    pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

    # Initalize game (unique to AI bot training)
    game = GameManager(
                SCREEN_SIZE, BATTLE_AI, "battleWorld3.txt", [], render_screen=False)

    # get action set info
    action_set = list(ACTIONS.keys())
    action_qty = len(action_set)

    # While game is not won perform steps
    while not game.isWon():

        # Print state info
        obs = game.getState() 
        print("\n\nSTATE OBS:")
        print("Mario: ", obs[0])
        print("Luigi: ", obs[1])
        print("Bullets: ", obs[2])

        # Select Rand Actions
        actions = [action_set[random.randint(0,action_qty-1)] for _ in range(2)]

        # Step with actions and report
        game.updateBots(actions)
        print("\nPLAYER ACTIONS:")
        print("Mario: ", actions[0] )
        print("Luigi: ", actions[1] )

        # Obtain Rewards
        rewards = game.update(SECONDS)
        print("\nPLAYER REWARDS:")
        print("Mario: ", rewards[0] )
        print("Luigi: ", rewards[1] )

        
        # Pause for next state, option 
        q = input("\n[Enter] to step [q] to quit... ")
        if q == "q": break
    
if __name__ == "__main__":
    main()
