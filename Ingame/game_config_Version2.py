"""
Game configuration - centralized settings for the jump-n-run game.
"""

# Model & file paths
MODEL_DIR = 'models'
DEFAULT_MODEL_URL = 'https://github.com/KhronosGroup/glTF-Sample-Models/raw/master/2.0/Fox/glTF-Binary/Fox.glb'
DEFAULT_MODEL_FILENAME = 'model.glb'

# Lane configuration
LANE_X = [-2.0, 0.0, 2.0]
NUM_LANES = len(LANE_X)

# World generation
NUM_INITIAL_SEGMENTS = 10
SEGMENT_LENGTH = 10.0
SEGMENT_WIDTH = 6.0
WORLD_SPEED = 8.0
CROUCH_SPEED_FACTOR = 0.7

# Procedural generation chances
OBSTACLE_CHANCE = 0.25
COIN_CHANCE = 0.35

# Sizes
OBSTACLE_SIZE = (0.6, 1.4, 0.6)  # (width, height, depth)
COIN_SIZE = 0.35

# Physics
GRAVITY = 30.0
JUMP_SPEED = 12.0

# Particles
PARTICLE_LIFETIME = 0.9
PARTICLE_COUNT = 8
PARTICLE_SPEED = 3.5
LEAF_CHANCE = 0.35

# Input handling
INPUT_TIMEOUT = 0.7  # seconds to reset input on timeout

# Camera
CAMERA_FOLLOW_SPEED = 6.0
CAMERA_OFFSET = (0, 5, -10)
CAMERA_ROTATION = (10, 0, 0)
CAMERA_LOOK_OFFSET = (0, 1.0, 8)

# Window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Jump N Run - 3 Lanes (Body Movement Controlled)"

# HUD
SCORE_TEXT_POS = (-0.85, 0.45)
SCORE_TEXT_SCALE = 2
INFO_TEXT_POS = (-0.85, 0.40)
INFO_TEXT_SCALE = 1.2