#!/usr/bin/env python3
"""Interactive play script - Human vs AI zombies.

This script allows you to play Pac-Man vs Zombies in your terminal, controlling
Pac-Man while AI zombies try to catch you.

Usage:
    python scripts/play.py                    # Play with default settings
    python scripts/play.py --show-legal-moves # Show available actions
    python scripts/play.py --show-ai-thinking # See AI decisions
    python scripts/play.py --save-replay game.json  # Save game for analysis
    python scripts/play.py --no-unicode --no-colors # ASCII-only mode

Controls:
    Arrow Keys / WASD - Move Pac-Man
    F / Space         - Shoot zombie (must be exactly 2 cells away)
    Q                 - Quit game

Game Rules:
    - Collect vaccines (💉) to cure adjacent zombies (+10 points each)
    - Shoot zombies 2 cells away (3 shots total)
    - Avoid pits (⚫) and obstacles (█)
    - Exit (🚪) appears after all zombies are cured
    - Win: Reach exit with no zombies remaining
    - Lose: Captured by zombie or fall into pit
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path for direct script execution
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pacman_zombie.core.board import Board
from pacman_zombie.agents.zombie_agent import ZombieAgent
from pacman_zombie.learning.weights import WeightManager
from pacman_zombie.ui.terminal_renderer import TerminalRenderer

# Try to import keyboard library for real-time input
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Play Pac-Man vs Zombies - Human vs AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--weights-dir',
        type=Path,
        default=Path('weights'),
        help='Directory containing trained weights (default: ./weights)'
    )

    parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable terminal colors'
    )

    parser.add_argument(
        '--no-unicode',
        action='store_true',
        help='Use ASCII symbols instead of Unicode emojis'
    )

    parser.add_argument(
        '--show-legal-moves',
        action='store_true',
        help='Display legal actions each turn'
    )

    parser.add_argument(
        '--show-ai-thinking',
        action='store_true',
        help='Show AI zombie decision details'
    )

    parser.add_argument(
        '--save-replay',
        type=Path,
        metavar='FILE',
        help='Save game history to JSON file'
    )

    return parser.parse_args()


def get_user_action_keyboard() -> Optional[str]:
    """Get user action using keyboard library (real-time arrow keys).

    Returns:
        Action string or 'QUIT' or None if invalid
    """
    print("Your move (Arrow keys or F=shoot, Q=quit): ", end='', flush=True)

    while True:
        if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
            print("↑ UP")
            return "UP"
        elif keyboard.is_pressed('down') or keyboard.is_pressed('s'):
            print("↓ DOWN")
            return "DOWN"
        elif keyboard.is_pressed('left') or keyboard.is_pressed('a'):
            print("← LEFT")
            return "LEFT"
        elif keyboard.is_pressed('right') or keyboard.is_pressed('d'):
            print("→ RIGHT")
            return "RIGHT"
        elif keyboard.is_pressed('f') or keyboard.is_pressed('space'):
            print("🔫 SHOOT")
            return "SHOOT"
        elif keyboard.is_pressed('q'):
            print("QUIT")
            return "QUIT"


def get_user_action_input() -> Optional[str]:
    """Get user action using standard input (type + Enter fallback).

    Returns:
        Action string or 'QUIT' or None if invalid
    """
    print("Your move (W=up, S=down, A=left, D=right, F=shoot, Q=quit): ", end='', flush=True)

    try:
        user_input = input().strip().upper()
    except (EOFError, KeyboardInterrupt):
        print()
        return "QUIT"

    # Map input to actions
    input_map = {
        'W': 'UP',
        'S': 'DOWN',
        'A': 'LEFT',
        'D': 'RIGHT',
        'F': 'SHOOT',
        'Q': 'QUIT'
    }

    return input_map.get(user_input)


def get_user_action(use_keyboard: bool = False) -> Optional[str]:
    """Get user action from input.

    Args:
        use_keyboard: If True, try keyboard library first

    Returns:
        Action string or 'QUIT' or None if invalid
    """
    if use_keyboard and KEYBOARD_AVAILABLE:
        try:
            return get_user_action_keyboard()
        except Exception:
            # Fall back to input() if keyboard fails
            pass

    return get_user_action_input()


def save_game_replay(
    move_history: list,
    filepath: Path,
    board: Board,
    outcome: str
) -> None:
    """Save game replay to JSON file.

    Args:
        move_history: List of move dictionaries
        filepath: Path to save replay
        board: Final board state
        outcome: Game outcome message
    """
    replay_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'outcome': outcome,
            'final_score': board.score,
            'zombies_cured': board.num_zombie_cure,
            'zombies_shot': board.num_shooted_zombie,
            'total_turns': len([m for m in move_history if 'player' in m])
        },
        'moves': move_history
    }

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(replay_data, f, indent=2)

    print(f"Game replay saved to: {filepath}")


def print_welcome(renderer: TerminalRenderer) -> None:
    """Print welcome message and controls.

    Args:
        renderer: Renderer instance (for legend)
    """
    print("\n" + "=" * 60)
    print(" " * 15 + "PAC-MAN vs ZOMBIES" + " " * 15)
    print(" " * 17 + "Human vs AI Mode" + " " * 17)
    print("=" * 60)

    renderer.render_legend()

    print("CONTROLS:")
    if KEYBOARD_AVAILABLE:
        print("  Arrow Keys - Move Pac-Man")
        print("  W/A/S/D    - Alternative movement")
    else:
        print("  W/A/S/D    - Move Pac-Man (type letter + Enter)")

    print("  F / Space  - Shoot zombie")
    print("  Q          - Quit game")
    print()

    print("GOAL:")
    print("  1. Collect vaccines to cure all zombies")
    print("  2. Reach the exit when all zombies are gone")
    print("  3. Avoid being captured or falling into pits!")
    print()

    input("Press Enter to start...")


def main() -> None:
    """Main game loop."""
    args = parse_args()

    # Load zombie AI weights
    zombie_weights_path = args.weights_dir / 'zombie_weights.json'

    try:
        zombie_weights, metadata = WeightManager.load(zombie_weights_path)
        print(f"Loaded zombie AI weights from: {zombie_weights_path}")
        if metadata:
            print(f"  Trained for {metadata.episodes_trained} episodes")
    except FileNotFoundError:
        print(f"ERROR: Zombie weights not found at {zombie_weights_path}")
        print("Please ensure weights exist in the weights/ directory")
        sys.exit(1)

    # Initialize game components
    board = Board()
    zombie_agent = ZombieAgent(zombie_weights)
    renderer = TerminalRenderer(
        use_unicode=not args.no_unicode,
        use_colors=not args.no_colors
    )

    # Print welcome
    print_welcome(renderer)

    # Game state tracking
    move_history = []
    turn_number = 0
    use_keyboard = KEYBOARD_AVAILABLE and not args.no_unicode  # Disable keyboard in ASCII mode

    if use_keyboard:
        print("Using real-time keyboard input (Arrow keys enabled)\n")
    else:
        print("Using standard input mode (type + Enter)\n")

    # Main game loop
    try:
        while not board.is_game_over():
            # Render board
            renderer.render(board)
            turn_number += 1

            # Show legal moves if requested
            if args.show_legal_moves:
                legal = board.get_possible_action()
                print(f"Legal moves: {', '.join(legal)}")

            # Get human action
            action = get_user_action(use_keyboard)

            if action == 'QUIT':
                print("\nGame quit by player.")
                outcome = "QUIT"
                break

            if action is None:
                print("Invalid input! Please try again.")
                turn_number -= 1  # Don't count invalid turns
                input("Press Enter to continue...")
                continue

            # Validate action is legal
            legal_actions = board.get_possible_action()
            if action not in legal_actions:
                print(f"Illegal move! Legal moves are: {', '.join(legal_actions)}")
                turn_number -= 1
                input("Press Enter to continue...")
                continue

            # Execute player action
            board.player_action(action)
            move_history.append({'turn': turn_number, 'player': action})

            # Check immediate game over (player fell in pit, etc.)
            if board.is_game_over():
                break

            # AI zombie turn
            zombie_actions = zombie_agent.select_actions_all_zombies(board)

            # Show AI thinking if requested
            if args.show_ai_thinking:
                print(f"\nAI Zombies planning:")
                for row, col, zaction in zombie_actions:
                    print(f"  Zombie at ({row},{col}) → {zaction}")
                input("Press Enter to see zombie moves...")

            board.zombies_action(zombie_actions)
            move_history.append({'turn': turn_number, 'zombies': zombie_actions})

        # Determine outcome and render game over
        renderer.render(board)

        if board.player_captured_by_zombies():
            outcome = "LOSS - Captured by zombies"
            renderer.render_game_over(board, "GAME OVER - Captured by zombies!")
        elif board.player_fell_into_pit():
            outcome = "LOSS - Fell into pit"
            renderer.render_game_over(board, "GAME OVER - Fell into pit!")
        elif not board.exit_exist() and board.find_zombies_number() == 0:
            outcome = "WIN - All zombies cured and exit reached"
            renderer.render_game_over(board, "YOU WIN! All zombies cured, exit reached!")
        else:
            outcome = "QUIT"

        # Save replay if requested
        if args.save_replay and outcome != "QUIT":
            save_game_replay(move_history, args.save_replay, board, outcome)

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user (Ctrl+C)")
        outcome = "INTERRUPTED"
        if args.save_replay:
            save_game_replay(move_history, args.save_replay, board, outcome)

    print("\nThanks for playing!")


if __name__ == '__main__':
    main()
