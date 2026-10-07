# Maze Runner (Member 1 Implementation)

This is the initial foundation module for the **"Maze Runner with AI-Controlled Enemy"** project.
It handles maze generation, player creation, smooth keyboard movement, wall collisions, boundary enforcement, and exit detection using **Python** and **Pygame**.

Enemy pathfinding (BFS / A*) will be added by Member 2.

---

## 📁 Project Structure

```
MazeRunner/
├── main.py      # Main entry point & Pygame 60 FPS game loop
├── maze.py      # Maze generation, data structure, wall rects, and BFS helpers
├── player.py    # Player character class, movement physics & collision resolution
└── README.md    # Documentation & Member 2 integration guide
```

---

## 🛠️ Prerequisites & Installation

Make sure Python (version 3.10+) is installed.

### Install Pygame:
Open your terminal or command prompt and run:

```bash
pip install pygame
```

*(Note: On newer Python releases like Python 3.14+, use `pip install pygame-ce` for Community Edition wheels if needed).*

---

## 🚀 How to Run the Game

Navigate to the project directory and run `main.py`:

```bash
# If you are in the workspace root:
python MazeRunner/main.py

# Or navigate into the folder:
cd MazeRunner
python main.py
```

---

## 🎮 Controls

| Action | Keys |
| :--- | :--- |
| **Move Up** | `W` or `Up Arrow` |
| **Move Down** | `S` or `Down Arrow` |
| **Move Left** | `A` or `Left Arrow` |
| **Move Right** | `D` or `Right Arrow` |
| **Restart / Reset to Start** | `R` |
| **Quit Game** | `ESC` |

---

## 🧩 What This Module Does

1. **Procedural 2D Grid Maze Generation**:
   - Generates a guaranteed-solvable maze using the Recursive Backtracker (DFS) algorithm.
   - Grid symbols used:
     - `'#'`: Solid Wall
     - `'0'`: Walkable Path
     - `'P'`: Player Starting Position (top-left area)
     - `'E'`: Exit Portal (bottom-right area)
2. **Player Character**:
   - Automatically detects and spawns at the `'P'` position in the maze grid without hard-coding coordinates.
   - Distinct, glowing cyan runner with animated eyes indicating direction of motion.
3. **Smooth Movement & Wall Collision**:
   - Axis-separated collision detection (X and Y handled independently).
   - Allows natural sliding along walls when moving diagonally or pressing into corners.
   - Clamped to the maze outer boundary so the player can never escape.
4. **Exit Detection**:
   - Detects when the player reaches the glowing emerald `'E'` cell.
   - Pauses movement and displays an attractive **"YOU WIN!"** overlay with options to restart (`[R]`) or quit (`[ESC]`).

---

## 🤝 For Member 2: BFS / Enemy AI Integration Guide

The `Maze` and `Player` classes are specifically structured so that Member 2 can implement the BFS enemy chaser with minimal effort.

### 1. Where the Maze Data is Stored
Inside `maze.py`, the `Maze` class stores the 2D grid in `self.grid`:
- A 2-dimensional list of characters: `grid[row][col]`.
- Dimensions are available as `maze.rows` and `maze.cols`.

### 2. Available Helper Methods in `maze.py`

| Method | Return Type | Description |
| :--- | :--- | :--- |
| `maze.get_grid()` | `list[list[str]]` | Returns the raw 2D grid matrix. |
| `maze.get_player_start()` | `tuple[int, int]` | Returns `(row, col)` of the start cell `'P'`. |
| `maze.get_exit_pos()` | `tuple[int, int]` | Returns `(row, col)` of the exit cell `'E'`. |
| `maze.get_walls()` | `list[tuple[int, int]]` | Returns a list of all wall coordinates. |
| `maze.get_walkable_positions()` | `list[tuple[int, int]]` | Returns a list of all walkable coordinates. |
| `maze.is_walkable(row, col)` | `bool` | Returns `True` if `(row, col)` is in bounds and not `'#'`. |
| `maze.get_neighbors(row, col)` | `list[tuple[int, int]]` | Returns adjacent walkable `[(nr, nc), ...]`. **Perfect for BFS!** |
| `maze.grid_to_pixel(row, col)` | `tuple[int, int]` | Converts grid coordinates to screen pixel center `(x, y)`. |
| `maze.pixel_to_grid(x, y)` | `tuple[int, int]` | Converts screen pixel coordinates to grid `(row, col)`. |

### 3. Tracking Player Position for Enemy AI
In `player.py`, call:
```python
current_player_grid_pos = player.get_grid_position()
# Returns (row, col) where the player is currently located
```

### 4. Quick BFS Example for Member 2
Here is how Member 2 can compute the shortest path from the enemy to the player using our helpers:

```python
from collections import deque

def find_shortest_path_bfs(maze, enemy_pos, player_pos):
    """
    Finds shortest path from enemy_pos (r, c) to player_pos (r, c).
    Returns list of (row, col) steps to follow.
    """
    queue = deque([[enemy_pos]])
    visited = {enemy_pos}

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current == player_pos:
            return path  # Full path from enemy to player

        for neighbor in maze.get_neighbors(current[0], current[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return []  # No path found
```

All collision rects, rendering pipeline, and game loop hooks in `main.py` are ready for Member 2's enemy instance!
