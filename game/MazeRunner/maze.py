"""
maze.py - Maze Generation and Management Module
Part of Member 1's implementation for "Maze Runner with AI-Controlled Enemy"

Responsible for:
1. Generating/loading a clean 2D grid-based maze.
2. Storing walls ('#'), walkable paths ('0'), player start ('P'), and exit ('E').
3. Providing collision rectangles for Pygame.
4. Rendering the maze (floor, walls, exit portal).
5. Providing structured maze data and helper methods for Member 2's BFS pathfinding.
"""

import random
from collections import deque
import pygame

# Grid symbols as specified:
# '#' = wall
# '0' = walkable path
# 'P' = player start
# 'E' = exit
WALL = '#'
PATH = '0'
PLAYER_START = 'P'
EXIT = 'E'


def generate_maze(rows=15, cols=19, seed=None, braid_ratio=0.15):
    """
    Procedurally generates a 2D maze using the Recursive Backtracker (DFS) algorithm.
    Guarantees a valid, solvable path between player start ('P') and exit ('E').
    
    Args:
        rows (int): Number of rows (must be odd, will be adjusted if even).
        cols (int): Number of columns (must be odd, will be adjusted if even).
        seed (int, optional): Random seed for reproducible maze layouts.
        braid_ratio (float): Probability of removing dead-end walls to create
                             loops for alternative paths (great for BFS & enemy chasing).
    
    Returns:
        list of list of str: 2D grid of characters ('#', '0', 'P', 'E').
    """
    if seed is not None:
        random.seed(seed)

    # Ensure odd dimensions for proper maze generation
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1

    # 1. Initialize grid completely filled with walls
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]

    # 2. Carve passages using Depth-First Search (Recursive Backtracker)
    start_r, start_c = 1, 1
    grid[start_r][start_c] = PATH
    stack = [(start_r, start_c)]

    while stack:
        cr, cc = stack[-1]
        neighbors = []

        # Check neighbors 2 cells away (North, South, West, East)
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = cr + dr, cc + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and grid[nr][nc] == WALL:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            # Pick a random unvisited neighbor and carve path to it
            nr, nc, dr, dc = random.choice(neighbors)
            grid[cr + dr // 2][cc + dc // 2] = PATH  # Wall between
            grid[nr][nc] = PATH                      # Destination cell
            stack.append((nr, nc))
        else:
            stack.pop()

    # 3. Optional Braiding: remove a few walls between paths to create alternative loops
    if braid_ratio > 0:
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == WALL:
                    # Check if wall separates two walkable cells horizontally or vertically
                    horiz_open = (grid[r][c - 1] == PATH and grid[r][c + 1] == PATH and
                                  grid[r - 1][c] == WALL and grid[r + 1][c] == WALL)
                    vert_open = (grid[r - 1][c] == PATH and grid[r + 1][c] == PATH and
                                 grid[r][c - 1] == WALL and grid[r][c + 1] == WALL)
                    if (horiz_open or vert_open) and random.random() < braid_ratio:
                        grid[r][c] = PATH

    # 4. Set player start and exit positions
    grid[1][1] = PLAYER_START
    grid[rows - 2][cols - 2] = EXIT

    # 5. Sanity check: verify that exit is reachable from start via BFS
    if not is_solvable(grid, (1, 1), (rows - 2, cols - 2)):
        # Fallback carve direct connection if ever blocked
        grid[rows - 2][cols - 3] = PATH

    return grid


def is_solvable(grid, start, goal):
    """
    Helper function to verify that a path exists between start and goal.
    Uses standard Breadth-First Search (BFS).
    """
    rows = len(grid)
    cols = len(grid[0])
    queue = deque([start])
    visited = {start}

    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return True

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] != WALL and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    return False


