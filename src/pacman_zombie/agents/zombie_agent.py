"""Zombie agent using linear function approximation."""

import random
from typing import TYPE_CHECKING, List, Tuple

from numpy.typing import NDArray

from .features import ZombieFeatureExtractor, V_hat

if TYPE_CHECKING:
    from ..core.board import Board


class ZombieAgent:
    """Zombie agent that selects actions using learned weights.

    This agent uses a greedy policy to select actions that maximize estimated
    value, where value is computed using linear function approximation.

    Unlike Pac-Man, zombies operate cooperatively - each zombie on the board
    independently selects its best action given the current state.
    """

    def __init__(self, weights: NDArray):
        """Initialize Zombie agent with weights.

        Args:
            weights: 3-dimensional weight vector for feature linear combination
        """
        if len(weights) != 3:
            raise ValueError(f"Zombie requires 3 weights, got {len(weights)}")

        self.weights = weights
        self.feature_extractor = ZombieFeatureExtractor()

    def select_action(self, board: 'Board', zombie_row: int, zombie_col: int) -> str:
        """Select best action for a single zombie using greedy policy.

        Args:
            board: Current game board state
            zombie_row: Zombie's current row position
            zombie_col: Zombie's current column position

        Returns:
            Action string: one of UP, DOWN, LEFT, RIGHT

        Algorithm:
            1. Get all legal actions for this zombie's position
            2. Randomly shuffle actions (for tie-breaking)
            3. For each action:
               a. Get successor state
               b. Extract features from successor
               c. Compute V_hat(features, weights)
            4. Return action with maximum value
        """
        actions = board.get_possible_action_zombie(zombie_row, zombie_col)

        if not actions:
            # No legal actions (zombie is trapped)
            return "UP"  # Default fallback

        # Shuffle for random tie-breaking
        random.shuffle(actions)

        max_value = float('-inf')
        best_action = actions[0]

        for action in actions:
            # Get hypothetical next state
            successor_state = board.get_successor_state_zombie(action, zombie_row, zombie_col)

            # Calculate zombie's position in successor state
            move_delta = board.move_dict[action]
            successor_row = zombie_row + move_delta[0]
            successor_col = zombie_col + move_delta[1]

            # Extract features and compute value
            features = self.feature_extractor.extract(board, successor_state, successor_row, successor_col)
            value = V_hat(features, self.weights)

            # Update best action if this is better
            if value > max_value:
                max_value = value
                best_action = action

        return best_action

    def select_actions_all_zombies(self, board: 'Board') -> List[Tuple[int, int, str]]:
        """Select actions for all zombies on the board.

        Args:
            board: Current game board state

        Returns:
            List of (row, col, action) tuples, one for each zombie

        Example:
            >>> zombie_agent = ZombieAgent(weights)
            >>> actions = zombie_agent.select_actions_all_zombies(board)
            >>> board.zombies_action(actions)
        """
        zombie_positions = board.get_zombies_position()
        best_actions = []

        for zombie_pos in zombie_positions:
            row, col = zombie_pos[0], zombie_pos[1]
            best_action = self.select_action(board, row, col)
            best_actions.append((row, col, best_action))

        return best_actions

    def get_action_values(self, board: 'Board', zombie_row: int, zombie_col: int) -> dict:
        """Get value estimates for all possible actions (for analysis/debugging).

        Args:
            board: Current game board state
            zombie_row: Zombie's current row position
            zombie_col: Zombie's current column position

        Returns:
            Dictionary mapping action strings to their estimated values
        """
        actions = board.get_possible_action_zombie(zombie_row, zombie_col)
        action_values = {}

        for action in actions:
            successor_state = board.get_successor_state_zombie(action, zombie_row, zombie_col)
            move_delta = board.move_dict[action]
            successor_row = zombie_row + move_delta[0]
            successor_col = zombie_col + move_delta[1]
            features = self.feature_extractor.extract(board, successor_state, successor_row, successor_col)
            value = V_hat(features, self.weights)
            action_values[action] = value

        return action_values
