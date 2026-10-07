"""
================================================================================
MAZE RUNNER - MAIN APPLICATION ENTRY POINT (main.py)
================================================================================
Hackathon Project: Maze Runner with AI-Controlled Enemy
Technology: Python, Pygame, BFS Pathfinding

Architecture:
  - ui.py: Member 3 (UI/UX, visual styling, animations, HUD, coins, screens)
  - bfs.py: Member 1 (BFS shortest-path search algorithm)
  - game_logic.py: Member 2 (State transitions, rules, coins, 3 levels)
  - main.py: Integration loop coordinating events, updates, and rendering.

Window Dimensions:
  Width: 1000px, Height: 700px
================================================================================
"""

import sys
import pygame

import ui
from game_logic import GameManager


def main():
    # 1. Initialize Pygame Environment
    pygame.init()
    pygame.font.init()

    # Configure responsive key-repeat for smooth tile-by-tile movement
    # (Delay: 220ms, Interval: 140ms. Stops immediately when key is released.)
    pygame.key.set_repeat(220, 140)

    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Runner // AI-Controlled Pursuit (BFS)")
    clock = pygame.time.Clock()

    # 2. Viewport Layout (Left: Maze Game Area, Right: Telemetry HUD)
    MAZE_VIEWPORT = pygame.Rect(20, 52, 690, 628)
    HUD_RECT = pygame.Rect(725, 52, 255, 628)

    # 3. Instantiate Game Manager
    game = GameManager()

    # Dynamic button rect trackers for active modal interaction
    active_buttons = {}

    running = True
    while running:
        current_ticks = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        # ----------------------------------------------------------------------
        # EVENT HANDLING
        # ----------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # KEYBOARD INPUTS
            elif event.type == pygame.KEYDOWN:
                if game.state == "MENU":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        game.start_game(current_ticks)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif game.state == "PLAYING":
                    # Human Player movement: ONLY moves on explicit keypress
                    if event.key in (pygame.K_w, pygame.K_UP):
                        game.move_player(-1, 0)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        game.move_player(1, 0)
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        game.move_player(0, -1)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        game.move_player(0, 1)
                    # Quick level retry
                    elif event.key == pygame.K_r:
                        game.retry_level(current_ticks)
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

                elif game.state == "WIN":
                    # Advance to Next Level
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        game.next_level(current_ticks)
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

                elif game.state == "FINAL_WIN":
                    # Restart Complete Campaign from Level 1
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                        game.start_game(current_ticks)
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

                elif game.state == "GAME_OVER":
                    # Retry Current Level
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                        game.retry_level(current_ticks)
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

            # MOUSE CLICKS ON UI BUTTONS
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state == "MENU":
                    if active_buttons.get("start_button") and active_buttons["start_button"].collidepoint(mouse_pos):
                        game.start_game(current_ticks)
                    elif active_buttons.get("quit_button") and active_buttons["quit_button"].collidepoint(mouse_pos):
                        running = False

                elif game.state == "WIN":
                    if active_buttons.get("next_button") and active_buttons["next_button"].collidepoint(mouse_pos):
                        game.next_level(current_ticks)
                    elif active_buttons.get("menu_button") and active_buttons["menu_button"].collidepoint(mouse_pos):
                        game.state = "MENU"

                elif game.state == "FINAL_WIN":
                    if active_buttons.get("play_again_button") and active_buttons["play_again_button"].collidepoint(mouse_pos):
                        game.start_game(current_ticks)
                    elif active_buttons.get("menu_button") and active_buttons["menu_button"].collidepoint(mouse_pos):
                        game.state = "MENU"

                elif game.state == "GAME_OVER":
                    if active_buttons.get("retry_button") and active_buttons["retry_button"].collidepoint(mouse_pos):
                        game.retry_level(current_ticks)
                    elif active_buttons.get("menu_button") and active_buttons["menu_button"].collidepoint(mouse_pos):
                        game.state = "MENU"

        # ----------------------------------------------------------------------
        # GAME STATE UPDATES
        # ----------------------------------------------------------------------
        if game.state == "PLAYING":
            game.update_timer(current_ticks)
            game.update_enemy(current_ticks)

        # ----------------------------------------------------------------------
        # RENDERING PIPELINE (Delegated cleanly to ui.py)
        # ----------------------------------------------------------------------
        if game.state == "MENU":
            active_buttons = ui.draw_start_screen(screen, WINDOW_WIDTH, WINDOW_HEIGHT, mouse_pos)

        elif game.state == "PLAYING":
            screen.fill(ui.BACKGROUND)
            ui.draw_top_bar(screen, WINDOW_WIDTH, fps=clock.get_fps())

            cell_size, offset_x, offset_y = ui.calculate_viewport(game.maze, MAZE_VIEWPORT)

            # 1. Base Maze Grid
            ui.draw_maze(screen, game.maze, cell_size, offset_x, offset_y)

            # 2. AI BFS Path Visualization
            ui.draw_ai_path(screen, game.ai_path, cell_size, offset_x, offset_y)

            # 3. Collectible Coins
            ui.draw_coins(screen, game.coins, cell_size, offset_x, offset_y)

            # 4. Extraction Exit
            ui.draw_exit(screen, game.exit_pos, cell_size, offset_x, offset_y)

            # 5. Player Character (Human-Controlled)
            ui.draw_player(screen, game.player_pos, cell_size, offset_x, offset_y)

            # 6. Enemy AI Hunter
            ui.draw_enemy(screen, game.enemy_pos, cell_size, offset_x, offset_y)

            # 7. Telemetry HUD
            ui.draw_hud(screen, game.get_telemetry_for_ui(), HUD_RECT)

        elif game.state == "WIN":
            # Contextual game board underneath
            screen.fill(ui.BACKGROUND)
            ui.draw_top_bar(screen, WINDOW_WIDTH, fps=clock.get_fps())
            cell_size, offset_x, offset_y = ui.calculate_viewport(game.maze, MAZE_VIEWPORT)
            ui.draw_maze(screen, game.maze, cell_size, offset_x, offset_y)
            ui.draw_ai_path(screen, game.ai_path, cell_size, offset_x, offset_y)
            ui.draw_coins(screen, game.coins, cell_size, offset_x, offset_y)
            ui.draw_exit(screen, game.exit_pos, cell_size, offset_x, offset_y)
            ui.draw_player(screen, game.player_pos, cell_size, offset_x, offset_y)
            ui.draw_enemy(screen, game.enemy_pos, cell_size, offset_x, offset_y)
            ui.draw_hud(screen, game.get_telemetry_for_ui(), HUD_RECT)

            # Level Victory Modal
            active_buttons = ui.draw_victory_screen(screen, game.get_telemetry_for_ui(), WINDOW_WIDTH, WINDOW_HEIGHT, mouse_pos)

        elif game.state == "FINAL_WIN":
            # Contextual game board underneath
            screen.fill(ui.BACKGROUND)
            ui.draw_top_bar(screen, WINDOW_WIDTH, fps=clock.get_fps())
            cell_size, offset_x, offset_y = ui.calculate_viewport(game.maze, MAZE_VIEWPORT)
            ui.draw_maze(screen, game.maze, cell_size, offset_x, offset_y)
            ui.draw_exit(screen, game.exit_pos, cell_size, offset_x, offset_y)
            ui.draw_player(screen, game.player_pos, cell_size, offset_x, offset_y)
            ui.draw_enemy(screen, game.enemy_pos, cell_size, offset_x, offset_y)
            ui.draw_hud(screen, game.get_telemetry_for_ui(), HUD_RECT)

            # Final Grand Victory Modal
            active_buttons = ui.draw_final_victory_screen(screen, game.get_telemetry_for_ui(), WINDOW_WIDTH, WINDOW_HEIGHT, mouse_pos)

        elif game.state == "GAME_OVER":
            # Contextual game board underneath
            screen.fill(ui.BACKGROUND)
            ui.draw_top_bar(screen, WINDOW_WIDTH, fps=clock.get_fps())
            cell_size, offset_x, offset_y = ui.calculate_viewport(game.maze, MAZE_VIEWPORT)
            ui.draw_maze(screen, game.maze, cell_size, offset_x, offset_y)
            ui.draw_ai_path(screen, game.ai_path, cell_size, offset_x, offset_y)
            ui.draw_coins(screen, game.coins, cell_size, offset_x, offset_y)
            ui.draw_exit(screen, game.exit_pos, cell_size, offset_x, offset_y)
            ui.draw_player(screen, game.player_pos, cell_size, offset_x, offset_y)
            ui.draw_enemy(screen, game.enemy_pos, cell_size, offset_x, offset_y)
            ui.draw_hud(screen, game.get_telemetry_for_ui(), HUD_RECT)

            # Game Over Modal
            active_buttons = ui.draw_game_over_screen(screen, game.get_telemetry_for_ui(), WINDOW_WIDTH, WINDOW_HEIGHT, mouse_pos)

        # ----------------------------------------------------------------------
        # DISPLAY FLIP & FRAME REGULATION
        # ----------------------------------------------------------------------
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
