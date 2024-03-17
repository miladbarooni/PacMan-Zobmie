# Pac-man Z Edition Game - Function Approximation and Adversarial Learning

## Project Overview

This project aims to design a Pac-Man game variant featuring a Pac-Man and four zombies. The objective is to optimize agent behaviors using function approximation and adversarial learning to determine the best set of weights for feature vectors representing game state evaluations.

### Project Goals

- Develop a game with one Pac-Man and four zombies using adversarial learning and function approximation.
- Implement separate agent behaviors for the Pac-Man and zombies, optimizing through training.
- Design a game board model to enforce game rules and dynamics.

### Game Rules

1. Zombies attempt to capture the Pac-Man, which happens if a zombie reaches any adjacent cell to the Pac-Man.
2. The Pac-Man can shoot zombies, limited to straight (non-diagonal) lines and within two cells.
3. A vaccine exists on the map; if the Pac-Man retrieves it, it can heal adjacent zombies, causing them to flee.
4. The game ends when no zombies remain, and the Pac-Man must reach the designated exit point. Prematurely reaching the exit or falling into pits results in a loss.
5. Zombies reappear randomly on the map upon falling into pits.

### Board Model

- The board is initialized with random placements of the Pac-Man, zombies, pits, obstacles, and a vaccine.
- Methods implement movement rules, validate positions, and check game-ending conditions.
- Features extraction based on the successor states for both Pac-Man and zombies, guiding their next actions.

### Training Model

- Training involves adversarial learning, with the Pac-Man and zombies iteratively adjusting their strategies based on the outcomes of game sessions.
- The process fine-tunes weights used in function approximation, improving decision-making over time.

### User Interface

- A graphical user interface allows for interactive gameplay, with the user controlling the Pac-Man against AI-driven zombies.
- The game provides visual and audio feedback for actions and events.

### Implementation Details

- Agents (Pac-Man and zombies) are implemented in separate files, each determining actions based on the current game state and learned weights.
- The project employs function approximation to evaluate the potential outcomes of actions, guiding agent decisions towards optimal strategies.

### Conclusion

The game showcases the application of machine learning techniques in a familiar setting, illustrating how adversarial learning and function approximation can lead to sophisticated behavior in AI agents.

