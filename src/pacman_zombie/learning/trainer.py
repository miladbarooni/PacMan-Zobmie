"""Training module for Pac-Man and Zombie agents using temporal difference learning.

This module implements the exact training algorithms from the original agent.py and zombie.py
files, preserving the sacred weight update formulas:

PAC-MAN:  w = w + α * (V_train - V_hat) * features  (COOPERATIVE)
ZOMBIE:   w = w - α * (V_train - V_hat) * features  (ADVERSARIAL)

CRITICAL: The difference is the operator (+ vs -). Do NOT modify these formulas.
"""

import copy
import random
from typing import TYPE_CHECKING, Optional, Tuple, List

import numpy as np
from numpy.typing import NDArray

from ..agents.features import V_hat

if TYPE_CHECKING:
    from ..core.board import Board


class PacmanTrainer:
    """Trainer for Pac-Man agent using temporal difference learning.

    Uses cooperative learning: agent improves by maximizing its own value function.

    Weight Update Formula (SACRED - DO NOT MODIFY):
        w_new = w_old + α * (V_train - V_hat(features, w_old)) * features
    """

    def __init__(self, initial_weights: Optional[NDArray] = None):
        """Initialize Pac-Man trainer.

        Args:
            initial_weights: Starting weights (8-dimensional). If None, random init.
        """
        if initial_weights is None:
            # Random initialization between -0.5 and 0.5
            self.w_hat_player = np.random.rand(8) - 0.5
        else:
            if len(initial_weights) != 8:
                raise ValueError(f"Pac-Man requires 8 weights, got {len(initial_weights)}")
            self.w_hat_player = np.array(initial_weights, dtype=float)

        # Training statistics
        self.num_win = 0
        self.num_episodes = 0

    def train_episode(
        self,
        board: 'Board',
        zombie_weights: NDArray,
        alpha: float = 0.01,
        max_steps: int = 1000
    ) -> Tuple[float, int, bool]:
        """Train Pac-Man for one episode against zombie agent.

        Args:
            board: Game board (fresh episode)
            zombie_weights: Weights for zombie opponent (3-dimensional)
            alpha: Learning rate (default: 0.01)
            max_steps: Maximum steps per episode (default: 1000)

        Returns:
            Tuple of (final_V_train, steps_taken, won)

        Algorithm (from agent.py lines 683-756):
            1. Get current state and features
            2. Select best action using greedy policy over w_hat_player
            3. Execute player action
            4. Zombies take their best actions using zombie_weights
            5. Compute V_train based on game outcome
            6. Update weights: w = w + α * (V_train - V_hat) * features
            7. Repeat until game over or max_steps
        """
        V_train = 0
        steps = 0

        while not board.is_game_over():
            steps += 1
            if steps >= max_steps:
                break

            # Current state and features
            current_state = copy.deepcopy(board.grid)
            current_features_player = board.extract_features(current_state)

            # Select best action for Pac-Man (greedy policy)
            max_V_player = -np.inf
            best_action_player = None
            actions_player = board.get_possible_action()
            random.shuffle(actions_player)  # Random tie-breaking

            for action_player in actions_player:
                successor_state_player = board.get_successor_state(action_player)
                successor_features_player = board.extract_features(successor_state_player)
                successor_V_player = V_hat(successor_features_player, self.w_hat_player)

                if successor_V_player >= max_V_player:
                    best_action_player = action_player
                    max_V_player = successor_V_player

            # Execute player action
            board.player_action(best_action_player)

            # Zombies take their actions
            zombies_positions = board.get_zombies_position()
            best_actions = []

            for zombie_pos in zombies_positions:
                row, col = zombie_pos[0], zombie_pos[1]
                actions_zombie = board.get_possible_action_zombie(row, col)
                max_V_zombie = -np.inf
                best_action_zombie = None
                random.shuffle(actions_zombie)

                for action_zombie in actions_zombie:
                    successor_state_zombie = board.get_successor_state_zombie(
                        action_zombie, row, col
                    )
                    move_delta = board.move_dict[action_zombie]
                    successor_row = row + move_delta[0]
                    successor_col = col + move_delta[1]
                    successor_features_zombie = board.extract_features_zombie(
                        successor_state_zombie, successor_row, successor_col
                    )
                    successor_V_zombie = V_hat(successor_features_zombie, zombie_weights)

                    if successor_V_zombie > max_V_zombie:
                        best_action_zombie = action_zombie
                        max_V_zombie = successor_V_zombie

                best_actions.append((row, col, best_action_zombie))

            board.zombies_action(best_actions)

            # Compute V_train based on outcome
            V_train = max_V_player  # Default

            # Win condition: all zombies gone AND exit reached
            if not board.exit_exist() and board.find_zombies_number() == 0:
                V_train = 1000
                self.num_win += 1
                won = True
                # SACRED WEIGHT UPDATE - PAC-MAN (ADDITION)
                self.w_hat_player = (
                    self.w_hat_player +
                    alpha * (V_train - V_hat(current_features_player, self.w_hat_player)) *
                    np.array(current_features_player)
                )
                break

            # Early exit penalty
            if not board.exit_exist():
                V_train = -100

            # Loss conditions
            if board.player_captured_by_zombies():
                V_train = -1000
                won = False
            elif board.player_fell_into_pit():
                V_train = -1000
                won = False
            else:
                won = False

            # SACRED WEIGHT UPDATE - PAC-MAN (ADDITION)
            # Formula from agent.py line 755
            self.w_hat_player = (
                self.w_hat_player +
                alpha * (V_train - V_hat(current_features_player, self.w_hat_player)) *
                np.array(current_features_player)
            )

        self.num_episodes += 1
        return V_train, steps, won


