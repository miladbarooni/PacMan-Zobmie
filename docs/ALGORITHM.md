# Learning Algorithm - Pac-Man vs Zombies

Deep dive into the temporal difference learning algorithm with adversarial training.

---

## Table of Contents

- [Overview](#overview)
- [Temporal Difference Learning](#temporal-difference-learning)
- [Linear Function Approximation](#linear-function-approximation)
- [Adversarial Training](#adversarial-training)
- [Greedy Policy](#greedy-policy)
- [Training Process](#training-process)
- [Mathematical Derivation](#mathematical-derivation)
- [Implementation Details](#implementation-details)

---

## Overview

This project uses **Temporal Difference (TD) Learning** with **Linear Function Approximation** in an **Adversarial** setting.

**Key Components**:
1. **State Representation**: Features φ(s) extracted from game state
2. **Value Function**: V(s) = w · φ(s) estimates state quality
3. **Policy**: Greedy action selection (choose max value action)
4. **Learning**: Update weights based on observed rewards
5. **Adversarial**: Zombie learns to minimize Pac-Man's value

---

## Temporal Difference Learning

### Core Idea

**Learn from experience** by comparing predictions with outcomes:

```
Predicted Value    vs    Actual Outcome
     V_hat(s)            V_train (reward + future)
```

**TD Error**:
```
δ = V_train - V_hat(s)
```

- δ > 0: State better than expected → increase value
- δ < 0: State worse than expected → decrease value

### Weight Update Rule

**General Form**:
```
w_new = w_old + α · δ · φ(s)
w_new = w_old + α · (V_train - w_old · φ(s)) · φ(s)
```

Where:
- α = learning rate (step size)
- δ = TD error
- φ(s) = feature vector
- w = weight vector

---

## Linear Function Approximation

### Why Linear?

**Advantages**:
- ✅ **Fast**: Dot product is O(n) where n = num features
- ✅ **Interpretable**: Each weight has clear meaning
- ✅ **Stable**: Convergence guarantees under certain conditions
- ✅ **Sample Efficient**: Learns from fewer episodes than deep learning

**Trade-off**:
- ❌ Cannot represent complex non-linear relationships
- ✅ BUT: Good features can capture most important patterns

### Value Function

```
V(s) = w₁·φ₁(s) + w₂·φ₂(s) + ... + wₙ·φₙ(s)
V(s) = w · φ(s)  # Dot product
```

**Example** (Pac-Man with 8 features):
```python
φ(s) = [0.5, 0.0, 4.0, 0.3, 0.2, 1.0, 0.8, 0.1]  # Features
w    = [-19.5, 7.2, 23.6, -2.6, 2.3, 7.0, 0.01, 0.24]  # Weights

V(s) = (-19.5)(0.5) + (7.2)(0.0) + (23.6)(4.0) + ...
     = -9.75 + 0 + 94.4 + ... ≈ 95.3
```

### Feature Vector φ(s)

**Pac-Man** (8-dimensional):
```python
φ_pacman(s) = [
    distance_to_exit / 20,
    shooting_opportunity,
    num_vaccines_remaining,
    distance_to_vaccine / 20,
    distance_to_zombie / 20,
    has_vaccine (0 or 1),
    distance_to_obstacle / 20,
    distance_to_pit / 20
]
```

**Zombie** (3-dimensional):
```python
φ_zombie(s) = [
    distance_to_pacman / 20,
    distance_to_pit / 20,
    distance_to_obstacle / 40
]
```

See [FEATURES.md](FEATURES.md) for detailed feature engineering.

---

## Adversarial Training

### The Key Innovation

**Standard RL**: Agent learns to maximize its own reward

**Adversarial RL**: Two agents with opposing objectives

```
Pac-Man:  Maximize value  → w + α · δ · φ(s)
Zombie:   Minimize value  → w - α · δ · φ(s)  ← Note the MINUS!
```

### Why It Works

**Game Theory Perspective**:
- This is a **zero-sum game**
- Pac-Man's win = Zombie's loss
- Optimal strategy: play against best opponent

**Learning Dynamics**:
1. Pac-Man learns strategy
2. Zombies learn counter-strategy
3. Pac-Man adapts to counter-counter-strategy
4. ... (continues until equilibrium)

### Mathematical Formulation

**Pac-Man's Objective**:
```
max V_pacman(s) = max w_pacman · φ_pacman(s)
```

**Zombie's Objective**:
```
min V_pacman(s) = max (-V_pacman(s)) = max w_zombie · φ_zombie(s)
```

**Weight Updates**:
```python
# Pac-Man: Maximize value (cooperative)
w_pacman ← w_pacman + α * (V_train - V_hat) * φ_pacman

# Zombie: Minimize Pac-Man's value (adversarial)
w_zombie ← w_zombie - α * (V_train - V_hat) * φ_zombie  # MINUS!
```

The minus sign makes zombies learn to **decrease** Pac-Man's value!

---

## Greedy Policy

### Action Selection

**Policy** π(s): Maps state to action

**Greedy Policy**: Always choose action with highest value

```python
def select_action(state):
    max_value = -infinity
    best_action = None

    for action in legal_actions:
        successor = get_successor(state, action)
        value = V_hat(successor)  # w · φ(successor)

        if value > max_value:
            max_value = value
            best_action = action

    return best_action
```

### Exploration vs Exploitation

**This implementation**: 100% Greedy (no exploration)

**Why no ε-greedy?**
- Random board initialization provides exploration
- Adversarial opponent provides variety
- Greedy policy simpler and faster

**Random Tie-Breaking**:
```python
random.shuffle(actions)  # Randomize order before evaluation
# If multiple actions have same value, first one wins (now random)
```

---

## Training Process

### Episode Structure

**One Episode** (~200-500 steps):

```
1. Initialize random board
2. Repeat until game over or max_steps:
    a. Pac-Man selects action (greedy over w_pacman)
    b. Execute Pac-Man action
    c. Zombies select actions (greedy over w_zombie)
    d. Execute zombie actions
    e. Compute V_train based on outcome
    f. Update w_pacman using TD formula
    g. Update w_zombie using adversarial TD formula
3. Record statistics (win/loss, steps, etc.)
```

### V_train Computation

**Pac-Man's Training Value**:

```python
# Default: Value of chosen action
V_train = V_hat(successor_state)

# Terminal states override:
if all_zombies_cured and reached_exit:
    V_train = +1000  # WIN

if captured_by_zombie:
    V_train = -1000  # LOSE

if fell_in_pit:
    V_train = -1000  # LOSE

if reached_exit_early:
    V_train = -100  # PENALTY
```

**Zombie's Training Value**:

```python
# Default: Value of chosen action
V_train = V_hat(successor_state)

# Terminal states:
if captured_pacman:
    V_train = +1000  # WIN (for zombie)

if fell_in_pit:
    V_train = -100  # PENALTY (respawn)

if pacman_cured_zombie:
    V_train = -1000  # LOSE
```

### Weight Update Implementation

**Pac-Man Update** (from [trainer.py:155](../src/pacman_zombie/learning/trainer.py#L155)):

```python
# SACRED FORMULA - DO NOT MODIFY
self.w_hat_player = (
    self.w_hat_player +
    alpha * (V_train - V_hat(current_features_player, self.w_hat_player)) *
    np.array(current_features_player)
)
```

**Zombie Update** (from [trainer.py:327](../src/pacman_zombie/learning/trainer.py#L327)):

```python
# SACRED FORMULA - DO NOT MODIFY
self.w_hat_zombie = (
    self.w_hat_zombie -  # MINUS for adversarial learning
    alpha * (V_train - V_hat(current_features_zombie, self.w_hat_zombie)) *
    np.array(current_features_zombie)
)
```

---

## Mathematical Derivation

### TD Learning Foundation

**Bellman Equation** (simplified, no discounting):
```
V(s) = R(s, a) + V(s')
```

Where:
- R(s, a) = immediate reward
- s' = successor state after action a

**Approximation**:
```
V(s) ≈ w · φ(s)
```

**TD Error**:
```
δ = [R(s, a) + V(s')] - V(s)
  = V_train - V_hat(s)
```

**Gradient Descent** on squared error:
```
L = ½(V_train - w·φ(s))²

∂L/∂w = -(V_train - w·φ(s)) · φ(s)
       = -δ · φ(s)

w ← w - α · ∂L/∂w
w ← w + α · δ · φ(s)  # Standard update
```

### Adversarial Extension

**Zombie wants to minimize Pac-Man's value**:

```
Minimize V_pacman(s)
⟺ Maximize -V_pacman(s)
⟺ Gradient Ascent on -V_pacman(s)

w_zombie ← w_zombie - α · δ · φ(s)  # Negation of standard update
```

This creates **minimax** dynamics:
```
max_{w_pacman} min_{w_zombie} V_pacman(s)
```

---

## Implementation Details

### Hyperparameters

**Default Values**:
```python
alpha = 0.01            # Learning rate
max_episodes = 10000    # Training episodes
max_steps = 1000        # Steps per episode
```

**Learning Rate Selection**:
- Too small (0.001): Slow convergence
- Too large (0.1): Unstable, oscillations
- **Recommended** (0.01): Good balance

### Convergence Behavior

**Typical Training Curve**:
```
Episode 0-1000:   Win rate ~10-20% (random play)
Episode 1000-3000: Win rate increases to ~30%
Episode 3000-6000: Win rate plateaus ~40-45%
Episode 6000-10000: Fine-tuning, slight improvements
```

**Indicators of Good Training**:
- ✅ Win rate increases over time
- ✅ Final win rate > overall win rate
- ✅ Weights stabilize (small changes in late episodes)

**Common Issues**:
- ❌ Win rate stuck at 0%: Learning rate too low or opponent too strong
- ❌ Wild oscillations: Learning rate too high
- ❌ No improvement: Features may need redesign

### Computational Complexity

**Per Episode**:
```
T = average steps per episode (~300)
A = average legal actions (~4)
F = feature dimension (8 for Pac-Man, 3 for Zombie)

Feature extraction: O(F) per action
Value computation: O(F) per action (dot product)
Weight update: O(F) per step

Total: O(T · A · F) ≈ O(300 · 4 · 8) = O(9,600) operations
```

**For 10,000 Episodes**:
```
~96 million operations
~20 minutes on modern CPU
```

### Memory Requirements

```
Weights: 8 floats (Pac-Man) + 3 floats (Zombie) = 88 bytes
Board state: ~150 cells × 8 bytes = 1.2 KB
Episode history: negligible (only final weights saved)

Total: < 2 KB (extremely efficient!)
```

---

## Comparison with Other Algorithms

| Algorithm | Sample Efficiency | Computation | Interpretability |
|-----------|-------------------|-------------|------------------|
| **TD Linear (ours)** | ⭐⭐⭐ Good | ⭐⭐⭐ Fast | ⭐⭐⭐ High |
| Q-Learning (tabular) | ⭐ Poor (huge state space) | ⭐⭐ Medium | ⭐⭐⭐ High |
| Deep Q-Network (DQN) | ⭐⭐⭐⭐ Excellent | ⭐ Slow | ⭐ Low |
| Policy Gradient | ⭐⭐ Fair | ⭐⭐ Medium | ⭐ Low |
| AlphaZero | ⭐⭐⭐⭐⭐ Best | ⭐ Very Slow | ⭐ Very Low |

**Why TD + Linear for this project**:
1. State space manageable with good features
2. Fast training (minutes, not hours)
3. Interpretable learned strategies
4. Educational value (understand what AI learned)

---

## Advanced Topics

### Stability and Convergence

**TD Learning with linear FA** can diverge under certain conditions:

**Our Safeguards**:
- ✅ On-policy learning (policy generates data)
- ✅ Feature scaling (normalization)
- ✅ Reasonable learning rate
- ✅ Bounded rewards

**Convergence Theorem** (Tsitsiklis & Van Roy, 1997):
Under mild conditions, TD(0) with linear FA converges to a neighborhood of the optimal solution.

### Multi-Agent Learning Dynamics

**Nash Equilibrium**: Neither agent can improve by changing strategy alone

**Our Game**:
- Not guaranteed to reach Nash equilibrium
- Continuous adaptation (arms race)
- Empirically: strategies stabilize after ~5,000 episodes

### Feature Importance Analysis

**Weight Magnitude** ≈ Feature Importance

**Pac-Man Example** (after training):
```python
w = [-19.5, 7.2, 23.6, -2.6, 2.3, 7.0, 0.01, 0.24]
     ^     ^    ^      ^     ^    ^     ^     ^
     |     |    |      |     |    |     |     |
Most Important: Feature 2 (vaccines), Feature 0 (exit)
Least Important: Feature 6 (obstacles)
```

---

## Practical Training Tips

### 1. Start Simple

```bash
# Quick test (100 episodes)
python scripts/train.py pacman --episodes 100

# Verify learning is happening (win rate should increase)
```

### 2. Monitor Progress

```
Episode 1000: Win Rate 12% ← Learning
Episode 2000: Win Rate 23% ← Improving
Episode 3000: Win Rate 35% ← Good
Episode 4000: Win Rate 42% ← Plateauing
```

### 3. Tune Hyperparameters

```bash
# Conservative (stable)
--learning-rate 0.001 --episodes 20000

# Aggressive (fast but risky)
--learning-rate 0.05 --episodes 5000

# Recommended
--learning-rate 0.01 --episodes 10000
```

### 4. Iterative Improvement

```bash
# Train Pac-Man
python scripts/train.py pacman --episodes 10000

# Train Zombie against trained Pac-Man
python scripts/train.py zombie \
    --opponent-weights weights/pacman_weights.json

# Retrain Pac-Man against improved Zombie
python scripts/train.py pacman \
    --continue-from weights/pacman_weights.json \
    --opponent-weights weights/zombie_weights.json \
    --episodes 5000
```

---

## References

### Classic Papers

1. **Sutton, R. S., & Barto, A. G. (2018)**. *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
   - Chapter 6: Temporal-Difference Learning
   - Chapter 9: On-policy Approximation

2. **Tsitsiklis, J. N., & Van Roy, B. (1997)**. *An analysis of temporal-difference learning with function approximation*. IEEE Transactions on Automatic Control.

3. **Silver, D., et al. (2017)**. *Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm*. arXiv:1712.01815.
   - Adversarial self-play in games

### Implementation References

- [src/pacman_zombie/learning/trainer.py](../src/pacman_zombie/learning/trainer.py) - Training implementation
- [src/pacman_zombie/agents/features.py](../src/pacman_zombie/agents/features.py) - Feature extraction
- [TRAINING_GUIDE.md](../TRAINING_GUIDE.md) - Practical training guide

---

## Related Documentation

- [README.md](../README.md) - Project overview
- [docs/FEATURES.md](FEATURES.md) - Feature engineering details
- [docs/GAME_RULES.md](GAME_RULES.md) - Complete game rules
- [TRAINING_GUIDE.md](../TRAINING_GUIDE.md) - Training tutorial

---

**Now you understand how the AI learns!** 🧠🎓

```bash
# Train your own agents
python scripts/train.py both --episodes 10000
```
