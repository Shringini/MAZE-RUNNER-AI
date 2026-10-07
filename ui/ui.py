"""
================================================================================
MAZE RUNNER - UI / UX & VISUAL DESIGN MODULE (ui.py)
================================================================================
Role: Member 3 - UI/UX + Pygame Visual Design
Tech: Python + Pygame

Description:
  Handles all visual presentation, futuristic dark-theme styling, HUD rendering,
  BFS path visualization, coins, player/enemy/exit visual effects, and state screens
  (Start, Level Victory, Final Victory, Game Over).

Design Principles:
  - Pure presentation layer: accepts game data and renders visuals.
  - Zero pathfinding or game-rule logic inside this module.
  - Responsive: dynamically scales to any maze dimensions (not hardcoded to 10x10).
  - High performance: cached fonts and precomputed surfaces for smooth 60 FPS.
================================================================================
"""

import math
import pygame

# ==============================================================================
# 1. COLOR PALETTE (Dark Futuristic AI Theme)
# ==============================================================================
# Core colors defined by project specification
BACKGROUND = (10, 12, 20)          # Void Navy / Dark Background
WALL = (35, 45, 75)                # Futuristic Indigo Wall
PATH = (18, 22, 35)                # Dark Sector Floor
PLAYER = (50, 220, 255)            # Cyber Neon Cyan
ENEMY = (255, 70, 80)              # Alert Crimson Red
EXIT = (70, 240, 140)              # Extraction Emerald Green
BFS_PATH = (255, 210, 60)          # AI Calculation Amber Gold
COIN = (255, 200, 50)              # Collectible Gold Coin
WHITE = (240, 240, 240)            # Crisp Text White
GRAY = (150, 160, 180)             # Muted Telemetry Gray

# Polished UI & Accent Colors
PANEL_BG = (14, 18, 28)            # HUD Panel Background
PANEL_HEADER = (20, 26, 42)        # HUD Card Header
PANEL_BORDER = (40, 55, 88)        # Tech Border Frame
PANEL_BORDER_ACCENT = (50, 220, 255)  # Cyan Border Glow
WALL_HIGHLIGHT = (55, 70, 115)     # Wall 3D Edge Bevel
GRID_LINE = (24, 30, 48)           # Subtle Floor Grid Lines
BUTTON_BG = (22, 30, 50)           # Normal Button Face
BUTTON_HOVER = (38, 56, 92)        # Hovered Button Face
BUTTON_BORDER = (65, 110, 180)     # Normal Button Border
BUTTON_BORDER_HOVER = (50, 220, 255) # Hovered Cyan Glow Border
COIN_BORDER = (200, 150, 25)       # Coin Edge Ring
COIN_HIGHLIGHT = (255, 245, 180)   # Coin Specular Reflection


# ==============================================================================
# 2. FONT SYSTEM (Cached, Scalable Typography)
# ==============================================================================
class FontManager:
    """Centralized font cache to avoid recreating font instances every frame."""
    _fonts = {}

    @classmethod
    def get(cls, size=18, bold=False, mono=False):
        key = (size, bold, mono)
        if key not in cls._fonts:
            if mono:
                # Monospaced font for telemetry, coordinates, and timings
                font_names = ["Consolas", "Lucida Console", "Courier New", "monospace"]
            else:
                # Modern sans font for titles and labels
                font_names = ["Segoe UI", "Helvetica Neue", "Arial", "sans-serif"]
            cls._fonts[key] = pygame.font.SysFont(font_names, size, bold=bold)
        return cls._fonts[key]


# ==============================================================================
# 3. RESPONSIVE VIEWPORT & COORDINATE CONVERSION
# ==============================================================================
def calculate_viewport(maze, available_rect):
    """
    Dynamically computes cell_size and (offset_x, offset_y) so any maze
    dimensions fit neatly and stay centered within available_rect.
    """
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 1

    max_cell_w = available_rect.width // cols
    max_cell_h = available_rect.height // rows
    cell_size = max(8, min(max_cell_w, max_cell_h))

    maze_w = cols * cell_size
    maze_h = rows * cell_size

    offset_x = available_rect.left + (available_rect.width - maze_w) // 2
    offset_y = available_rect.top + (available_rect.height - maze_h) // 2

    return cell_size, offset_x, offset_y


def grid_to_pixel(row, col, cell_size, offset_x=0, offset_y=0):
    """Converts a (row, column) grid coordinate to top-left pixel (x, y)."""
    return offset_x + col * cell_size, offset_y + row * cell_size


