import pygame
from modules.UI.screenInfo import SCREEN_SIZE, UPSCALED_SCREEN_SIZE
from modules.rl.env import GunGameEnv


from collections import deque
from modules.rl.agent_ppo import Agent
import numpy as np
import matplotlib.pyplot as plt
import torch
import pandas as pd

# must be < 0.5
SECONDS = 0.017

episodes = 500
threshold_score = 150

# Load pygame basics to keep it from getting upset
pygame.init()
pygame.display.set_caption("M@rio+")
pygame.display.set_mode(list(UPSCALED_SCREEN_SIZE), flags=pygame.HIDDEN)

# Initalize game env (unique to AI bot training)
env = GunGameEnv()


state_size = (52) # 6 features per player, 5 for each of 8 bullets
action_size = env.action_qty
number_of_agents = len(env.game.getPlayers())

print_every = 10


def main():
    print("Start Training...")
    agent = Agent(state_size, action_size, load_pretrained=False)
    scores = run_ppo(env, agent, episodes)
    print("\nTraining finished.")

    scores = np.array(scores)
    x = np.where(scores >= threshold_score)
    print('The first time a score >= {} was reached at episode {}.'.format(threshold_score, x[0][0]))
    print('Max score reached: {:.4f}'.format(np.amax(scores)))

    df = pd.DataFrame({
        'x': np.arange(len(scores)),
        'y': scores, 
        }) 
    rolling_mean = df.y.rolling(window=50).mean()

    img_path ="scores_plot.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(df.x, df.y, label='Scores')
    plt.plot(df.x, rolling_mean, label='Moving avg', color='orange')
    plt.ylabel('Scores')
    plt.xlabel('Episodes')
    plt.legend()
    fig.savefig(fname=img_path)
    print('\nPlot saved to {}.'.format(img_path))


def run_ppo(env, agent, num_episodes=100):
    scores = []
    scores_window = deque(maxlen=100)

    for i_episode in range(1, num_episodes+1):
        agent.step(env)
        max_score = agent.act(env)
        scores.append(max_score)
        scores_window.append(max_score)

        print('\r{}/{} Episode. Current score: {:.4f} Avg last 100 score: {:.4f}'.\
            format(i_episode, num_episodes, max_score, np.mean(scores_window)), end="")
        
        if i_episode % print_every == 0:
            print('\r{}/{} Episode. Current score: {:.4f} Avg last 100 score: {:.4f}'.\
                format(i_episode, num_episodes, max_score, np.mean(scores_window)))

        if np.mean(scores_window) > threshold_score:
            agent.save()
            print('\rEnvironment solved after {} episodes. Avg last 100 score: {:.4f}'.\
                format(i_episode, np.mean(scores_window)))
            break

    return scores



if __name__ == "__main__":
    main()