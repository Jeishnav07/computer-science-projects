import numpy  #use numpy for sampling gaussian noise

#Add gaussian noise to a continuous position (x,y)
def apply_noise(pos, sigma):
    #takes pos=(x,y) floats, returns noisy (x,y) floats
    x, y = pos
    nx = x + float(numpy.random.normal(0.0, sigma))
    ny = y + float(numpy.random.normal(0.0, sigma))
    return (nx, ny)

#Map continuous position to the nearest grid cell and clamp inside bounds
def nearest_cell_from_pos(pos, width, height):
    x, y = pos
    gx = int(round(x))
    gy = int(round(y))
    gx = max(0, min(width - 1, gx))
    gy = max(0, min(height - 1, gy))
    return (gx, gy)

#Snap noisy continuous position to nearest anchor if it's within radius
def snap_to_nearest_anchor(pos, anchors, radius):
    #anchors: list of (x,y) grid coords
    best = None
    best_dist = None
    for a in anchors:
        dx = pos[0] - a[0]
        dy = pos[1] - a[1]
        d = (dx*dx + dy*dy) ** 0.5
        if best is None or d < best_dist:
            best = a
            best_dist = d
    #if nearest anchor is within radius return that anchor, else None
    if best_dist is not None and best_dist <= radius:
        return best
    return None
