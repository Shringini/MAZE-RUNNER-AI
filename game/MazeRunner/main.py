"""
main.py - Main Game Loop and Application Entry Point
Part of Member 1's implementation for "Maze Runner with AI-Controlled Enemy"

Responsible for:
1. Initializing Pygame and creating the game window.
2. Instantiating the Maze and Player components.
3. Managing the 60 FPS game loop.
4. Routing input and updating movement, wall collisions, and boundaries.
5. Detecting exit condition and rendering the "YOU WIN!" victory screen.
"""

import sys
import os
import pygame

# Ensure local module directory is in sys.path for clean imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from maze import Maze
from player import Player

# -----------------------------------------------------------------------------
# GAME CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------
WINDOW_WIDTH = 820
WINDOW_HEIGHT = 700
FPS = 60
TILE_SIZE = 38

# Color Palette (Modern Dark Slate / Cyber Aesthetic)
BG_COLOR = (15, 23, 42)          # Deep slate navy (#0F172A)
HEADER_BG = (24, 32, 47)         # Panel header (#18202F)
BORDER_COLOR = (51, 65, 85)      # Slate border (#334155)
TEXT_WHITE = (248, 250, 252)     # Off-white (#F8FAFC)
TEXT_MUTED = (148, 163, 184)     # Slate text (#94A3B8)
ACCENT_CYAN = (56, 189, 248)     # Cyan highlight (#38BDF8)
EMERALD_GREEN = (16, 185, 129)   # Emerald win color (#10B981)


def draw_header(surface, font_title, font_sub):
    """Draws the top title bar and controls guide."""
    # Top banner background
    header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 65)
    pygame.draw.rect(surface, HEADER_BG, header_rect)
    pygame.draw.line(surface, BORDER_COLOR, (0, 65), (WINDOW_WIDTH, 65), 1)

    # Title text
    title_surf = font_title.render("MAZE RUNNER", True, ACCENT_CYAN)
    surface.blit(title_surf, (30, 12))

    # Controls instructions
    controls_text = "Move: WASD / Arrow Keys   |   Restart: [R]   |   Quit: [ESC]"
    controls_surf = font_sub.render(controls_text, True, TEXT_MUTED)
    controls_rect = controls_surf.get_rect(midright=(WINDOW_WIDTH - 30, 32))
    surface.blit(controls_surf, controls_rect)


def draw_victory_modal(surface, font_win, font_sub):
    """Draws an attractive victory dialog overlay when player reaches the exit."""
    # 1. Dark semi-transparent backdrop
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 23, 42, 185))
    surface.blit(overlay, (0, 0))

    # 2. Centered dialog box
    box_w, box_h = 440, 220
    box_x = (WINDOW_WIDTH - box_w) // 2
    box_y = (WINDOW_HEIGHT - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(surface, (30, 41, 59), box_rect, border_radius=12)
    pygame.draw.rect(surface, EMERALD_GREEN, box_rect, width=3, border_radius=12)

    # 3. Victory texts
    win_title = font_win.render("YOU WIN!", True, EMERALD_GREEN)
    win_title_rect = win_title.get_rect(center=(WINDOW_WIDTH // 2, box_y + 55))
    surface.blit(win_title, win_title_rect)

    desc_surf = font_sub.render("You successfully navigated the maze to the exit!", True, TEXT_WHITE)
    desc_rect = desc_surf.get_rect(center=(WINDOW_WIDTH // 2, box_y + 115))
    surface.blit(desc_surf, desc_rect)

    hint_surf = font_sub.render("Press [R] to Play Again   •   Press [ESC] to Quit", True, ACCENT_CYAN)
    hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, box_y + 165))
    surface.blit(hint_surf, hint_rect)


def main():
    """Main game function."""
    pygame.init()
    pygame.display.set_caption("Maze Runner")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Typography
    font_title = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
    font_sub = pygame.font.SysFont("Arial", 15)
    font_win = pygame.font.SysFont("Trebuchet MS", 38, bold=True)

    # -------------------------------------------------------------------------
    # 1. INITIALIZE MAZE
    # -------------------------------------------------------------------------
    # Maze dimensions: 15 rows x 19 cols
    # Maze pixel size: 19 * 38 = 722px wide, 15 * 38 = 570px high
    # Center maze within the window below the header (header is 65px)
    maze_cols = 19
    maze_rows = 15
    offset_x = (WINDOW_WIDTH - (maze_cols * TILE_SIZE)) // 2
    offset_y = 65 + ((WINDOW_HEIGHT - 65 - (maze_rows * TILE_SIZE)) // 2)

    # Create maze (automatically generates a solvable 15x19 grid)
    maze = Maze(grid=None, cell_size=TILE_SIZE, offset_x=offset_x, offset_y=offset_y)

    # -------------------------------------------------------------------------
    # 2. INITIALIZE PLAYER (at starting cell 'P' from the maze)
    # -------------------------------------------------------------------------
    start_row, start_col = maze.get_player_start()
    player = Player(
        start_row=start_row,
        start_col=start_col,
        cell_size=TILE_SIZE,
        offset_x=offset_x,
        offset_y=offset_y,
        speed=3.6
    )

    # Game state variables
    game_won = False
    running = True

    # =========================================================================
    # MAIN GAME LOOP
    # =========================================================================
    while running:
        # 1. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset player back to starting position and reset win state
                    player.reset_to_start()
                    game_won = False

        # 2. GAME UPDATE LOGIC
        if not game_won:
            # Update player movement with wall collisions and boundary constraints
            player.update(maze.wall_rects, maze.bounds_rect)

            # Check if player has reached the exit tile 'E'
            if maze.check_exit_reached(player.rect):
                game_won = True

            # -----------------------------------------------------------------
            # NOTE FOR MEMBER 2 (AI ENEMY INTEGRATION):
            # When implementing enemy AI with BFS:
            # 1. Obtain player's grid position: player_grid_pos = player.get_grid_position()
            # 2. Run your BFS algorithm using maze.get_neighbors(r, c) or maze.get_grid()
            # 3. Update enemy movement along the computed shortest path!
            # -----------------------------------------------------------------

        # 3. RENDERING
        screen.fill(BG_COLOR)

        # Draw Header
        draw_header(screen, font_title, font_sub)

        # Draw Maze (Floor, Walls, Exit Portal)
        maze.draw(screen)

        # Draw Player
        player.draw(screen)

        # Draw Victory Screen if Win condition met
        if game_won:
            draw_victory_modal(screen, font_win, font_sub)

        # Refresh display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
