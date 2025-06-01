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