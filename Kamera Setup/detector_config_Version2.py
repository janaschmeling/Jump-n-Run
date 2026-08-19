"""
Detector configuration - centralized settings for person direction detection.
"""

# Video input
FRAME_WIDTH = 480  # reduced from 640 for faster processing
FRAME_SKIP_DISPLAY = 2  # show video every N frames (set higher for headless)

# Detection & tracking
SMOOTH_HISTORY = 3  # reduced from 5 for lower latency
MOVEMENT_THRESHOLD = 30  # increased slightly for noise reduction
MIN_FRAMES_BETWEEN_EVENTS = 8  # reduced from 10 for more responsive input
DETECT_INTERVAL = 45  # increased from 30 (fewer DNN calls)
DETECTION_CONF = 0.6  # increased from 0.5 (fewer false positives)

# Model paths
MODEL_DIR = "models"
PROTOTXT_URL = "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt"
CAFFEMODEL_URL = "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.caffemodel"
PROTOTXT_PATH = f"{MODEL_DIR}/MobileNetSSD_deploy.prototxt"
CAFFEMODEL_PATH = f"{MODEL_DIR}/MobileNetSSD_deploy.caffemodel"

# DNN & class
PERSON_CLASS_ID = 15
DNN_INPUT_SIZE = (300, 300)
DNN_SCALE = 0.007843
DNN_MEAN = 127.5

# Display/debugging
SHOW_VIDEO = True  # Set to False for headless mode (faster)
DISPLAY_FPS = True
DISPLAY_STATUS = True

# Threading
OUTPUT_QUEUE_SIZE = 10