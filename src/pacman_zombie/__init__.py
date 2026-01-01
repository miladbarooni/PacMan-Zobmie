"""Pac-Man vs Zombies: Adversarial Learning Game.

A Pac-Man variant demonstrating adversarial reinforcement learning through
linear function approximation. Both Pac-Man and Zombies learn optimal
strategies by playing against each other.
"""

__version__ = '2.0.0'
__author__ = 'Pac-Man vs Zombies Contributors'
__license__ = 'MIT'

# Core imports
from .core.board import Board
from .agents.pacman_agent import PacmanAgent
from .agents.zombie_agent import ZombieAgent
from .agents.features import V_hat
from .learning.weights import WeightManager, WeightMetadata

__all__ = [
    '__version__',
    'Board',
    'PacmanAgent',
    'ZombieAgent',
    'V_hat',
    'WeightManager',
    'WeightMetadata',
]
