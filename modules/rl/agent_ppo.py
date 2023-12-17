from collections import deque
from modules.rl.neural import ActorCritic
from modules.managers.gamemodes import ACTIONS
import numpy as np
import torch
import random
import torch
import torch.nn as nn
import torch.optim as optim
import random

use_cuda = torch.cuda.is_available()
DEVICE = torch.device("cuda" if use_cuda else "cpu")
print(f"Use cuda: {use_cuda} -- device: {DEVICE}")

# Enviroment Constant
SEED = 42
MAX_EPISODES = 100000

# Network Constants
LR = 5e-4     
HIDDEN_SIZE = 256

# Learning Constants
USE_ENTROPY = True        
ENTROPY_WEIGHT = 0.005      
CLIP_PARAM = 0.2            # clipping parameter for PPO surrogate

# Training Constants
NUM_STEPS_PER_ENV = 1024    # num of transitions we sample for each training iter
MINIBATCH_SIZE = 128		# minibatch size 
EPOCHS = 8				    # optimize surrogate loss with K epochs  

GRADIENT_CLIPPING = 2       # gradient clipping norm


# Other Constants
GAMMA = 0.999               # discount factor for returns
TAU = 0.95					# gae (generalized advantage estimation) param
BASELINE = 0                #reward structure is too sparse

SELF_PLAY = True


