from ai.bfs import bfs


class SimpleMaze:
    def get_neighbors(self, row, col):
        grid = [
            [0, 0, 0],
            [1, 1, 0],
            [0, 0, 0]
        ]

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        neighbors = []

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if (
                0 <= new_row < len(grid)
                and 0 <= new_col < len(grid[0])
                and grid[new_row][new_col] == 0
            ):
                neighbors.append((new_row, new_col))

        return neighbors


def test_bfs_finds_path():
    maze = SimpleMaze()

    path = bfs(maze, (0, 0), (2, 2))

    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)
    assert len(path) > 0


def test_bfs_start_equals_goal():
    maze = SimpleMaze()

    path = bfs(maze, (0, 0), (0, 0))

    assert path == [(0, 0)]