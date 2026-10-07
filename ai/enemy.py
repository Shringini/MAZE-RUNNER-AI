import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pygame

from ai.bfs import bfs
from game.MazeRunner.maze import Maze


class Enemy:
    """
    AI-controlled enemy for the Maze Runner game.

    The enemy:
    - Starts at a specified maze grid position.
    - Uses BFS to find the shortest path to the player.
    - Moves one maze cell at a time.
    - Uses the Maze class to determine valid paths.
    - Converts grid positions to pixel positions for Pygame.
    """

    def __init__(
        self,
        maze,
        start_position,
        cell_size=38,
        offset_x=0,
        offset_y=0,
        speed=2.0
    ):
        """
        Args:
            maze: Maze object from maze.py.
            start_position: (row, col) starting grid position.
            cell_size: Size of one maze cell in pixels.
            offset_x: Horizontal maze offset.
            offset_y: Vertical maze offset.
            speed: Enemy movement speed in pixels per frame.
        """

        self.maze = maze

        # Current grid position
        self.position = start_position

        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.speed = speed

        # BFS path
        self.path = []

        # Current target cell
        self.target_position = None

        # Convert starting grid position to pixel position
        start_x, start_y = self.maze.grid_to_pixel(
            start_position[0],
            start_position[1]
        )

        # Enemy size
        self.size = max(16, int(cell_size * 0.65))

        # Enemy collision rectangle
        self.rect = pygame.Rect(
            0,
            0,
            self.size,
            self.size
        )

        self.rect.center = (start_x, start_y)

        # Floating-point position for smooth movement
        self.pos_x = float(self.rect.centerx)
        self.pos_y = float(self.rect.centery)

        # Direction the enemy is facing
        self.facing_dir = (1, 0)

        # Animation timer
        self.animation_timer = 0.0

    # ============================================================
    # GRID POSITION
    # ============================================================

    def get_grid_position(self):
        """
        Return the enemy's current maze grid position.

        Returns:
            (row, col)
        """

        return self.maze.pixel_to_grid(
            self.rect.centerx,
            self.rect.centery
        )

    # ============================================================
    # FIND BFS PATH
    # ============================================================

    def find_path(self, player_position):
        """
        Calculate the shortest path from the enemy
        to the player's current grid position.

        Args:
            player_position: (row, col)

        Returns:
            BFS path as a list of grid positions.
        """

        self.position = self.get_grid_position()

        self.path = bfs(
            self.maze,
            self.position,
            player_position
        )

        # Remove the current enemy cell.
        # The next cell is where the enemy should move.
        if len(self.path) > 1:
            self.path = self.path[1:]
        else:
            self.path = []

        return self.path

    # ============================================================
    # MOVE TOWARD NEXT CELL
    # ============================================================

    def move_toward_target(self):
        """
        Smoothly move the enemy toward the next BFS cell.
        """

        if self.target_position is None:
            return

        # Convert target grid cell to pixel coordinates
        target_x, target_y = self.maze.grid_to_pixel(
            self.target_position[0],
            self.target_position[1]
        )

        dx = target_x - self.pos_x
        dy = target_y - self.pos_y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        # Target reached
        if distance <= self.speed:

            self.pos_x = float(target_x)
            self.pos_y = float(target_y)

            self.rect.center = (
                target_x,
                target_y
            )

            # Update grid position
            self.position = self.target_position

            # Target completed
            self.target_position = None

            return

        # Normalize movement direction
        dx /= distance
        dy /= distance

        # Update facing direction
        if abs(dx) >= abs(dy):
            self.facing_dir = (
                1 if dx > 0 else -1,
                0
            )
        else:
            self.facing_dir = (
                0,
                1 if dy > 0 else -1
            )

        # Move smoothly
        self.pos_x += dx * self.speed
        self.pos_y += dy * self.speed

        self.rect.center = (
            round(self.pos_x),
            round(self.pos_y)
        )

    # ============================================================
    # UPDATE ENEMY
    # ============================================================

    def update(self, player_position):
        """
        Update enemy AI.

        The enemy:
        1. Gets its current grid position.
        2. Calculates a BFS path to the player.
        3. Selects the next cell.
        4. Moves toward that cell.

        Args:
            player_position: (row, col)

        Returns:
            Current enemy grid position.
        """

        self.animation_timer += 0.1

        # Current enemy grid position
        self.position = self.get_grid_position()

        # If enemy has no target, find a path
        if self.target_position is None:

            path = self.find_path(
                player_position
            )

            if path:
                self.target_position = path[0]

        # Move toward target
        self.move_toward_target()

        return self.get_grid_position()

    # ============================================================
    # CHECK IF ENEMY CAUGHT PLAYER
    # ============================================================

    def caught_player(self, player):
        """
        Check whether the enemy has collided with the player.

        Args:
            player: Player object.

        Returns:
            True if enemy caught player.
        """

        return self.rect.colliderect(
            player.rect
        )

    # ============================================================
    # DRAW ENEMY
    # ============================================================

    def draw(self, surface):
        """
        Draw the enemy on the Pygame screen.
        """

        cx, cy = self.rect.center

        radius = self.size // 2

        # --------------------------------------------------------
        # Outer glow
        # --------------------------------------------------------

        glow_color = (220, 38, 38)

        pygame.draw.circle(
            surface,
            glow_color,
            (cx, cy),
            radius + 4,
            2
        )

        # --------------------------------------------------------
        # Enemy body
        # --------------------------------------------------------

        body_color = (239, 68, 68)

        pygame.draw.circle(
            surface,
            body_color,
            (cx, cy),
            radius
        )

        # --------------------------------------------------------
        # Inner body
        # --------------------------------------------------------

        inner_color = (248, 113, 113)

        pygame.draw.circle(
            surface,
            inner_color,
            (cx, cy),
            max(4, radius // 2)
        )

        # --------------------------------------------------------
        # Directional eyes
        # --------------------------------------------------------

        fx, fy = self.facing_dir

        eye_color = (20, 20, 30)

        eye_offset = max(
            3,
            radius // 3
        )

        if fx != 0:

            eye_x = cx + fx * eye_offset

            pygame.draw.circle(
                surface,
                eye_color,
                (eye_x, cy - 3),
                2
            )

            pygame.draw.circle(
                surface,
                eye_color,
                (eye_x, cy + 3),
                2
            )

        else:

            eye_y = cy + fy * eye_offset

            pygame.draw.circle(
                surface,
                eye_color,
                (cx - 3, eye_y),
                2
            )

            pygame.draw.circle(
                surface,
                eye_color,
                (cx + 3, eye_y),
                2
            )


# ================================================================
# SIMPLE TEST
# ================================================================

if __name__ == "__main__":

    pygame.init()

    # Create the same type of Maze used by the game
    maze = Maze(
        cell_size=38
    )

    # Start enemy at a walkable cell.
    # Here we use the maze player start as an example.
    start_position = maze.get_player_start()

    enemy = Enemy(
        maze,
        start_position,
        cell_size=38,
        speed=2.0
    )

    # Use the exit as a test target
    player_position = maze.get_exit_pos()

    print("Enemy starting position:")
    print(enemy.position)

    print("\nFinding BFS path...")

    path = enemy.find_path(
        player_position
    )

    print("BFS path:")
    print(path)

    print("\nEnemy target:")
    print(enemy.target_position)

    pygame.quit()