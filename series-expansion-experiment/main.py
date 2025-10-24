import pygame
import sys
import display_window

# Main application loop moved here (fixed indentation / event handling)
running = True  # continue running while True

while running:
    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # pass events to input boxes and buttons defined in display_window
        # (these must run for all events, not only when QUIT happened)
        display_window.input_box.handle_event(event)
        display_window.centre_input.handle_event(event)
        display_window.num_terms_input.handle_event(event)
        for button in display_window.buttons:
            button.handle_event(event)

    # --- Drawing UI background and left panel ---
    display_window.screen.fill(display_window.white)  # fill full window background
    pygame.draw.rect(
        display_window.screen,
        display_window.light_grey,
        pygame.Rect(0, 0, display_window.panel_width, display_window.screen_height),
    )

    # headings and instruction text on the left panel
    display_window.draw_text(
        display_window.screen,
        "Series Visualiser",
        display_window.large_font,
        16,
        12,
        display_window.dark_grey,
    )
    display_window.draw_text(
        display_window.screen,
        "Enter function (e.g. exp(x), sin(x)):",
        display_window.small_font,
        16,
        44,
        display_window.dark_grey,
    )

    # draw the main function input box
    display_window.input_box.draw(display_window.screen)

    # draw the experiment control labels and inputs
    display_window.draw_text(
        display_window.screen, "Centre (float):", display_window.small_font, 16, 296, display_window.dark_grey
    )
    display_window.centre_input.draw(display_window.screen)
    display_window.draw_text(
        display_window.screen,
        "Number of terms (int):",
        display_window.small_font,
        16,
        336,
        display_window.dark_grey,
    )
    display_window.num_terms_input.draw(display_window.screen)

    # draw the buttons
    for button in display_window.buttons:
        button.draw(surface=display_window.screen)

    # directory info (outside the button loop)
    display_window.draw_text(
        display_window.screen,
        f"Plots saved to: {display_window.settings.plots_directory}",
        display_window.small_font,
        16,
        412,
        display_window.dark_grey,
    )

    # right-side display rectangle (preview area)
    display_rect = pygame.Rect(
        display_window.panel_width + 10,
        10,
        display_window.display_width - 20,
        display_window.screen_height - 20,
    )
    pygame.draw.rect(display_window.screen, (250, 250, 250), display_rect)  # preview background
    pygame.draw.rect(display_window.screen, display_window.dark_grey, display_rect, 1)  # border

    # blit the plot preview if available, otherwise placeholder text
    if display_window.last_plot_surface is not None:
        display_window.screen.blit(display_window.last_plot_surface, (display_window.panel_width + 20, 20))
    else:
        display_window.draw_text(
            display_window.screen,
            "Plot will appear here after you click a button.",
            display_window.small_font,
            display_window.panel_width + 20,
            30,
            display_window.dark_grey,
        )

    # draw experiment stats if present
    stats_y = 460
    stats = display_window.experiment_stats
    if stats["centre_used"] is not None:
        display_window.draw_text(display_window.screen, f"Centre: {stats['centre_used']}", display_window.small_font, 16, stats_y, display_window.dark_grey)
        display_window.draw_text(display_window.screen, f"Terms: {stats['num_terms_used']}", display_window.small_font, 16, stats_y + 18, display_window.dark_grey)
        display_window.draw_text(display_window.screen, "Maclaurin:", display_window.small_font, 16, stats_y + 40, display_window.dark_grey)
        maclaurin_max = f"{stats['maclaurin_max_error']:.3g}" if stats['maclaurin_max_error'] is not None else "N/A"
        maclaurin_mse = f"{stats['maclaurin_mse']:.3g}" if stats['maclaurin_mse'] is not None else "N/A"
        display_window.draw_text(display_window.screen, f"  max err = {maclaurin_max}", display_window.small_font, 16, stats_y + 58, display_window.dark_grey)
        display_window.draw_text(display_window.screen, f"  MSE     = {maclaurin_mse}", display_window.small_font, 16, stats_y + 76, display_window.dark_grey)
        display_window.draw_text(display_window.screen, "Taylor:", display_window.small_font, 16, stats_y + 98, display_window.dark_grey)
        taylor_max = f"{stats['taylor_max_error']:.3g}" if stats['taylor_max_error'] is not None else "N/A"
        taylor_mse = f"{stats['taylor_mse']:.3g}" if stats['taylor_mse'] is not None else "N/A"
        display_window.draw_text(display_window.screen, f"  max err = {taylor_max}", display_window.small_font, 16, stats_y + 116, display_window.dark_grey)
        display_window.draw_text(display_window.screen, f"  MSE     = {taylor_mse}", display_window.small_font, 16, stats_y + 134, display_window.dark_grey)
    else:
        display_window.draw_text(display_window.screen, "Run an experiment to see error stats here.", display_window.small_font, 16, stats_y, display_window.dark_grey)

    # update the display and cap FPS
    pygame.display.flip()
    display_window.clock.tick(30)

# cleanup on exit
pygame.quit()
sys.exit()
