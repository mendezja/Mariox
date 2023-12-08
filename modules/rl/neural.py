from torch import nn
import copy


class MarioNet(nn.Module):
    """DDQN"""

    def __init__(self, input_dim, output_dim):
        super().__init__()

        self.online = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
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
