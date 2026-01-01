# Training Guide - Pac-Man vs Zombies

## Overview

This guide explains how to train (or retrain) the Pac-Man and Zombie agents using temporal difference learning. The training implementation preserves the exact weight update formulas from the original code:

```
PAC-MAN:  w = w + α * (V_train - V_hat) * features  (COOPERATIVE)
ZOMBIE:   w = w - α * (V_train - V_hat) * features  (ADVERSARIAL)
```

**CRITICAL**: The difference is the operator (+ vs -), making this true adversarial learning.

---

## Quick Start

### Train Pac-Man Agent

```bash
# Basic training (10,000 episodes, learning rate 0.01)
python scripts/train.py pacman --episodes 10000 --learning-rate 0.01

# Fast test run
python scripts/train.py pacman --episodes 100
```

### Train Zombie Agent

```bash
# Basic training
python scripts/train.py zombie --episodes 10000 --learning-rate 0.01

# Fast test run
python scripts/train.py zombie --episodes 100
```

### Train Both Agents

```bash
# Trains Pac-Man first, then Zombie against trained Pac-Man
python scripts/train.py both --episodes 5000
```

---

## Command-Line Options

### Required Arguments

```bash
python scripts/train.py {pacman|zombie|both}
```

- `pacman` - Train Pac-Man agent only
- `zombie` - Train Zombie agent only
- `both` - Train both agents sequentially

### Optional Arguments

#### Training Parameters

```bash
--episodes N              # Number of training episodes (default: 10000)
--learning-rate ALPHA     # Learning rate α (default: 0.01)
--max-steps N             # Max steps per episode (default: 1000)
--seed N                  # Random seed for reproducibility
```

#### Weight Management

```bash
--continue-from FILE      # Continue training from existing weights
--opponent-weights FILE   # Use specific weights for opponent
--output-dir DIR          # Where to save weights (default: ./weights)
--save-interval N         # Save checkpoint every N episodes (default: 1000)
```

#### Statistics

```bash
--stats-window N          # Window for win rate calculation (default: 100)
```

---

## Training Workflows

### Scenario 1: Train from Scratch

Train both agents from random initialization:

```bash
# Step 1: Train Pac-Man against random zombie
python scripts/train.py pacman \
    --episodes 10000 \
    --learning-rate 0.01 \
    --seed 42

# Step 2: Train Zombie against trained Pac-Man
python scripts/train.py zombie \
    --episodes 10000 \
    --learning-rate 0.01 \
    --opponent-weights weights/pacman_weights.json \
    --seed 42
```

**OR** use the shortcut:

```bash
python scripts/train.py both --episodes 10000 --learning-rate 0.01 --seed 42
```

---

### Scenario 2: Continue Training (Fine-Tuning)

Resume training from existing weights:

```bash
# Continue Pac-Man training for 5000 more episodes
python scripts/train.py pacman \
    --continue-from weights/pacman_weights.json \
    --episodes 5000 \
    --learning-rate 0.001  # Lower learning rate for fine-tuning

# Continue Zombie training
python scripts/train.py zombie \
    --continue-from weights/zombie_weights.json \
    --episodes 5000 \
    --learning-rate 0.001 \
    --opponent-weights weights/pacman_weights.json
```

---

### Scenario 3: Experiment with Different Learning Rates

```bash
# Conservative learning (slower but more stable)
python scripts/train.py pacman --episodes 20000 --learning-rate 0.001

# Aggressive learning (faster but potentially unstable)
python scripts/train.py pacman --episodes 5000 --learning-rate 0.05

# Recommended default
python scripts/train.py pacman --episodes 10000 --learning-rate 0.01
```

---

### Scenario 4: Train Against Specific Opponent

Train Zombie against a specific version of Pac-Man:

```bash
python scripts/train.py zombie \
    --episodes 10000 \
    --opponent-weights weights/pacman_weights_ep5000.json \
    --output-dir weights/zombie_vs_pacman_v5000
```

---

## Understanding the Output

### During Training