class Maze:
    """
    Represents the grid maze in Pygame.
    Handles storage, rendering, collision rects, and integration APIs for BFS.
    """

    def __init__(self, grid=None, cell_size=38, offset_x=0, offset_y=0):
        """
        Initialize the maze.

        Args:
            grid (list of list or list of str, optional): Pre-defined maze grid.
                If None, a standard solvable maze is procedurally generated.
            cell_size (int): Pixel size for each square cell.
            offset_x (int): Horizontal offset (pixels) to center the maze.
            offset_y (int): Vertical offset (pixels) to center the maze.
        """
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        # If no grid provided, generate a fresh solvable 15x19 maze with fixed seed
        if grid is None:
            self.grid = generate_maze(rows=15, cols=19, seed=42)
        else:
            # Convert list of strings to list of lists if needed
            self.grid = [list(row) if isinstance(row, str) else list(row) for row in grid]

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

        # Automatically locate player start ('P') and exit ('E')
        self.player_start = None
        self.exit_pos = None
        self._find_special_cells()

        if self.player_start is None:
            raise ValueError("Maze grid must contain a player start 'P'!")
        if self.exit_pos is None:
            raise ValueError("Maze grid must contain an exit 'E'!")

        # Pygame Wall rectangles for collision detection
        self.wall_rects = []
        self._build_wall_rects()

        # Pygame Exit rectangle for win condition detection
        er, ec = self.exit_pos
        self.exit_rect = pygame.Rect(
            self.offset_x + ec * self.cell_size,
            self.offset_y + er * self.cell_size,
            self.cell_size,
            self.cell_size
        )

        # Maze outer boundary rectangle
        self.bounds_rect = pygame.Rect(
            self.offset_x,
            self.offset_y,
            self.cols * self.cell_size,
            self.rows * self.cell_size
        )

        # Pulse timer for visual exit animation
        self.animation_timer = 0.0

    def _find_special_cells(self):
        """Scans the grid to automatically find 'P' and 'E' positions."""
        for r in range(self.rows):
            for c in range(self.cols):
                char = self.grid[r][c]
                if char == PLAYER_START:
                    self.player_start = (r, c)
                elif char == EXIT:
                    self.exit_pos = (r, c)

    def _build_wall_rects(self):
        """Constructs Pygame Rect objects for all wall cells."""
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

    def check_exit_reached(self, player_rect):
        """
        Checks if the player's bounding box reaches the exit.

        Args:
            player_rect (pygame.Rect): The player's collision rectangle.

        Returns:
            bool: True if player reached the exit, False otherwise.
        """
        return player_rect.colliderect(self.exit_rect)

    def draw(self, surface):
        """
        Renders the maze onto the Pygame surface with modern, clean styling.
        Floor: Slate-navy dark floor.
        Walls: Sleek indigo blocks with 3D bevels.
        Exit: Glowing emerald green portal.
        """
        self.animation_timer += 0.05

        # 1. Draw maze floor background
        floor_color = (24, 32, 47)      # Dark slate floor
        grid_line_color = (32, 43, 62)  # Subtle floor grid accents
        pygame.draw.rect(surface, floor_color, self.bounds_rect)

        # Subtle cell grid lines for a clean technical look
        for r in range(self.rows + 1):
            y = self.offset_y + r * self.cell_size
            pygame.draw.line(surface, grid_line_color, (self.offset_x, y), (self.offset_x + self.cols * self.cell_size, y), 1)
        for c in range(self.cols + 1):
            x = self.offset_x + c * self.cell_size
            pygame.draw.line(surface, grid_line_color, (x, self.offset_y), (x, self.offset_y + self.rows * self.cell_size), 1)

        # 2. Draw walls with clean modern styling
        wall_color = (45, 55, 75)        # Base wall slate
        wall_highlight = (65, 80, 108)   # Bevel highlight top-left
        wall_shadow = (28, 35, 48)       # Bevel shadow bottom-right

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == WALL:
                    wx = self.offset_x + c * self.cell_size
                    wy = self.offset_y + r * self.cell_size
                    w_rect = pygame.Rect(wx, wy, self.cell_size, self.cell_size)

                    # Base wall block
                    pygame.draw.rect(surface, wall_color, w_rect)

                    # Subtle 3D bevel borders
                    pygame.draw.line(surface, wall_highlight, (wx, wy), (wx + self.cell_size - 1, wy), 2)
                    pygame.draw.line(surface, wall_highlight, (wx, wy), (wx, wy + self.cell_size - 1), 2)
                    pygame.draw.line(surface, wall_shadow, (wx, wy + self.cell_size - 1), (wx + self.cell_size - 1, wy + self.cell_size - 1), 2)
                    pygame.draw.line(surface, wall_shadow, (wx + self.cell_size - 1, wy), (wx + self.cell_size - 1, wy + self.cell_size - 1), 2)

        # 3. Draw Exit Portal ('E')
        er, ec = self.exit_pos
        ex = self.offset_x + ec * self.cell_size
        ey = self.offset_y + er * self.cell_size
        center = (ex + self.cell_size // 2, ey + self.cell_size // 2)

        # Pulsing glow animation
        pulse_val = (random.random() * 0.1) if False else abs(random.random())  # soft static fallback
        import math
        pulse = (math.sin(self.animation_timer * 2.0) + 1.0) / 2.0  # 0.0 to 1.0
        glow_radius = int((self.cell_size // 2 - 2) + pulse * 3)

        # Exit tile background
        exit_bg = (16, 50, 40)
        pygame.draw.rect(surface, exit_bg, self.exit_rect, border_radius=4)

        # Outer glow ring
        glow_color = (52, 211, 153)  # Emerald light
        pygame.draw.circle(surface, glow_color, center, glow_radius, 2)

        # Inner portal core
        core_color = (16, 185, 129)  # Emerald solid
        pygame.draw.circle(surface, core_color, center, max(4, self.cell_size // 3))

        # "E" / EXIT text icon in center
        font = pygame.font.SysFont("Arial", max(12, int(self.cell_size * 0.4)), bold=True)
        txt = font.render("E", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=center)
        surface.blit(txt, txt_rect)

        # 4. Outer boundary border
        pygame.draw.rect(surface, (79, 70, 229), self.bounds_rect, 2)  # Sleek indigo perimeter

    # =========================================================================
    # FUTURE TEAM INTEGRATION API (FOR MEMBER 2 / BFS / ENEMY PATHFINDING)
    # =========================================================================

    def get_grid(self):
        """
        Returns the raw 2D maze grid list.
        Useful for Member 2 to inspect grid[row][col].
        
        Returns:
            list of list of str: 2D array of grid cells ('#', '0', 'P', 'E').
        """
        return self.grid

    def get_player_start(self):
        """
        Returns the (row, col) coordinates of the player's starting cell 'P'.
        
        Returns:
            tuple of (int, int): (start_row, start_col).
        """
        return self.player_start

    def get_exit_pos(self):
        """
        Returns the (row, col) coordinates of the exit cell 'E'.
        
        Returns:
            tuple of (int, int): (exit_row, exit_col).
        """
        return self.exit_pos

    def get_walls(self):
        """
        Returns a list of all (row, col) coordinates occupied by walls.
        
        Returns:
            list of (int, int): Wall cell coordinates.
        """
        walls = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == WALL:
                    walls.append((r, c))
        return walls

    def get_walkable_positions(self):
        """
        Returns a list of all (row, col) walkable positions in the maze
        (cells that are NOT walls).
        
        Returns:
            list of (int, int): Walkable cell coordinates.
        """
        walkable = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != WALL:
                    walkable.append((r, c))
        return walkable

    def is_walkable(self, row, col):
        """
        Checks whether a given (row, col) coordinate is inside the maze
        and is a walkable cell (not a wall).
        
        Args:
            row (int): Row index.
            col (int): Column index.
            
        Returns:
            bool: True if walkable, False if wall or out of bounds.
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] != WALL
        return False

    def get_neighbors(self, row, col):
        """
        Returns all valid, walkable orthogonal neighbor cells (Up, Down, Left, Right).
        This method is tailor-made for Member 2's BFS pathfinding algorithm!
        
        Args:
            row (int): Current cell row.
            col (int): Current cell col.
            
        Returns:
            list of (int, int): Adjacent walkable (next_row, next_col) coordinates.
        """
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def grid_to_pixel(self, row, col):
        """
        Converts grid coordinates (row, col) to screen pixel coordinates (x, y)
        centered within that grid tile.
        
        Returns:
            tuple of (int, int): (pixel_x, pixel_y) center of cell.
        """
        px = self.offset_x + col * self.cell_size + self.cell_size // 2
        py = self.offset_y + row * self.cell_size + self.cell_size // 2
        return (px, py)

    def pixel_to_grid(self, x, y):
        """
        Converts screen pixel coordinates (x, y) to grid coordinates (row, col).
        
        Returns:
            tuple of (int, int): (row, col) or None if out of bounds.
        """
        col = int((x - self.offset_x) // self.cell_size)
        row = int((y - self.offset_y) // self.cell_size)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None
