from collections import deque
from modules.rl.neural import ActorCritic
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
# NUM_ENVS = 16                  

# Network Constants
LR = 5e-4     
HIDDEN_SIZE = 256

# Learning Constants
USE_ENTROPY = True        
ENTROPY_WEIGHT = 0.001      
CLIP_PARAM = 0.2            # clipping parameter for PPO surrogate
# TARGET_KL = 0.015

# Training Constants
NUM_STEPS_PER_ENV = 1024    # num of transitions we sample for each training iter
MINIBATCH_SIZE = 128			# minibatch size 
EPOCHS = 8				    # optimize surrogate loss with K epochs  

GRADIENT_CLIPPING = 2       # gradient clipping norm


# Other Constants
GAMMA = 0.999               # discount factor for returns
TAU = 0.95					# gae (generalized advantage estimation) param

BASELINE = 0 #130


class Agent(): 

    def __init__(self, state_size, action_size, load_pretrained=False):
        self.state_size = state_size
        self.action_size = action_size

        self.ac_model = ActorCritic(state_size, action_size, HIDDEN_SIZE)
        self.ac_model_optim = optim.Adam(self.ac_model.parameters(), lr=LR)
        random.seed(SEED)

        self.use_cuda = torch.cuda.is_available()
        
        print('Number of trainable actor critic model parameters: ', \
        	self.count_parameters())

        if load_pretrained:
            print('Loading pre-trained actor critic model from checkpoint.')
            self.ac_model.load_state_dict(torch.load("checkpoints/ac_model.pth", map_location=torch.device(DEVICE)))


    def count_parameters(self):
        return sum(p.numel() for p in self.ac_model.parameters() if p.requires_grad)


    def act(self, env):
        """ Run current action policy and check which score it is reaching.
        """
        # env_info = env.reset(train_mode=True)
        # states = env_info.vector_observations
        # states1 = states[0]
        # states2 = states[1]
        
        state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(env.reset())
        state = state.unsqueeze(0)
        action_set = env.action_set

        scores = np.zeros(2)
        self.ac_model.eval()

        while True:
            with torch.no_grad():
                # self-play: the same actor critic model is used for two players
                
                mario_actions, _, _, _ = self.ac_model(state) 
                mario_action = torch.argmax(mario_actions, axis=1)[0].item()
                luigi_actions, _, _, _ = self.ac_model(state)
                luigi_action = torch.argmax(luigi_actions, axis=1).item()

            actions = [action_set[mario_action], action_set[luigi_action]]


            # env_info =env.step(actions)
            # next_states = env_info.vector_observations
            # dones = env_info.local_done
            # scores += env_info.rewards
            # states = next_states
            # states1 = states[0]
            # states2 = states[1]

            next_state, rewards, dones = env.step(actions)

            scores += rewards 
            state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(next_state)
            state = state.unsqueeze(0)

            if np.any(dones):
                break
        self.ac_model.train()
        return np.max(scores)


    def step(self, env):
        """ Collect trajectories/episodes and invoke learning step.
        Params
        ======
            env:            unity Tennis environment 
        """
        # env_info = env.reset()
        # states = env_info.vector_observations
        # states1 = states[0]
        # states2 = states[1]
        state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(env.reset())
        state = state.unsqueeze(0)
        action_set = env.action_set

        trajectory1 = deque()    # trajectory of player 1
        trajectory2 = deque()    # trajectory of player 2

        for k in range(NUM_STEPS_PER_ENV):
            with torch.no_grad():
                # self-play: the same actor critic model is used for two players
                actions1, log_probs1, _, values1 = self.ac_model(state) 
                mario_action = torch.argmax(actions1, axis=1).item()
                actions2, log_probs2, _, values2 = self.ac_model(state)
                luigi_action = torch.argmax(actions2, axis=1).item()
 
            # actions = torch.cat((actions1, actions2), dim=0)
            # env_info = env.step([actions.cpu().numpy()])

            # next_state = env_info.vector_observations[0]
            # next_state = env_info.vector_observations[1]

            # rewards = env_info.rewards
            # rewards1 = np.array(rewards[0]).reshape([1])
            # rewards2 = np.array(rewards[1]).reshape([1])

            actions = [action_set[mario_action], action_set[luigi_action]]

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
        self.learn(trajectory1, pending_value1)
        self.learn(trajectory2, pending_value2)

        trajectory1.clear()
        trajectory2.clear()


    def learn(self, trajectory, pending_value):
        """ Make PPO learning step. 
        Params
        ======
            trajectory:     trajectory/episode
            pending_value:  pendig critic value from last state
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
        # print(states.shape, actions.shape, log_probs_old.shape, returns.shape, advantages.shape)
        dataset = torch.utils.data.TensorDataset(states, actions, log_probs_old, returns, advantages)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=MINIBATCH_SIZE, shuffle=True)
        dataiter = iter(dataloader)
       
        # update the actor critic modelK_EPOCHS times
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
        torch.save(self.ac_model.state_dict(), "checkpoints/ac_model.pth")