```
============================================================
TRAINING PAC-MAN AGENT
============================================================
Initializing with random weights...
  Initial weights: [ 0.09865848 -0.34398136 -0.34400548 -0.44191639
                     0.36617615  0.10111501  0.20807258 -0.47941551]

Training parameters:
  Episodes: 10000
  Learning rate: 0.01
  Max steps/episode: 1000
  Stats window: 100

Episode 1000/10000 | Win Rate: 12.00% | Steps: 456 | V_train: -1000.0
Episode 2000/10000 | Win Rate: 23.00% | Steps: 231 | V_train: 1000.0
...
```

**Metrics Explained**:
- **Win Rate**: Percentage of wins in the last N episodes (default: 100)
- **Steps**: Number of steps taken in that episode
- **V_train**: Final training value for that episode
  - `1000` = Win
  - `-1000` = Loss (captured or fell in pit)
  - `-100` = Early exit penalty

### After Training

```
============================================================
TRAINING COMPLETE
============================================================
Total episodes: 10000
Total wins: 2,342
Overall win rate: 23.42%
Final 100-episode win rate: 45.50%
Training time: 0:12:34

Final weights: [ 1.23 -45.67  89.01 ...]
Saved to: weights/pacman_weights.json
```

**Key Insights**:
- **Overall win rate**: Performance across all episodes
- **Final N-episode win rate**: Recent performance (shows learning trend)
- **Final weights**: Learned policy parameters

If `Final win rate > Overall win rate`, the agent is **still improving** - consider more episodes!

---

## Saved Files

### Weight Files

Training automatically saves:

1. **Checkpoints** (every N episodes):
   - `weights/pacman_weights_ep1000.json`
   - `weights/pacman_weights_ep2000.json`
   - etc.

2. **Final weights**:
   - `weights/pacman_weights.json`
   - `weights/zombie_weights.json`

### Weight File Format

```json
{
  "weights": [1.23, -45.67, 89.01, ...],
  "metadata": {
    "episodes_trained": 10000,
    "final_win_rate": 0.4550,
    "timestamp": "2026-01-01T12:34:56.789",
    "learning_rate": 0.01,
    "feature_count": 8,
    "agent_type": "pacman"
  }
}
```

---

## Algorithm Details

### Pac-Man Training (Cooperative)

**Weight Update Formula (SACRED)**:
```python
w_new = w_old + α * (V_train - V_hat(features, w_old)) * features
```

**Reward Structure**:
- `V_train = +1000` - Win (all zombies cured + exit reached)
- `V_train = -1000` - Loss (captured by zombie OR fell in pit)
- `V_train = -100` - Early exit penalty (exit missing)
- `V_train = max_V` - Default (greedy action value)

**Features** (8-dimensional):
1. Distance to exit (when zombies cleared)
2. Shooting opportunity
3. Remaining vaccines
4. Distance to vaccine
5. Distance to nearest zombie
6. Has vaccine (binary)
7. Distance to obstacles
8. Distance to pit

---

### Zombie Training (Adversarial)

**Weight Update Formula (SACRED)**:
```python
w_new = w_old - α * (V_train - V_hat(features, w_old)) * features
```

Note the **MINUS** sign - this is adversarial learning!

**Reward Structure**:
- `V_train = +1000` - Win (captured Pac-Man)
- `V_train = -1000` - Loss (cured by vaccine)
- `V_train = -100` - Fell into pit
- `V_train = max_V` - Default (greedy action value)

**Features** (3-dimensional):
1. Distance to Pac-Man (chase or flee)
2. Distance to pit (avoidance)
3. Distance to obstacles (avoidance)

---

## Hyperparameter Tuning Tips

### Learning Rate (α)

| Value | Behavior | Use Case |
|-------|----------|----------|
| 0.001 | Slow, stable | Fine-tuning, long training |
| 0.01 | **Recommended** | Default training |
| 0.05 | Fast, volatile | Quick experiments |
| 0.1+ | Very unstable | Not recommended |

### Episodes

| Count | Training Time | Quality |
|-------|---------------|---------|
| 100 | ~10 seconds | Testing only |
| 1,000 | ~2 minutes | Basic learning |
| 10,000 | ~20 minutes | **Recommended** |
| 50,000+ | 2+ hours | High quality |

### Max Steps

Default: 1000 steps/episode

- **Lower** (500): Faster training, may not explore fully
- **Higher** (2000): Slower training, more thorough exploration

