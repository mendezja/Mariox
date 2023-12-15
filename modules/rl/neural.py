import copy
import numpy as np
import torch
import torch.nn as nn 
from torch import distributions




class MarioNet(nn.Module):
    """DDQN"""

    def __init__(self, input_dim, output_dim):
        super().__init__()

        self.online = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
            # nn.Conv2d(in_channels=c, out_channels=32, kernel_size=8, stride=4),
            # nn.ReLU(),
            # nn.Conv2d(in_channels=32, out_channels=64, kernel_size=4, stride=2),
            # nn.ReLU(),
            # nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1),
            # nn.ReLU(),
            # nn.Flatten(),
            # nn.Linear(3136, 512),
            # nn.ReLU(),
            # nn.Linear(512, output_dim),
        )

        self.target = copy.deepcopy(self.online)

        for p in self.target.parameters():
            p.requires_grad = False

    def forward(self, input, model):
        """Forward pass"""
        if model == "online":
            return self.online(input)
        elif model == "target":
            return self.target(input)


class ActorCritic(nn.Module):
    """PPO"""
    def __init__(self, num_inputs, num_outputs, hidden_size, std=0.0):
        # super(ActorCritic, self).__init__()
        super().__init__()

        self.actor = nn.Sequential(
            self.layer_init(nn.Linear(num_inputs, hidden_size)),
            nn.Tanh(),
            self.layer_init(nn.Linear(hidden_size, num_outputs)),
        )

        self.critic = nn.Sequential(
            self.layer_init(nn.Linear(num_inputs, hidden_size)),
            nn.Tanh(),
            self.layer_init(nn.Linear(hidden_size, 1), std=1.0),
        )

        self.log_std = nn.Parameter(torch.ones(1, num_outputs) * std)

    def layer_init(self, layer, std=np.sqrt(2), bias_const=0.0):
        nn.init.orthogonal_(layer.weight, std)
        nn.init.constant_(layer.bias, bias_const)
        return layer

    def forward(self, x, action=None):
        value = self.critic(x)

        mu = self.actor(x)
        std = self.log_std.exp().expand_as(mu)  # make log_std the same shape as mu
        dist = distributions.Normal(mu, std) 

        if action == None:
            action = dist.sample() 

        log_prob = dist.log_prob(action)
        log_prob = torch.sum(log_prob, dim=1, keepdim=True)
        entropy = dist.entropy()
        entropy = torch.sum(entropy, dim=1, keepdim=True)

        return action, log_prob, entropy, value

