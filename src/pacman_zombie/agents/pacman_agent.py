"""Pac-Man agent using linear function approximation."""

import random
from typing import TYPE_CHECKING

from numpy.typing import NDArray

from .features import PacmanFeatureExtractor, V_hat

if TYPE_CHECKING:
    from ..core.board import Board


class PacmanAgent:
    """Pac-Man agent that selects actions using learned weights.

    This agent uses a greedy policy: it selects the action that maximizes
    the estimated value of the resulting state, where value is computed
    using linear function approximation: V(s) = w · φ(s)

    The agent can operate in two modes:
    - With pre-trained weights: Uses learned strategy
    - Random initialization: For training new weights
    """

    def __init__(self, weights: NDArray):
        """Initialize Pac-Man agent with weights.

        Args:
            weights: 8-dimensional weight vector for feature linear combination
        """
        if len(weights) != 8:
            raise ValueError(f"Pac-Man requires 8 weights, got {len(weights)}")

        self.weights = weights
        self.feature_extractor = PacmanFeatureExtractor()

    def select_action(self, board: 'Board') -> str:
        """Select best action using greedy policy with random tie-breaking.

        Evaluates all possible actions, computes value of resulting state for each,
        and selects the action with highest value. Uses random shuffle to break ties.

        Args:
            board: Current game board state

        Returns:
            Action string: one of UP, DOWN, LEFT, RIGHT, SHOOT

        Algorithm:
            1. Get all legal actions from board
            2. Randomly shuffle actions (for tie-breaking)
            3. For each action:
               a. Get successor state
               b. Extract features from successor
               c. Compute V_hat(features, weights)
            4. Return action with maximum value
        """
        actions = board.get_possible_action()

        if not actions:
            # No legal actions (shouldn't happen in normal game)
            return "UP"  # Default fallback

        # Shuffle for random tie-breaking
        random.shuffle(actions)

        max_value = float('-inf')
        best_action = actions[0]

        for action in actions:
            # Get hypothetical next state
            successor_state = board.get_successor_state(action)

            # Extract features and compute value
            features = self.feature_extractor.extract(board, successor_state)
            value = V_hat(features, self.weights)

            # Update best action if this is better
            if value >= max_value:
                max_value = value
                best_action = action

        return best_action

    def get_action_values(self, board: 'Board') -> dict:
        """Get value estimates for all possible actions (for analysis/debugging).

        Args:
            board: Current game board state

        Returns:
            Dictionary mapping action strings to their estimated values
        """
        actions = board.get_possible_action()
        action_values = {}

        for action in actions:
            successor_state = board.get_successor_state(action)
            features = self.feature_extractor.extract(board, successor_state)
            value = V_hat(features, self.weights)
            action_values[action] = value

        return action_values
