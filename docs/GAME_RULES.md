# Game Rules - Pac-Man vs Zombies

Complete reference for all game mechanics, rules, and interactions.

---

## Table of Contents

- [Overview](#overview)
- [Game Entities](#game-entities)
- [Win & Lose Conditions](#win--lose-conditions)
- [Movement Rules](#movement-rules)
- [Combat Mechanics](#combat-mechanics)
- [Vaccine System](#vaccine-system)
- [Scoring](#scoring)
- [Board Configuration](#board-configuration)
- [Advanced Mechanics](#advanced-mechanics)

---

## Overview

Pac-Man vs Zombies is a turn-based adversarial game where:
- **Pac-Man** must collect vaccines, cure all zombies, and escape through the exit
- **Zombies** must capture Pac-Man before being cured
- The board contains obstacles, pits, vaccines, and an exit

**Key Principle**: Pac-Man cannot reach the exit until ALL zombies are cured.

---

## Game Entities

### Pac-Man (🟡 / @)

**Properties**:
- Position: Single cell on the board
- Shots: Starts with 3 shots
- Vaccine status: Can hold at most 1 vaccine at a time
- Health: Dies instantly if captured or falls in pit

**Abilities**:
1. **Move**: Up, Down, Left, Right (one cell per turn)
2. **Shoot**: Kill zombie 2 cells away in straight line
3. **Cure**: Adjacent zombies when holding vaccine

---

### Zombies (🧟 / Z)

**Properties**:
- Count: Always 4 zombies
- Position: Each zombie occupies one cell
- AI Controlled: Make decisions using learned weights

**Behavior**:
- **Chase Mode** (default): Move toward Pac-Man
- **Flee Mode**: Run away when Pac-Man has vaccine
- **Coordinate**: Each zombie acts independently but all move each turn

**Special**: Zombies respawn randomly if they fall in pit

---

### Obstacles (█ / #)

**Properties**:
- Impassable terrain
- Count: 10 obstacles per board
- Position: Random placement at game start

**Rules**:
- Neither Pac-Man nor zombies can pass through
- Block shooting line of sight
- Affect feature calculations (distance)

---

### Vaccine (💉 / +)

**Properties**:
- Spawn count: Up to 4 vaccines total in game
- Effect: Allows Pac-Man to cure adjacent zombies
- Collection: Auto-collected when Pac-Man moves onto cell

**Mechanics**:
- Only 1 vaccine exists on board at a time
- After curing zombie, new vaccine spawns (until limit reached)
- Pac-Man can only hold 1 vaccine at a time
- Vaccine respawn limit: 4 total

---

### Exit (🚪 / X)

**Properties**:
- Position: Random placement at game start
- Visibility: Always visible on board
- Access: Only available after all zombies cured

**Rules**:
- **Cannot use** if any zombies remain
- Attempting early exit: -100 penalty, game continues
- **Win condition**: Reach exit when 0 zombies remain

---

### Pit (⚫ / O)

**Properties**:
- Instant death for Pac-Man
- Respawn trigger for zombies
- Position: Single pit per board

**Effects**:
- **Pac-Man**: Game over (-1000 penalty)
- **Zombie**: Removed from board, respawns randomly

---

## Win & Lose Conditions

### Pac-Man Wins

**Condition**: ALL of the following must be true:
1. ✅ All 4 zombies cured (removed from board)
2. ✅ Pac-Man reaches exit cell
3. ✅ Exit no longer exists on board (consumed)

**Reward**: +1000

---

### Pac-Man Loses

**Any** of the following triggers game over:

#### 1. Captured by Zombie

- Zombie moves to **any adjacent cell** (8 directions including diagonals)
- Instant game over
- **Penalty**: -1000

#### 2. Falls into Pit

- Pac-Man moves onto pit cell
- Instant game over
- **Penalty**: -1000

#### 3. Reaches Exit Early

- Tries to reach exit while zombies still active
- **Penalty**: -100
- Game continues (not instant death)

---

## Movement Rules

### General Movement

**Valid Moves**:
- UP: row - 1
- DOWN: row + 1
- LEFT: col - 1
- RIGHT: col + 1

**Restrictions**:
- Cannot move outside board boundaries (0 to width-1, 0 to height-1)
- Cannot move onto obstacles
- Pac-Man cannot move onto pits (game over)
- Zombies CAN move onto pits (they respawn)

### Turn Order

Each game turn:
1. **Pac-Man acts first** - Selects and executes one action
2. **Zombies act second** - All zombies select and execute actions simultaneously
3. **Check game over** conditions
4. Repeat

---

## Combat Mechanics

### Shooting

**Requirements**:
- Pac-Man must have remaining shots (max 3)
- Zombie must be exactly 2 cells away
- Must be in straight line (UP/DOWN/LEFT/RIGHT only)
- No obstacles between Pac-Man and zombie

**Range**:
```
Valid shooting positions (X = Pac-Man, Z = Zombie target):

      Z            .
      .            Z
      X    or  Z . X . Z
      .            Z
      Z            .

EXACTLY 2 cells away, straight lines only
```

**Effect**:
- Targeted zombie removed from board
- Shot count decreases by 1
- No points awarded for shooting

**Invalid Shots**:
- Diagonal: NOT allowed
- 1 cell away: Too close
- 3+ cells away: Out of range
- Obstacle blocking: No line of sight

---

## Vaccine System

### Collection

**Automatic**:
- Pac-Man moves onto vaccine cell → auto-collected
- Vaccine removed from board
- Pac-Man's `has_vaccine` status = True

### Curing Zombies

**Requirements**:
- Pac-Man must have vaccine
- Zombie must be in **any adjacent cell** (8 directions including diagonals)

**Adjacent cells** (X = Pac-Man, Z = valid zombie positions):
```
Z Z Z
Z X Z
Z Z Z
```

**Effect**:
- Zombie removed from board permanently
- Vaccine consumed (Pac-Man no longer has it)
- +10 points to score
- Cure counter increments
- New vaccine spawns (if < 4 total cured)

### Vaccine Respawn

**Logic**:
```python
if num_zombie_cure < VACCINE_RESPAWN_LIMIT (4):
    spawn_new_vaccine()
```

**Example**:
- Game starts: 1 vaccine on board
- Cure zombie #1: vaccine consumed, new one spawns
- Cure zombie #2: vaccine consumed, new one spawns
- Cure zombie #3: vaccine consumed, new one spawns
- Cure zombie #4: vaccine consumed, NO MORE SPAWN (limit reached)

---

## Scoring

### Point System

| Event | Points |
|-------|--------|
| Cure zombie with vaccine | +10 |
| Shoot zombie | 0 (no points) |
| Win (reach exit) | N/A (tracked as win) |
| Lose (captured/pit) | N/A (tracked as loss) |

### Score Tracking

```python
board.score           # Current score
board.num_zombie_cure # Zombies cured (with vaccine)
board.num_shooted_zombie # Zombies killed (with shooting)
```

**Note**: Shooting doesn't give points, but curing does!

---

## Board Configuration

### Default Settings

```python
BOARD_WIDTH = 10          # Columns
BOARD_HEIGHT = 15         # Rows
NUM_ZOMBIES = 4           # Always 4
NUM_OBSTACLES = 10        # Random placement
NUM_VACCINES = 4          # Respawn limit
NUM_SHOTS = 3             # Pac-Man's ammo
```

### Board Size

```
10 columns × 15 rows = 150 total cells

Grid coordinates:
- (0, 0) = top-left
- (14, 9) = bottom-right
```

### Entity Limits

| Entity | Count | Notes |
|--------|-------|-------|
| Pac-Man | 1 | Always |
| Zombies | 4 | Always |
| Obstacles | 10 | Fixed at start |
| Vaccine | 0-1 | Only 1 on board at a time |
| Exit | 1 | Fixed at start |
| Pit | 1 | Fixed at start |

---

## Advanced Mechanics

### Zombie Behavior Modes

**Chase Mode** (default):
- When Pac-Man has NO vaccine
- Zombies move toward Pac-Man
- Feature weight: negative multiplier on distance

**Flee Mode**:
- When Pac-Man HAS vaccine
- Zombies move away from Pac-Man
- Feature weight: positive multiplier on distance

Implementation:
```python
# In feature extraction
if board.has_vaccine:
    go_to_player = 10  # Flee (positive = increase distance)
else:
    go_to_player = -10  # Chase (negative = decrease distance)
```

### Pit Mechanics

**Pac-Man**:
```python
if board.player_fell_into_pit():
    game_over = True
    penalty = -1000
```

**Zombie**:
```python
if zombie_at_pit_position:
    remove_zombie_from_board()
    spawn_zombie_at_random_empty_cell()
    # Zombie continues playing
```

### Exit Accessibility

**Check**:
```python
def can_use_exit():
    return board.find_zombies_number() == 0
```

**Scenarios**:
1. Zombies remain: Pac-Man reaches exit → -100 penalty, continue game
2. All zombies cured: Pac-Man reaches exit → WIN (+1000)

### Collision Detection

**Capture Check** (zombie wins):
```python
def player_captured_by_zombies():
    player_row, player_col = board.player_position

    # Check all 8 adjacent cells
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue  # Skip center

            check_row = player_row + dr
            check_col = player_col + dc

            if grid[check_row][check_col] == "Z":
                return True  # Captured!

    return False
```

---

## Game Flow Example

### Turn-by-Turn Example

**Initial State**:
```
Pac-Man: (7, 7)
Zombies: (4, 2), (4, 8), (6, 6), (8, 8)
Vaccine: (1, 8)
Shots: 3
```

**Turn 1**:
- Pac-Man moves UP to (6, 7)
- Zombies move toward Pac-Man
- Check: Not captured, not in pit → continue

**Turn 2**:
- Pac-Man moves UP to (5, 7)
- Zombies continue approaching
- Check: continue

**Turn 3**:
- Pac-Man shoots zombie at (4, 7) → zombie removed, shots = 2
- Remaining zombies move
- Check: continue

**Turn 4**:
- Pac-Man moves to vaccine (1, 8)
- Vaccine auto-collected, has_vaccine = True
- Zombies now FLEE (Pac-Man has vaccine)

**Turn 5**:
- Pac-Man moves adjacent to zombie
- Zombie cured, removed from board
- Score +10, new vaccine spawns

**Repeat until**:
- All zombies cured → Pac-Man moves to exit → WIN
- Or zombie catches Pac-Man → LOSE

---

## Special Cases

### Simultaneous Events

**Priority Order**:
1. Pac-Man action executed
2. Vaccine collection checked
3. Zombies action executed
4. Capture check
5. Pit check
6. Cure check
7. Exit check

### Edge Cases

**What if...**

Q: Pac-Man shoots last zombie?
A: No vaccine needed, can go straight to exit

Q: Pac-Man has vaccine but no zombies nearby?
A: Must move adjacent to cure, or shoot from distance

Q: All vaccines used but zombies remain?
A: Must shoot remaining zombies (if ammo left) or get captured

Q: Out of shots and vaccines?
A: Only option is to get captured (lose) or find remaining vaccine

Q: Zombie and Pac-Man swap positions?
A: Cannot happen - capture is checked after each move

---

## Constants Reference

All game constants (from [src/pacman_zombie/core/constants.py](../src/pacman_zombie/core/constants.py)):

```python
# Board dimensions
DEFAULT_BOARD_WIDTH = 10
DEFAULT_BOARD_HEIGHT = 15

# Entity counts
DEFAULT_NUM_ZOMBIES = 4
DEFAULT_NUM_OBSTACLES = 10
DEFAULT_NUM_VACCINES = 4
DEFAULT_NUM_SHOTS = 3

# Mechanics
SHOOTING_RANGE = 2
VACCINE_RESPAWN_LIMIT = 4

# Rewards (for training)
REWARD_WIN = 1000
REWARD_LOSE = -1000
REWARD_EXIT_EARLY = -100
REWARD_PIT = -100
```

---

## Related Documentation

- [README.md](../README.md) - Project overview
- [PLAY_GUIDE.md](../PLAY_GUIDE.md) - How to play
- [docs/ALGORITHM.md](ALGORITHM.md) - Learning algorithm
- [docs/FEATURES.md](FEATURES.md) - Feature engineering

---

**Master these rules, then challenge the AI zombies!** 🟡🧟

```bash
python scripts/play.py
```
