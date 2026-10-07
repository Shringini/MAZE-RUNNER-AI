from game.MazeRunner.maze import Maze


def test_maze_has_start_and_exit():
    maze = Maze()

    start = maze.get_player_start()
    exit_pos = maze.get_exit_pos()

    assert start is not None
    assert exit_pos is not None
    assert start != exit_pos


def test_maze_start_is_walkable():
    maze = Maze()

    start = maze.get_player_start()

    assert maze.is_walkable(start[0], start[1])


def test_maze_has_neighbors():
    maze = Maze()

    start = maze.get_player_start()

    neighbors = maze.get_neighbors(start[0], start[1])

    assert len(neighbors) > 0