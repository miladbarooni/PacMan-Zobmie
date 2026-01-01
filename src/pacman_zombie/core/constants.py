"""Game constants and configuration defaults.

This module contains all constant values used throughout the game, including
board dimensions, entity counts, rewards, and symbolic representations.

IMPORTANT: Reward values are part of the core learning algorithm and should
NOT be modified without retraining agents.
"""

from typing import Dict, Tuple

# ============================================================================
# Board Dimensions
# ============================================================================

DEFAULT_BOARD_WIDTH: int = 10
"""Default width of the game board in cells."""

DEFAULT_BOARD_HEIGHT: int = 15
"""Default height of the game board in cells."""

# ============================================================================
# Entity Counts
# ============================================================================

DEFAULT_NUM_ZOMBIES: int = 4
"""Default number of zombies on the board."""

DEFAULT_NUM_OBSTACLES: int = 10
"""Default number of obstacles on the board."""

DEFAULT_NUM_VACCINES: int = 4
"""Total number of vaccines available in the game."""

DEFAULT_NUM_SHOTS: int = 3
"""Number of shots Pac-Man starts with."""

# ============================================================================
# Game Mechanics
# ============================================================================

SHOOTING_RANGE: int = 2
"""Maximum distance (in cells) Pac-Man can shoot."""

VACCINE_RESPAWN_LIMIT: int = 4
"""Maximum number of times vaccines can respawn."""

# ============================================================================
# Rewards (CRITICAL - DO NOT MODIFY)
# ============================================================================
# These reward values are integral to the learning algorithm.
# Modifying them requires retraining both agents from scratch.

REWARD_WIN: int = 1000
"""Reward for Pac-Man winning (all zombies eliminated, exit reached)."""

REWARD_LOSE: int = -1000
"""Penalty for Pac-Man losing (captured or fell in pit)."""

REWARD_EXIT_EARLY: int = -100
"""Penalty for reaching exit before all zombies are eliminated."""

REWARD_PIT: int = -100
"""Penalty for falling into a pit."""

REWARD_ZOMBIE_CURED: int = -1000
"""Penalty for zombie being cured by Pac-Man's vaccine."""

REWARD_ZOMBIE_WIN: int = 1000
"""Reward for zombie capturing Pac-Man."""

# ============================================================================
# Entity Symbols
# ============================================================================
# Character representations for board cells.

SYMBOL_PLAYER: str = "A"
"""Symbol for Pac-Man on the board."""

SYMBOL_ZOMBIE: str = "Z"
"""Symbol for zombie on the board."""

SYMBOL_OBSTACLE: str = "O"
"""Symbol for obstacle on the board."""

SYMBOL_VACCINE: str = "V"
"""Symbol for vaccine on the board."""

SYMBOL_EXIT: str = "E"
"""Symbol for exit on the board."""

SYMBOL_PIT: str = "P"
"""Symbol for pit on the board."""

# ============================================================================
# Movement Directions
# ============================================================================

MOVE_UP: str = "UP"
"""Move up action."""

MOVE_DOWN: str = "DOWN"
"""Move down action."""

MOVE_LEFT: str = "LEFT"
"""Move left action."""

MOVE_RIGHT: str = "RIGHT"
"""Move right action."""

ACTION_SHOOT: str = "SHOOT"
"""Shoot action."""

MOVE_DELTAS: Dict[str, Tuple[int, int]] = {
    MOVE_UP: (-1, 0),
    MOVE_DOWN: (1, 0),
    MOVE_LEFT: (0, -1),
    MOVE_RIGHT: (0, 1)
}
"""Mapping of movement actions to (row_delta, col_delta) tuples."""

# ============================================================================
# Feature Extraction Constants
# ============================================================================
# These constants are used in feature extraction and affect learning.
# DO NOT MODIFY without understanding their impact on trained weights.

FEATURE_DISTANCE_SCALE: float = 20.0
"""Scaling factor for distance features (division factor)."""

FEATURE_OBSTACLE_SCALE: float = 40.0
"""Scaling factor for obstacle distance features (zombies only)."""

# Feature multipliers for Pac-Man
MULTIPLIER_GO_TO_EXIT_ACTIVE: float = 100.0
"""Multiplier for exit distance when no zombies remain."""

MULTIPLIER_GO_TO_EXIT_INACTIVE: float = 0.0
"""Multiplier for exit distance when zombies still exist."""

MULTIPLIER_SHOOT_DEFAULT: float = -1000000.0
"""Default multiplier for shooting (strongly discourages when not appropriate)."""

MULTIPLIER_SHOOT_WITH_VACCINE: float = 0.0
"""Multiplier for shooting when Pac-Man has vaccine."""

MULTIPLIER_PIT_ZOMBIES_CLEARED: float = 10.0
"""Pit avoidance multiplier when zombies are cleared."""

MULTIPLIER_PIT_DEFAULT: float = 1.0
"""Default pit avoidance multiplier."""

# Feature multipliers for Zombies
MULTIPLIER_ZOMBIE_CHASE: float = -10.0
"""Multiplier for chasing Pac-Man (negative to minimize distance)."""

MULTIPLIER_ZOMBIE_FLEE: float = 10.0
"""Multiplier for fleeing from Pac-Man when they have vaccine."""
