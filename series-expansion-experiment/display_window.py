import pygame
import sys
import os
import settings
from series import evaluate_series_function
from plot_helper import plot_series_graphs
import numpy  # used in callbacks to compute stats

# initialise pygame
pygame.init()

# set up window dimensions for UI
screen_width = 1000
screen_height = 600
panel_width = 300      # width for left control panel
display_width = screen_width - panel_width  # width for right display area

# create the main display window
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Series Expansion Visualizer")

white = (255, 255, 255)
light_grey = (240, 240, 240)
dark_grey = (50, 50, 50)
button_background = (30, 130, 180)
button_hovered = (40, 170, 220)

small_font = pygame.font.SysFont('Arial', 16)
medium_font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 32)

def draw_text(surface, text, font, x, y, color=dark_grey):
    """Helper function to draw text on a surface at (x, y)"""
    txt_surf = font.render(text, True, color)
    rect = txt_surf.get_rect(topleft=(x, y))
    surface.blit(txt_surf, rect)
    return rect

class Button:
    """Class representing a clickable button in the UI"""
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)   # button rectangle
        self.text = text                                # button label
        self.callback = callback                        # function to call on click
        self.hovered = False                            # hover flag

    def draw(self, surface):
        background = button_hovered if self.hovered else button_background
        pygame.draw.rect(surface, background, self.rect)               # draw button bg
        text = medium_font.render(self.text, True, white)             # render text
        surface.blit(text, text.get_rect(center=self.rect.center))    # center text

    def handle_event(self, event):
        # update hover state on mouse motion
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        # handle click (left mouse button)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()   # call the provided callback

class TextInput:
    """Class representing a text input box"""
    def __init__(self, x, y, width, height, text=""):
        self.rect = pygame.Rect(x, y, width, height)   # rectangle for the input box
        self.text = text                                # current text string
        self.active = False                             # focus state
        self.cursor_visible = True                      # cursor blink visible flag
        self.cursor_timer = 0                           # timer for blinking

    def draw(self, surf):
        background = white if self.active else light_grey  # white when active, grey otherwise
        pygame.draw.rect(surf, background, self.rect)      # input background
        pygame.draw.rect(surf, dark_grey, self.rect, 1)    # border
        txt_surf = medium_font.render(self.text, True, dark_grey)  # render current text
        surf.blit(txt_surf, (self.rect.x + 6, self.rect.y + 6))    # draw at slight inset
        if self.active:                             # show blinking cursor only when active
            self.cursor_timer += clock.get_time() / 1000.0
            if self.cursor_timer > 0.5:
                self.cursor_timer = 0.0
                self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                cursor_x = self.rect.x + 6 + medium_font.size(self.text)[0] + 2
                pygame.draw.line(
                    surf,
                    dark_grey,
                    (cursor_x, self.rect.y + 6),
                    (cursor_x, self.rect.y + self.rect.height - 6),
                    2
                )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # focus/unfocus depending on whether click was inside the box
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            # process keyboard when active
            if event.key == pygame.K_RETURN:
                self.active = False                  # Enter unfocuses
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]          # delete last char
            else:
                character = event.unicode
                if character and character.isprintable():
                    self.text += character          # append typed character

# frame clock used for consistent FPS and cursor blink timing
clock = pygame.time.Clock()

# create UI controls: input box and placeholders for the last plot
# pass default text as positional argument
input_box = TextInput(16, 64, panel_width - 32, 36, "exp(x)")
# small inputs for Day 5: centre and number of terms
centre_input = TextInput(16, 320, panel_width - 32, 28, "0.0")
num_terms_input = TextInput(16, 360, panel_width - 32, 28, "5")

last_plot_surface = None    # will hold pygame Surface loaded from saved PNG
last_plot_path = None       # path to last saved PNG file

# experiment stats container for UI display (populated by run_experiment callback)
experiment_stats = {
    "maclaurin_max_error": None,
    "maclaurin_mse": None,
    "taylor_max_error": None,
    "taylor_mse": None,
    "centre_used": None,
    "num_terms_used": None
}

# --- callbacks with inline evaluation & plotting (keeps code simple) ---

def start_maclaurin_plot():
    """
    Callback to compute series (Maclaurin centre=0), save plot PNG and load it into pygame.
    This runs inline and will block the UI while computing/saving the plot.
    """
    global last_plot_surface, last_plot_path
    fn = input_box.text.strip() or "exp(x)"

    # evaluate the true function and both approximations using the series module
    x, y_true, y_mac, y_tay, meta = evaluate_series_function(
        fn,
        centre=0.0,
        maclaurin_num_terms=settings.default_num_terms,
        taylor_num_terms=settings.default_num_terms,
        x_min=settings.min_x,
        x_max=settings.max_x,
        num_x_points=settings.num_x_points
    )

    # save plot to PNG
    safe_fn = fn.replace('/', '_div_').replace(' ', '')
    out_fname = os.path.join(settings.plots_directory, f"{safe_fn}_plot.png")
    plot_series_graphs(x, y_true, y_mac, y_tay, meta, out_filename=out_fname)

    # load saved PNG and prepare preview surface
    last_plot_path = out_fname
    last_plot_surface = pygame.image.load(last_plot_path).convert()
    last_plot_surface = pygame.transform.smoothscale(
        last_plot_surface, (display_width - 40, screen_height - 80)
    )

