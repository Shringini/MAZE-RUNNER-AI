"""
player.py - Player Character and Movement Module
Part of Member 1's implementation for "Maze Runner with AI-Controlled Enemy"

Responsible for:
1. Initializing the player at the start cell 'P' from the maze.
2. Handling smooth keyboard movement (WASD or Arrow keys).
3. Implementing robust axis-separated AABB wall collision (sliding along walls).
4. Enforcing maze boundaries so the player never escapes.
5. Drawing an attractive, animated character with directional indicators.
6. Exposing the player's current grid position for Member 2's BFS enemy AI.
"""

import math
import pygame


class Player:
    """
    Represents the user-controlled player character in the maze.
    """

    def __init__(self, start_row, start_col, cell_size=38, offset_x=0, offset_y=0, speed=3.5):
        """
        Initialize player at the detected start position ('P').

        Args:
            start_row (int): Starting grid row index (detected from 'P').
            start_col (int): Starting grid column index (detected from 'P').
            cell_size (int): Size of each grid cell in pixels.
            offset_x (int): Horizontal maze screen offset.
            offset_y (int): Vertical maze screen offset.
            speed (float): Movement speed in pixels per frame.
        """
        self.start_row = start_row
        self.start_col = start_col
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.speed = speed

        # Hitbox size is slightly smaller than cell size (e.g., ~68%)
        # This provides smooth cornering and prevents snagging when turning into corridors
        self.size = max(16, int(cell_size * 0.68))

        # Collision rectangle & floating-point position for precision
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.reset_to_start()

        # Direction vector player is currently facing: (dx, dy)
        # Default facing right (1, 0)
        self.facing_dir = (1, 0)

        # Subtle walk bobbing animation timer
        self.step_counter = 0.0

    def reset_to_start(self):
        """Resets the player to the original starting cell."""
        # Calculate pixel center of the starting cell
        center_x = self.offset_x + self.start_col * self.cell_size + self.cell_size // 2
        center_y = self.offset_y + self.start_row * self.cell_size + self.cell_size // 2
        self.rect.center = (center_x, center_y)

        # Store precise floating point coordinates
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def handle_input(self):
        """
        Reads user keyboard input for Arrow keys or WASD.

        Returns:
            tuple of (float, float): Normalized movement direction (dx, dy).
        """
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        # Horizontal movement: A / Left or D / Right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0

        # Vertical movement: W / Up or S / Down
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0

        # Normalize diagonal movement so diagonal speed matches orthogonal speed
        if dx != 0.0 and dy != 0.0:
            inv_len = 1.0 / math.sqrt(2.0)
            dx *= inv_len
            dy *= inv_len

        return dx * self.speed, dy * self.speed

    def update(self, wall_rects, bounds_rect):
        """
        Updates player movement and handles wall collisions.
        Uses separate X and Y collision resolution to allow smooth sliding along walls.

        Args:
            wall_rects (list of pygame.Rect): List of maze wall collision rectangles.
            bounds_rect (pygame.Rect): Bounding rectangle of the entire maze.
        """
        dx, dy = self.handle_input()

        # Update facing direction if moving
        if dx != 0.0 or dy != 0.0:
            # Determine primary facing axis
            if abs(dx) >= abs(dy):
                self.facing_dir = (1 if dx > 0 else -1, 0)
            else:
                self.facing_dir = (0, 1 if dy > 0 else -1)
            self.step_counter += 0.2

        # -----------------------------------------------------------------
        # STEP 1: X-Axis Movement & Wall Collision
        # -----------------------------------------------------------------
        if dx != 0.0:
            self.pos_x += dx
            self.rect.x = round(self.pos_x)

            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if dx > 0:  # Moving Right -> Hit Left side of wall
                        self.rect.right = wall.left
                    elif dx < 0:  # Moving Left -> Hit Right side of wall
                        self.rect.left = wall.right
                    # Synchronize float position with resolved collision boundary
                    self.pos_x = float(self.rect.x)

        # -----------------------------------------------------------------
        # STEP 2: Y-Axis Movement & Wall Collision (Allows sliding along walls)
        # -----------------------------------------------------------------
        if dy != 0.0:
            self.pos_y += dy
            self.rect.y = round(self.pos_y)

            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if dy > 0:  # Moving Down -> Hit Top side of wall
                        self.rect.bottom = wall.top
                    elif dy < 0:  # Moving Up -> Hit Bottom side of wall
                        self.rect.top = wall.bottom
                    # Synchronize float position with resolved collision boundary
                    self.pos_y = float(self.rect.y)

        # -----------------------------------------------------------------
        # STEP 3: Boundary Clamping (Player cannot escape the maze)
        # -----------------------------------------------------------------
        if bounds_rect:
            # Constrain player inside the outer maze rectangle
            if self.rect.left < bounds_rect.left:
                self.rect.left = bounds_rect.left
                self.pos_x = float(self.rect.x)
            if self.rect.right > bounds_rect.right:
                self.rect.right = bounds_rect.right
                self.pos_x = float(self.rect.x)
            if self.rect.top < bounds_rect.top:
                self.rect.top = bounds_rect.top
                self.pos_y = float(self.rect.y)
            if self.rect.bottom > bounds_rect.bottom:
                self.rect.bottom = bounds_rect.bottom
                self.pos_y = float(self.rect.y)

    def get_grid_position(self):
        """
        Calculates and returns the player's current (row, col) position in the maze.
        Based on the center point of the player's rectangle.
        CRITICAL for Member 2's BFS algorithm so the enemy knows where the player is.

        Returns:
            tuple of (int, int): Current (row, col) coordinates.
        """
        col = int((self.rect.centerx - self.offset_x) // self.cell_size)
        row = int((self.rect.centery - self.offset_y) // self.cell_size)
        return (row, col)

    def draw(self, surface):
        """
        Renders the player character on screen.
        Clean, modern aesthetic:
        - Outer glow aura.
        - Vibrant cyan body circle.
        - Directional eye dots / visor pointing in the direction of movement.
        """
        cx, cy = self.rect.center
        radius = self.size // 2

        # 1. Outer cyan glow ring
        glow_color = (14, 165, 233, 100)
        pygame.draw.circle(surface, (14, 116, 160), (cx, cy), radius + 2, 2)

        # 2. Main character body (Bright Sky Blue / Cyan)
        body_color = (56, 189, 248)  # #38BDF8
        pygame.draw.circle(surface, body_color, (cx, cy), radius)

        # 3. Inner core highlight
        core_color = (186, 230, 253)  # #BAE6FD
        pygame.draw.circle(surface, core_color, (cx, cy), max(2, radius // 2))

        # 4. Directional eyes / visor showing facing direction
        fx, fy = self.facing_dir
        eye_color = (15, 23, 42)  # Dark slate eye dots

        eye_offset = max(3, radius // 3)
        if fx != 0:  # Facing horizontal
            eye_x = cx + fx * eye_offset
            pygame.draw.circle(surface, eye_color, (eye_x, cy - 3), 2)
            pygame.draw.circle(surface, eye_color, (eye_x, cy + 3), 2)
        else:  # Facing vertical
            eye_y = cy + fy * eye_offset
            pygame.draw.circle(surface, eye_color, (cx - 3, eye_y), 2)
            pygame.draw.circle(surface, eye_color, (cx + 3, eye_y), 2)
