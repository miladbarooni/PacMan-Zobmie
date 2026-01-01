"""Terminal-based ASCII/Unicode renderer for the game.

This module provides a colorful terminal visualization of the game board
using unicode emojis or ASCII characters, with cross-platform color support.
"""

import os
import sys
from typing import TYPE_CHECKING, Optional

try:
    from colorama import Fore, Back, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

if TYPE_CHECKING:
    from ..core.board import Board


class TerminalRenderer:
    """Renders game board to terminal using ASCII/Unicode and colors.

    Supports two visual modes:
    - Unicode mode: Emoji symbols with colors (🟡🧟💉🚪)
    - ASCII mode: Plain text symbols (@, Z, +, X)

    Colors are provided by colorama for cross-platform support.
    """

    def __init__(self, use_unicode: bool = True, use_colors: bool = True):
        """Initialize renderer with display preferences.

        Args:
            use_unicode: If True, use emoji symbols. If False, use ASCII.
            use_colors: If True, use terminal colors (requires colorama).
        """
        self.use_unicode = use_unicode
        self.use_colors = use_colors and COLORAMA_AVAILABLE

        # Initialize colorama for cross-platform color support
        if self.use_colors:
            colorama_init(autoreset=True)

        # Symbol mappings
        if self.use_unicode:
            self.symbols = {
                'A': '🟡',  # Pac-Man
                'Z': '🧟',  # Zombie
                'O': '█',   # Obstacle
                'V': '💉',  # Vaccine
                'E': '🚪',  # Exit
                'P': '⚫',  # Pit
                None: ' '   # Empty
            }
        else:
            self.symbols = {
                'A': '@',   # Pac-Man
                'Z': 'Z',   # Zombie
                'O': '#',   # Obstacle
                'V': '+',   # Vaccine
                'E': 'X',   # Exit
                'P': 'O',   # Pit
                None: '.'   # Empty
            }

        # Color mappings (only used if use_colors is True)
        if self.use_colors:
            self.colors = {
                'A': Fore.YELLOW,        # Pac-Man: Yellow
                'Z': Fore.GREEN,         # Zombie: Green
                'O': Fore.WHITE,         # Obstacle: White/Bright
                'V': Fore.CYAN,          # Vaccine: Cyan
                'E': Fore.BLUE,          # Exit: Blue
                'P': Fore.RED,           # Pit: Red
                None: Fore.WHITE         # Empty: Default
            }

    def _get_symbol(self, cell_value: Optional[str]) -> str:
        """Get display symbol for a board cell value.

        Args:
            cell_value: Board cell content ('A', 'Z', 'O', 'V', 'E', 'P', or None)

        Returns:
            Display symbol for the cell
        """
        return self.symbols.get(cell_value, '?')

    def _get_colored_symbol(self, cell_value: Optional[str]) -> str:
        """Get colored display symbol for a board cell.

        Args:
            cell_value: Board cell content

        Returns:
            Colored symbol string (or plain if colors disabled)
        """
        symbol = self._get_symbol(cell_value)

        if self.use_colors and cell_value in self.colors:
            return f"{self.colors[cell_value]}{symbol}{Style.RESET_ALL}"
        else:
            return symbol

    def _render_status_line(self, board: 'Board') -> str:
        """Build status HUD line showing game stats.

        Args:
            board: Current game board state

        Returns:
            Formatted status string
        """
        vaccine_status = "Yes" if board.has_vaccine else "No"
        active_zombies = board.find_zombies_number()

        status = (
            f"Score: {board.score:4d} | "
            f"Shots: {board.shoot}/3 | "
            f"Vaccine: {vaccine_status:3s} | "
            f"Cured: {board.num_zombie_cure} | "
            f"Zombies: {active_zombies}"
        )

        return status

    def clear_screen(self) -> None:
        """Clear terminal screen (cross-platform)."""
        if sys.platform.startswith('win'):
            os.system('cls')
        else:
            os.system('clear')

    def render(self, board: 'Board', clear: bool = True) -> None:
        """Render the current game board to terminal.

        Args:
            board: Game board to render
            clear: If True, clear screen before rendering
        """
        if clear:
            self.clear_screen()

        # Print header
        print("=" * 60)
        print(" " * 15 + "PAC-MAN vs ZOMBIES" + " " * 15)
        print("=" * 60)
        print()

        # Print status line
        status = self._render_status_line(board)
        print(status)
        print()

        # Build board with borders
        # Top border
        border_color = Fore.WHITE if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""

        print(f"{border_color}┌{'─' * (board.width * 2)}┐{reset}")

        # Render each row
        for row in range(board.height):
            row_display = f"{border_color}│{reset}"

            for col in range(board.width):
                cell_value = board.grid[row][col]
                symbol = self._get_colored_symbol(cell_value)
                row_display += symbol + " "

            row_display += f"{border_color}│{reset}"
            print(row_display)

        # Bottom border
        print(f"{border_color}└{'─' * (board.width * 2)}┘{reset}")
        print()

    def render_game_over(self, board: 'Board', message: str) -> None:
        """Render final game state with game over message.

        Args:
            board: Final game board state
            message: Game over message (win/lose text)
        """
        # Render final board state
        self.render(board, clear=False)

        # Print game over message with styling
        print("=" * 60)

        if self.use_colors:
            if "WIN" in message.upper():
                color = Fore.GREEN
            else:
                color = Fore.RED
            print(f"{color}{Style.BRIGHT}{message.center(60)}{Style.RESET_ALL}")
        else:
            print(message.center(60))

        print("=" * 60)
        print()

        # Print final stats
        print(f"Final Score: {board.score}")
        print(f"Zombies Cured: {board.num_zombie_cure}")
        print(f"Zombies Shot: {board.num_shooted_zombie}")
        print()

    def render_legend(self) -> None:
        """Display legend showing what each symbol means (optional helper)."""
        print("\nLEGEND:")
        print(f"  {self._get_colored_symbol('A')} - Pac-Man (You)")
        print(f"  {self._get_colored_symbol('Z')} - Zombie (AI)")
        print(f"  {self._get_colored_symbol('V')} - Vaccine (Cure adjacent zombies)")
        print(f"  {self._get_colored_symbol('E')} - Exit (Appears after all zombies cured)")
        print(f"  {self._get_colored_symbol('O')} - Obstacle (Cannot pass)")
        print(f"  {self._get_colored_symbol('P')} - Pit (Avoid!)")
        print()