def start_taylor_plot():
    """
    Callback to compute series centered at 0.5 (example), save plot PNG and load it into pygame.
    """
    global last_plot_surface, last_plot_path
    fn = input_box.text.strip() or "exp(x)"

    # evaluate with centre 0.5
    x, y_true, y_mac, y_tay, meta = evaluate_series_function(
        fn,
        centre=0.5,
        maclaurin_num_terms=settings.default_num_terms,
        taylor_num_terms=settings.default_num_terms,
        x_min=settings.min_x,
        x_max=settings.max_x,
        num_x_points=settings.num_x_points
    )

    # save & load image
    safe_fn = fn.replace('/', '_div_').replace(' ', '')
    out_fname = os.path.join(settings.plots_directory, f"{safe_fn}_plot.png")
    plot_series_graphs(x, y_true, y_mac, y_tay, meta, out_filename=out_fname)
    last_plot_path = out_fname
    last_plot_surface = pygame.image.load(last_plot_path).convert()
    last_plot_surface = pygame.transform.smoothscale(
        last_plot_surface, (display_width - 40, screen_height - 80)
    )

def start_run_experiment():
    """
    Runs a single experiment instance using the user-specified centre and number of terms.
    Populates experiment_stats with error values and updates the preview image.
    """
    global last_plot_surface, last_plot_path, experiment_stats

    # read inputs
    fn = input_box.text.strip() or "exp(x)"
    # parse centre input safely
    centre_text = centre_input.text.strip()
    try:
        centre_val = float(centre_text) if centre_text != "" else 0.0
    except Exception:
        centre_val = 0.0
    # parse number-of-terms input safely
    num_terms_text = num_terms_input.text.strip()
    try:
        num_terms_val = int(num_terms_text) if num_terms_text != "" else settings.default_num_terms
        if num_terms_val < 1:
            num_terms_val = 1
        if num_terms_val > settings.max_num_terms:
            num_terms_val = settings.max_num_terms
    except Exception:
        num_terms_val = settings.default_num_terms

    # evaluate series with given parameters
    x, y_true, y_mac, y_tay, meta = evaluate_series_function(
        fn,
        centre=centre_val,
        maclaurin_num_terms=num_terms_val,
        taylor_num_terms=num_terms_val,
        x_min=settings.min_x,
        x_max=settings.max_x,
        num_x_points=settings.num_x_points
    )

    # compute error stats using numpy, ignoring NaNs
    with numpy.errstate(all="ignore"):
        mac_diff = numpy.abs(y_true - y_mac)
        mac_max_err = float(numpy.nanmax(mac_diff)) if mac_diff.size else float('nan')
        mac_mse = float(numpy.nanmean((y_true - y_mac)**2)) if y_true.size else float('nan')

        tay_diff = numpy.abs(y_true - y_tay)
        tay_max_err = float(numpy.nanmax(tay_diff)) if tay_diff.size else float('nan')
        tay_mse = float(numpy.nanmean((y_true - y_tay)**2)) if y_true.size else float('nan')

    # store stats for UI display
    experiment_stats["maclaurin_max_error"] = mac_max_err
    experiment_stats["maclaurin_mse"] = mac_mse
    experiment_stats["taylor_max_error"] = tay_max_err
    experiment_stats["taylor_mse"] = tay_mse
    experiment_stats["centre_used"] = centre_val
    experiment_stats["num_terms_used"] = num_terms_val

    # save the plot and load preview
    safe_fn = fn.replace('/', '_div_').replace(' ', '')
    out_fname = os.path.join(settings.plots_directory, f"{safe_fn}_plot.png")
    plot_series_graphs(x, y_true, y_mac, y_tay, meta, out_filename=out_fname)
    last_plot_path = out_fname
    last_plot_surface = pygame.image.load(last_plot_path).convert()
    last_plot_surface = pygame.transform.smoothscale(
        last_plot_surface, (display_width - 40, screen_height - 80)
    )

# create button instances, passing the callbacks defined above
btn_mac = Button(16, 120, panel_width - 32, 44, "Plot Maclaurin", start_maclaurin_plot)
btn_tay = Button(16, 176, panel_width - 32, 44, "Plot Taylor (c=0.5)", start_taylor_plot)
btn_exp = Button(16, 232, panel_width - 32, 44, "Run Experiment (single)", start_run_experiment)

# list of buttons for event handling and drawing
buttons = [btn_mac, btn_tay, btn_exp]

