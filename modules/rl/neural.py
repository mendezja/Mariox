from torch import nn
import copy


class MarioNet(nn.Module):
    """DDQN"""

    def __init__(self, input_dim, output_dim):
        super().__init__()

        self.online = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(), 
            nn.Linear(64, output_dim)
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
