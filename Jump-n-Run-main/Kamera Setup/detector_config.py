"""
Detector configuration - centralized settings for person direction detection.
"""

# VIDEO input
FRAME_WIDTH = 480  # reduced from 640 for faster processing
FRAME_SKIP_DISPLAY = 2  # show video every N frames (show higher for headless)

# Detection & tracking
SMOOTH_HISTORY = 3  # reduced from 5 for lower latency
MOVEMENT_THRESHOLD = 30  # increased slightly for noise reduction
MIN_FRAMES_BETWEEN_EVENTS = 8  # reduced from 10 for more responsive input
DETECT_CONF = 0.45  # increased from 0.4 (fewer false positives)
DETECTION_INTERVAL = 45  # increased from 30 (fewer repeated detections)
DETECTIONION_CONF = 0.6  # increased from 0.5 (more conservative confidence)

# Model paths
MODEL_DIR = "models"
PROTOTXT_URL = "https://raw.githubusercontent.com/chuangqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt"
CAFFEMODEL_URL = "https://raw.githubusercontent.com/chuangqi305/MobileNet-SSD/master/MobileNetSSD_deploy.caffemodel"
PROTOTXT_PATH = f"{MODEL_DIR}/MobileNetSSD_deploy.prototxt"
CAFFEMODEL_PATH = f"{MODEL_DIR}/MobileNetSSD_deploy.caffemodel"

# DNN & display tuning
PERSON_CLASS_ID = 15
DNN_INPUT_SIZE = (300, 300)
DNN_SCALE = 0.007843
DNN_MEAN = 127.5

# Display / debugging
SHOW_VIDEO = True  # set False for headless / CI
DISPLAY_FPS = True
DISPLAY_STATUS = True

# Threading
OUTPUT_QUEUE_SIZE = 10

# Camera source configuration
# CAMERA_SOURCE may be one of:
# - None: auto-scan common device indices (0..max_scan) and pick the first working camera
# - an integer (e.g. 0, 1): use that camera device index
# - a string path/URL (e.g. "/dev/video2" or "rtsp://..." or "http://192.168.x.x:8080/live")
# To use your Insta360 device, you can either set CAMERA_SOURCE to the device index
# the OS assigns to Insta360 (e.g. 2), or set it to the camera's stream URL if it exposes one.
CAMERA_SOURCE = None

# Prefer local UVC cameras (device indices / OS device paths) over network streams.
# When True the helper will scan local device indices first, then try any provided
# stream URL or explicit string source. This ensures connected webcams (Insta360 Link)
# are chosen before an RTSP/HTTP stream when both are available.
PREFER_LOCAL_CAMERA = True

# How long to wait when trying each device (seconds)
_CAMERA_OPEN_TIMEOUT = 1.5


def _try_convert_index(src):
    """Try to convert src to int device index, otherwise return original value."""
    try:
        return int(src)
    except (TypeError, ValueError):
        return src


def _is_probable_url(src):
    """Return True if src looks like a network stream URL (rtsp/http)"""
    if not isinstance(src, str):
        return False
    s = src.lower()
    return s.startswith("rtsp:") or s.startswith("http:") or s.startswith("https:")


def open_camera_source(cv2, max_scan=8, timeout_seconds=None, prefer_local=None):
    """
    Try to open a cv2.VideoCapture for CAMERA_SOURCE.

    Behavior:
    - If CAMERA_SOURCE is set and is a local device index or path (int or '/dev/...'), it will be
      tried first.
    - If PREFER_LOCAL_CAMERA (or prefer_local=True) is set, the function will scan local device
      indices 0..max_scan and return the first working camera before trying any URL stream.
    - If CAMERA_SOURCE is a network URL (rtsp/http) and prefer_local is True, network URL will be
      tried only after scanning local devices.

    Returns an opened cv2.VideoCapture or None if none could be opened.
    """
    import time

    if timeout_seconds is None:
        timeout_seconds = _CAMERA_OPEN_TIMEOUT

    if prefer_local is None:
        prefer_local = PREFER_LOCAL_CAMERA

    source = CAMERA_SOURCE

    # If prefer_local is set, scan local indices first
    if prefer_local:
        for i in range(0, max_scan + 1):
            try:
                cap = cv2.VideoCapture(i)
                t0 = time.time()
                while time.time() - t0 < timeout_seconds:
                    if cap.isOpened():
                        ret, _ = cap.read()
                        if ret:
                            return cap
                    time.sleep(0.05)
                try:
                    cap.release()
                except Exception:
                    pass
            except Exception:
                pass

    # If an explicit source is provided, attempt it (either index, path or URL)
    if source is not None:
        candidate = _try_convert_index(source)

        # If the source looks like a URL and we preferred local cameras, try it now
        cap = cv2.VideoCapture(candidate)
        t0 = time.time()
        while time.time() - t0 < timeout_seconds:
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    return cap
            time.sleep(0.05)
        try:
            cap.release()
        except Exception:
            pass

    # If we didn't prefer local earlier or explicit source failed, and prefer_local was False,
    # scan local indices as a fallback
    if not prefer_local:
        for i in range(0, max_scan + 1):
            try:
                cap = cv2.VideoCapture(i)
                t0 = time.time()
                while time.time() - t0 < timeout_seconds:
                    if cap.isOpened():
                        ret, _ = cap.read()
                        if ret:
                            return cap
                    time.sleep(0.05)
                try:
                    cap.release()
                except Exception:
                    pass
            except Exception:
                pass

    # No camera found
    return None
