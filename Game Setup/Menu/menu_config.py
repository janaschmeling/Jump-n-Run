"""
Menu configuration - centralized settings for the game menu.
"""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Jump N Run - Main Menu"
BACKGROUND_COLOR = (20, 20, 40)  # Dark blue

# Colors (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_HIGHLIGHT = (100, 200, 255)

# Button settings
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20
BUTTON_CORNER_RADIUS = 10

# Font settings
TITLE_FONT_SIZE = 3.0
BUTTON_FONT_SIZE = 1.5
SUBTITLE_FONT_SIZE = 1.0

# Menu positions
MENU_CENTER_X = WINDOW_WIDTH / 2
MENU_TOP_Y = WINDOW_HEIGHT * 0.2
MENU_SPACING = 100

# Animation settings
BUTTON_HOVER_SCALE = 1.1
BUTTON_PRESS_SCALE = 0.95
MENU_FADE_SPEED = 5.0
MENU_SLIDE_SPEED = 10.0

# Input settings
INPUT_COOLDOWN = 0.3  # seconds between key inputs
CONTROLLER_DEADZONE = 0.5

# Settings menu
SETTINGS_OPTIONS = [
    {"name": "Difficulty", "values": ["Easy", "Normal", "Hard"], "default": 1},
    {"name": "Volume", "values": ["Mute", "Low", "Medium", "High"], "default": 2},
    {"name": "Graphics", "values": ["Low", "Medium", "High"], "default": 1},
    {"name": "Show FPS", "values": ["Off", "On"], "default": 0},
]

# Menu states
MENU_STATE_MAIN = "main"
MENU_STATE_SETTINGS = "settings"
MENU_STATE_PLAYING = "playing"
MENU_STATE_PAUSED = "paused"
MENU_STATE_QUIT = "quit"