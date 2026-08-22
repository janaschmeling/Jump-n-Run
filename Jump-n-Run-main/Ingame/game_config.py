"""
Game configuration - centralized settings for the jump-n-run game.
"""

# Model & file paths
MODEL_DIR = 'models'
DEFAULT_MODEL_URL = 'https://github.com/KhronosGroup/glTF-Sample-Models/raw/master/2.0/Fox/glTF-Binary/Fox.glb'
DEFAULT_MODEL_FILENAME = 'model.glb'
DEFAULT_MODEL_FILENAME = 'model.glb'

# Lane configuration
LANE_X = [-2.0, 0.0, 2.0]
NUM_LANES = len(LANE_X)

# World generation
NUM_INITIAL_SEGMENTS = 10
SEGMENT_LENGTH = 10.0
SEGMENT_WIDTH = 6.0

# Base world speed in game units per second
# WORLD_SPEED set to ~11.111 units/sec which approximates 40 km/h if 1 unit == 1 meter
WORLD_SPEED = 11.111

# Segment visual
SEGMENt_WIDTH = SEGMENT_WIDTH

# Obstacle & spawn
OBSTACLE_CHANCE = 0.25
OBSTACLE_SIZE = (0.8, 1.6, 0.8)

# Coins removed (kept here for legacy compatibility)
COIN_CHANCE = 0.0
COIN_SIZE = (0.3, 0.3, 0.3)

# Physics
GRAVITY = 30.0
JUMP_SPEED = 12.0  # not used - jump disabled

# Particle / visual
PARTICLE_COUNT = 8
PARTICLE_SPEED = 3.5
LEAF_CHANCE = 0.3

# Input handling
INPUT_TIMEOUT = 0.7

# Camera & window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'Jump N Run - 3 Lanes (Body Movement Controlled)'
CAMERA_FOLLOW_SPEED = 6.0
# camera offset: x follows player.x, y is height, z is behind the player (negative forwards)
CAMERA_OFFSET = (0, 3.0, 8.0)
CAMERA_ROTATION = (18, 0, 0)
CAMERA_LOOK_OFFSET = (0, 0.6, -6.0)
CAMERA_POSITION_LOCK = True

# HUD
SCORE_TEXT_POS = (-0.86, 0.42)
SCORE_TEXT_SCALE = 1.2
INFO_TEXT_POS = (-0.86, 0.35)
INFO_TEXT_SCALE = 0.8

# Display
SCORE_TEXT_POS = (-0.86, 0.42)

# Hit & game over settings
HIT_OVERLAY_DURATION = 2.0
MAX_HITS = 2
WARNING_SOUND_PATH = 'assets/warn.wav'  # placeholder path

# Other tuning
CROUCH_SPEED_FACTOR = 0.95

