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
STATE_LOADING = 0
STATE_MENU = 1
STATE_PRELUDE = 2
STATE_HOW_TO_PLAY = 3
STATE_SETTINGS = 4
STATE_CREDITS = 5

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