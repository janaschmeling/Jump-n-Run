"""
Tracking state management - maintains tracker, detection state, history.
"""
from collections import deque
from detector_config import SMOOTH_HISTORY, DETECT_INTERVAL, MIN_FRAMES_BETWEEN_EVENTS


class TrackingState:
    """Manages tracking state and centroid history."""
    
    def __init__(self):
        self.tracker = None
        self.tracking = False
        self.centroid_history = deque(maxlen=SMOOTH_HISTORY)
        self.last_reported_centroid = None
        self.last_detection_frame = -DETECT_INTERVAL
        self.last_event_frame = -MIN_FRAMES_BETWEEN_EVENTS

    def start_tracking(self, tracker, frame, bbox):
        """Initialize tracker on detected person."""
        try:
            self.tracker = tracker
            ok = tracker.init(frame, tuple(bbox))
            if ok:
                self.tracking = True
                self.centroid_history.clear()
                from detector_vision import centroid_from_bbox
                cent = centroid_from_bbox(bbox)
                self.centroid_history.append(cent)
                self.last_reported_centroid = None
                return True
            else:
                self.tracking = False
                self.tracker = None
                return False
        except Exception:
            self.tracking = False
            self.tracker = None
            return False

    def update_tracking(self, frame):
        """Update tracker and return success, bbox."""
        if not self.tracking or self.tracker is None:
            return False, None
        
        try:
            ok, box = self.tracker.update(frame)
            if ok:
                x, y, w, h = [int(v) for v in box]
                if w <= 0 or h <= 0:
                    self.tracking = False
                    return False, None
                return True, (x, y, w, h)
            else:
                self.tracking = False
                return False, None
        except Exception:
            self.tracking = False
            return False, None

    def add_centroid(self, centroid):
        """Add centroid to history."""
        self.centroid_history.append(centroid)

    def get_smoothed_centroid(self):
        """Get smoothed centroid or None."""
        if not self.centroid_history:
            return None
        from detector_vision import compute_smoothed_centroid
        return compute_smoothed_centroid(self.centroid_history)

    def should_detect(self, frame_idx):
        """Check if DNN detection should run (frame skipping)."""
        if not self.tracking:
            return True
        if (frame_idx - self.last_detection_frame) >= DETECT_INTERVAL:
            return True
        return False

    def mark_detection_frame(self, frame_idx):
        """Mark frame as detection run."""
        self.last_detection_frame = frame_idx

    def should_emit_event(self, frame_idx):
        """Check if enough frames have passed since last event."""
        if (frame_idx - self.last_event_frame) >= MIN_FRAMES_BETWEEN_EVENTS:
            return True
        return False

    def mark_event_frame(self, frame_idx):
        """Mark frame as event emission."""
        self.last_event_frame = frame_idx
        from detector_vision import centroid_from_bbox
        # last_reported_centroid updated separately in main loop

    def reset(self):
        """Reset tracking state."""
        self.tracker = None
        self.tracking = False
        self.centroid_history.clear()
        self.last_reported_centroid = None