map_width = 20
map_height = 12
tile_size = 32
start_pos = (2, 6)

#Set of blocked cells on the grid (walls/obstacles)
walls = {
    (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
    (11, 1), (12, 1), (13, 1), (14, 1),
    (11, 9), (12, 9), (15, 9), (16, 9),
    (8, 6), (9, 6),
    (9, 3), (9, 4),
    (11, 5),
    (13, 5), (14, 5),
    (16, 3), (16, 4), (17, 4)
}

#Named map targets used by the UI and experiments
key_locations = {
    "Gate A": (17, 2),
    "Gate B": (17, 9),
    "Nandos": (10, 4),
    "Boots": (13, 9), 
    "Sports Direct": (14, 2)
}

#Anchor points/beacons that noisy readings can snap to
anchor_points = [(1, 6), (3, 6), (2, 5), (2, 7),(4, 4), (4, 8), (0, 4), (0, 8),]
