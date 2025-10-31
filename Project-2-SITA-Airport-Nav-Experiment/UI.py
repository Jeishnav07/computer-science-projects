import pygame
import airport_map

#Colour values used for drawing the map and UI elements
background_colour = (240, 240, 240)
grid_colour = (200, 200, 200)
wall_colour = (30, 30, 30)
start_colour = (20, 120, 20)
target_colour = (180, 40, 40)
target_selected_colour = (255, 165, 0)
anchor_colour = (10, 150, 150)
text_colour = (40, 40, 40)
panel_colour = (220, 220, 220)

#Pixel dimensions of the grid area used for layout
grid_pixel_width = airport_map.map_width * airport_map.tile_size  
grid_pixel_height = airport_map.map_height * airport_map.tile_size + 230 #extra space needed for control panel

#Convert a grid cell to top-left pixel coords for drawing
def grid_to_pixel(cell):
    return cell[0] * airport_map.tile_size, cell[1] * airport_map.tile_size

#Convert a pixel position into a grid cell and clamp to map bounds
def pixel_to_grid(pos):
    px, py = pos
    gx = px // airport_map.tile_size
    gy = py // airport_map.tile_size
    gx = max(0, min(airport_map.map_width - 1, gx))
    gy = max(0, min(airport_map.map_height - 1, gy))
    return (gx, gy)

#Draw the grid and blocked wall cells onto the surface
def draw_grid(surface):
    surface.fill(background_colour)  #fill panel background
    for y in range(airport_map.map_height):  #rows
        for x in range(airport_map.map_width):  #columns
            rect = pygame.Rect(x * airport_map.tile_size, y * airport_map.tile_size, airport_map.tile_size, airport_map.tile_size)
            if (x, y) in airport_map.walls:
                pygame.draw.rect(surface, wall_colour, rect)  #draw wall cell
            else:
                pygame.draw.rect(surface, (255, 255, 255), rect)  #empty floor cell
            pygame.draw.rect(surface, grid_colour, rect, 1)  #grid border

