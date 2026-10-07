from collections import deque


def bfs(maze, start, goal):
    """
    Breadth-First Search pathfinding.

    Args:
        maze: Maze object from maze.py
        start: (row, col) - enemy position
        goal: (row, col) - player position

    Returns:
        List of (row, col) positions representing the shortest path.
        Returns [] if no path exists.
    """

    # If enemy is already at player position
    if start == goal:
        return [start]

    # Queue stores positions BFS needs to explore
    queue = deque([start])

    # Remember positions already visited
    visited = {start}

    # Remember previous position for path reconstruction
    parent = {start: None}

    while queue:

        current = queue.popleft()

        # Did we reach the player?
        if current == goal:
            break

        # Get valid walkable neighbors from Maze
        neighbors = maze.get_neighbors(
            current[0],
            current[1]
        )

        for new_position in neighbors:

            # Skip already visited positions
            if new_position in visited:
                continue

            # Mark as visited
            visited.add(new_position)

            # Remember where we came from
            parent[new_position] = current

            # Add to BFS queue
            queue.append(new_position)

    # No path found
    if goal not in parent:
        return []

    # Reconstruct path from player back to enemy
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    # Reverse because we built it backwards
    path.reverse()

    return path