---

## Troubleshooting

### "Win rate stays at 0%"

**Causes**:
- Learning rate too low
- Not enough episodes
- Opponent too strong

**Solutions**:
```bash
# Increase learning rate
python scripts/train.py pacman --learning-rate 0.05

# Train against random opponent first
python scripts/train.py pacman --episodes 20000
```

### "Weights explode to huge values"

**Cause**: Learning rate too high

**Solution**:
```bash
python scripts/train.py pacman --learning-rate 0.001
```

### "Training very slow"

**Cause**: max_steps too high

**Solution**:
```bash
python scripts/train.py pacman --max-steps 500
```

### "Want faster progress feedback"

**Solution**: Install tqdm for progress bars
```bash
pip install tqdm
```

---

## Reproducibility

Use `--seed` for reproducible results:

```bash
# Run 1
python scripts/train.py pacman --episodes 1000 --seed 42

# Run 2 (will produce identical weights)
python scripts/train.py pacman --episodes 1000 --seed 42
```

---

## Comparing Training Runs

Train multiple versions and compare:

```bash
# Version 1: Conservative
python scripts/train.py pacman \
    --episodes 10000 \
    --learning-rate 0.001 \
    --output-dir weights/v1_conservative \
    --seed 1

# Version 2: Aggressive
python scripts/train.py pacman \
    --episodes 10000 \
    --learning-rate 0.05 \
    --output-dir weights/v2_aggressive \
    --seed 1

# Version 3: Longer training
python scripts/train.py pacman \
    --episodes 50000 \
    --learning-rate 0.01 \
    --output-dir weights/v3_long \
    --seed 1
```

Then test each version:
```bash
python scripts/play.py --weights-dir weights/v1_conservative
python scripts/play.py --weights-dir weights/v2_aggressive
python scripts/play.py --weights-dir weights/v3_long
```

---

## Technical Implementation

**Files**:
- [src/pacman_zombie/learning/trainer.py](src/pacman_zombie/learning/trainer.py) - Core training logic
- [scripts/train.py](scripts/train.py) - CLI interface

**Preserves Original Algorithm**:
- ✅ Exact weight update formulas from agent.py (line 755) and zombie.py (line 762)
- ✅ Same reward structure
- ✅ Same greedy policy selection
- ✅ Same episode termination conditions
- ✅ Same max steps (1000)
- ✅ Same feature extraction

**Improvements**:
- Progress bars (via tqdm)
- Checkpoint saving
- Metadata tracking
- Reproducible training (seed support)
- Continue training support
- Comprehensive CLI

---

## Next Steps

After training:

1. **Test your agents**:
   ```bash
   python scripts/play.py
   ```

2. **Compare with original weights**:
   ```bash
   # Play with your new weights
   python scripts/play.py --weights-dir weights/

   # Play with original (if you backed them up)
   python scripts/play.py --weights-dir weights_backup/
   ```

3. **Analyze performance**:
   - Check win rates in final summary
   - Look at checkpoint progression
   - Test in different scenarios

4. **Iterate**:
   - Adjust hyperparameters based on results
   - Continue training if needed
   - Try different opponent strengths

---

## Advanced: Custom Training Loops

If you need more control, use the trainer classes directly:

```python
from pacman_zombie.core.board import Board
from pacman_zombie.learning.trainer import PacmanTrainer, ZombieTrainer
import numpy as np

# Initialize trainers
pacman_trainer = PacmanTrainer()
zombie_trainer = ZombieTrainer()

# Custom training loop
for episode in range(10000):
    board = Board()

    # Train episode
    V_train, steps, won = pacman_trainer.train_episode(
        board=board,
        zombie_weights=zombie_trainer.w_hat_zombie,
        alpha=0.01,
        max_steps=1000
    )

    # Custom logic here...
    if won:
        print(f"Episode {episode}: WIN!")

# Access final weights
print(pacman_trainer.w_hat_player)
print(zombie_trainer.w_hat_zombie)
```

---

## References

- Original training implementation: [agent.py](agent.py) (line 683-756)
- Original zombie training: [zombie.py](zombie.py) (line 686-762)
- Weight update formulas are SACRED - do not modify
- See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for full project status

---

Happy training! 🟡🧟