#Draw start position, anchors and named key locations (targets)
def draw_start_and_targets(surface, selected_target_name=None):
    #draw anchors as small circles
    for anchor in airport_map.anchor_points:
        px, py = grid_to_pixel(anchor)
        cx = px + airport_map.tile_size // 2
        cy = py + airport_map.tile_size // 2
        pygame.draw.circle(surface, anchor_colour, (cx, cy), 6)

    #draw start (check-in) as a small rectangle inset within cell
    sx, sy = grid_to_pixel(airport_map.start_pos)
    start_rect = pygame.Rect(sx + 4, sy + 4, airport_map.tile_size - 8, airport_map.tile_size - 8)
    pygame.draw.rect(surface, start_colour, start_rect)

    #draw targets (gates/shops) as circles with labels
    for name, cell in airport_map.key_locations.items():
        tx, ty = grid_to_pixel(cell)
        center = (tx + airport_map.tile_size // 2, ty + airport_map.tile_size // 2)
        color = target_selected_colour if name == selected_target_name else target_colour
        pygame.draw.circle(surface, color, center, 10)
        font = pygame.font.SysFont('Arial', 12)
        label = font.render(name, True, text_colour)
        surface.blit(label, (tx + airport_map.tile_size + 4, ty))

#Draw a path overlay as inset rectangles so true vs noisy is clear
def draw_path(surface, path, color=None):
    if not path:
        return  #nothing to draw

    if color is None:
        path_color = (0, 100, 220)  #blue for the path
    else:
        path_color = color
    inset = 6  #inset so the path square doesn't fill the whole cell
    for cell in path:
        px, py = grid_to_pixel(cell)  #top-left pixel of cell
        rect = pygame.Rect(px + inset, py + inset, airport_map.tile_size - inset * 2, airport_map.tile_size - inset * 2)
        pygame.draw.rect(surface, path_color, rect)  #draw path block

#Draw the info panel with controls, current sigma/anchor and stats
def draw_side_panel(surface, panel_rect, selected_target_name, font, sigma, anchor_radius, noise_stats, real_len, noisy_len):
    pygame.draw.rect(surface, panel_colour, panel_rect)  #panel background
    title = font.render("Airport Navigation Panel", True, text_colour)
    surface.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
    start_text = font.render(f"Start position: {airport_map.start_pos}", True, text_colour)
    surface.blit(start_text, (panel_rect.x + 10, panel_rect.y + 40))
    surface.blit(font.render("Click a target on the map to select it.", True, text_colour), (panel_rect.x + 10, panel_rect.y + 70))
    if selected_target_name:
        surface.blit(font.render(f"Selected: {selected_target_name}", True, text_colour), (panel_rect.x + 10, panel_rect.y + 100))
    else:
        surface.blit(font.render("No target selected.", True, text_colour), (panel_rect.x + 10, panel_rect.y + 100))

    #list available targets
    y_off = 140
    surface.blit(font.render("Targets:", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    for name in airport_map.key_locations.keys():
        surface.blit(font.render(" - " + name, True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
        y_off += 18

    #show controls and sigma/anchor values
    y_off += 8
    surface.blit(font.render("Controls:", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(" p / o : increase/decrease sigma", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(" j / k : inc/dec anchor radius", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(" r : run single noisy trial", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(" m : run 10 noisy trials", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(" c : save stats to output file", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))

    #draw sigma and anchor numeric values
    y_off += 24
    surface.blit(font.render(f"Sigma value(gaussian noise): {sigma}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(f"Anchor radius: {anchor_radius}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))

    #draw recent path lengths and last single-trial stats
    y_off += 24
    surface.blit(font.render(f"True length: {real_len if real_len is not None else 'N/A'}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    surface.blit(font.render(f"Noisy length: {noisy_len if noisy_len is not None else 'N/A'}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    if noise_stats.get("changed") is not None:
        changed_text = "Yes" if noise_stats["changed"] else "No"
        surface.blit(font.render(f"Path changed?: {changed_text}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
        y_off += 18
    if noise_stats.get("length_ratio") is not None:
        lr = noise_stats["length_ratio"]
        lr_str = f"{lr:.3g}" if lr == lr else "N/A"
        surface.blit(font.render(f"Len ratio: {lr_str}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
        y_off += 18

    #show aggregate stats if present
    if noise_stats.get("aggregate"):
        agg = noise_stats["aggregate"]
        surface.blit(font.render(f"Change rate: {agg['change_rate']:.3f}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
        y_off += 18
        m = agg['mean_length_ratio']
        mstr = f"{m:.3g}" if m == m else "N/A"
        surface.blit(font.render(f"Mean len ratio: {mstr}", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
        y_off += 18

    #legend for the colours used in the UI
    y_off += 12
    surface.blit(font.render("Legend:", True, text_colour), (panel_rect.x + 10, panel_rect.y + y_off))
    y_off += 18
    #blue square
    pygame.draw.rect(surface, (0, 100, 220), pygame.Rect(panel_rect.x + 10, panel_rect.y + y_off, 12, 12))
    surface.blit(font.render(" True path", True, text_colour), (panel_rect.x + 30, panel_rect.y + y_off - 2))
    y_off += 18
    #orange square
    pygame.draw.rect(surface, (220, 120, 20), pygame.Rect(panel_rect.x + 10, panel_rect.y + y_off, 12, 12))
    surface.blit(font.render(" Noisy path", True, text_colour), (panel_rect.x + 30, panel_rect.y + y_off - 2))
    y_off += 18
    #anchor dot
    pygame.draw.circle(surface, anchor_colour, (panel_rect.x + 16, panel_rect.y + y_off + 6), 6)
    surface.blit(font.render(" Anchor", True, text_colour), (panel_rect.x + 30, panel_rect.y + y_off - 2))