def grid_to_center(row, col, cell_size, offset_x=0, offset_y=0):
    """Converts a (row, column) grid coordinate to the center pixel (cx, cy)."""
    return (offset_x + col * cell_size + cell_size // 2,
            offset_y + row * cell_size + cell_size // 2)


# ==============================================================================
# 4. MAZE RENDERING
# ==============================================================================
def draw_maze(screen, maze, cell_size, offset_x=0, offset_y=0):
    """
    Renders walls and walkable paths for any grid dimension.
    - Distinct 3D futuristic partition effect on walls.
    - Subtle cyber grid lines on walkable floor cells.
    - Outer border frame to encase the maze cleanly.
    """
    rows = len(maze)
    if rows == 0:
        return
    cols = len(maze[0])

    maze_rect = pygame.Rect(offset_x, offset_y, cols * cell_size, rows * cell_size)

    # Subtle backdrop for the maze area
    pygame.draw.rect(screen, PATH, maze_rect)

    for r in range(rows):
        for c in range(cols):
            x, y = grid_to_pixel(r, c, cell_size, offset_x, offset_y)
            rect = pygame.Rect(x, y, cell_size, cell_size)

            if maze[r][c] == 1:
                # WALL: Main wall body
                pygame.draw.rect(screen, WALL, rect)

                # Wall 3D top bevel highlight for modern sci-fi depth
                bevel_size = max(2, cell_size // 7)
                pygame.draw.rect(screen, WALL_HIGHLIGHT, (x, y, cell_size, bevel_size))
                pygame.draw.rect(screen, WALL_HIGHLIGHT, (x, y, bevel_size, cell_size))

                # Subtle wall inner boundary line
                pygame.draw.rect(screen, (20, 26, 46), rect, 1)
            else:
                # WALKABLE PATH: floor cell with subtle tech dot in center
                pygame.draw.rect(screen, GRID_LINE, rect, 1)
                if cell_size >= 20:
                    dot_radius = max(1, cell_size // 14)
                    cx, cy = grid_to_center(r, c, cell_size, offset_x, offset_y)
                    pygame.draw.circle(screen, (28, 36, 56), (cx, cy), dot_radius)

    # Clean outer bounding frame
    pygame.draw.rect(screen, PANEL_BORDER, maze_rect, 2)


# ==============================================================================
# 5. COLLECTIBLE COINS RENDERING
# ==============================================================================
def draw_coins(screen, coins, cell_size, offset_x=0, offset_y=0):
    """
    Renders collectible gold coins on walkable cells.
    Visuals:
      - Gold/yellow circular coin with outer border and specular gleam.
      - Subtle breathing animation pulse.
    """
    if not coins:
        return

    ticks = pygame.time.get_ticks()
    # Subtle breathing pulse
    pulse = math.sin(ticks * 0.008) * 1.0

    base_r = max(4, int(cell_size * 0.24))
    r = max(3, int(base_r + pulse))

    for (row, col) in coins:
        cx, cy = grid_to_center(row, col, cell_size, offset_x, offset_y)

        # Soft outer gold glow
        glow_r = r + max(2, cell_size // 10)
        glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 50, 45), (glow_r + 2, glow_r + 2), glow_r)
        screen.blit(glow_surf, (cx - glow_r - 2, cy - glow_r - 2))

        # Main coin circle
        pygame.draw.circle(screen, COIN, (cx, cy), r)
        # Outer coin border ring
        pygame.draw.circle(screen, COIN_BORDER, (cx, cy), r, width=max(1, cell_size // 18))
        # Inner coin core
        inner_r = max(1, r // 2)
        pygame.draw.circle(screen, (255, 225, 100), (cx, cy), inner_r)
        # Specular glint highlight (top-left)
        glint_offset = max(1, r // 3)
        pygame.draw.circle(screen, COIN_HIGHLIGHT, (cx - glint_offset, cy - glint_offset), max(1, r // 4))


# ==============================================================================
# 6. BFS PATH VISUALIZATION (CRITICAL AI OBSERVABILITY)
# ==============================================================================
def draw_ai_path(screen, path, cell_size, offset_x=0, offset_y=0):
    """
    Visualizes the BFS path computed by the AI.
    Features:
      - Subtle, semi-transparent amber highlighting.
      - Connected laser trajectory between waypoint centers.
      - Animated pulse wave showing real-time AI decision-making.
      - Safe handling: gracefully handles empty, single-node, or None paths.
    """
    if not path or len(path) < 2:
        return

    ticks = pygame.time.get_ticks()
    pulse_phase = (ticks * 0.006) % (2 * math.pi)
    glow_alpha = int(80 + 35 * math.sin(pulse_phase))

    pixel_points = [
        grid_to_center(r, c, cell_size, offset_x, offset_y)
        for (r, c) in path
    ]

    # Layer 1: Semi-transparent glowing path cells
    glow_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    inner_pad = max(2, cell_size // 6)
    inner_size = max(4, cell_size - 2 * inner_pad)

    for i, (r, c) in enumerate(path[1:-1], start=1):
        x, y = grid_to_pixel(r, c, cell_size, offset_x, offset_y)
        wave = math.sin(ticks * 0.008 - i * 0.4)
        node_alpha = max(30, min(140, int(glow_alpha + 40 * wave)))

        glow_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(
            glow_surf,
            (*BFS_PATH, node_alpha),
            (inner_pad, inner_pad, inner_size, inner_size),
            border_radius=max(2, cell_size // 8)
        )
        screen.blit(glow_surf, (x, y))

    # Layer 2: Connecting laser line along trajectory
    line_width = max(2, cell_size // 10)
    for i in range(len(pixel_points) - 1):
        p1 = pixel_points[i]
        p2 = pixel_points[i + 1]
        pygame.draw.line(screen, (*BFS_PATH, 160), p1, p2, width=line_width + 2)
        pygame.draw.line(screen, (255, 245, 180), p1, p2, width=max(1, line_width - 1))

    # Layer 3: Waypoint beacon dots on path nodes
    dot_radius = max(2, cell_size // 9)
    for i, pt in enumerate(pixel_points[1:-1]):
        wave = (math.sin(ticks * 0.01 - i * 0.5) + 1.0) / 2.0
        r_dyn = dot_radius + int(wave * 2)
        pygame.draw.circle(screen, BFS_PATH, pt, r_dyn)
        pygame.draw.circle(screen, (255, 255, 220), pt, max(1, r_dyn // 2))


# ==============================================================================
# 7. PLAYER VISUALIZATION
# ==============================================================================
def draw_player(screen, player_pos, cell_size, offset_x=0, offset_y=0):
    """
    Renders the player character in neon cyan.
    Visuals:
      - Multi-layered glowing core.
      - Soft animated pulse ring.
      - Tech sensor/beacon center.
    """
    if not player_pos:
        return

    r, c = player_pos
    cx, cy = grid_to_center(r, c, cell_size, offset_x, offset_y)
    ticks = pygame.time.get_ticks()

    base_radius = max(4, int(cell_size * 0.36))
    pulse = math.sin(ticks * 0.007) * 2.0
    radius = max(3, int(base_radius + pulse))

    # Outer soft glow
    glow_radius = radius + max(4, cell_size // 6)
    glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (50, 220, 255, 55), (glow_radius + 2, glow_radius + 2), glow_radius)
    screen.blit(glow_surf, (cx - glow_radius - 2, cy - glow_radius - 2))

    # Main player body (Cyan)
    pygame.draw.circle(screen, PLAYER, (cx, cy), radius)

    # Inner cyber core (Bright cyan / white center)
    core_radius = max(2, radius // 2)
    pygame.draw.circle(screen, (220, 250, 255), (cx, cy), core_radius)

    # Clean border ring
    pygame.draw.circle(screen, (20, 100, 150), (cx, cy), radius, max(1, cell_size // 16))


# ==============================================================================
# 8. ENEMY VISUALIZATION (AI HUNTER)
# ==============================================================================
def draw_enemy(screen, enemy_pos, cell_size, offset_x=0, offset_y=0):
    """
    Renders the AI-controlled enemy in alert crimson red.
    Visuals:
      - Threatening diamond drone silhouette.
      - Pulsating radar sonar ring expanding outward.
      - Warning core clearly communicating active pursuit.
    """
    if not enemy_pos:
        return

    r, c = enemy_pos
    cx, cy = grid_to_center(r, c, cell_size, offset_x, offset_y)
    ticks = pygame.time.get_ticks()

    # Expanding radar sonar ring
    sonar_cycle = (ticks * 0.003) % 1.0
    sonar_radius = int(cell_size * 0.25 + sonar_cycle * (cell_size * 0.45))
    sonar_alpha = max(0, int(150 * (1.0 - sonar_cycle)))

    if sonar_radius > 0 and sonar_alpha > 0:
        sonar_surf = pygame.Surface((sonar_radius * 2 + 4, sonar_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            sonar_surf,
            (*ENEMY, sonar_alpha),
            (sonar_radius + 2, sonar_radius + 2),
            sonar_radius,
            width=2
        )
        screen.blit(sonar_surf, (cx - sonar_radius - 2, cy - sonar_radius - 2))

    # Main enemy diamond drone body
    d = max(5, int(cell_size * 0.38))
    pulse = math.sin(ticks * 0.01) * 1.5
    d_pulse = max(4, int(d + pulse))

    diamond_pts = [
        (cx, cy - d_pulse),
        (cx + d_pulse, cy),
        (cx, cy + d_pulse),
        (cx - d_pulse, cy)
    ]

    pygame.draw.polygon(screen, ENEMY, diamond_pts)

    inner_d = max(2, d_pulse // 2)
    inner_pts = [
        (cx, cy - inner_d),
        (cx + inner_d, cy),
        (cx, cy + inner_d),
        (cx - inner_d, cy)
    ]
    pygame.draw.polygon(screen, (255, 210, 215), inner_pts)
    pygame.draw.polygon(screen, (160, 20, 30), diamond_pts, max(1, cell_size // 14))


# ==============================================================================
# 9. EXIT VISUALIZATION (EXTRACTION BEACON)
# ==============================================================================
def draw_exit(screen, exit_pos, cell_size, offset_x=0, offset_y=0):
    """
    Renders the extraction exit portal in vibrant cyber green.
    """
    if not exit_pos:
        return

    r, c = exit_pos
    cx, cy = grid_to_center(r, c, cell_size, offset_x, offset_y)
    ticks = pygame.time.get_ticks()

    max_r = max(5, int(cell_size * 0.40))
    pulse = (math.sin(ticks * 0.008) + 1.0) / 2.0
    r_outer = max_r + int(pulse * 3)

    # Ambient green glow
    glow_surf = pygame.Surface((r_outer * 2 + 6, r_outer * 2 + 6), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (70, 240, 140, 60), (r_outer + 3, r_outer + 3), r_outer)
    screen.blit(glow_surf, (cx - r_outer - 3, cy - r_outer - 3))

    # Outer target ring
    pygame.draw.circle(screen, EXIT, (cx, cy), max_r, width=max(1, cell_size // 14))

    # Inner beacon ring
    r_mid = max(3, int(max_r * 0.6))
    pygame.draw.circle(screen, (120, 255, 175), (cx, cy), r_mid, width=max(1, cell_size // 18))

    # Center power core
    r_core = max(2, int(max_r * 0.3))
    pygame.draw.circle(screen, (230, 255, 240), (cx, cy), r_core)

    # Tactical crosshairs
    cross_len = max(3, cell_size // 5)
    line_w = max(1, cell_size // 20)
    pygame.draw.line(screen, EXIT, (cx - cross_len, cy), (cx - r_mid, cy), line_w)
    pygame.draw.line(screen, EXIT, (cx + r_mid, cy), (cx + cross_len, cy), line_w)
    pygame.draw.line(screen, EXIT, (cx, cy - cross_len), (cx, cy - r_mid), line_w)
    pygame.draw.line(screen, EXIT, (cx, cy + r_mid), (cx, cy + cross_len), line_w)


# ==============================================================================
# 10. BUTTON SYSTEM (Interactive UI Elements)
# ==============================================================================
def draw_button(screen, text, rect, is_hovered, primary=True, font_size=18):
    """
    Renders a styled futuristic button with hover feedback and corner accents.
    """
    bg_color = BUTTON_HOVER if is_hovered else BUTTON_BG
    border_color = (
        (BUTTON_BORDER_HOVER if primary else WHITE)
        if is_hovered else
        (BUTTON_BORDER if primary else (80, 100, 130))
    )

    pygame.draw.rect(screen, bg_color, rect, border_radius=6)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=6)

    corner_len = 6
    if is_hovered:
        accent = BUTTON_BORDER_HOVER if primary else EXIT
        pygame.draw.line(screen, accent, (rect.left + 2, rect.top + 2), (rect.left + 2 + corner_len, rect.top + 2), 2)
        pygame.draw.line(screen, accent, (rect.left + 2, rect.top + 2), (rect.left + 2, rect.top + 2 + corner_len), 2)
        pygame.draw.line(screen, accent, (rect.right - 2, rect.bottom - 2), (rect.right - 2 - corner_len, rect.bottom - 2), 2)
        pygame.draw.line(screen, accent, (rect.right - 2, rect.bottom - 2), (rect.right - 2, rect.bottom - 2 - corner_len), 2)

    font = FontManager.get(font_size, bold=True)
    text_color = WHITE if is_hovered else (210, 225, 245)
    txt_surf = font.render(text, True, text_color)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)


# ==============================================================================
# 11. HUD / TELEMETRY PANEL
# ==============================================================================
def draw_hud(screen, game_state, hud_rect):
    """
    Renders the futuristic right-side HUD telemetry panel.
    Displays:
      - LEVEL: X / Total
      - SCORE: Persisted Score
      - COINS: collected / total
      - AI SURVEILLANCE: ALGORITHM, AI STATUS, DISTANCE, PATH LENGTH
      - OPERATOR TELEMETRY: POSITION, MOVES, TIME
      - MAP KEY & LEGEND
    """
    pygame.draw.rect(screen, PANEL_BG, hud_rect, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, hud_rect, width=2, border_radius=8)

    # Header Banner
    header_rect = pygame.Rect(hud_rect.left, hud_rect.top, hud_rect.width, 42)
    pygame.draw.rect(screen, PANEL_HEADER, header_rect, border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, PANEL_BORDER, (hud_rect.left, hud_rect.top + 42), (hud_rect.right, hud_rect.top + 42), 2)

    title_font = FontManager.get(15, bold=True, mono=True)
    header_text = title_font.render("TELEMETRY // HUD", True, PLAYER)
    screen.blit(header_text, (hud_rect.left + 16, hud_rect.top + 12))

    def draw_card(y_pos, height, title):
        card_rect = pygame.Rect(hud_rect.left + 12, y_pos, hud_rect.width - 24, height)
        pygame.draw.rect(screen, (20, 25, 38), card_rect, border_radius=6)
        pygame.draw.rect(screen, (34, 45, 68), card_rect, width=1, border_radius=6)

        lbl_font = FontManager.get(11, bold=True, mono=True)
        lbl_surf = lbl_font.render(title, True, GRAY)
        screen.blit(lbl_surf, (card_rect.left + 10, card_rect.top + 7))
        return card_rect

    curr_y = hud_rect.top + 50
    f_sub = FontManager.get(11, bold=False, mono=True)
    f_val = FontManager.get(13, bold=True, mono=True)

    # --- CARD 1: MISSION & LEVEL STATUS ---
    c1 = draw_card(curr_y, 90, "MISSION TELEMETRY")
    
    # Level Row
    lvl = game_state.get("level", 1)
    tot_lvl = game_state.get("total_levels", 3)
    screen.blit(f_sub.render("LEVEL:", True, GRAY), (c1.left + 10, c1.top + 25))
    screen.blit(f_val.render(f"{lvl} / {tot_lvl}", True, PLAYER), (c1.left + 105, c1.top + 24))

    # Score Row
    score = game_state.get("score", 0)
    screen.blit(f_sub.render("SCORE:", True, GRAY), (c1.left + 10, c1.top + 46))
    screen.blit(f_val.render(str(score), True, (255, 230, 80)), (c1.left + 105, c1.top + 45))

    # Coins Row
    coins_c = game_state.get("coins_collected", 0)
    coins_t = game_state.get("total_coins", 0)
    screen.blit(f_sub.render("COINS:", True, GRAY), (c1.left + 10, c1.top + 67))
    screen.blit(f_val.render(f"{coins_c} / {coins_t}", True, COIN), (c1.left + 105, c1.top + 66))
    curr_y += 98

    # --- CARD 2: AI SURVEILLANCE STATUS ---
    c2 = draw_card(curr_y, 138, "AI SURVEILLANCE MATRIX")

    # Algorithm
    screen.blit(f_sub.render("ALGORITHM:", True, GRAY), (c2.left + 10, c2.top + 26))
    algo_str = game_state.get("algorithm", "BFS")
    screen.blit(f_val.render(algo_str, True, BFS_PATH), (c2.left + 105, c2.top + 25))

    # AI Status Badge
    screen.blit(f_sub.render("AI STATUS:", True, GRAY), (c2.left + 10, c2.top + 52))
    ai_status = game_state.get("ai_status", "HUNTING")
    badge_color = ENEMY if ai_status == "HUNTING" else (100, 220, 100)
    badge_rect = pygame.Rect(c2.left + 105, c2.top + 49, 86, 20)
    pygame.draw.rect(screen, (40, 15, 20) if ai_status == "HUNTING" else (15, 35, 20), badge_rect, border_radius=4)
    pygame.draw.rect(screen, badge_color, badge_rect, width=1, border_radius=4)
    badge_surf = FontManager.get(10, bold=True, mono=True).render(ai_status, True, badge_color)
    screen.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

    # Distance
    dist = game_state.get("distance", "--")
    dist_str = f"{dist} cells" if dist != "--" else "--"
    screen.blit(f_sub.render("DISTANCE:", True, GRAY), (c2.left + 10, c2.top + 80))
    screen.blit(f_val.render(dist_str, True, WHITE), (c2.left + 105, c2.top + 79))

    # Path Length
    path_len = game_state.get("path_length", "--")
    path_str = f"{path_len} steps" if path_len != "--" else "--"
    screen.blit(f_sub.render("PATH LEN:", True, GRAY), (c2.left + 10, c2.top + 108))
    screen.blit(f_val.render(path_str, True, BFS_PATH), (c2.left + 105, c2.top + 107))
    curr_y += 146

    # --- CARD 3: PLAYER TELEMETRY ---
    c3 = draw_card(curr_y, 90, "OPERATOR TELEMETRY")
    p_pos = game_state.get("player_pos", None)
    pos_str = f"({p_pos[0]}, {p_pos[1]})" if p_pos else "N/A"
    screen.blit(f_sub.render("POSITION:", True, GRAY), (c3.left + 10, c3.top + 25))
    screen.blit(f_val.render(pos_str, True, PLAYER), (c3.left + 105, c3.top + 24))

    moves = game_state.get("moves_count", 0)
    screen.blit(f_sub.render("MOVES:", True, GRAY), (c3.left + 10, c3.top + 46))
    screen.blit(f_val.render(str(moves), True, WHITE), (c3.left + 105, c3.top + 45))

    elapsed_time = game_state.get("time_elapsed", "00:00")
    screen.blit(f_sub.render("TIME:", True, GRAY), (c3.left + 10, c3.top + 67))
    screen.blit(f_val.render(str(elapsed_time), True, WHITE), (c3.left + 105, c3.top + 66))
    curr_y += 98

    # --- CARD 4: TACTICAL MAP LEGEND ---
    c4 = draw_card(curr_y, 115, "MAP KEY & LEGEND")
    legend_items = [
        ("Player (Agent)", PLAYER, "circle"),
        ("AI Hunter", ENEMY, "diamond"),
        ("Extraction Beacon", EXIT, "ring"),
        ("Collectible Coin", COIN, "coin"),
        ("BFS Projected Route", BFS_PATH, "line")
    ]
    leg_y = c4.top + 23
    for label, col, shape in legend_items:
        icon_x = c4.left + 16
        icon_y = leg_y + 6
        if shape == "circle":
            pygame.draw.circle(screen, col, (icon_x, icon_y), 4)
        elif shape == "diamond":
            pts = [(icon_x, icon_y - 4), (icon_x + 4, icon_y), (icon_x, icon_y + 4), (icon_x - 4, icon_y)]
            pygame.draw.polygon(screen, col, pts)
        elif shape == "ring":
            pygame.draw.circle(screen, col, (icon_x, icon_y), 4, 2)
        elif shape == "coin":
            pygame.draw.circle(screen, col, (icon_x, icon_y), 4)
            pygame.draw.circle(screen, COIN_BORDER, (icon_x, icon_y), 4, 1)
        elif shape == "line":
            pygame.draw.line(screen, col, (icon_x - 5, icon_y), (icon_x + 5, icon_y), 3)

        leg_text = FontManager.get(10).render(label, True, (200, 210, 225))
        screen.blit(leg_text, (icon_x + 13, leg_y))
        leg_y += 18

    # Controls hint at bottom
    ctrl_surf = FontManager.get(11, mono=True).render("Move: [W/A/S/D] or [Arrows]", True, (110, 130, 160))
    screen.blit(ctrl_surf, (hud_rect.left + 16, hud_rect.bottom - 22))


# ==============================================================================
# 12. START SCREEN
# ==============================================================================
def draw_start_screen(screen, window_width, window_height, mouse_pos=(0, 0)):
    """
    Renders the Start/Menu screen.
    Returns:
        dict containing button Rects: {'start_button': rect, 'quit_button': rect}
    """
    screen.fill(BACKGROUND)
    ticks = pygame.time.get_ticks()

    grid_gap = 50
    for x in range(0, window_width, grid_gap):
        pygame.draw.line(screen, (15, 20, 32), (x, 0), (x, window_height), 1)
    for y in range(0, window_height, grid_gap):
        pygame.draw.line(screen, (15, 20, 32), (0, y), (window_width, y), 1)

    radar_y = int((ticks * 0.08) % window_height)
    sweep_surf = pygame.Surface((window_width, 40), pygame.SRCALPHA)
    for i in range(40):
        alpha = int(25 * (1.0 - i / 40.0))
        pygame.draw.line(sweep_surf, (*PLAYER, alpha), (0, i), (window_width, i), 1)
    screen.blit(sweep_surf, (0, radar_y))

    card_w, card_h = 640, 510
    card_x = (window_width - card_w) // 2
    card_y = (window_height - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    pygame.draw.rect(screen, PANEL_BG, card_rect, border_radius=12)
    pygame.draw.rect(screen, PANEL_BORDER, card_rect, width=2, border_radius=12)

    top_bar = pygame.Rect(card_x, card_y, card_w, 6)
    pygame.draw.rect(screen, PLAYER, top_bar, border_top_left_radius=12, border_top_right_radius=12)

    title_font = FontManager.get(44, bold=True)
    title_surf = title_font.render("MAZE RUNNER", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(window_width // 2, card_y + 55)))

    sub_font = FontManager.get(18, bold=True, mono=True)
    sub_surf = sub_font.render("ESCAPE THE AI", True, PLAYER)
    screen.blit(sub_surf, sub_surf.get_rect(center=(window_width // 2, card_y + 102)))

    brief_rect = pygame.Rect(card_x + 40, card_y + 135, card_w - 80, 110)
    pygame.draw.rect(screen, (18, 24, 38), brief_rect, border_radius=8)
    pygame.draw.rect(screen, (32, 44, 70), brief_rect, width=1, border_radius=8)

    desc_font = FontManager.get(13)
    lines = [
        "MISSION: Reach the exit beacon before the AI catches you.",
        "ADAPTIVE PURSUIT: Enemy calculates optimal routes using BFS pathfinding.",
        "COLLECTIBLES: Gather coins (+10 pts) and earn level bonuses (+100 pts).",
        "PROGRESSION: Complete 3 escalating sectors to escape the system."
    ]
    for idx, line in enumerate(lines):
        line_surf = desc_font.render(line, True, (210, 220, 235))
        screen.blit(line_surf, (brief_rect.left + 16, brief_rect.top + 14 + idx * 24))

    ctrl_rect = pygame.Rect(card_x + 40, card_y + 260, card_w - 80, 75)
    pygame.draw.rect(screen, (18, 24, 38), ctrl_rect, border_radius=8)
    pygame.draw.rect(screen, (32, 44, 70), ctrl_rect, width=1, border_radius=8)

    c_head = FontManager.get(12, bold=True, mono=True).render("TACTICAL CONTROLS", True, BFS_PATH)
    screen.blit(c_head, (ctrl_rect.left + 16, ctrl_rect.top + 12))

    c_body = FontManager.get(14).render("Move: [W / A / S / D]  or  [Arrow Keys]     Restart: [R]", True, WHITE)
    screen.blit(c_body, (ctrl_rect.left + 16, ctrl_rect.top + 38))

    btn_w, btn_h = 220, 48
    start_btn = pygame.Rect(window_width // 2 - btn_w - 15, card_y + 370, btn_w, btn_h)
    quit_btn = pygame.Rect(window_width // 2 + 15, card_y + 370, btn_w, btn_h)

    start_hover = start_btn.collidepoint(mouse_pos)
    quit_hover = quit_btn.collidepoint(mouse_pos)

    draw_button(screen, "START GAME", start_btn, start_hover, primary=True, font_size=16)
    draw_button(screen, "QUIT", quit_btn, quit_hover, primary=False, font_size=16)

    p_text = FontManager.get(13, mono=True).render("Press [SPACE] or Click to Start", True, GRAY)
    screen.blit(p_text, p_text.get_rect(center=(window_width // 2, card_y + 458)))

    return {"start_button": start_btn, "quit_button": quit_btn}


# ==============================================================================
# 13. LEVEL VICTORY SCREEN
# ==============================================================================
def draw_victory_screen(screen, game_state, window_width, window_height, mouse_pos=(0, 0)):
    """
    Renders the level completion screen when player reaches the exit.
    Returns:
        dict containing button Rects: {'next_button': rect, 'menu_button': rect}
    """
    dim_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    dim_surface.fill((8, 20, 16, 230))
    screen.blit(dim_surface, (0, 0))

    card_w, card_h = 580, 470
    card_x = (window_width - card_w) // 2
    card_y = (window_height - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    pygame.draw.rect(screen, (14, 26, 22), card_rect, border_radius=12)
    pygame.draw.rect(screen, (30, 95, 60), card_rect, width=2, border_radius=12)

    top_bar = pygame.Rect(card_x, card_y, card_w, 6)
    pygame.draw.rect(screen, EXIT, top_bar, border_top_left_radius=12, border_top_right_radius=12)

    title_font = FontManager.get(36, bold=True)
    title_surf = title_font.render("MISSION COMPLETE", True, EXIT)
    screen.blit(title_surf, title_surf.get_rect(center=(window_width // 2, card_y + 48)))

    lvl = game_state.get("level", 1)
    sub_font = FontManager.get(16, bold=True, mono=True)
    sub_surf = sub_font.render(f"YOU ESCAPED! — LEVEL {lvl} COMPLETE", True, (190, 255, 215))
    screen.blit(sub_surf, sub_surf.get_rect(center=(window_width // 2, card_y + 92)))

    # Stats Card
    stats_rect = pygame.Rect(card_x + 35, card_y + 120, card_w - 70, 185)
    pygame.draw.rect(screen, (18, 34, 28), stats_rect, border_radius=8)
    pygame.draw.rect(screen, (35, 75, 55), stats_rect, width=1, border_radius=8)

    f_sub = FontManager.get(13, mono=True)
    f_val = FontManager.get(14, bold=True, mono=True)

    c_collected = game_state.get("coins_collected", 0)
    c_total = game_state.get("total_coins", 0)
    coin_pts = game_state.get("level_coin_score", c_collected * 10)
    lvl_bonus = game_state.get("level_bonus", 100)
    lvl_gain = coin_pts + lvl_bonus
    tot_score = game_state.get("score", 0) + lvl_bonus

    row_y = stats_rect.top + 16
    items = [
        ("COINS COLLECTED:", f"{c_collected} / {c_total}", WHITE),
        ("COIN POINTS:", f"+{coin_pts}", COIN),
        ("LEVEL BONUS:", f"+{lvl_bonus}", EXIT),
        ("LEVEL SCORE:", f"+{lvl_gain}", (120, 255, 180)),
        ("TOTAL SCORE:", f"{tot_score}", (255, 230, 80))
    ]

    for label, val, color in items:
        screen.blit(f_sub.render(label, True, GRAY), (stats_rect.left + 24, row_y))
        screen.blit(f_val.render(val, True, color), (stats_rect.left + 230, row_y))
        row_y += 32

    # Buttons
    btn_w, btn_h = 200, 48
    next_btn = pygame.Rect(window_width // 2 - btn_w - 12, card_y + 335, btn_w, btn_h)
    menu_btn = pygame.Rect(window_width // 2 + 12, card_y + 335, btn_w, btn_h)

    n_hover = next_btn.collidepoint(mouse_pos)
    m_hover = menu_btn.collidepoint(mouse_pos)

    draw_button(screen, "NEXT LEVEL", next_btn, n_hover, primary=True, font_size=15)
    draw_button(screen, "MAIN MENU", menu_btn, m_hover, primary=False, font_size=15)

    hint_surf = FontManager.get(12, mono=True).render("Press [SPACE] or [ENTER] for Next Level", True, GRAY)
    screen.blit(hint_surf, hint_surf.get_rect(center=(window_width // 2, card_y + 420)))

    return {"next_button": next_btn, "menu_button": menu_btn}


# Alias for backward compatibility
draw_victory = draw_victory_screen


# ==============================================================================
# 14. FINAL VICTORY SCREEN (GAME COMPLETE)
# ==============================================================================
def draw_final_victory_screen(screen, game_state, window_width, window_height, mouse_pos=(0, 0)):
    """
    Renders the Grand Finale celebration screen after completing all 3 levels.
    Returns:
        dict containing button Rects: {'play_again_button': rect, 'menu_button': rect}
    """
    dim_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    dim_surface.fill((6, 24, 18, 240))
    screen.blit(dim_surface, (0, 0))

    card_w, card_h = 600, 480
    card_x = (window_width - card_w) // 2
    card_y = (window_height - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    pygame.draw.rect(screen, (12, 30, 24), card_rect, border_radius=12)
    pygame.draw.rect(screen, (40, 130, 80), card_rect, width=2, border_radius=12)

    top_bar = pygame.Rect(card_x, card_y, card_w, 6)
    pygame.draw.rect(screen, EXIT, top_bar, border_top_left_radius=12, border_top_right_radius=12)

    title_font = FontManager.get(40, bold=True)
    title_surf = title_font.render("GAME COMPLETE!", True, EXIT)
    screen.blit(title_surf, title_surf.get_rect(center=(window_width // 2, card_y + 50)))

    sub_font = FontManager.get(16, bold=True, mono=True)
    sub_surf = sub_font.render("YOU ESCAPED THE AI! ALL SECTORS CLEARED", True, (210, 255, 230))
    screen.blit(sub_surf, sub_surf.get_rect(center=(window_width // 2, card_y + 96)))

    stats_rect = pygame.Rect(card_x + 40, card_y + 130, card_w - 80, 160)
    pygame.draw.rect(screen, (16, 40, 32), stats_rect, border_radius=8)
    pygame.draw.rect(screen, (40, 95, 65), stats_rect, width=1, border_radius=8)

    f_sub = FontManager.get(13, mono=True)
    f_val = FontManager.get(15, bold=True, mono=True)

    final_score = game_state.get("score", 0)
    all_coins = game_state.get("all_time_coins", 0)
    levels_done = game_state.get("total_levels", 3)

    row_y = stats_rect.top + 22
    items = [
        ("FINAL SCORE:", str(final_score), (255, 235, 90)),
        ("TOTAL COINS:", str(all_coins), COIN),
        ("LEVELS COMPLETED:", f"{levels_done} / {levels_done}", EXIT),
        ("CAMPAIGN STATUS:", "EXTRACTION CERTIFIED", PLAYER)
    ]

    for label, val, color in items:
        screen.blit(f_sub.render(label, True, GRAY), (stats_rect.left + 24, row_y))
        screen.blit(f_val.render(val, True, color), (stats_rect.left + 230, row_y))
        row_y += 32

    btn_w, btn_h = 200, 48
    play_again_btn = pygame.Rect(window_width // 2 - btn_w - 12, card_y + 330, btn_w, btn_h)
    menu_btn = pygame.Rect(window_width // 2 + 12, card_y + 330, btn_w, btn_h)

    p_hover = play_again_btn.collidepoint(mouse_pos)
    m_hover = menu_btn.collidepoint(mouse_pos)

    draw_button(screen, "PLAY AGAIN", play_again_btn, p_hover, primary=True, font_size=15)
    draw_button(screen, "MAIN MENU", menu_btn, m_hover, primary=False, font_size=15)

    hint_surf = FontManager.get(12, mono=True).render("Press [SPACE] or Click to Play Again", True, GRAY)
    screen.blit(hint_surf, hint_surf.get_rect(center=(window_width // 2, card_y + 418)))

    return {"play_again_button": play_again_btn, "menu_button": menu_btn}


# ==============================================================================
# 15. GAME OVER / LOSS SCREEN
# ==============================================================================
def draw_game_over_screen(screen, game_state, window_width, window_height, mouse_pos=(0, 0)):
    """
    Renders the game over screen when player is caught by the AI enemy.
    Returns:
        dict containing button Rects: {'retry_button': rect, 'menu_button': rect}
    """
    dim_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    dim_surface.fill((16, 8, 12, 230))
    screen.blit(dim_surface, (0, 0))

    card_w, card_h = 560, 440
    card_x = (window_width - card_w) // 2
    card_y = (window_height - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    pygame.draw.rect(screen, (22, 16, 24), card_rect, border_radius=12)
    pygame.draw.rect(screen, (100, 30, 40), card_rect, width=2, border_radius=12)

    top_bar = pygame.Rect(card_x, card_y, card_w, 6)
    pygame.draw.rect(screen, ENEMY, top_bar, border_top_left_radius=12, border_top_right_radius=12)

    title_font = FontManager.get(42, bold=True)
    title_surf = title_font.render("GAME OVER", True, ENEMY)
    screen.blit(title_surf, title_surf.get_rect(center=(window_width // 2, card_y + 55)))

    sub_font = FontManager.get(16, bold=True, mono=True)
    sub_surf = sub_font.render("THE AI FOUND YOU", True, (255, 170, 180))
    screen.blit(sub_surf, sub_surf.get_rect(center=(window_width // 2, card_y + 105)))

    stats_rect = pygame.Rect(card_x + 40, card_y + 135, card_w - 80, 140)
    pygame.draw.rect(screen, (28, 18, 24), stats_rect, border_radius=8)
    pygame.draw.rect(screen, (75, 25, 35), stats_rect, width=1, border_radius=8)

    f_sub = FontManager.get(13, mono=True)
    f_val = FontManager.get(14, bold=True, mono=True)

    lvl = game_state.get("level", 1)
    score = game_state.get("score", 0)
    coins_c = game_state.get("coins_collected", 0)
    coins_t = game_state.get("total_coins", 0)

    row_y = stats_rect.top + 20
    items = [
        ("LEVEL:", str(lvl), PLAYER),
        ("SCORE:", str(score), (255, 230, 80)),
        ("COINS:", f"{coins_c} / {coins_t}", COIN),
        ("AI PURSUIT:", "INTERCEPTION CONFIRMED", ENEMY)
    ]

    for label, val, color in items:
        screen.blit(f_sub.render(label, True, GRAY), (stats_rect.left + 24, row_y))
        screen.blit(f_val.render(val, True, color), (stats_rect.left + 180, row_y))
        row_y += 28

    btn_w, btn_h = 190, 46
    retry_btn = pygame.Rect(window_width // 2 - btn_w - 12, card_y + 305, btn_w, btn_h)
    menu_btn = pygame.Rect(window_width // 2 + 12, card_y + 305, btn_w, btn_h)

    r_hover = retry_btn.collidepoint(mouse_pos)
    m_hover = menu_btn.collidepoint(mouse_pos)

    draw_button(screen, "RETRY LEVEL", retry_btn, r_hover, primary=True, font_size=15)
    draw_button(screen, "MAIN MENU", menu_btn, m_hover, primary=False, font_size=15)

    hint_surf = FontManager.get(12, mono=True).render("Press [SPACE] or [R] to Retry", True, GRAY)
    screen.blit(hint_surf, hint_surf.get_rect(center=(window_width // 2, card_y + 385)))

    return {"retry_button": retry_btn, "menu_button": menu_btn}


# Alias for backward compatibility
draw_game_over = draw_game_over_screen


# ==============================================================================
# 16. TOP NAVIGATION HEADER
# ==============================================================================
def draw_top_bar(screen, window_width, title="MAZE RUNNER // AI TACTICAL DISPLAY", fps=60):
    """Renders the futuristic top bar across the full window width."""
    bar_rect = pygame.Rect(0, 0, window_width, 42)
    pygame.draw.rect(screen, (13, 16, 26), bar_rect)
    pygame.draw.line(screen, PANEL_BORDER, (0, 42), (window_width, 42), 1)

    pygame.draw.rect(screen, PLAYER, (0, 0, 180, 3))

    t_font = FontManager.get(14, bold=True, mono=True)
    t_surf = t_font.render(str(title), True, WHITE)
    screen.blit(t_surf, (20, 12))

    fps_font = FontManager.get(12, mono=True)
    fps_surf = fps_font.render(f"FPS: {int(fps)} | SYSTEM: ONLINE", True, (100, 210, 130))
    screen.blit(fps_surf, (window_width - fps_surf.get_width() - 20, 14))
