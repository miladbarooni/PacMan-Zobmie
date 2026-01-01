# Feature Engineering - Pac-Man vs Zombies

Complete reference for feature extraction and state representation in the learning algorithm.

---

## Overview

Both Pac-Man and Zombie agents use **linear function approximation** to estimate state values:

```
V(s) = w₁·φ₁(s) + w₂·φ₂(s) + ... + wₙ·φₙ(s) = w · φ(s)
```

Where:
- `φ(s)` = feature vector extracted from state `s`
- `w` = learned weight vector
- `V(s)` = estimated value of state `s`

**Key Insight**: Features encode domain knowledge about what makes a state "good" or "bad".

---

## Pac-Man Features (8-dimensional)

### Feature 0: Distance to Exit (Conditional)

**Purpose**: Guide Pac-Man to exit after zombies are cleared

**Formula**:
```python
if num_zombies == 0:  # All zombies cured
    go_to_exit = 100.0
else:
    go_to_exit = 0.0

distance_to_exit = manhattan_distance(pacman_pos, exit_pos)
feature[0] = go_to_exit * (distance_to_exit / 20.0)
```

**Interpretation**:
- **When zombies remain**: Feature = 0 (exit irrelevant)
- **After zombies cleared**: Feature = scaled distance (larger = farther from exit)
- **Learned weight** (typically negative): Encourages moving toward exit

**Example**:
```
Zombies = 0, Distance = 10 cells
feature[0] = 100.0 * (10 / 20.0) = 50.0
```

---

### Feature 1: Shooting Opportunity

**Purpose**: Identify when shooting is beneficial

**Formula**:
```python
if has_vaccine:
    shoot_mult = 0.0  # Prefer curing over shooting when have vaccine
else:
    shoot_mult = -1000000.0  # Strongly discourage shooting without strategy

if can_shoot():  # Zombie exactly 2 cells away
    num_zombies_in_range = count_shootable_zombies()
else:
    num_zombies_in_range = 0

feature[1] = shoot_mult * num_zombies_in_range
```

**Interpretation**:
- **Large negative value**: Shooting available but not strategic
- **Zero**: Has vaccine (prefer curing) or no shooting opportunity
- **Learned weight**: Balances shooting vs other strategies

---

### Feature 2: Remaining Vaccines

**Purpose**: Track vaccine availability

**Formula**:
```python
feature[2] = num_remain_vaccine  # 0 to 4
```

**Interpretation**:
- **Higher value**: More vaccines will spawn
- **Lower value**: Fewer curing opportunities left
- **Learned weight** (typically positive): Value having vaccines available

---

### Feature 3: Distance to Vaccine (Conditional)

**Purpose**: Guide Pac-Man to collect vaccines

**Formula**:
```python
if vaccine_exists and not has_vaccine:
    go_to_vaccine = 100.0
else:
    go_to_vaccine = 0.0

distance_to_vaccine = manhattan_distance(pacman_pos, vaccine_pos)
feature[3] = go_to_vaccine * (distance_to_vaccine / 20.0)
```

**Interpretation**:
- **Non-zero**: Vaccine on board, Pac-Man doesn't have one
- **Zero**: Already has vaccine or no vaccine on board
- **Learned weight** (typically negative): Encourages collecting vaccines

---

### Feature 4: Distance to Nearest Zombie

**Purpose**: Encourage/discourage approaching zombies

**Formula**:
```python
if num_zombies > 0 and has_vaccine:
    go_to_zombies = 100.0  # Approach to cure
else:
    go_to_zombies = 0.0  # Avoid when no vaccine

min_zombie_distance = min(manhattan_distance(pacman_pos, z) for z in zombies)
feature[4] = go_to_zombies * (min_zombie_distance / 20.0)
```

**Interpretation**:
- **With vaccine**: Non-zero, encourages approaching to cure
- **Without vaccine**: Zero, avoidance handled by zombie behavior
- **Learned weight**: Balances aggression when equipped

---

### Feature 5: Has Vaccine (Binary)

**Purpose**: Track current vaccine possession

**Formula**:
```python
feature[5] = 1.0 if has_vaccine else 0.0
```

**Interpretation**:
- **1.0**: Currently holding vaccine (can cure)
- **0.0**: No vaccine (must collect or shoot)
- **Learned weight**: Values having the strategic advantage

---

### Feature 6: Distance to Obstacles

