#!/usr/bin/env python3
"""Training script for Pac-Man and Zombie agents using temporal difference learning.

This script trains agents using the exact algorithms from the original implementation,
preserving the sacred weight update formulas:

PAC-MAN:  w = w + α * (V_train - V_hat) * features  (COOPERATIVE)
ZOMBIE:   w = w - α * (V_train - V_hat) * features  (ADVERSARIAL)

Usage:
    # Train Pac-Man agent
    python scripts/train.py pacman --episodes 10000 --learning-rate 0.01

    # Train Zombie agent
    python scripts/train.py zombie --episodes 10000 --learning-rate 0.01

    # Continue training from existing weights
    python scripts/train.py pacman --continue-from weights/pacman_weights.json

    # Train both agents (sequential)
    python scripts/train.py both --episodes 5000
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

# Add src to path for direct script execution
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pacman_zombie.core.board import Board
from pacman_zombie.learning.trainer import PacmanTrainer, ZombieTrainer
from pacman_zombie.learning.weights import WeightManager, WeightMetadata

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not available. Install for progress bars: pip install tqdm")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Train Pac-Man and Zombie agents using temporal difference learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'agent',
        choices=['pacman', 'zombie', 'both'],
        help='Which agent to train'
    )

    parser.add_argument(
        '--episodes',
        type=int,
        default=10000,
        help='Number of training episodes (default: 10000)'
    )

    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.01,
        help='Learning rate alpha (default: 0.01)'
    )

    parser.add_argument(
        '--max-steps',
        type=int,
        default=1000,
        help='Maximum steps per episode (default: 1000)'
    )

    parser.add_argument(
        '--continue-from',
        type=Path,
        metavar='WEIGHTS_FILE',
        help='Continue training from existing weights file'
    )

    parser.add_argument(
        '--opponent-weights',
        type=Path,
        metavar='WEIGHTS_FILE',
        help='Use specific weights for opponent agent'
    )

    parser.add_argument(
        '--save-interval',
        type=int,
        default=1000,
        help='Save weights every N episodes (default: 1000)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('weights'),
        help='Directory to save trained weights (default: ./weights)'
    )

    parser.add_argument(
        '--stats-window',
        type=int,
        default=100,
        help='Window size for computing win rate statistics (default: 100)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility'
    )

    return parser.parse_args()


def train_pacman(
    args: argparse.Namespace,
    zombie_weights: np.ndarray
) -> None:
    """Train Pac-Man agent.

    Args:
        args: Command-line arguments
        zombie_weights: Opponent zombie weights (3-dimensional)
    """
    print("\n" + "=" * 60)
    print("TRAINING PAC-MAN AGENT")
    print("=" * 60)

    # Initialize or load trainer
    if args.continue_from:
        print(f"Loading initial weights from: {args.continue_from}")
        initial_weights, metadata = WeightManager.load(args.continue_from)
        if metadata:
            print(f"  Previously trained for {metadata.episodes_trained} episodes")
            print(f"  Final win rate: {metadata.final_win_rate:.2%}")
        trainer = PacmanTrainer(initial_weights)
    else:
        print("Initializing with random weights...")
        trainer = PacmanTrainer()

    print(f"  Initial weights: {trainer.w_hat_player}")
    print(f"\nTraining parameters:")
    print(f"  Episodes: {args.episodes}")
    print(f"  Learning rate: {args.learning_rate}")
    print(f"  Max steps/episode: {args.max_steps}")
    print(f"  Stats window: {args.stats_window}")
    print()

    # Training statistics
    recent_wins = []
    start_time = datetime.now()

    # Progress bar
    if TQDM_AVAILABLE:
        pbar = tqdm(range(args.episodes), desc="Training", ncols=100)
    else:
        pbar = range(args.episodes)

    for episode in pbar:
        # Create fresh board for episode
        board = Board()

        # Train one episode
        V_train, steps, won = trainer.train_episode(
            board=board,
            zombie_weights=zombie_weights,
            alpha=args.learning_rate,
            max_steps=args.max_steps
        )

        # Track statistics
        recent_wins.append(1 if won else 0)
        if len(recent_wins) > args.stats_window:
            recent_wins.pop(0)

        # Update progress bar or print status
        if TQDM_AVAILABLE:
            win_rate = np.mean(recent_wins) if recent_wins else 0
            pbar.set_postfix({
                'Win%': f'{win_rate:.1%}',
                'Steps': steps,
                'V': f'{V_train:.1f}'
            })
        else:
            if (episode + 1) % args.save_interval == 0:
                win_rate = np.mean(recent_wins) if recent_wins else 0
                print(f"Episode {episode + 1}/{args.episodes} | "
                      f"Win Rate: {win_rate:.2%} | "
                      f"Steps: {steps} | "
                      f"V_train: {V_train:.1f}")

        # Save checkpoint
        if (episode + 1) % args.save_interval == 0:
            checkpoint_path = args.output_dir / f'pacman_weights_ep{episode + 1}.json'
            win_rate = np.mean(recent_wins) if recent_wins else 0

            metadata = WeightMetadata(
                episodes_trained=episode + 1,
                final_win_rate=win_rate,
                timestamp=datetime.now().isoformat(),
                learning_rate=args.learning_rate,
                feature_count=8,
                agent_type='pacman'
            )

            WeightManager.save(trainer.w_hat_player, checkpoint_path, metadata)

            if not TQDM_AVAILABLE:
                print(f"  Saved checkpoint: {checkpoint_path}")

    if TQDM_AVAILABLE:
        pbar.close()

    # Save final weights
    final_path = args.output_dir / 'pacman_weights.json'
    final_win_rate = np.mean(recent_wins) if recent_wins else 0

    final_metadata = WeightMetadata(
        episodes_trained=args.episodes,
        final_win_rate=final_win_rate,
        timestamp=datetime.now().isoformat(),
        learning_rate=args.learning_rate,
        feature_count=8,
        agent_type='pacman'
    )

    WeightManager.save(trainer.w_hat_player, final_path, final_metadata)

    # Print summary
    elapsed = datetime.now() - start_time
    print(f"\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Total episodes: {args.episodes}")
    print(f"Total wins: {trainer.num_win}")
    print(f"Overall win rate: {trainer.num_win / args.episodes:.2%}")
    print(f"Final {args.stats_window}-episode win rate: {final_win_rate:.2%}")
    print(f"Training time: {elapsed}")
    print(f"\nFinal weights: {trainer.w_hat_player}")
    print(f"Saved to: {final_path}")
    print()


def train_zombie(
    args: argparse.Namespace,
    player_weights: np.ndarray
) -> None:
    """Train Zombie agent.

    Args:
        args: Command-line arguments
        player_weights: Opponent player weights (8-dimensional)
    """
    print("\n" + "=" * 60)
    print("TRAINING ZOMBIE AGENT")
    print("=" * 60)

    # Initialize or load trainer
    if args.continue_from:
        print(f"Loading initial weights from: {args.continue_from}")
        initial_weights, metadata = WeightManager.load(args.continue_from)
        if metadata:
            print(f"  Previously trained for {metadata.episodes_trained} episodes")
            print(f"  Final win rate: {metadata.final_win_rate:.2%}")
        trainer = ZombieTrainer(initial_weights)
    else:
        print("Initializing with random weights...")
        trainer = ZombieTrainer()

    print(f"  Initial weights: {trainer.w_hat_zombie}")
    print(f"\nTraining parameters:")
    print(f"  Episodes: {args.episodes}")
    print(f"  Learning rate: {args.learning_rate}")
    print(f"  Max steps/episode: {args.max_steps}")
    print(f"  Stats window: {args.stats_window}")
    print()

    # Training statistics
    recent_wins = []
    start_time = datetime.now()

    # Progress bar
    if TQDM_AVAILABLE:
        pbar = tqdm(range(args.episodes), desc="Training", ncols=100)
    else:
        pbar = range(args.episodes)

    for episode in pbar:
        # Create fresh board for episode
        board = Board()

        # Train one episode
        V_train, steps, won = trainer.train_episode(
            board=board,
            player_weights=player_weights,
            alpha=args.learning_rate,
            max_steps=args.max_steps
        )

        # Track statistics
        recent_wins.append(1 if won else 0)
        if len(recent_wins) > args.stats_window:
            recent_wins.pop(0)

        # Update progress bar or print status
        if TQDM_AVAILABLE:
            win_rate = np.mean(recent_wins) if recent_wins else 0
            pbar.set_postfix({
                'Win%': f'{win_rate:.1%}',
                'Steps': steps,
                'V': f'{V_train:.1f}'
            })
        else:
            if (episode + 1) % args.save_interval == 0:
                win_rate = np.mean(recent_wins) if recent_wins else 0
                print(f"Episode {episode + 1}/{args.episodes} | "
                      f"Win Rate: {win_rate:.2%} | "
                      f"Steps: {steps} | "
                      f"V_train: {V_train:.1f}")

        # Save checkpoint
        if (episode + 1) % args.save_interval == 0:
            checkpoint_path = args.output_dir / f'zombie_weights_ep{episode + 1}.json'
            win_rate = np.mean(recent_wins) if recent_wins else 0

            metadata = WeightMetadata(
                episodes_trained=episode + 1,
                final_win_rate=win_rate,
                timestamp=datetime.now().isoformat(),
                learning_rate=args.learning_rate,
                feature_count=3,
                agent_type='zombie'
            )

            WeightManager.save(trainer.w_hat_zombie, checkpoint_path, metadata)

            if not TQDM_AVAILABLE:
                print(f"  Saved checkpoint: {checkpoint_path}")

    if TQDM_AVAILABLE:
        pbar.close()

    # Save final weights
    final_path = args.output_dir / 'zombie_weights.json'
    final_win_rate = np.mean(recent_wins) if recent_wins else 0

    final_metadata = WeightMetadata(
        episodes_trained=args.episodes,
        final_win_rate=final_win_rate,
        timestamp=datetime.now().isoformat(),
        learning_rate=args.learning_rate,
        feature_count=3,
        agent_type='zombie'
    )

    WeightManager.save(trainer.w_hat_zombie, final_path, final_metadata)

    # Print summary
    elapsed = datetime.now() - start_time
    print(f"\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Total episodes: {args.episodes}")
    print(f"Total wins: {trainer.num_win}")
    print(f"Overall win rate: {trainer.num_win / args.episodes:.2%}")
    print(f"Final {args.stats_window}-episode win rate: {final_win_rate:.2%}")
    print(f"Training time: {elapsed}")
    print(f"\nFinal weights: {trainer.w_hat_zombie}")
    print(f"Saved to: {final_path}")
    print()


def main() -> None:
    """Main training orchestrator."""
    args = parse_args()

    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"Random seed set to: {args.seed}")

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load opponent weights
    if args.agent == 'pacman':
        # Load or initialize zombie weights
        if args.opponent_weights:
            print(f"Loading zombie opponent weights from: {args.opponent_weights}")
            zombie_weights, _ = WeightManager.load(args.opponent_weights)
        else:
            print("No zombie weights provided, using random initialization")
            zombie_weights = np.random.rand(3) - 0.5

        train_pacman(args, zombie_weights)

    elif args.agent == 'zombie':
        # Load or initialize player weights
        if args.opponent_weights:
            print(f"Loading player opponent weights from: {args.opponent_weights}")
            player_weights, _ = WeightManager.load(args.opponent_weights)
        else:
            print("No player weights provided, using random initialization")
            player_weights = np.random.rand(8) - 0.5

        train_zombie(args, player_weights)

    elif args.agent == 'both':
        # Train both agents sequentially
        print("Training both agents sequentially...")
        print("This will train Pac-Man first, then Zombie against trained Pac-Man")
        print()

        # First train Pac-Man against random zombie
        zombie_weights = np.random.rand(3) - 0.5
        train_pacman(args, zombie_weights)

        # Load trained Pac-Man weights
        pacman_path = args.output_dir / 'pacman_weights.json'
        player_weights, _ = WeightManager.load(pacman_path)

        # Then train Zombie against trained Pac-Man
        train_zombie(args, player_weights)

    print("All training complete!")


if __name__ == '__main__':
    main()
