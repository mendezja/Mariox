import torch
import random, numpy as np
from pathlib import Path

from modules.rl.neural import MarioNet
from collections import deque
from ..managers.gamemodes import ACTIONS


class Agent:
    def __init__(self, state_dim, action_dim, save_dir, checkpoint=None, isGame = True):
        self.action_set = ACTIONS

        # Assign state and action dimensions, create memory buffer
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.memory = deque(maxlen=100000)
        self.batch_size = 32

        # Exploration settings
        self.exploration_rate = 1
        self.exploration_rate_decay = 0.99999975
        self.exploration_rate_min = 0.1
        self.gamma = 0.99

        if isGame:
            self.exploration_rate = 0
            self.exploration_rate_decay = 0
            self.exploration_rate_min = 0
       
        self.curr_step = 0
        # Min number of experiences before training
        self.burnin = 1e5  
        # Number of experiences between updates to Q online
        self.learn_every = 3 
        # Number of experiences between Q target and Q online
        self.sync_every = 1e5   

        # number of experiences between saving the network
        self.save_every = 1e5   
        self.save_dir = save_dir

        self.use_cuda = torch.cuda.is_available()

        # Mario's DNN to predict the most optimal action
        self.net = MarioNet(self.state_dim, self.action_dim).float()
        if self.use_cuda:
            self.net = self.net.to(device='cuda')
        if checkpoint:
            self.load(checkpoint)

        # Loss and optimizer
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=0.00025)
        self.loss_fn = torch.nn.SmoothL1Loss()


    def act(self, state):
        """Given a state, choose an epsilon-greedy action and update value of step."""
        # Explore
        if np.random.rand() < self.exploration_rate:
            # Choose random action
            action_idx = np.random.randint(self.action_dim)
        # Exploit
        else:
            state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(state)
            state = state.unsqueeze(0)
            # Greedy action using online DQN
            action_values = self.net(state, model='online')
            # print(action_values)
            # Get argmax of Q values
            action_idx = torch.argmax(action_values, axis=1).item()
            # if self.action_set[str(action_idx)] == "shoot":
            #     print("shot")

        # Decay exploration rate
        self.exploration_rate *= self.exploration_rate_decay
        self.exploration_rate = max(self.exploration_rate_min, self.exploration_rate)

        # Increment step
        self.curr_step += 1
        return action_idx
    

    def cache(self, state, next_state, action, reward, done):
        """Store the experience to self.memory"""
        # print(state)
        state = torch.tensor(state, dtype=torch.float32)
        next_state = torch.tensor(next_state, dtype=torch.float32)
        action = torch.tensor([int(action)], dtype=torch.int32)
        reward = torch.tensor([reward], dtype=torch.int32)
        done = torch.tensor([done], dtype=torch.bool)
        # state = torch.FloatTensor(state).cuda() if self.use_cuda else torch.FloatTensor(state)
        # next_state = torch.FloatTensor(next_state).cuda() if self.use_cuda else torch.FloatTensor(next_state)
        # action = torch.LongTensor([action]).cuda() if self.use_cuda else torch.LongTensor([action])
        # reward = torch.DoubleTensor([reward]).cuda() if self.use_cuda else torch.DoubleTensor([reward])
        # done = torch.BoolTensor([done]).cuda() if self.use_cuda else torch.BoolTensor([done])

        self.memory.append( (state, next_state, action, reward, done,) )


    def recall(self):
        """Retrieve a batch of experiences from memory"""
        batch = random.sample(self.memory, self.batch_size)
        state, next_state, action, reward, done = map(torch.stack, zip(*batch))
        return state, next_state, action.squeeze(), reward.squeeze(), done.squeeze()


    def td_estimate(self, state, action):
        """Returns the TD Estimate"""
        current_Q = self.net(state, model='online')[np.arange(0, self.batch_size), action] # Q_online(s,a)
        return current_Q


    @torch.no_grad()
    def td_target(self, reward, next_state, done):
        """Returns the TD Target"""
        next_state_Q = self.net(next_state, model='online')
        best_action = torch.argmax(next_state_Q, axis=1)
        next_Q = self.net(next_state, model='target')[np.arange(0, self.batch_size), best_action]
        return (reward + (1 - done.float()) * self.gamma * next_Q).float()


    def update_Q_online(self, td_estimate, td_target) :
        """Updates Q_online"""
        # Calculate loss
        loss = self.loss_fn(td_estimate, td_target)
        # Backpropagate loss
        self.optimizer.zero_grad()
        loss.backward()
        # Update weights
        self.optimizer.step()   
        return loss.item()


    def sync_Q_target(self):
        """Syncs Q_target and Q_online"""
        self.net.target.load_state_dict(self.net.online.state_dict())


    def learn(self):
        """Update online action value (Q) function with a batch of experiences"""
        # print("Current step: ", self.curr_step)
        # print("Burnin: ", self.burnin)
        # print("Save every: ", self.save_every)
        # If in sync step, sync target and online nets
        if self.curr_step % self.sync_every == 0:
            # print("Syncing...")
            self.sync_Q_target()

        # If in save step, save nets
        if self.curr_step % self.save_every == 0:
            self.save()

        # If still in burn-in phase, do nothing
        if self.curr_step < self.burnin:
            return None, None

        # If not in learn step, do nothing
        if self.curr_step % self.learn_every != 0:
            return None, None

        # Sample from memory
        state, next_state, action, reward, done = self.recall()

        # Get TD Estimate
        td_est = self.td_estimate(state, action)

        # Get TD Target
        td_tgt = self.td_target(reward, next_state, done)

        # Backpropagate loss through Q_online
        loss = self.update_Q_online(td_est, td_tgt)

        return (td_est.mean().item(), loss)


    def save(self):
        """Save model to save_dir"""
        save_path = self.save_dir / f"mario_net_{int(self.curr_step // self.save_every)}.chkpt"
        torch.save(
            dict(
                model=self.net.state_dict(),
                exploration_rate=self.exploration_rate
            ),
            save_path
        )
        print(f"MarioNet saved to {save_path} at step {self.curr_step}")


    def load(self, load_path):
        """Load model from load_path"""
        if not load_path.exists():
            raise ValueError(f"{load_path} does not exist")

        ckp = torch.load(load_path, map_location=('cuda' if self.use_cuda else 'cpu'))
        exploration_rate = ckp.get('exploration_rate')
        state_dict = ckp.get('model')

        print(f"Loading model at {load_path} with exploration rate {exploration_rate}")
        self.net.load_state_dict(state_dict)
        self.exploration_rate = exploration_rate
