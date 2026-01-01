#!/usr/bin/env python3
"""Migrate legacy text weight files to new JSON format with metadata.

This script converts w_hat_player.txt and w_hat_zombie.txt to JSON format
with metadata, enabling better tracking of training history.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pacman_zombie.learning.weights import WeightManager, WeightMetadata


def main():
    """Migrate legacy weight files to JSON format."""
    root = Path(__file__).parent.parent

    # Migrate Pac-Man weights
    pacman_txt = root / 'w_hat_player.txt'
    pacman_json = root / 'weights' / 'pacman_weights.json'

    if pacman_txt.exists():
        print(f"Migrating {pacman_txt} -> {pacman_json}")
        weights, _ = WeightManager.load(pacman_txt)
        metadata = WeightMetadata(
            episodes_trained=10000,  # Assumed from original training
            final_win_rate=0.0,  # Unknown
            timestamp=datetime.now().isoformat(),
            learning_rate=0.01,
            feature_count=len(weights),
            agent_type='pacman'
        )
        WeightManager.save(weights, pacman_json, metadata)
        print(f"  ✓ Saved {len(weights)} weights")
    else:
        print(f"  ✗ {pacman_txt} not found")

    # Migrate Zombie weights
    zombie_txt = root / 'w_hat_zombie.txt'
    zombie_json = root / 'weights' / 'zombie_weights.json'

    if zombie_txt.exists():
        print(f"Migrating {zombie_txt} -> {zombie_json}")
        weights, _ = WeightManager.load(zombie_txt)
        metadata = WeightMetadata(
            episodes_trained=10000,  # Assumed from original training
            final_win_rate=0.0,  # Unknown
            timestamp=datetime.now().isoformat(),
            learning_rate=0.01,
            feature_count=len(weights),
            agent_type='zombie'
        )
        WeightManager.save(weights, zombie_json, metadata)
        print(f"  ✓ Saved {len(weights)} weights")
    else:
        print(f"  ✗ {zombie_txt} not found")

    print("\nMigration complete!")
    print(f"Original .txt files preserved")
    print(f"New JSON files created in {root / 'weights'}/")


if __name__ == '__main__':
    main()
