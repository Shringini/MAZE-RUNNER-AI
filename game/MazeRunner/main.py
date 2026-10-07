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

# Ensure local module directory and project root are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from maze import Maze
from player import Player
from ai.enemy import Enemy
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



def draw_game_over_modal(surface, font_over, font_sub):
    """Draws the game-over dialog when the enemy catches the player."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 23, 42, 185))
    surface.blit(overlay, (0, 0))

    box_w, box_h = 440, 220
    box_x = (WINDOW_WIDTH - box_w) // 2
    box_y = (WINDOW_HEIGHT - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(
        surface,
        (30, 41, 59),
        box_rect,
        border_radius=12
    )

    pygame.draw.rect(
        surface,
        (239, 68, 68),
        box_rect,
        width=3,
        border_radius=12
    )

    game_over_title = font_over.render(
        "GAME OVER",
        True,
        (239, 68, 68)
    )

    title_rect = game_over_title.get_rect(
        center=(WINDOW_WIDTH // 2, box_y + 55)
    )

    surface.blit(game_over_title, title_rect)

    desc_surf = font_sub.render(
        "The AI enemy caught you!",
        True,
        TEXT_WHITE
    )

    desc_rect = desc_surf.get_rect(
        center=(WINDOW_WIDTH // 2, box_y + 115)
    )

    surface.blit(desc_surf, desc_rect)

    hint_surf = font_sub.render(
        "Press [R] to Play Again   •   Press [ESC] to Quit",
        True,
        ACCENT_CYAN
    )

    hint_rect = hint_surf.get_rect(
        center=(WINDOW_WIDTH // 2, box_y + 165)
    )

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
    font_over = pygame.font.SysFont("Trebuchet MS", 38, bold=True)

    # -------------------------------------------------------------------------
    # 1. INITIALIZE MAZE
    # -------------------------------------------------------------------------
    maze_cols = 19
    maze_rows = 15

    offset_x = (WINDOW_WIDTH - (maze_cols * TILE_SIZE)) // 2
    offset_y = 65 + ((WINDOW_HEIGHT - 65 - (maze_rows * TILE_SIZE)) // 2)

    maze = Maze(
        grid=None,
        cell_size=TILE_SIZE,
        offset_x=offset_x,
        offset_y=offset_y
    )

    # -------------------------------------------------------------------------
    # 2. INITIALIZE PLAYER
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

    # -------------------------------------------------------------------------
    # 3. INITIALIZE AI ENEMY
    # -------------------------------------------------------------------------
    enemy_start = maze.get_exit_pos()

    enemy = Enemy(
        maze=maze,
        start_position=enemy_start,
        cell_size=TILE_SIZE,
        offset_x=offset_x,
        offset_y=offset_y,
        speed=2.0
    )

    # Game state
    game_won = False
    game_over = False
    running = True

    # =========================================================================
    # MAIN GAME LOOP
    # =========================================================================
    while running:

        # ---------------------------------------------------------------------
        # 1. EVENT HANDLING
        # ---------------------------------------------------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    # Restart player
                    player.reset_to_start()

                    # Restart enemy
                    enemy = Enemy(
                        maze=maze,
                        start_position=enemy_start,
                        cell_size=TILE_SIZE,
                        offset_x=offset_x,
                        offset_y=offset_y,
                        speed=2.0
                    )

                    game_won = False
                    game_over = False

        # ---------------------------------------------------------------------
        # 2. GAME UPDATE LOGIC
        # ---------------------------------------------------------------------
        if not game_won and not game_over:

            # Update player movement and collision
            player.update(
                maze.wall_rects,
                maze.bounds_rect
            )

            # Get player's current grid position
            player_grid_pos = player.get_grid_position()

            # Enemy follows player using BFS
            enemy.update(player_grid_pos)

            # Check if enemy catches player
            if enemy.caught_player(player):
                game_over = True

            # Check if player reaches exit
            elif maze.check_exit_reached(player.rect):
                game_won = True

        # ---------------------------------------------------------------------
        # 3. RENDERING
        # ---------------------------------------------------------------------
        screen.fill(BG_COLOR)

        # Header
        draw_header(
            screen,
            font_title,
            font_sub
        )

        # Maze
        maze.draw(screen)

        # Enemy
        enemy.draw(screen)

        # Player
        player.draw(screen)

        # Victory screen
        if game_won:
            draw_victory_modal(
                screen,
                font_win,
                font_sub
            )

        # Game-over screen
        elif game_over:
            draw_game_over_modal(
                screen,
                font_over,
                font_sub
            )

        # Refresh display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    
