import sys
import pygame
import airport_map
import UI
import A_star
import gaussian_noise
import path_comparision
import os
import csv

pygame.init()

screen_width = UI.grid_pixel_width + 220
screen_height = UI.grid_pixel_height

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Airport Navigation")

clock = pygame.time.Clock()
panel_font = pygame.font.SysFont('Arial', 16)
panel_rect = pygame.Rect(UI.grid_pixel_width, 0, 220, screen_height)

sel_target = None
real_path = []
noisy_path = []
real_path_len = None
noisy_path_len = None

noise_sigma = 0.3
anchor_r = 1.0

noise_stats = {
    "changed": None,
    "length_ratio": None,
    "aggregate": None
}

running = True

#Saves CSV of aggregate or last run stats for external analysis
def save_stats_to_csv():
    #create output folder
    os.makedirs("output", exist_ok=True)
    csv_path = os.path.join("output", "noise_stats.csv")

    #if we have aggregate metrics, save them otherwise save single trial snapshot
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        #header
        writer.writerow(["sigma", "anchor_r", "change_rate", "mean_length_ratio", "last_changed", "last_len_ratio"])
        agg = noise_stats.get("aggregate")
        if agg:
            change_rate = agg.get("change_rate")
            mean_len_ratio = agg.get("mean_length_ratio")
        else:
            change_rate = ""
            mean_len_ratio = ""
        last_changed = noise_stats.get("changed")
        last_len_ratio = noise_stats.get("length_ratio")
        writer.writerow([noise_sigma, anchor_r, change_rate, mean_len_ratio, last_changed, last_len_ratio])

#Run one noisy trial: noise -> snap -> A* on the reported cell
def run_single_noisy_trial():
    #run single trial: apply noise, snap, compute reported path, compare to real_path
    global noisy_path, noisy_path_len, noise_stats
    if not sel_target:
        return
    goal = airport_map.key_locations[sel_target]

    #continuous start pos = grid coords of start (floats)
    start_cont = (float(airport_map.start_pos[0]), float(airport_map.start_pos[1]))
    #apply gaussian noise
    noisy_cont = gaussian_noise.apply_noise(start_cont, noise_sigma)
    #nearest cell from noisy continuous pos
    reported_cell = gaussian_noise.nearest_cell_from_pos(noisy_cont, airport_map.map_width, airport_map.map_height)
    #try snapping to nearest anchor
    snapped_anchor = gaussian_noise.snap_to_nearest_anchor(noisy_cont, airport_map.anchor_points, anchor_r)
    if snapped_anchor is not None:
        reported_cell = snapped_anchor

    #compute reported path using A*
    reported_path = A_star.find_path(reported_cell, goal, airport_map.walls, airport_map.map_width, airport_map.map_height)

    #set noisy_path to reported_path for drawing (orange)
    noisy_path = reported_path
    noisy_path_len = len(noisy_path) if noisy_path else None

    #compute simple comparison stats vs real_path (already computed when target was selected)
    changed, ratio = path_comparision.path_changed_and_length_ratio(real_path, noisy_path)
    noise_stats["changed"] = changed
    noise_stats["length_ratio"] = ratio
    noise_stats["aggregate"] = None  #single trial => no aggregate