**Purpose**: Avoid getting trapped

**Formula**:
```python
min_obstacle_distance = min(manhattan_distance(pacman_pos, obs) for obs in obstacles)
feature[6] = min_obstacle_distance / 20.0
```

**Interpretation**:
- **Smaller value**: Close to obstacles (potentially trapped)
- **Larger value**: Open space
- **Learned weight** (typically positive): Value open space

---

### Feature 7: Distance to Pit (Conditional)

**Purpose**: Avoid falling into pit

**Formula**:
```python
if num_zombies == 0:  # After zombies cleared
    pit_mult = 10.0  # Strongly avoid
else:
    pit_mult = 1.0  # Normal avoidance

distance_to_pit = manhattan_distance(pacman_pos, pit_pos)
feature[7] = pit_mult * (distance_to_pit / 20.0)
```

**Interpretation**:
- **Higher multiplier when zombies cleared**: Can't afford to lose now
- **Lower otherwise**: Focus on zombies first
- **Learned weight** (typically positive): Avoid pits

---

## Zombie Features (3-dimensional)

### Feature 0: Distance to Pac-Man (Behavioral)

**Purpose**: Chase or flee based on Pac-Man's vaccine status

**Formula**:
```python
if pacman_has_vaccine:
    go_to_player = 10.0  # FLEE (positive = increase distance)
else:
    go_to_player = -10.0  # CHASE (negative = decrease distance)

distance_to_pacman = manhattan_distance(zombie_pos, pacman_pos)
feature[0] = go_to_player * (distance_to_pacman / 20.0)
```

**Interpretation**:
- **Pac-Man has vaccine**: Positive feature (flee away)
- **Pac-Man unarmed**: Negative feature (chase down)
- **Learned weight**: Adjusts chase/flee aggressiveness
- **This is the CORE adversarial behavior**

---

### Feature 1: Distance to Pit

**Purpose**: Avoid falling in pit (causes respawn)

**Formula**:
```python
distance_to_pit = manhattan_distance(zombie_pos, pit_pos)
feature[1] = distance_to_pit / 20.0
```

**Interpretation**:
- **Smaller value**: Close to pit (risky)
- **Larger value**: Safe distance
- **Learned weight** (typically positive): Avoid respawning

---

### Feature 2: Distance to Obstacles

**Purpose**: Avoid getting trapped or blocked

**Formula**:
```python
min_obstacle_distance = min(manhattan_distance(zombie_pos, obs) for obs in obstacles)
feature[2] = min_obstacle_distance / 40.0  # Note: divided by 40, not 20
```

**Interpretation**:
- **Smaller value**: Near obstacles
- **Larger value**: Open path to Pac-Man
- **Learned weight**: Balance between direct pursuit and safe paths

---

## Feature Design Principles

### 1. Normalization

**All distance features divided by scale factor** (20 or 40):
- Prevents feature magnitude dominance
- Keeps features in similar ranges
- Helps learning converge faster

**Example**:
```python
# Without normalization
distance = 15  # Could be 0-20 range

# With normalization
feature = 15 / 20.0 = 0.75  # Now 0-1 range
```

---

### 2. Conditional Activation

**Features "turn on" based on game state**:

```python
# Feature only matters in specific contexts
if condition_met:
    multiplier = 100.0  # Active
else:
    multiplier = 0.0  # Inactive

feature = multiplier * scaled_value
```

**Benefits**:
- Clear behavioral modes
- Easier to learn separate strategies
- Interpretable learned weights

---

### 3. Behavioral Multipliers

**Sign indicates direction of preference**:

```python
# NEGATIVE: Want to MINIMIZE this value
go_to_exit = -100.0  # Decrease distance to exit

# POSITIVE: Want to MAXIMIZE this value
flee_from_pacman = 10.0  # Increase distance from Pac-Man
```

**Adversarial learning**:
- Pac-Man: `w ← w + α * error * features` (increase good features)
- Zombie: `w ← w - α * error * features` (increase opposite)

---

## Feature Extraction Code

### Pac-Man Feature Extraction

```python
def extract_features(board, successor_state):
    """Extract 8-dimensional feature vector for Pac-Man."""
    features = np.zeros(8)

    # Feature 0: Distance to exit (when zombies cleared)
    if board.find_zombies_number() == 0:
        distance = manhattan_distance(pacman_pos, exit_pos)
        features[0] = 100.0 * (distance / 20.0)

    # Feature 1: Shooting opportunity
    # ... (see board.py for full implementation)

    return features
```

