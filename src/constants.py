# UI Colors
UI_COLORS = {
    'PANEL_BG': (45, 45, 55),
    'PANEL_BORDER': (80, 80, 90),
    'TEXT_PRIMARY': (230, 230, 240),
    'TEXT_SECONDARY': (180, 180, 180),
    'HIGHLIGHT': (120, 120, 220),
    'SUCCESS': (100, 220, 100),
    'ERROR': (220, 100, 100),
    'DISABLED': (150, 150, 160),
    'OVERLAY_BG': (0, 0, 0, 200),

    # Compass
    'COMPASS_BODY_DARK': (30, 30, 30),
    'COMPASS_BODY_MID': (50, 50, 50),
    'COMPASS_BODY_LIGHT': (80, 80, 80),
    'COMPASS_BORDER': (120, 120, 120),
    'COMPASS_INNER_RING': (70, 70, 70),
    'COMPASS_NEEDLE_PRIMARY': (255, 50, 50),
    'COMPASS_NEEDLE_SECONDARY': (200, 0, 0),
    'COMPASS_TAIL_PRIMARY': (220, 220, 220),
    'COMPASS_TAIL_SECONDARY': (170, 170, 170),
    'COMPASS_CARDINAL': (200, 200, 200),
    'COMPASS_INTERCARDINAL': (140, 140, 140),
    'COMPASS_PIVOT': (80, 80, 80),
    'COMPASS_PIVOT_CENTER': (255, 255, 255),
}
 
# UI Dimensions
UI_DIMENSIONS = {
    'DIALOG_HEIGHT': 150,
    'DIALOG_PADDING': 20,
    'DIALOG_BOTTOM_PADDING': 10,
    'DIALOG_HORIZONTAL_PADDING_PERCENT': 0.05,  # 5% of screen width
    'POPUP_BASE_Y_OFFSET': 100,  # Distance from bottom for popups
    'COMPASS_SIZE': 64,
    'COMPASS_MARGIN': 15,
}

# Animation Settings
UI_ANIMATION = {
    'CHAR_DELAY': 30,  # Milliseconds between characters in typewriter effect
    'TRIANGLE_SCALE_MIN': 0.9,
    'TRIANGLE_SCALE_MAX': 1.1,
    'TRIANGLE_SCALE_SPEED': 0.02,
    'POPUP_FADE_DURATION': 500,  # Milliseconds for popup fade out
}

# Font Sizes
UI_FONT_SIZES = {
    'LARGE': 28,
    'MEDIUM': 24,
    'SMALL': 16,
    'TINY': 14,
}

# UI Elements Alpha Values
UI_ALPHA = {
    'DIALOG_BG': 245,
    'POPUP_BG': 200,
    'OVERLAY': 200,
}

# Interactable Colors
INTERACTABLE_COLORS = {
    'DOOR_LOCKED': (255, 0, 255),
    'DOOR_OPEN': (0, 255, 255),
    'NOTE': (0, 255, 0),
    'EMPTY': (150, 150, 150),
    'COLLECTED': (100, 100, 100),
    'SELECTED': (255, 255, 0),
}

# Display settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 572
TERMINAL_GREEN = (0, 255, 0)
TERMINAL_DIM_GREEN = (0, 180, 0)
BG_COLOR = (10, 20, 10)

# Font settings
FONT_PATH = "assets/fonts/PixelSerif.ttf"
TERMINAL_FONT_SIZE = 24
TITLE_FONT_SIZE = 72
MENU_FONT_SIZE = 48

# Game states
STATE_MENU = 0
STATE_MENU_LOADING = 0.1
STATE_MENU_HOW_TO_PLAY = 0.2
STATE_MENU_SETTINGS = 0.3
STATE_MENU_CREDITS = 0.4
STATE_PRELUDE = 1
STATE_GAME = 2

# Menu configuration
MENU_ITEMS = ["Play", "How To Play", "Settings", "Credits", "Exit"]
CREATORS = ["[name1]", "[name2]", "[name3]", "[name4]"]
TITLE = "The Final String: Win By Making Better Passwords"
CONTROLS_TEXT = "Press 'W' or Up Arrow to move up, 'S' or Down Arrow to move down"

# Loading configuration
LOADING_DELAY = 2000
LOADING_STAGES = [
    ("Initializing engine", True),
    ("Generating levels", True),
    ("Loading assets", True),
    ("Finalizing setup", True)
]

TERMINAL_GREEN = (0, 255, 0)
TERMINAL_DIM_GREEN = (0, 180, 0)
TERMINAL_YELLOW = (255, 255, 0)