#Run multiple noisy trials and aggregate the results for experiments
def run_multiple_trials(num_trials=10):
    #run several trials and aggregate results
    global noise_stats, noisy_path
    if not sel_target:
        return
    goal = airport_map.key_locations[sel_target]

    trial_results = []
    last_reported_path = []
    for i in range(num_trials):
        #apply noise, map to cell, snap to anchor
        start_cont = (float(airport_map.start_pos[0]), float(airport_map.start_pos[1]))
        noisy_cont = gaussian_noise.apply_noise(start_cont, noise_sigma)
        reported_cell = gaussian_noise.nearest_cell_from_pos(noisy_cont, airport_map.map_width, airport_map.map_height)
        snapped_anchor = gaussian_noise.snap_to_nearest_anchor(noisy_cont, airport_map.anchor_points, anchor_r)
        if snapped_anchor is not None:
            reported_cell = snapped_anchor
        #get path
        reported_path = A_star.find_path(reported_cell, goal, airport_map.walls, airport_map.map_width, airport_map.map_height)
        #record comparison
        changed, ratio = path_comparision.path_changed_and_length_ratio(real_path, reported_path)
        trial_results.append((changed, ratio))
        last_reported_path = reported_path

    #aggregate metrics
    agg = path_comparision.aggregate_trials(trial_results)
    #set the noisy_path to the last trial for visualization
    noisy_path = last_reported_path
    noise_stats["aggregate"] = agg
    #also set last-single-trial-like fields for convenience
    noise_stats["changed"] = trial_results[-1][0]
    noise_stats["length_ratio"] = trial_results[-1][1]

#main loop: handle events, compute path, draw everything
while running:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            running = False

        #left mouse click to select a target on the grid
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            #only process clicks inside the grid area 
            if mx < UI.grid_pixel_width and my < UI.grid_pixel_height:
                clicked_cell = UI.pixel_to_grid((mx, my))  #convert pixel into grid
                found = None
                #check whether clicked exactly on a named target cell
                for name, coord in airport_map.key_locations.items():
                    if coord == clicked_cell:
                        found = name
                        break
                sel_target = found  #will be None if click was not a target

                #when selection changes recompute the real_path
                if sel_target:
                    goal = airport_map.key_locations[sel_target]
                    real_path = A_star.find_path(airport_map.start_pos, goal, airport_map.walls, airport_map.map_width, airport_map.map_height)
                    real_path_len = len(real_path) if real_path else None
                    #clear noisy results when selecting new target
                    noisy_path = []
                    noisy_path_len = None
                    noise_stats = {"changed": None, "length_ratio": None, "aggregate": None}
                else:
                    real_path = []
                    real_path_len = None
                    noisy_path = []
                    noisy_path_len = None
                    noise_stats = {"changed": None, "length_ratio": None, "aggregate": None}

        #keyboard controls for sigma, anchor radius and running trials
        if event.type == pygame.KEYDOWN:
            #increase sigma 
            if event.key == pygame.K_p:  
                noise_sigma = round(noise_sigma + 0.1, 3)
            #decrease sigma 
            if event.key == pygame.K_o:  
                noise_sigma = max(0.0, round(noise_sigma - 0.1, 3))
            #increase anchor radius 
            if event.key == pygame.K_j:  
                anchor_r = round(anchor_r + 0.25, 3)
            #decrease anchor radius 
            if event.key == pygame.K_k:  
                anchor_r = max(0.0, round(anchor_r - 0.25, 3))
            #run single noisy trial
            if event.key == pygame.K_r:
                run_single_noisy_trial()
            #run multiple trials (10)
            if event.key == pygame.K_m:
                run_multiple_trials(10)
            #save current stats to CSV
            if event.key == pygame.K_c:
                save_stats_to_csv()

    #drawing grid surface
    grid_surface = pygame.Surface((UI.grid_pixel_width, UI.grid_pixel_height))
    UI.draw_grid(grid_surface) 

    #draw true path
    if real_path:
        UI.draw_path(grid_surface, real_path)  #default color is blue

    #draw noisy path on top if it exists
    if noisy_path:
        orange = (220, 120, 20)
        #pass orange explicitly so it doesn't default to blue
        UI.draw_path(grid_surface, noisy_path, color=orange)

    #draw start, anchors and targets on top of the paths
    UI.draw_start_and_targets(grid_surface, sel_target)

    #blit grid to screen
    screen.blit(grid_surface, (0, 0))

    #draw side panel and target info, pass sigma/anchor/stats and path lengths
    UI.draw_side_panel(screen, panel_rect, sel_target, panel_font, noise_sigma, anchor_r, noise_stats, real_path_len, noisy_path_len)

    #update the display and cap FPS
    pygame.display.flip()
    clock.tick(30)

#cleanup and exit
pygame.quit()
sys.exit()
