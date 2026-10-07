from game.MazeRunner.maze import Maze
from ai.enemy import Enemy


def test_enemy_finds_path_to_player():
    maze = Maze()

    start = maze.get_player_start()
    exit_pos = maze.get_exit_pos()

    enemy = Enemy(
        maze=maze,
        start_position=start,
        cell_size=38,
        speed=2.0
    )

    path = enemy.find_path(exit_pos)

    assert path is not None
    assert len(path) > 0
    assert path[-1] == exit_pos


def test_enemy_starts_at_correct_position():
    maze = Maze()

    start = maze.get_player_start()

    enemy = Enemy(
        maze=maze,
        start_position=start,
        cell_size=38,
        speed=2.0
    )

    assert enemy.get_grid_position() == start