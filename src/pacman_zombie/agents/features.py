"""Feature extraction for Pac-Man and Zombie agents.

This module contains feature extractors that convert game states into numerical
feature vectors used by learning agents. Feature engineering is critical to the
learning algorithm's performance.

IMPORTANT: The exact feature formulas are integral to trained weights.
Modifying these requires retraining all agents from scratch.
"""

from typing import TYPE_CHECKING, List

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from ..core.board import Board


class PacmanFeatureExtractor:
    """Extracts feature vectors for Pac-Man agent decision making.

    This extractor produces an 8-dimensional feature vector representing:
    1. Distance to exit (weighted by context)
    2. Shooting opportunity value
    3. Remaining vaccines available
    4. Distance to nearest vaccine
    5. Distance to nearest zombie (weighted by context)
    6. Has vaccine flag (binary)
    7. Minimum distance to obstacles
    8. Distance to pit (weighted by context)

    Feature weights (multipliers) dynamically adjust based on game state:
    - When Pac-Man has vaccine: prioritize approaching zombies to cure them
    - When no zombies remain: prioritize reaching exit
    - Otherwise: avoid zombies and seek shooting opportunities

    The feature extraction logic is currently delegated to Board.extract_features()
    for backward compatibility. Future refactoring should move the logic here.
    """

    def extract(self, board: 'Board', successor_state: List[List[str]]) -> NDArray:
        """Extract 8-dimensional feature vector from game state.

        Args:
            board: Current board state (for has_vaccine, shoot count, etc.)
            successor_state: Hypothetical next board state after taking an action

        Returns:
            numpy array of 8 float values representing:
            [0] go_to_exit * (distance_to_exit / 20)
            [1] shoot * num_zombies
            [2] remaining_vaccines
            [3] go_to_vaccine * (distance_to_vaccine / 20)
            [4] go_to_zombies * (distance_to_nearest_zombie / 20)
            [5] has_vaccine (binary)
            [6] min(distance_to_obstacles) / 20
            [7] pit * (distance_to_pit / 20)

        Note:
            Multipliers (go_to_exit, shoot, etc.) are context-dependent:
            - go_to_exit: 100 when zombies=0, else 0
            - shoot: -1000000 normally, 0 with vaccine
            - go_to_zombies: -1 with vaccine (flee), 1 otherwise (approach)
            - pit: 10 when zombies=0, 1 otherwise
        """
        return board.extract_features(successor_state)


class ZombieFeatureExtractor:
    """Extracts feature vectors for Zombie agent decision making.

    This extractor produces a 3-dimensional feature vector representing:
    1. Distance to Pac-Man (negative to encourage approach, positive to flee)
    2. Distance to pit (to avoid falling in)
    3. Minimum distance to obstacles (obstacle awareness)

    Feature weights adjust based on whether Pac-Man has vaccine:
    - Without vaccine: chase Pac-Man (negative multiplier minimizes distance)
    - With vaccine: flee from Pac-Man (positive multiplier maximizes distance)

    The feature extraction logic is currently delegated to Board.extract_features_zombie()
    for backward compatibility. Future refactoring should move the logic here.
    """

    def extract(
        self,
        board: 'Board',
        successor_state: List[List[str]],
        zombie_row: int,
        zombie_col: int
    ) -> NDArray:
        """Extract 3-dimensional feature vector from game state.

        Args:
            board: Current board state (for has_vaccine flag)
            successor_state: Hypothetical next board state after taking an action
            zombie_row: Zombie's row position in successor state
            zombie_col: Zombie's column position in successor state

        Returns:
            numpy array of 3 float values representing:
            [0] go_to_player * (distance_to_player / 20)
            [1] distance_to_pit / 20
            [2] min(distance_to_obstacles) / 40

        Note:
            go_to_player multiplier is context-dependent:
            - -10 when Pac-Man doesn't have vaccine (chase)
            - +10 when Pac-Man has vaccine (flee)
        """
        return board.extract_features_zombie(successor_state, zombie_row, zombie_col)


def V_hat(features: NDArray, weights: NDArray) -> float:
    """Compute linear value approximation.

    This is the core value function used by both agents:
    V(s) ≈ w · φ(s) = Σᵢ wᵢ * φᵢ(s)

    where:
    - w are the learned weights
    - φ(s) are the extracted features

    Args:
        features: Feature vector (numpy array)
        weights: Weight vector (numpy array, same dimension as features)

    Returns:
        Estimated value of the state (scalar)

    Example:
        >>> features = np.array([1.5, 0.0, 3.0, 2.1, 1.0, 1.0, 0.5, 0.8])
        >>> weights = np.array([-19.5, 7.2, 23.6, -2.6, 2.3, 7.0, 0.01, 0.24])
        >>> value = V_hat(features, weights)
    """
    return np.dot(weights, features)