class ZombieTrainer:
    """Trainer for Zombie agent using adversarial temporal difference learning.

    Uses adversarial learning: agent improves by opposing the player's objectives.

    Weight Update Formula (SACRED - DO NOT MODIFY):
        w_new = w_old - α * (V_train - V_hat(features, w_old)) * features

    CRITICAL: Note the MINUS sign (adversarial learning).
    """

    def __init__(self, initial_weights: Optional[NDArray] = None):
        """Initialize Zombie trainer.

        Args:
            initial_weights: Starting weights (3-dimensional). If None, random init.
        """
        if initial_weights is None:
            # Random initialization between -0.5 and 0.5
            self.w_hat_zombie = np.random.rand(3) - 0.5
        else:
            if len(initial_weights) != 3:
                raise ValueError(f"Zombie requires 3 weights, got {len(initial_weights)}")
            self.w_hat_zombie = np.array(initial_weights, dtype=float)

        # Training statistics
        self.num_win = 0
        self.num_episodes = 0

    def train_episode(
        self,
        board: 'Board',
        player_weights: NDArray,
        alpha: float = 0.01,
        max_steps: int = 1000
    ) -> Tuple[float, int, bool]:
        """Train Zombie for one episode against player agent.

        Args:
            board: Game board (fresh episode)
            player_weights: Weights for player opponent (8-dimensional)
            alpha: Learning rate (default: 0.01)
            max_steps: Maximum steps per episode (default: 1000)

        Returns:
            Tuple of (final_V_train, steps_taken, won)

        Algorithm (from zombie.py lines 686-762):
            1. Get current state and features (for first zombie)
            2. Select best zombie actions using greedy policy over w_hat_zombie
            3. Player takes best action using player_weights
            4. Execute zombie and player actions
            5. Compute V_train based on game outcome
            6. Update weights: w = w - α * (V_train - V_hat) * features (ADVERSARIAL)
            7. Repeat until game over or max_steps
        """
        V_train = 0
        steps = 0
        won = False

        while not board.is_game_over():
            steps += 1
            if steps >= max_steps:
                break

            # Current state and features (for zombie perspective)
            current_state = copy.deepcopy(board.grid)
            # Note: We use the first zombie's position for feature extraction
            # This matches the original implementation's approach
            zombies_positions = board.get_zombies_position()
            if not zombies_positions:
                # No zombies left, episode should end
                break
            first_zombie_row, first_zombie_col = zombies_positions[0][0], zombies_positions[0][1]
            current_features_zombie = board.extract_features_zombie(
                current_state, first_zombie_row, first_zombie_col
            )

            # Select best actions for all zombies
            zombies_positions = board.get_zombies_position()
            best_actions_zombies = []

            for zombie_pos in zombies_positions:
                row, col = zombie_pos[0], zombie_pos[1]
                actions_zombie = board.get_possible_action_zombie(row, col)
                max_V_zombie = -np.inf
                best_action_zombie = None
                random.shuffle(actions_zombie)

                for action_zombie in actions_zombie:
                    successor_state_zombie = board.get_successor_state_zombie(
                        action_zombie, row, col
                    )
                    move_delta = board.move_dict[action_zombie]
                    successor_row = row + move_delta[0]
                    successor_col = col + move_delta[1]
                    successor_features_zombie = board.extract_features_zombie(
                        successor_state_zombie, successor_row, successor_col
                    )
                    successor_V_zombie = V_hat(successor_features_zombie, self.w_hat_zombie)

                    if successor_V_zombie > max_V_zombie:
                        best_action_zombie = action_zombie
                        max_V_zombie = successor_V_zombie

                best_actions_zombies.append((row, col, best_action_zombie))

            # Select best action for player
            max_V_player = -np.inf
            best_action_player = None
            actions_player = board.get_possible_action()
            random.shuffle(actions_player)

            for action_player in actions_player:
                successor_state_player = board.get_successor_state(action_player)
                successor_features_player = board.extract_features(successor_state_player)
                successor_V_player = V_hat(successor_features_player, player_weights)

                if successor_V_player > max_V_player:
                    best_action_player = action_player
                    max_V_player = successor_V_player

            # Execute actions (zombies first, then player)
            board.zombies_action(best_actions_zombies)
            board.player_action(best_action_player)

            # Compute V_train based on outcome
            V_train = max_V_zombie  # Default (from first zombie calculation)

            # Win condition for zombie: captured player
            if board.player_captured_by_zombies():
                V_train = 1000
                self.num_win += 1
                won = True

            # Zombie fell into pit
            if board.zombie_fell_into_pit():
                V_train = -100

            # Player cured zombie (zombie's loss)
            if board.player_cure_zombie():
                V_train = -1000

            # SACRED WEIGHT UPDATE - ZOMBIE (SUBTRACTION - ADVERSARIAL)
            # Formula from zombie.py line 762
            self.w_hat_zombie = (
                self.w_hat_zombie -
                alpha * (V_train - V_hat(current_features_zombie, self.w_hat_zombie)) *
                np.array(current_features_zombie)
            )

        self.num_episodes += 1
        return V_train, steps, won