### Zombie Feature Extraction

```python
def extract_features_zombie(board, successor_state, zombie_row, zombie_col):
    """Extract 3-dimensional feature vector for specific zombie."""
    features = np.zeros(3)

    # Feature 0: Chase/flee Pac-Man
    if board.has_vaccine:
        multiplier = 10.0  # Flee
    else:
        multiplier = -10.0  # Chase

    distance = manhattan_distance((zombie_row, zombie_col), pacman_pos)
    features[0] = multiplier * (distance / 20.0)

    # ... (see board.py for full implementation)

    return features
```

---

## Learned Weight Examples

### Typical Pac-Man Weights (after 10,000 episodes)

```python
w_pacman = [
    -19.54,  # Feature 0: Exit distance (negative = approach when active)
      7.23,  # Feature 1: Shooting (balances with other strategies)
     23.63,  # Feature 2: Remaining vaccines (positive = value availability)
     -2.64,  # Feature 3: Vaccine distance (negative = collect them)
      2.32,  # Feature 4: Zombie distance (slightly positive when aggressive)
      7.02,  # Feature 5: Has vaccine (positive = valuable state)
      0.01,  # Feature 6: Obstacle distance (minimal impact)
      0.24   # Feature 7: Pit distance (small positive = mild avoidance)
]
```

**Interpretation**:
- Strong negative weight on Feature 0: Rush to exit when clear
- Largest positive weight on Feature 2: Highly values vaccine availability
- Positive weight on Feature 5: Holding vaccine is advantageous

### Typical Zombie Weights (after 10,000 episodes)

```python
w_zombie = [
    134.74,  # Feature 0: Pac-Man distance (large positive from adversarial learning)
    -13.44,  # Feature 1: Pit distance (negative = avoid pits)
     -2.96   # Feature 2: Obstacle distance (negative = avoid getting stuck)
]
```

**Interpretation**:
- Large positive weight on Feature 0: Due to adversarial learning (minimizes Pac-Man's value)
- When chasing (multiplier = -10): Effective coefficient = 134.74 * (-10) = very negative → close gap
- When fleeing (multiplier = +10): Effective coefficient = 134.74 * (+10) = very positive → increase distance

---

## Feature Engineering Best Practices

### What Makes Good Features?

1. **Relevant**: Captures important game state information
2. **Normalized**: Similar scale across features
3. **Independent**: Minimal correlation between features
4. **Interpretable**: Clear meaning for debugging
5. **Efficient**: Fast to compute (called thousands of times)

### Common Pitfalls

❌ **Too many features**: Overfitting, slow learning
❌ **Redundant features**: Waste learning capacity
❌ **Unnormalized**: Some features dominate
❌ **Non-stationary**: Feature meaning changes during game
❌ **Expensive computation**: Slows training significantly

### Our Choices

✅ **8 Pac-Man features**: Comprehensive but not excessive
✅ **3 Zombie features**: Simpler adversary (easier to learn against)
✅ **Distance normalization**: All scaled by 20 or 40
✅ **Conditional activation**: Clear behavioral modes
✅ **Manhattan distance**: Fast to compute (no sqrt)

---

## Extending Features

Want to add new features? Follow this template:

```python
# 1. Define feature extraction
def extract_new_feature(board, successor_state):
    # Compute raw value
    raw_value = compute_something(board)

    # Normalize to reasonable scale
    normalized = raw_value / SCALE_FACTOR

    # Apply conditional logic if needed
    if some_condition:
        multiplier = 100.0
    else:
        multiplier = 0.0

    return multiplier * normalized

# 2. Add to feature vector
features[NEW_INDEX] = extract_new_feature(board, state)

# 3. Update weight vector dimension
w_pacman = np.random.rand(9)  # Was 8, now 9

# 4. Retrain from scratch
python scripts/train.py pacman --episodes 10000
```

---

## Related Documentation

- [README.md](../README.md) - Project overview
- [docs/ALGORITHM.md](ALGORITHM.md) - Learning algorithm details
- [docs/GAME_RULES.md](GAME_RULES.md) - Complete game rules
- [TRAINING_GUIDE.md](../TRAINING_GUIDE.md) - Training tutorial

---

**Understand the features, understand the AI!** 🎯
