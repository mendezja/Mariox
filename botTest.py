
import pygame  
import random
from modules.managers.gameManager import GameManager
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE 
from modules.managers.gamemodes import *

def main():

    # Load pygame basics to keep it from getting upset 
    pygame.init()
    pygame.display.set_caption("M@rio+")
    pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

    gameClock = pygame.time.Clock()

    # Initalize game (unique to AI bot training)
    game = GameManager(
                SCREEN_SIZE, BATTLE_AI, "battleWorld3.txt", [], False)

    # get action set info
    action_set = list(ACTIONS.keys())
    action_qty = len(action_set)

    # While game is not won perform steps
    while not game.isWon():

        # Print state info 
        print("\n\nState: \n", game.getState())
        
        # Select Rand Actions
        actions = [action_set[random.randint(0,action_qty-1)] for _ in range(2)]

        # Step with actions and report
        game.updateBots(actions)
        print("\nAgent Actions:")
        print("Mario: ", actions[0] )
        print("Luigi: ", actions[1] )

        # Obtain Rewards
        rewards = game.update(0.6)
        print("\nRewards:")
        print("Mario: ", rewards[0] )
        print("Luigi: ", rewards[1] )

        
        # Pause for next state, option 
        q = input("\n[Enter] to step [q] to quit... ")
        if q == "q": break
    
if __name__ == "__main__":
    main()
