"""
Model management - downloading and loading DNN models.
"""
import os
import sys
import urllib.request
from detector_config import (MODEL_DIR, PROTOTXT_PATH, CAFFEMODEL_PATH,
                            PROTOTXT_URL, CAFFEMODEL_URL)


def download_progress(block_num, block_size, total_size):
    """Simple download progress indicator."""
    if total_size <= 0:
        return
    downloaded = block_num * block_size
    percent = min(100, (downloaded * 100) // total_size)
    if percent % 10 == 0:
        print(f"  {percent}%", file=sys.stderr, end='\r')


def ensure_model_files():
    """Ensure model directory and files exist; download if missing."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    if not os.path.exists(PROTOTXT_PATH):
        print("Downloading prototxt...", file=sys.stderr)
        try:
            urllib.request.urlretrieve(PROTOTXT_URL, PROTOTXT_PATH, download_progress)
            print("\nPrototext downloaded.", file=sys.stderr)
        except Exception as e:
            print(f"Failed to download prototxt: {e}", file=sys.stderr)
            if not os.path.exists(PROTOTXT_PATH):
                raise

    if not os.path.exists(CAFFEMODEL_PATH):
        print("Downloading caffemodel (this may take a minute)...", file=sys.stderr)
        try:
            urllib.request.urlretrieve(CAFFEMODEL_URL, CAFFEMODEL_PATH, download_progress)
            print("\nCaffemodel downloaded.", file=sys.stderr)
        except Exception as e:
            print(f"Failed to download caffemodel: {e}", file=sys.stderr)
            if not os.path.exists(CAFFEMODEL_PATH):
                raise


def load_dnn_model():
    """Load the MobileNet-SSD DNN model for person detection."""
    import cv2
    print("Loading DNN model...", file=sys.stderr)
    net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, CAFFEMODEL_PATH)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net


def create_tracker():
    """Create a KCF tracker with compatibility across OpenCV versions."""
    import cv2
    tracker = None
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
        tracker = cv2.legacy.TrackerKCF_create()
    elif hasattr(cv2, "TrackerKCF_create"):
        tracker = cv2.TrackerKCF_create()
    else:
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
            tracker = cv2.legacy.TrackerCSRT_create()
        elif hasattr(cv2, "TrackerCSRT_create"):
            tracker = cv2.TrackerCSRT_create()
        else:
            raise RuntimeError("No KCF/CSRT tracker found in OpenCV build.")
    return tracker