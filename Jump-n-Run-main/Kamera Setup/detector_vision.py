"""
Computer vision operations - detection, tracking, centroid computation.
"""
import cv2
import numpy as np
from detector_config import (DETECTION_CONF, PERSON_CLASS_ID, DNN_INPUT_SIZE,
                            DNN_SCALE, DNN_MEAN)


def detect_largest_person(net, frame, conf_threshold=DETECTION_CONF):
    """
    Run DNN detection and return bbox (x, y, w, h) for the largest person or None.
    
    Optimized:
    - Early exit on low confidence
    - Vectorized bounds checking
    - Only returns if area > current largest
    """
    h, w = frame.shape[:2]
    
    # Prepare blob for MobileNetSSD (expects 300x300)
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, DNN_INPUT_SIZE), DNN_SCALE, DNN_INPUT_SIZE, DNN_MEAN)
    net.setInput(blob)
    detections = net.forward()

    largest_bbox = None
    largest_area = 0

    # Detections format for MobileNetSSD: [1, 1, N, 7]
    num_detections = detections.shape[2]
    for i in range(num_detections):
        confidence = float(detections[0, 0, i, 2])
        
        # Early exit: skip low-confidence detections
        if confidence < conf_threshold:
            continue
        
        cls = int(detections[0, 0, i, 1])
        
        # Early exit: skip non-person classes
        if cls != PERSON_CLASS_ID:
            continue

        # Compute bbox with bounds checking (vectorized)
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        startX, startY, endX, endY = np.clip(box.astype("int"), 0, [w-1, h-1, w-1, h-1])
        
        bw = endX - startX
        bh = endY - startY
        
        if bw <= 0 or bh <= 0:
            continue
        
        area = bw * bh
        if area > largest_area:
            largest_area = area
            largest_bbox = (startX, startY, bw, bh)

    return largest_bbox


def centroid_from_bbox(bbox):
    """Compute centroid from bbox (x, y, w, h) -> (cx, cy)."""
    x, y, w, h = bbox
    return (int(x + w / 2), int(y + h / 2))


def compute_smoothed_centroid(history):
    """
    Compute smoothed centroid from deque using numpy.
    Faster than looping in Python.
    """
    if not history:
        return None
    points = np.array(list(history))
    smoothed = points.mean(axis=0).astype(int)
    return tuple(smoothed)


def compute_movement(centroid1, centroid2):
    """Compute movement vector (dx, dy) between two centroids."""
    if centroid1 is None or centroid2 is None:
        return 0, 0
    dx = centroid2[0] - centroid1[0]
    dy = centroid2[1] - centroid1[1]
    return dx, dy