class Agent_PPO(): 

    def __init__(self, state_size, action_size, load_pretrained=False):
        self.state_size = state_size
        self.action_size = action_size

        self.action_set = list(ACTIONS.keys())

        self.ac_model = ActorCritic(state_size, action_size, HIDDEN_SIZE)
        self.ac_model_optim = optim.Adam(self.ac_model.parameters(), lr=LR)
        random.seed(SEED)
        self.max = 0

        self.use_cuda = torch.cuda.is_available()

        if load_pretrained:
            # print('Loading pre-trained actor critic model from checkpoint.')
            self.ac_model.load_state_dict(torch.load("checkpoints/final_ac_model/ac_model.pth", map_location=torch.device(DEVICE)))


    def count_parameters(self):
        return sum(p.numel() for p in self.ac_model.parameters() if p.requires_grad)


    def act(self, state, both=False):
        state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(state)
        state = state.unsqueeze(0)

        with torch.no_grad(): 
            mario_actions,log_probs1, _, values1 = self.ac_model(state) 
            mario_action = torch.argmax(mario_actions, axis=1)[0].item()
            if not SELF_PLAY:
                mario_action = random.randint(0, self.action_size-1)

            luigi_actions,log_probs1, _, values1 = self.ac_model(state)
            luigi_action = torch.argmax(luigi_actions, axis=1).item()

        actions = [self.action_set[mario_action], self.action_set[luigi_action]]
        if both:
          return actions

        return actions[1]

    def act_episode(self, env):
        """ Run current action policy and check which score it is reaching.
        """  
        state = env.reset()

        count = 0
        scores = np.zeros(2)
        self.ac_model.eval()

        while True and count < MAX_EPISODES: 

            actions = self.act(state,both=True)

            next_state, rewards, dones = env.step(actions)

            scores += rewards  
            state = next_state

            count +=1

            if np.any(dones):
                break
        
        self.max = max(count, self.max)
        print("\n",self.max)
        self.ac_model.train()
        return np.max(scores)


    def step(self, env):
        """ Collect trajectories/episodes and invoke learning step.
        """ 
        state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(env.reset())
        state = state.unsqueeze(0) 

        trajectory1 = deque()    # trajectory of player 1
        trajectory2 = deque()    # trajectory of player 2

        for k in range(NUM_STEPS_PER_ENV):
            with torch.no_grad():
                # self-play: the same actor critic model is used for two players
                actions1, log_probs1, _, values1 = self.ac_model(state) 
                mario_action = torch.argmax(actions1, axis=1).item() 

                if not SELF_PLAY:
                    mario_action = random.randint(0, self.action_size-1)
                
                actions2, log_probs2, _, values2 = self.ac_model(state)
                luigi_action = torch.argmax(actions2, axis=1).item()
 

            actions = [self.action_set[mario_action], self.action_set[luigi_action]]

            next_state, rewards, done = env.step(actions)

            rewards1 = np.array(rewards[0] ).reshape([1]) 
            rewards2 = np.array(rewards[1] ).reshape([1])

            dones = np.array(done).astype(np.uint8)


            if np.any(dones):
                dones1 = np.array([1.])
                dones2 = np.array([1.])
            else:
                dones1 = np.array([0.])
                dones2 = np.array([0.])

            trajectory1.append(
                [state, values1, actions1, log_probs1, rewards1, 1 - dones1])
            trajectory2.append(
                [state, values2, actions2, log_probs2, rewards2, 1 - dones2])
            
            state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(next_state)
            state = state.unsqueeze(0)

        pending_value1 = self.ac_model(state)[-1]
        pending_value2 = self.ac_model(state)[-1]
        trajectory1.append([state, pending_value1, None, None, None, None])
        trajectory2.append([state, pending_value2, None, None, None, None])

        # self-play: the same actor critic model is used for two players
        if SELF_PLAY:
            self.learn(trajectory1, pending_value1)

        self.learn(trajectory2, pending_value2)

        trajectory1.clear()
        trajectory2.clear()


    def learn(self, trajectory, pending_value):
        """ Make PPO learning step.  
        """
        storage = deque()
        advantages = torch.Tensor(np.zeros((1, 1)))
        returns = pending_value.detach()

        for i in reversed(range(len(trajectory) - 1)):
            states, value, actions, log_probs, rewards, dones = trajectory[i]
            states = torch.Tensor(states).resize_(1, 52)
            actions = torch.Tensor(actions)
            rewards = torch.Tensor(rewards).unsqueeze(1)
            next_value = trajectory[i + 1][1]
            dones = torch.Tensor(dones).unsqueeze(1)
            returns = rewards + GAMMA * dones * returns

            # calculate generalized advantage estimation
            td_error = rewards + GAMMA * dones * next_value.detach() - value.detach()
            advantages = advantages * TAU * GAMMA * dones + td_error
            storage.append([states, actions, log_probs, returns, advantages])

        states, actions, log_probs_old, returns, advantages = map(lambda x: torch.cat(x, dim=0), zip(*storage))
        advantages = (advantages - advantages.mean()) / advantages.std()

        storage.clear() 
        dataset = torch.utils.data.TensorDataset(states, actions, log_probs_old, returns, advantages)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=MINIBATCH_SIZE, shuffle=True)
        dataiter = iter(dataloader)
       
        # update the actor critic model K_EPOCHS times
        for _ in range(EPOCHS):
            # sample states, actions, log_probs_old, returns, advantages
            sampled_states, sampled_actions, sampled_log_probs_old, sampled_returns, sampled_advantages = next(dataiter)

            _, log_probs, entropy, values = self.ac_model(sampled_states, sampled_actions)
            ratio = (log_probs - sampled_log_probs_old).exp()
            surrogate = ratio * sampled_advantages
            surrogate_clipped = torch.clamp(ratio, 1.0 - CLIP_PARAM, 1.0 + CLIP_PARAM) * sampled_advantages

            if USE_ENTROPY:
                loss_policy = - torch.min(surrogate, surrogate_clipped).mean(0) - ENTROPY_WEIGHT * entropy.mean()
            else: 
                loss_policy = - torch.min(surrogate, surrogate_clipped).mean(0)
            
            loss_value = 0.5 * (sampled_returns - values).pow(2).mean()
            loss_total = loss_policy + loss_value
            self.ac_model_optim.zero_grad()
            loss_total.backward()
            nn.utils.clip_grad_norm_(self.ac_model.parameters(), GRADIENT_CLIPPING)
            self.ac_model_optim.step()

            del loss_policy
            del loss_value
            

    def save(self):
        print("a=saving...")
        torch.save(self.ac_model.state_dict(), "ac_model.pth")



