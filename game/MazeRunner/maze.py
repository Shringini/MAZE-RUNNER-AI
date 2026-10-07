"""
maze.py - Maze Generation and Management Module
Part of Member 1's implementation for "Maze Runner with AI-Controlled Enemy"

Responsible for:
1. Generating/loading a clean 2D grid-based maze.
2. Storing walls ('#'), walkable paths ('0'), player start ('P'), and exit ('E').
3. Providing collision rectangles for Pygame.
4. Rendering the maze.
5. Providing structured maze data and helper methods for BFS pathfinding.
"""

import random
from collections import deque
import pygame


# =============================================================================
# GRID SYMBOLS
# =============================================================================

WALL = '#'
PATH = '0'
PLAYER_START = 'P'
EXIT = 'E'


# =============================================================================
# MAZE GENERATION
# =============================================================================

def generate_maze(rows=15, cols=21, seed=None, braid_ratio=0.40):
    """
    Generate a solvable maze using Recursive Backtracker DFS.

    A higher braid_ratio creates additional connections between corridors,
    giving the player multiple possible routes to the exit.

    Args:
        rows (int): Number of rows.
        cols (int): Number of columns.
        seed (int, optional): Random seed.
        braid_ratio (float): Probability of opening extra walls.

    Returns:
        list[list[str]]: Generated maze grid.
    """

    if seed is not None:
        random.seed(seed)

    # Maze generation works best with odd dimensions
    if rows % 2 == 0:
        rows += 1

    if cols % 2 == 0:
        cols += 1

    # -------------------------------------------------------------------------
    # 1. Start with a grid completely filled with walls
    # -------------------------------------------------------------------------

    grid = [[WALL for _ in range(cols)] for _ in range(rows)]

    start_r, start_c = 1, 1

    grid[start_r][start_c] = PATH

    stack = [(start_r, start_c)]

    # -------------------------------------------------------------------------
    # 2. Recursive Backtracker / DFS maze generation
    # -------------------------------------------------------------------------

    while stack:

        current_r, current_c = stack[-1]

        neighbors = []

        directions = [
            (-2, 0),   # Up
            (2, 0),    # Down
            (0, -2),   # Left
            (0, 2)     # Right
        ]

        for dr, dc in directions:

            new_r = current_r + dr
            new_c = current_c + dc

            if (
                0 < new_r < rows - 1
                and 0 < new_c < cols - 1
                and grid[new_r][new_c] == WALL
            ):
                neighbors.append((new_r, new_c, dr, dc))

        if neighbors:

            new_r, new_c, dr, dc = random.choice(neighbors)

            # Open the wall between current cell and new cell
            grid[current_r + dr // 2][current_c + dc // 2] = PATH

            # Open the new cell
            grid[new_r][new_c] = PATH

            stack.append((new_r, new_c))

        else:

            stack.pop()

    # -------------------------------------------------------------------------
    # 3. Add extra connections / loops
    #
    # Higher braid_ratio = more alternative routes.
    # -------------------------------------------------------------------------

    for r in range(1, rows - 1):

        for c in range(1, cols - 1):

            if grid[r][c] != WALL:
                continue

            # Horizontal connection:
            # PATH # PATH
            horizontal_open = (
                grid[r][c - 1] == PATH
                and grid[r][c + 1] == PATH
                and grid[r - 1][c] == WALL
                and grid[r + 1][c] == WALL
            )

            # Vertical connection:
            # PATH
            #  #
            # PATH
            vertical_open = (
                grid[r - 1][c] == PATH
                and grid[r + 1][c] == PATH
                and grid[r][c - 1] == WALL
                and grid[r][c + 1] == WALL
            )

            if (horizontal_open or vertical_open):

                if random.random() < braid_ratio:
                    grid[r][c] = PATH

    # -------------------------------------------------------------------------
    # 4. Set player start and exit
    # -------------------------------------------------------------------------

    grid[1][1] = PLAYER_START

    exit_position = (rows - 2, cols - 2)

    grid[exit_position[0]][exit_position[1]] = EXIT

    # -------------------------------------------------------------------------
    # 5. Make absolutely sure the exit is reachable
    # -------------------------------------------------------------------------

    if not is_solvable(
        grid,
        (1, 1),
        exit_position
    ):

        # Create a guaranteed connection toward the exit
        for c in range(1, cols - 1):
            grid[1][c] = PATH

        for r in range(1, rows - 1):
            grid[r][cols - 2] = PATH

        grid[1][1] = PLAYER_START
        grid[rows - 2][cols - 2] = EXIT

    return grid


# =============================================================================
# SOLVABILITY CHECK
# =============================================================================

def is_solvable(grid, start, goal):
    """
    Check whether the goal can be reached from the start using BFS.
    """

    rows = len(grid)
    cols = len(grid[0])

    queue = deque([start])

    visited = {start}

    while queue:

        current = queue.popleft()

        if current == goal:
            return True

        current_r, current_c = current

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        for dr, dc in directions:

            new_r = current_r + dr
            new_c = current_c + dc

            if not (
                0 <= new_r < rows
                and 0 <= new_c < cols
            ):
                continue

            if grid[new_r][new_c] == WALL:
                continue

            new_position = (new_r, new_c)

            if new_position in visited:
                continue

            visited.add(new_position)
            queue.append(new_position)

    return False


# =============================================================================
# MAZE CLASS
# =============================================================================

class Maze:
    """
    Represents the maze inside Pygame.

    Provides:
    - Maze storage
    - Wall collision rectangles
    - Exit detection
    - Rendering
    - BFS helper functions
    - Grid/pixel conversion
    """

    def __init__(
        self,
        grid=None,
        cell_size=38,
        offset_x=0,
        offset_y=0
    ):

        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        # ---------------------------------------------------------------------
        # Generate the larger maze when no grid is supplied
        # ---------------------------------------------------------------------

        if grid is None:

            self.grid = generate_maze(
                rows=15,
                cols=21,
                seed=42,
                braid_ratio=0.40
            )

        else:

            self.grid = [
                list(row) if isinstance(row, str) else list(row)
                for row in grid
            ]

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

        # ---------------------------------------------------------------------
        # Find player and exit
        # ---------------------------------------------------------------------

        self.player_start = None
        self.exit_pos = None

        self._find_special_cells()

        if self.player_start is None:
            raise ValueError(
                "Maze grid must contain a player start 'P'!"
            )

        if self.exit_pos is None:
            raise ValueError(
                "Maze grid must contain an exit 'E'!"
            )

        # ---------------------------------------------------------------------
        # Create wall collision rectangles
        # ---------------------------------------------------------------------

        self.wall_rects = []

        self._build_wall_rects()

        # ---------------------------------------------------------------------
        # Create exit rectangle
        # ---------------------------------------------------------------------

        exit_row, exit_col = self.exit_pos

        self.exit_rect = pygame.Rect(
            self.offset_x + exit_col * self.cell_size,
            self.offset_y + exit_row * self.cell_size,
            self.cell_size,
            self.cell_size
        )

        # ---------------------------------------------------------------------
        # Outer maze boundary
        # ---------------------------------------------------------------------

        self.bounds_rect = pygame.Rect(
            self.offset_x,
            self.offset_y,
            self.cols * self.cell_size,
            self.rows * self.cell_size
        )

        # Animation timer for exit
        self.animation_timer = 0.0

    # =========================================================================
    # FIND PLAYER AND EXIT
    # =========================================================================

    def _find_special_cells(self):

        for r in range(self.rows):

            for c in range(self.cols):

                cell = self.grid[r][c]

                if cell == PLAYER_START:
                    self.player_start = (r, c)

                elif cell == EXIT:
                    self.exit_pos = (r, c)

    # =========================================================================
    # BUILD WALL COLLISION RECTANGLES
    # =========================================================================

    def _build_wall_rects(self):

        self.wall_rects.clear()

        for r in range(self.rows):

            for c in range(self.cols):

                if self.grid[r][c] == WALL:

                    rect = pygame.Rect(
                        self.offset_x + c * self.cell_size,
                        self.offset_y + r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )

                    self.wall_rects.append(rect)

    # =========================================================================
    # EXIT CHECK
    # =========================================================================

    def check_exit_reached(self, player_rect):

        return player_rect.colliderect(
            self.exit_rect
        )

    # =========================================================================
    # DRAW MAZE
    # =========================================================================

    def draw(self, surface):

        self.animation_timer += 0.05

        # ---------------------------------------------------------------------
        # Colors
        # ---------------------------------------------------------------------

        floor_color = (24, 32, 47)
        grid_line_color = (32, 43, 62)

        wall_color = (45, 55, 75)
        wall_highlight = (65, 80, 108)
        wall_shadow = (28, 35, 48)

        # ---------------------------------------------------------------------
        # Floor
        # ---------------------------------------------------------------------

        pygame.draw.rect(
            surface,
            floor_color,
            self.bounds_rect
        )

        # ---------------------------------------------------------------------
        # Grid lines
        # ---------------------------------------------------------------------

        for r in range(self.rows + 1):

            y = self.offset_y + r * self.cell_size

            pygame.draw.line(
                surface,
                grid_line_color,
                (self.offset_x, y),
                (
                    self.offset_x + self.cols * self.cell_size,
                    y
                ),
                1
            )

        for c in range(self.cols + 1):

            x = self.offset_x + c * self.cell_size

            pygame.draw.line(
                surface,
                grid_line_color,
                (x, self.offset_y),
                (
                    x,
                    self.offset_y + self.rows * self.cell_size
                ),
                1
            )

        # ---------------------------------------------------------------------
        # Walls
        # ---------------------------------------------------------------------

        for r in range(self.rows):

            for c in range(self.cols):

                if self.grid[r][c] != WALL:
                    continue

                wx = self.offset_x + c * self.cell_size
                wy = self.offset_y + r * self.cell_size

                wall_rect = pygame.Rect(
                    wx,
                    wy,
                    self.cell_size,
                    self.cell_size
                )

                pygame.draw.rect(
                    surface,
                    wall_color,
                    wall_rect
                )

                # Highlight
                pygame.draw.line(
                    surface,
                    wall_highlight,
                    (wx, wy),
                    (
                        wx + self.cell_size - 1,
                        wy
                    ),
                    2
                )

                pygame.draw.line(
                    surface,
                    wall_highlight,
                    (wx, wy),
                    (
                        wx,
                        wy + self.cell_size - 1
                    ),
                    2
                )

                # Shadow
                pygame.draw.line(
                    surface,
                    wall_shadow,
                    (
                        wx,
                        wy + self.cell_size - 1
                    ),
                    (
                        wx + self.cell_size - 1,
                        wy + self.cell_size - 1
                    ),
                    2
                )

                pygame.draw.line(
                    surface,
                    wall_shadow,
                    (
                        wx + self.cell_size - 1,
                        wy
                    ),
                    (
                        wx + self.cell_size - 1,
                        wy + self.cell_size - 1
                    ),
                    2
                )

        # ---------------------------------------------------------------------
        # Exit Portal
        # ---------------------------------------------------------------------

        exit_row, exit_col = self.exit_pos

        exit_x = (
            self.offset_x
            + exit_col * self.cell_size
        )

        exit_y = (
            self.offset_y
            + exit_row * self.cell_size
        )

        center = (
            exit_x + self.cell_size // 2,
            exit_y + self.cell_size // 2
        )

        import math

        pulse = (
            math.sin(self.animation_timer * 2.0) + 1.0
        ) / 2.0

        glow_radius = int(
            (self.cell_size // 2 - 2)
            + pulse * 3
        )

        # Exit background
        exit_bg = (16, 50, 40)

        pygame.draw.rect(
            surface,
            exit_bg,
            self.exit_rect,
            border_radius=4
        )

        # Glow
        glow_color = (52, 211, 153)

        pygame.draw.circle(
            surface,
            glow_color,
            center,
            glow_radius,
            2
        )

        # Core
        core_color = (16, 185, 129)

        pygame.draw.circle(
            surface,
            core_color,
            center,
            max(4, self.cell_size // 3)
        )

        # E text
        font = pygame.font.SysFont(
            "Arial",
            max(12, int(self.cell_size * 0.4)),
            bold=True
        )

        text = font.render(
            "E",
            True,
            (255, 255, 255)
        )

        text_rect = text.get_rect(
            center=center
        )

        surface.blit(
            text,
            text_rect
        )

        # ---------------------------------------------------------------------
        # Outer border
        # ---------------------------------------------------------------------

        pygame.draw.rect(
            surface,
            (79, 70, 229),
            self.bounds_rect,
            2
        )

    # =========================================================================
    # BFS / AI INTEGRATION FUNCTIONS
    # =========================================================================

    def get_grid(self):
        """Return the complete 2D maze grid."""

        return self.grid

    def get_player_start(self):
        """Return player starting position as (row, col)."""

        return self.player_start

    def get_exit_pos(self):
        """Return exit position as (row, col)."""

        return self.exit_pos

    def get_walls(self):
        """Return all wall positions."""

        walls = []

        for r in range(self.rows):

            for c in range(self.cols):

                if self.grid[r][c] == WALL:
                    walls.append((r, c))

        return walls

    def get_walkable_positions(self):
        """Return all walkable positions."""

        walkable = []

        for r in range(self.rows):

            for c in range(self.cols):

                if self.grid[r][c] != WALL:
                    walkable.append((r, c))

        return walkable

    def is_walkable(self, row, col):
        """Check whether a grid position is walkable."""

        if (
            0 <= row < self.rows
            and 0 <= col < self.cols
        ):

            return self.grid[row][col] != WALL

        return False

    def get_neighbors(self, row, col):
        """
        Return all valid walkable neighboring cells.

        Used directly by BFS.
        """

        neighbors = []

        directions = [
            (-1, 0),  # Up
            (1, 0),   # Down
            (0, -1),  # Left
            (0, 1)    # Right
        ]

        for dr, dc in directions:

            new_row = row + dr
            new_col = col + dc

            if self.is_walkable(
                new_row,
                new_col
            ):

                neighbors.append(
                    (new_row, new_col)
                )

        return neighbors

    # =========================================================================
    # GRID <-> PIXEL CONVERSION
    # =========================================================================

    def grid_to_pixel(self, row, col):
        """
        Convert grid coordinates to pixel center coordinates.
        """

        pixel_x = (
            self.offset_x
            + col * self.cell_size
            + self.cell_size // 2
        )

        pixel_y = (
            self.offset_y
            + row * self.cell_size
            + self.cell_size // 2
        )

        return (
            pixel_x,
            pixel_y
        )

    def pixel_to_grid(self, x, y):
        """
        Convert pixel coordinates to grid coordinates.
        """

        col = int(
            (x - self.offset_x)
            // self.cell_size
        )

        row = int(
            (y - self.offset_y)
            // self.cell_size
        )

        if (
            0 <= row < self.rows
            and 0 <= col < self.cols
        ):

            return (
                row,
                col
            )

        return None