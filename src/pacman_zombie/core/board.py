"""Game board implementation.

This module contains the Board class which manages the game state, enforces rules,
and provides methods for agent interaction. The board is represented as a 2D grid
where each cell can contain game entities.

IMPORTANT: This class contains game logic that is integral to the learning algorithm.
Feature extraction methods are included here and should be moved to agents/features.py
in a future refactoring phase.
"""

import copy
import math
import random
from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from .constants import *


class Board:
    """Game board managing state and rules.

    The board is represented as a 2D grid where each cell can contain:
    - None (empty cell)
    - "A" (Pac-Man player)
    - "Z" (Zombie)
    - "O" (Obstacle)
    - "V" (Vaccine)
    - "E" (Exit)
    - "P" (Pit)

    The board handles:
    - Entity placement and movement
    - Game rule enforcement (win/loss conditions)
    - Feature extraction for learning agents
    - State successor generation for planning
    """

    def __init__(
        self,
        width: int = DEFAULT_BOARD_WIDTH,
        height: int = DEFAULT_BOARD_HEIGHT,
        num_zombies: int = DEFAULT_NUM_ZOMBIES,
        num_obstacles: int = DEFAULT_NUM_OBSTACLES,
        num_vaccines: int = DEFAULT_NUM_VACCINES,
        num_shots: int = DEFAULT_NUM_SHOTS
    ):
        """Initialize board with configurable dimensions and entity counts.

        Args:
            width: Board width in cells
            height: Board height in cells
            num_zombies: Number of zombies to place
            num_obstacles: Number of obstacles to place
            num_vaccines: Total vaccines available in game
            num_shots: Number of shots Pac-Man starts with
        """
        self.width = width
        self.height = height
        self.grid: List[List[Optional[str]]] = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Entity positions
        self.player_position: Optional[Tuple[int, int]] = None
        self.zombies_positions: List[Optional[Tuple[int, int]]] = [None for _ in range(num_zombies)]
        self.obstacle_positions: List[Optional[Tuple[int, int]]] = [None for _ in range(num_obstacles)]
        self.vaccine_position: Optional[Tuple[int, int]] = None
        self.exit_position: Optional[Tuple[int, int]] = None
        self.pit_position: Optional[Tuple[int, int]] = None

        # Game state
        self.score: int = 0
        self.num_zombie_cure: int = 0
        self.shoot: int = num_shots
        self.has_vaccine: bool = False
        self.num_shooted_zombie: int = 0
        self.num_remain_vaccine: int = num_vaccines
        self.play_pickup: bool = True  # Sound flag for UI

        # Initialize grid with random entity placement
        self.player_position = self.generate_random_position()
        self.zombies_positions = [self.generate_random_position() for _ in range(num_zombies)]
        self.obstacle_positions = [self.generate_random_position() for _ in range(num_obstacles)]
        self.vaccine_position = self.generate_random_position()
        self.exit_position = self.generate_random_position()
        self.pit_position = self.generate_random_position()

        # Place entities on grid
        self.grid[self.player_position[0]][self.player_position[1]] = SYMBOL_PLAYER
        for zombie_pos in self.zombies_positions:
            self.grid[zombie_pos[0]][zombie_pos[1]] = SYMBOL_ZOMBIE
        for obstacle_pos in self.obstacle_positions:
            self.grid[obstacle_pos[0]][obstacle_pos[1]] = SYMBOL_OBSTACLE
        self.grid[self.vaccine_position[0]][self.vaccine_position[1]] = SYMBOL_VACCINE
        self.grid[self.exit_position[0]][self.exit_position[1]] = SYMBOL_EXIT
        self.grid[self.pit_position[0]][self.pit_position[1]] = SYMBOL_PIT

        # Movement mapping
        self.move_dict = MOVE_DELTAS

    def generate_random_position(self) -> Tuple[int, int]:
        """Generate random unoccupied position on board.

        Recursively tries random positions until finding an empty one.

        Returns:
            (row, col) tuple of unoccupied position
        """
        x = random.randint(0, self.height - 1)
        y = random.randint(0, self.width - 1)
        position = (x, y)

        occupied_positions = (
            [self.player_position] +
            self.zombies_positions +
            self.obstacle_positions +
            [self.vaccine_position, self.exit_position, self.pit_position]
        )

        if any(pos == position for pos in occupied_positions if pos is not None):
            return self.generate_random_position()

        return position

    def player_action(self, action: str) -> None:
        """Execute Pac-Man's action on the board.

        Moves Pac-Man or shoots zombies based on action. Does not validate
        action legality - caller should use get_possible_action() first.

        Args:
            action: One of UP, DOWN, LEFT, RIGHT, SHOOT
        """
        if action == MOVE_UP:
            if self.player_position[0] > 0 and self.grid[self.player_position[0]-1][self.player_position[1]] != SYMBOL_OBSTACLE:
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0]-1, self.player_position[1])
                self.grid[self.player_position[0]][self.player_position[1]] = SYMBOL_PLAYER

        elif action == MOVE_DOWN:
            if self.player_position[0] < self.height-1 and self.grid[self.player_position[0]+1][self.player_position[1]] != SYMBOL_OBSTACLE:
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0]+1, self.player_position[1])
                self.grid[self.player_position[0]][self.player_position[1]] = SYMBOL_PLAYER

        elif action == MOVE_LEFT:
            if self.player_position[1] > 0 and self.grid[self.player_position[0]][self.player_position[1]-1] != SYMBOL_OBSTACLE:
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0], self.player_position[1]-1)
                self.grid[self.player_position[0]][self.player_position[1]] = SYMBOL_PLAYER

        elif action == MOVE_RIGHT:
            if self.player_position[1] < self.width-1 and self.grid[self.player_position[0]][self.player_position[1]+1] != SYMBOL_OBSTACLE:
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0], self.player_position[1]+1)
                self.grid[self.player_position[0]][self.player_position[1]] = SYMBOL_PLAYER

        elif action == ACTION_SHOOT:
            # Shoot zombies in straight lines within 2 cells
            for i in range(self.height):
                for j in range(self.width):
                    if i-2 >= 0:
                        if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                            self.grid[i-2][j] = None
                            self.shoot -= 1
                    if i+2 < self.height:
                        if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                            self.grid[i+2][j] = None
                            self.shoot -= 1
                    if j-2 >= 0:
                        if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j-2] == SYMBOL_ZOMBIE and self.shoot != 0:
                            self.grid[i][j-2] = None
                            self.shoot -= 1
                    if j+2 < self.width:
                        if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j+2] == SYMBOL_ZOMBIE and self.shoot != 0:
                            self.grid[i][j+2] = None
                            self.shoot -= 1

    def zombies_action(self, best_actions: List[Tuple[int, int, str]]) -> None:
        """Execute multiple zombies' actions on the board.

        Args:
            best_actions: List of (row, col, action) tuples for each zombie
        """
        for acts in best_actions:
            zombies_position = acts[0], acts[1]
            action = acts[2]

            if action == MOVE_UP:
                if zombies_position[0] > 0 and (self.grid[zombies_position[0]-1][zombies_position[1]] == None or self.grid[zombies_position[0]-1][zombies_position[1]] == SYMBOL_PIT):
                    self.grid[zombies_position[0]][zombies_position[1]] = None
                    self.grid[zombies_position[0]-1][zombies_position[1]] = SYMBOL_ZOMBIE

            elif action == MOVE_DOWN:
                if zombies_position[0] < self.height-1 and (self.grid[zombies_position[0]+1][zombies_position[1]] == None or self.grid[zombies_position[0]+1][zombies_position[1]] == SYMBOL_PIT):
                    self.grid[zombies_position[0]][zombies_position[1]] = None
                    self.grid[zombies_position[0]+1][zombies_position[1]] = SYMBOL_ZOMBIE

            elif action == MOVE_LEFT:
                if zombies_position[1] > 0 and (self.grid[zombies_position[0]][zombies_position[1]-1] == None or self.grid[zombies_position[0]][zombies_position[1]-1] == SYMBOL_PIT):
                    self.grid[zombies_position[0]][zombies_position[1]] = None
                    self.grid[zombies_position[0]][zombies_position[1]-1] = SYMBOL_ZOMBIE

            elif action == MOVE_RIGHT:
                if zombies_position[1] < self.width-1 and (self.grid[zombies_position[0]][zombies_position[1]+1] == None or self.grid[zombies_position[0]][zombies_position[1]+1] == SYMBOL_PIT):
                    self.grid[zombies_position[0]][zombies_position[1]] = None
                    self.grid[zombies_position[0]][zombies_position[1]+1] = SYMBOL_ZOMBIE

    def use_vaccine(self) -> None:
        """Update has_vaccine flag based on whether vaccine still exists on board."""
        self.has_vaccine = True
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_VACCINE:
                    self.has_vaccine = False

    def can_shoot(self) -> bool:
        """Check if Pac-Man can shoot a zombie.

        Returns:
            True if there's a zombie within shooting range in a straight line
        """
        for i in range(self.height):
            for j in range(self.width):
                if i-2 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                        return True
                if i+2 < self.height:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                        return True
                if j-2 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j-2] == SYMBOL_ZOMBIE and self.shoot != 0:
                        return True
                if j+2 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j+2] == SYMBOL_ZOMBIE and self.shoot != 0:
                        return True
        return False

    def is_game_over(self) -> bool:
        """Check if game has ended (win or loss).

        Returns:
            True if game is over, False otherwise
        """
        self.zombie_fell_into_pit()
        self.use_vaccine()
        self.player_cure_zombie()

        if self.player_captured_by_zombies():
            return True

        if self.player_fell_into_pit():
            return True

        return False

    def exit_exist(self) -> bool:
        """Check if exit still exists on board.

        Returns:
            True if exit exists, False if Pac-Man reached it
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_EXIT:
                    return True
        return False

    def put_vaccine(self) -> None:
        """Spawn a new vaccine at random empty position."""
        while True:
            row = random.randint(0, self.height-1)
            col = random.randint(0, self.width-1)
            if self.grid[row][col] == None:
                self.grid[row][col] = SYMBOL_VACCINE
                self.play_pickup = True
                break

    def player_cure_zombie(self) -> bool:
        """Check and execute zombie curing if Pac-Man with vaccine is adjacent.

        Returns:
            True if a zombie was cured, False otherwise
        """
        for i in range(self.height):
            for j in range(self.width):
                # Check all 8 adjacent positions
                if i-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i-1][j] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if i+1 < self.height:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i+1][j] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j-1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j+1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                # Diagonal positions
                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j-1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i-1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j+1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i-1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j-1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i+1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j+1] == SYMBOL_ZOMBIE and self.has_vaccine:
                        self.grid[i+1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < VACCINE_RESPAWN_LIMIT:
                            self.put_vaccine()
                        return True

        return False

    def player_captured_by_zombies(self) -> bool:
        """Check if Pac-Man is captured by zombies.

        Returns:
            True if zombie is adjacent to Pac-Man (and Pac-Man doesn't have vaccine)
        """
        for i in range(self.height):
            for j in range(self.width):
                # Check all 8 adjacent positions
                if i-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if i+1 < self.height:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j-1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i][j+1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j-1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i-1][j+1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j-1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True
                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == SYMBOL_PLAYER and self.grid[i+1][j+1] == SYMBOL_ZOMBIE and not self.has_vaccine:
                        return True

        return False

    def zombie_captured_player(self) -> bool:
        """Alias for player_captured_by_zombies for zombie perspective.

        Returns:
            True if zombie captured Pac-Man
        """
        return self.player_captured_by_zombies()

    def player_fell_into_pit(self) -> bool:
        """Check if Pac-Man fell into pit.

        Returns:
            True if Pac-Man is on pit position
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_PIT:
                    return False
        if self.grid[self.pit_position[0]][self.pit_position[1]] == SYMBOL_PLAYER:
            return True
        return False

    def zombie_fell_into_pit(self) -> bool:
        """Check and handle zombie falling into pit.

        If zombie fell into pit, respawn it at random location.

        Returns:
            True if a zombie fell into pit (and was respawned)
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_PIT:
                    return False
        if self.grid[self.pit_position[0]][self.pit_position[1]] == SYMBOL_ZOMBIE:
            self.grid[self.pit_position[0]][self.pit_position[1]] = SYMBOL_PIT
            self.zombies_positions = [self.generate_random_position()]
            self.grid[self.zombies_positions[0][0]][self.zombies_positions[0][1]] = SYMBOL_ZOMBIE
            return True
        return False

    def find_zombies_number(self) -> int:
        """Count number of zombies currently on board.

        Returns:
            Number of zombies
        """
        num = 0
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_ZOMBIE:
                    num += 1
        return num

    def get_possible_action(self) -> List[str]:
        """Get list of legal actions for Pac-Man.

        Returns:
            List of action strings (UP, DOWN, LEFT, RIGHT, SHOOT)
        """
        actions = []
        row, col = 0, 0
        num_zombies = 0

        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_PLAYER:
                    row, col = i, j
                if self.grid[i][j] == SYMBOL_ZOMBIE:
                    num_zombies += 1

        if num_zombies > 0:
            # While zombies exist, cannot move to exit
            if row > 0 and self.grid[row-1][col] != SYMBOL_OBSTACLE and self.grid[row-1][col] != SYMBOL_EXIT:
                actions.append(MOVE_UP)
            if row < self.height-1 and self.grid[row+1][col] != SYMBOL_OBSTACLE and self.grid[row+1][col] != SYMBOL_EXIT:
                actions.append(MOVE_DOWN)
            if col > 0 and self.grid[row][col-1] != SYMBOL_OBSTACLE and self.grid[row][col-1] != SYMBOL_EXIT:
                actions.append(MOVE_LEFT)
            if col < self.width-1 and self.grid[row][col+1] != SYMBOL_OBSTACLE and self.grid[row][col+1] != SYMBOL_EXIT:
                actions.append(MOVE_RIGHT)
            if self.can_shoot():
                actions.append(ACTION_SHOOT)
        else:
            # No zombies, can move to exit
            if row > 0 and self.grid[row-1][col] != SYMBOL_OBSTACLE:
                actions.append(MOVE_UP)
            if row < self.height-1 and self.grid[row+1][col] != SYMBOL_OBSTACLE:
                actions.append(MOVE_DOWN)
            if col > 0 and self.grid[row][col-1] != SYMBOL_OBSTACLE:
                actions.append(MOVE_LEFT)
            if col < self.width-1 and self.grid[row][col+1] != SYMBOL_OBSTACLE:
                actions.append(MOVE_RIGHT)

        return actions

    def get_possible_action_zombie(self, row: int, col: int) -> List[str]:
        """Get list of legal actions for a zombie at given position.

        Args:
            row: Zombie's row position
            col: Zombie's column position

        Returns:
            List of action strings (UP, DOWN, LEFT, RIGHT)
        """
        actions = []

        if row > 0 and self.grid[row-1][col] != SYMBOL_OBSTACLE and self.grid[row-1][col] != SYMBOL_VACCINE and self.grid[row-1][col] != SYMBOL_EXIT:
            actions.append(MOVE_UP)
        if row < self.height-1 and self.grid[row+1][col] != SYMBOL_OBSTACLE and self.grid[row+1][col] != SYMBOL_VACCINE and self.grid[row+1][col] != SYMBOL_EXIT:
            actions.append(MOVE_DOWN)
        if col > 0 and self.grid[row][col-1] != SYMBOL_OBSTACLE and self.grid[row][col-1] != SYMBOL_VACCINE and self.grid[row][col-1] != SYMBOL_EXIT:
            actions.append(MOVE_LEFT)
        if col < self.width-1 and self.grid[row][col+1] != SYMBOL_OBSTACLE and self.grid[row][col+1] != SYMBOL_VACCINE and self.grid[row][col+1] != SYMBOL_EXIT:
            actions.append(MOVE_RIGHT)

        return actions

    def get_successor_state(self, action: str) -> List[List[Optional[str]]]:
        """Get hypothetical next state if Pac-Man takes given action.

        Used for planning - does not modify actual board state.

        Args:
            action: Action to simulate

        Returns:
            Deep copy of grid after action
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_PLAYER:
                    player_position = [i, j]

        grid_copy = copy.deepcopy(self.grid)

        if action == ACTION_SHOOT:
            for i in range(self.height):
                for j in range(self.width):
                    if i-2 >= 0:
                        if grid_copy[i][j] == SYMBOL_PLAYER and grid_copy[i-2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                            grid_copy[i-2][j] = None
                    if i+2 < self.height:
                        if grid_copy[i][j] == SYMBOL_PLAYER and grid_copy[i+2][j] == SYMBOL_ZOMBIE and self.shoot != 0:
                            grid_copy[i+2][j] = None
                    if j-2 >= 0:
                        if grid_copy[i][j] == SYMBOL_PLAYER and grid_copy[i][j-2] == SYMBOL_ZOMBIE and self.shoot != 0:
                            grid_copy[i][j-2] = None
                    if j+2 < self.width:
                        if grid_copy[i][j] == SYMBOL_PLAYER and grid_copy[i][j+2] == SYMBOL_ZOMBIE and self.shoot != 0:
                            grid_copy[i][j+2] = None
            return grid_copy
        else:
            grid_copy[player_position[0]][player_position[1]] = None
            grid_copy[player_position[0]+self.move_dict[action][0]][player_position[1]+self.move_dict[action][1]] = SYMBOL_PLAYER
            return grid_copy

    def get_successor_state_zombie(self, action: str, row: int, col: int) -> List[List[Optional[str]]]:
        """Get hypothetical next state if zombie takes given action.

        Used for planning - does not modify actual board state.

        Args:
            action: Action to simulate
            row: Zombie's current row
            col: Zombie's current column

        Returns:
            Deep copy of grid after action
        """
        zombie_position = [row, col]
        grid_copy = copy.deepcopy(self.grid)
        grid_copy[zombie_position[0]][zombie_position[1]] = None
        grid_copy[zombie_position[0]+self.move_dict[action][0]][zombie_position[1]+self.move_dict[action][1]] = SYMBOL_ZOMBIE
        return grid_copy

    def get_zombies_position(self) -> List[List[int]]:
        """Get positions of all zombies on board.

        Returns:
            List of [row, col] positions
        """
        zombies_positions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == SYMBOL_ZOMBIE:
                    zombie_position = [i, j]
                    zombies_positions.append(zombie_position)
        return zombies_positions

    # =========================================================================
    # FEATURE EXTRACTION METHODS
    # =========================================================================
    # TODO: These should be moved to agents/features.py in future refactoring
    # They are kept here temporarily to maintain compatibility with existing code

    def extract_features(self, successor_state: List[List[Optional[str]]]) -> NDArray:
        """Extract 8-dimensional feature vector for Pac-Man agent.

        CRITICAL: This exact formula is integral to learned weights.
        DO NOT MODIFY without retraining agents.

        Args:
            successor_state: Hypothetical next state after action

        Returns:
            8-element numpy array of features
        """
        features = []

        player_position = None
        number_of_zombie = 0
        distance_from_all_obstacle = []
        distance_from_vaccines = 0
        distance_from_all_zombies = []
        distance_from_pit = 0
        distance_from_exit = 0

        # Feature multipliers
        go_to_exit = 0
        shoot = MULTIPLIER_SHOOT_DEFAULT
        go_to_vaccine = 1
        go_to_zombies = 1
        distance_from_nearest_zombies = 0
        pit = MULTIPLIER_PIT_DEFAULT
        has_vaccine = 0

        if self.has_vaccine:
            has_vaccine = 1
            go_to_zombies = -1
            shoot = MULTIPLIER_SHOOT_WITH_VACCINE

        # Find player position
        for i in range(self.height):
            for j in range(self.width):
                if successor_state[i][j] == SYMBOL_PLAYER:
                    player_position = [i, j]

        # Calculate distances to all entities
        for i in range(self.height):
            for j in range(self.width):
                if successor_state[i][j] == SYMBOL_EXIT:
                    distance_from_exit = math.dist(player_position, [i, j])
                if successor_state[i][j] == SYMBOL_ZOMBIE:
                    number_of_zombie += 1
                    distance_from_all_zombies.append(math.dist(player_position, [i, j]))
                if successor_state[i][j] == SYMBOL_OBSTACLE:
                    distance_from_all_obstacle.append(math.dist(player_position, [i, j]))
                if successor_state[i][j] == SYMBOL_VACCINE:
                    distance_from_vaccines = math.dist(player_position, [i, j])
                if successor_state[i][j] == SYMBOL_PIT:
                    distance_from_pit = math.dist(player_position, [i, j])

        # Adjust multipliers based on game state
        if number_of_zombie == 0:
            go_to_exit = MULTIPLIER_GO_TO_EXIT_ACTIVE
            distance_from_nearest_zombies = 0
            go_to_vaccine = 0
            has_vaccine = 0
            go_to_zombies = 0
            pit = MULTIPLIER_PIT_ZOMBIES_CLEARED
        else:
            go_to_exit = MULTIPLIER_GO_TO_EXIT_INACTIVE
            distance_from_nearest_zombies = min(distance_from_all_zombies)
            go_to_vaccine = 1

        # Build feature vector
        features.append(go_to_exit * (distance_from_exit / FEATURE_DISTANCE_SCALE))
        features.append(shoot * number_of_zombie)
        remain_vaccine = VACCINE_RESPAWN_LIMIT - self.num_zombie_cure
        features.append(remain_vaccine)
        features.append(go_to_vaccine * distance_from_vaccines / FEATURE_DISTANCE_SCALE)
        features.append(go_to_zombies * distance_from_nearest_zombies / FEATURE_DISTANCE_SCALE)
        features.append(has_vaccine)
        features.append(min(distance_from_all_obstacle) / FEATURE_DISTANCE_SCALE)
        features.append(pit * distance_from_pit / FEATURE_DISTANCE_SCALE)

        return np.array(features)

    def extract_features_zombie(self, successor_state: List[List[Optional[str]]], row: int, col: int) -> NDArray:
        """Extract 3-dimensional feature vector for Zombie agent.

        CRITICAL: This exact formula is integral to learned weights.
        DO NOT MODIFY without retraining agents.

        Args:
            successor_state: Hypothetical next state after action
            row: Zombie's row position in successor state
            col: Zombie's column position in successor state

        Returns:
            3-element numpy array of features
        """
        features = []

        distance_from_all_obstacle = []
        distance_from_pit = 0
        go_to_player = MULTIPLIER_ZOMBIE_CHASE
        zombie_position = [row, col]
        distance_from_player = 0

        # Calculate distances
        for i in range(self.height):
            for j in range(self.width):
                if successor_state[i][j] == SYMBOL_PLAYER:
                    distance_from_player = math.dist(zombie_position, [i, j])
                if successor_state[i][j] == SYMBOL_OBSTACLE:
                    distance_from_all_obstacle.append(math.dist(zombie_position, [i, j]))
                if successor_state[i][j] == SYMBOL_PIT:
                    distance_from_pit = math.dist(zombie_position, [i, j])

        # Flee if Pac-Man has vaccine
        if self.has_vaccine:
            go_to_player = MULTIPLIER_ZOMBIE_FLEE

        # Build feature vector
        features.append(go_to_player * distance_from_player / FEATURE_DISTANCE_SCALE)
        features.append(distance_from_pit / FEATURE_DISTANCE_SCALE)
        features.append(min(distance_from_all_obstacle) / FEATURE_OBSTACLE_SCALE)

        return np.array(features)


def print_grid(grid: List[List[Optional[str]]]) -> None:
    """Print board grid to terminal (for debugging).

    Args:
        grid: 2D grid to print
    """
    print("===============================")
    for i in range(len(grid)):
        row = ""
        for j in range(len(grid[i])):
            row += grid[i][j] + "|" if grid[i][j] != None else " |"
        print(row + "|")
    print("===============================")
