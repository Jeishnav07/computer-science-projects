import heapq  #priority queue for the open set

#Compute Manhattan heuristic between two grid points
def manhattan(a, b):
    """Manhattan distance heuristic between two grid points a and b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#Yield valid 4-way neighbour cells that are inside the map bounds
def neighbors(node, width, height):
    """Return 4-neighbour cells (up, down, left, right) that are within bounds."""
    x, y = node
    #four cardinal moves
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        #skip neighbors outside the grid
        if 0 <= nx < width and 0 <= ny < height:
            yield (nx, ny)

#Reconstruct the path by following came_from links from goal back to start
def reconstruct_path(came_from, current):
    """Reconstructs path by following the came_from map from goal back to start."""
    path = [current]
    #follow parent links until we reach a node with no parent
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()  #reverse so path goes start -> goal
    return path

#Run the A* search and return a list of cells forming the path (or [] if no path)
def find_path(start, goal, walls, width, height):
    """
    Find a path from start to goal on a grid using A*.
    - start, goal: (x,y) tuples
    - walls: set of blocked (x,y) cells
    - width, height: grid dimensions
    Returns: list of (x,y) cells from start to goal (including both) or [] if no path.
    """
    #early exit if start or goal themselves are walls (return empty path)
    if start in walls or goal in walls:
        return []

    #the open set: heap of (f_score, counter, node)
    open_heap = []
    #g_score: cost from start to node (dict, default +inf)
    g_score = {start: 0}
    #f_score: estimated total cost (g + h)
    f_score = {start: manhattan(start, goal)}

    #came_from map to reconstruct path
    came_from = {}

    #tie-breaker counter to keep heap comparisons stable
    counter = 0
    heapq.heappush(open_heap, (f_score[start], counter, start))
    closed = set()  #closed set to record visited nodes

    while open_heap:
        #pop node with smallest f_score
        _, _, current = heapq.heappop(open_heap)

        #if reached the goal, reconstruct and return the path
        if current == goal:
            return reconstruct_path(came_from, current)

        #add to closed set
        if current in closed:
            continue
        closed.add(current)

        #explore neighbors
        for nb in neighbors(current, width, height):
            #skip walls and already closed nodes
            if nb in walls or nb in closed:
                continue

            tentative_g = g_score.get(current, float('inf')) + 1  #cost to neighbor (grid unit = 1)
            #if this is a better path to neighbor, record it
            if tentative_g < g_score.get(nb, float('inf')):
                came_from[nb] = current            #best parent for neighbor
                g_score[nb] = tentative_g
                f = tentative_g + manhattan(nb, goal)
                f_score[nb] = f
                counter += 1
                heapq.heappush(open_heap, (f, counter, nb))

    #if we exhaust the open set without finding goal, return empty path
    return []
