"""Weight management for trained agents.

This module handles saving and loading of learned weights, including metadata
about training history. Supports both JSON format (with metadata) and legacy
text format for backward compatibility.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray


@dataclass
class WeightMetadata:
    """Metadata associated with trained weights.

    Attributes:
        episodes_trained: Number of training episodes completed
        final_win_rate: Win rate over last 100 episodes
        timestamp: ISO format timestamp of when weights were saved
        learning_rate: Learning rate used during training
        feature_count: Number of features (dimension of weight vector)
        agent_type: Type of agent ('pacman' or 'zombie')
    """
    episodes_trained: int
    final_win_rate: float
    timestamp: str
    learning_rate: float
    feature_count: int
    agent_type: str = "unknown"

    def to_dict(self) -> dict:
        """Convert metadata to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'WeightMetadata':
        """Create metadata from dictionary."""
        return cls(**data)


class WeightManager:
    """Manager for saving and loading agent weights.

    Handles both JSON format (recommended) with metadata and legacy text format
    for backward compatibility with existing weight files.
    """

    @staticmethod
    def save(
        weights: NDArray,
        filepath: Path,
        metadata: Optional[WeightMetadata] = None
    ) -> None:
        """Save weights to JSON file with metadata.

        Args:
            weights: Weight vector to save
            filepath: Path to save file (should end in .json)
            metadata: Optional metadata to include

        Example:
            >>> weights = np.array([1.5, 2.3, -0.5])
            >>> meta = WeightMetadata(
            ...     episodes_trained=10000,
            ...     final_win_rate=0.75,
            ...     timestamp=datetime.now().isoformat(),
            ...     learning_rate=0.01,
            ...     feature_count=3,
            ...     agent_type='pacman'
            ... )
            >>> WeightManager.save(weights, Path('weights.json'), meta)
        """
        if metadata is None:
            metadata = WeightMetadata(
                episodes_trained=0,
                final_win_rate=0.0,
                timestamp=datetime.now().isoformat(),
                learning_rate=0.0,
                feature_count=len(weights),
                agent_type="unknown"
            )

        data = {
            "weights": weights.tolist(),
            "metadata": metadata.to_dict()
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(filepath: Path) -> Tuple[NDArray, Optional[WeightMetadata]]:
        """Load weights from file (JSON or legacy text format).

        Automatically detects format and loads appropriately. JSON files include
        metadata, text files do not.

        Args:
            filepath: Path to weight file (.json or .txt)

        Returns:
            Tuple of (weights array, metadata or None)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid

        Example:
            >>> weights, metadata = WeightManager.load(Path('weights.json'))
            >>> print(f"Trained for {metadata.episodes_trained} episodes")
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Weight file not found: {filepath}")

        # Detect format by extension or content
        if filepath.suffix == '.json':
            return WeightManager._load_json(filepath)
        elif filepath.suffix == '.txt':
            return WeightManager._load_text(filepath)
        else:
            # Try JSON first, fall back to text
            try:
                return WeightManager._load_json(filepath)
            except (json.JSONDecodeError, KeyError):
                return WeightManager._load_text(filepath)

    @staticmethod
    def _load_json(filepath: Path) -> Tuple[NDArray, WeightMetadata]:
        """Load weights from JSON format.

        Args:
            filepath: Path to JSON file

        Returns:
            Tuple of (weights array, metadata)
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        weights = np.array(data['weights'], dtype=float)
        metadata = WeightMetadata.from_dict(data['metadata'])

        return weights, metadata

    @staticmethod
    def _load_text(filepath: Path) -> Tuple[NDArray, None]:
        """Load weights from legacy text format (one weight per line).

        Args:
            filepath: Path to text file

        Returns:
            Tuple of (weights array, None)
        """
        with open(filepath, 'r') as f:
            lines = f.readlines()

        weights = []
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    weight = float(line)
                    weights.append(weight)
                except ValueError:
                    # Skip lines that can't be parsed as floats
                    continue

        if not weights:
            raise ValueError(f"No valid weights found in {filepath}")

        return np.array(weights, dtype=float), None

    @staticmethod
    def migrate_text_to_json(
        text_filepath: Path,
        json_filepath: Path,
        metadata: Optional[WeightMetadata] = None
    ) -> None:
        """Migrate legacy text format weights to JSON format.

        Args:
            text_filepath: Path to existing .txt weight file
            json_filepath: Path to save JSON file
            metadata: Optional metadata to include (will use defaults if None)

        Example:
            >>> WeightManager.migrate_text_to_json(
            ...     Path('w_hat_player.txt'),
            ...     Path('weights/pacman_weights.json'),
            ...     WeightMetadata(
            ...         episodes_trained=10000,
            ...         final_win_rate=0.0,
            ...         timestamp=datetime.now().isoformat(),
            ...         learning_rate=0.01,
            ...         feature_count=8,
            ...         agent_type='pacman'
            ...     )
            ... )
        """
        weights, _ = WeightManager._load_text(text_filepath)

        if metadata is None:
            metadata = WeightMetadata(
                episodes_trained=0,
                final_win_rate=0.0,
                timestamp=datetime.now().isoformat(),
                learning_rate=0.01,
                feature_count=len(weights),
                agent_type="migrated"
            )

        WeightManager.save(weights, json_filepath, metadata)
        print(f"Migrated {text_filepath} -> {json_filepath}")


def load_legacy_weights(player_file: str = 'w_hat_player.txt',
                       zombie_file: str = 'w_hat_zombie.txt') -> Tuple[NDArray, NDArray]:
    """Load weights from legacy text files (backward compatibility).

    Args:
        player_file: Path to Pac-Man weights file
        zombie_file: Path to Zombie weights file

    Returns:
        Tuple of (pacman_weights, zombie_weights)

    Example:
        >>> pacman_w, zombie_w = load_legacy_weights()
    """
    player_weights, _ = WeightManager.load(Path(player_file))
    zombie_weights, _ = WeightManager.load(Path(zombie_file))
    return player_weights, zombie_weights
