# Play Pac-Man vs Zombies - Quick Start Guide

## Implementation Complete! ✅

Your terminal-based Pac-Man vs Zombies game is now **fully playable**! You can control Pac-Man in your terminal while AI zombies try to catch you.

---

## Installation

First, install the new dependency:

```bash
pip install colorama
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## How to Play

### Basic Usage

```bash
# Play with default settings (Unicode emojis + colors)
python scripts/play.py
```

### With Options

```bash
# Show legal moves each turn (helpful for learning)
python scripts/play.py --show-legal-moves

# Watch AI zombies think (educational)
python scripts/play.py --show-ai-thinking

# Save game replay for analysis
python scripts/play.py --save-replay my_game.json

# Combine multiple options
python scripts/play.py --show-legal-moves --show-ai-thinking --save-replay game.json

# ASCII-only mode (maximum compatibility)
python scripts/play.py --no-unicode --no-colors
```

### Get Help

```bash
python scripts/play.py --help
```

---

## Controls

**During Gameplay:**
- **W** or **↑** - Move Up
- **S** or **↓** - Move Down
- **A** or **←** - Move Left
- **D** or **→** - Move Right
- **F** or **Space** - Shoot (zombie must be exactly 2 cells away)
- **Q** - Quit game

> **Note**: Depending on your system, you may use arrow keys (real-time) or WASD keys (type + Enter).

---

## Game Symbols

### Unicode Mode (Default)
- 🟡 - **Pac-Man** (You)
- 🧟 - **Zombie** (AI opponent)
- 💉 - **Vaccine** (Cure adjacent zombies)
- 🚪 - **Exit** (Appears after all zombies cured)
- █ - **Obstacle** (Cannot pass)
- ⚫ - **Pit** (Avoid! Instant death)

### ASCII Mode (`--no-unicode`)
- @ - Pac-Man
- Z - Zombie
- + - Vaccine
- X - Exit
- # - Obstacle
- O - Pit

---

## Game Rules

### Objective
1. **Collect vaccines** (💉) to cure adjacent zombies
2. **Shoot zombies** that are exactly 2 cells away (3 shots total)
3. **Avoid pits** (⚫) and **don't get captured** by zombies (🧟)
4. **Reach the exit** (🚪) after curing all zombies to win!

### Mechanics
- **Vaccine Curing**: Walk adjacent to a zombie while holding a vaccine (+10 points per cure)
- **Shooting**: Zombies must be exactly 2 cells away in a straight line (UP/DOWN/LEFT/RIGHT)
- **Respawning**: Up to 4 vaccines will spawn throughout the game
- **Exit**: Only appears after **all zombies are cured**
- **Win Condition**: Reach exit with no zombies remaining
- **Lose Conditions**:
  - Captured by a zombie
  - Fall into a pit

---

## Status HUD

During gameplay, you'll see a status line like this:

```
Score:   30 | Shots: 2/3 | Vaccine: Yes | Cured: 3 | Zombies: 1
```

- **Score**: Current points
- **Shots**: Remaining ammunition (out of 3 total)
- **Vaccine**: Whether you currently hold a vaccine
- **Cured**: Number of zombies cured so far
- **Zombies**: Active zombies still on the board

---

## Advanced Features

### Show Legal Moves (`--show-legal-moves`)

Displays available actions each turn:
```
Legal moves: UP, DOWN, LEFT, RIGHT, SHOOT
```

Helpful when learning game mechanics!

### AI Thinking Mode (`--show-ai-thinking`)

Shows what the AI zombies are planning:
```
AI Zombies planning:
  Zombie at (4,2) → DOWN
  Zombie at (7,8) → LEFT
  Zombie at (10,6) → UP
```

Great for understanding AI behavior!

### Save Replay (`--save-replay game.json`)

Saves your entire game to a JSON file:
```json
{
  "metadata": {
    "timestamp": "2026-01-01T...",
    "outcome": "WIN - All zombies cured and exit reached",
    "final_score": 40,
    "zombies_cured": 4,
    "total_turns": 25
  },
  "moves": [
    {"turn": 1, "player": "UP"},
    {"turn": 1, "zombies": [[4, 2, "DOWN"], ...]},
    ...
  ]
}
```

Perfect for analyzing your strategy or sharing victories!

---

## Example Session

Here's what a typical game looks like:

```
============================================================
               PAC-MAN vs ZOMBIES
============================================================

Score:    0 | Shots: 3/3 | Vaccine: No  | Cured: 0 | Zombies: 4

┌────────────────────┐
│  █             ⚫   │
│                💉   │
│                    │
│                    │
│    🧟       █     🧟 │
│                    │
│          🧟         │
│          🚪   █   🟡 │
│      █         🧟   │
│                  █ │
│                    │
│                    │
│                    │
│█   █           █ █ │
│    █               │
└────────────────────┘

Your move (W=up, S=down, A=left, D=right, F=shoot, Q=quit):
```

---

## Troubleshooting

### "Zombie weights not found"
Make sure you have `weights/zombie_weights.json` in your project directory. The game requires trained AI weights to run.

### No colors showing up?
Try running with `--no-colors` flag, or check if your terminal supports ANSI colors.

### Unicode symbols display incorrectly?
Use `--no-unicode` for ASCII-only mode:
```bash
python scripts/play.py --no-unicode
```

### Arrow keys not working?
The game will automatically fall back to WASD mode. Just type the letter and press Enter.

---

## What's New

This implementation adds:

✅ **Terminal Renderer** (`src/pacman_zombie/ui/terminal_renderer.py`)
  - Beautiful Unicode emoji symbols (🟡🧟💉🚪)
  - Cross-platform terminal colors via colorama
  - ASCII fallback mode for compatibility
  - Status HUD with game stats

✅ **Interactive Play Script** (`scripts/play.py`)
  - Human vs AI gameplay
  - Real-time keyboard input (with WASD fallback)
  - Legal moves display
  - AI thinking visualization
  - Game replay saving (JSON format)
  - Comprehensive CLI arguments

✅ **All Features Tested**
  - Verified on macOS terminal
  - Unicode + color rendering works
  - ASCII fallback works
  - All game mechanics functional

---

## Next Steps

Now that the game is playable, you can:

1. **Play and test** the game to validate AI behavior
2. **Implement the trainer** (Priority 2) to enable retraining
3. **Write documentation** (Priority 3) for the complete package
4. **Extract Pygame renderer** (Priority 4) for visual mode

---

## Technical Details

**Files Created:**
- `src/pacman_zombie/ui/terminal_renderer.py` (180 lines)
- `scripts/play.py` (270 lines)
- `src/pacman_zombie/ui/__init__.py` (updated)

**Dependencies Added:**
- `colorama>=0.4.6` (cross-platform terminal colors)

**No Core Logic Changed:**
- Zero modifications to `Board`, `Agent`, or `WeightManager` classes
- Backward compatible with all existing code
- Renderer uses read-only access to board state

---

## Have Fun!

Enjoy playing Pac-Man vs Zombies! Try to beat the AI zombies and cure them all! 🟡🧟💉

If you encounter any issues or have suggestions, feel free to ask!
