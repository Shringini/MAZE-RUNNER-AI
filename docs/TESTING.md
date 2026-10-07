# Maze Runner - Testing Documentation

## 1. Testing Overview

Testing was performed to verify that the Maze Runner game components work correctly after integration.

The main areas tested were:

- Maze generation
- BFS pathfinding
- Enemy AI
- Player and maze interaction
- Enemy and player interaction
- Game victory condition
- Game over condition
- Game restart functionality

---

## 2. Automated Testing

Automated testing was performed using `pytest`.

### Test Files

| Test File | Purpose |
|---|---|
| `test_bfs.py` | Tests BFS pathfinding |
| `test_enemy.py` | Tests enemy AI behaviour |
| `test_maze.py` | Tests maze functionality |

### Test Results

| Test Area | Number of Tests | Result |
|---|---:|---|
| BFS Pathfinding | 2 | PASS |
| Enemy AI | 2 | PASS |
| Maze | 3 | PASS |
| **Total** | **7** | **PASS** |

Final automated test result:

```text
7 passed