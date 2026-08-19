"""
Frame processing pipeline - detects, tracks, and classifies movement.
"""
import cv2
import imutils
from detector_config import (FRAME_WIDTH, MOVEMENT_THRESHOLD, SHOW_VIDEO,
                            DISPLAY_FPS, DISPLAY_STATUS, FRAME_SKIP_DISPLAY)
from detector_vision import (detect_largest_person, centroid_from_bbox,
                            compute_movement)


class FrameProcessor:
    """Processes video frames for detection and tracking."""
    
    def __init__(self, net, tracking_state):
        self.net = net
        self.tracking_state = tracking_state

    def process_frame(self, frame, frame_idx):
        """
        Process a single frame: detect, track, compute movement.
        
        Returns: (display_frame, should_emit_event, event_data)
        """
        # Resize frame for processing
        frame = imutils.resize(frame, width=FRAME_WIDTH)
        display = frame.copy()
        h, w = frame.shape[:2]

        # Detection (frame-skipped)
        if self.tracking_state.should_detect(frame_idx):
            bbox = detect_largest_person(self.net, frame)
            self.tracking_state.mark_detection_frame(frame_idx)
            
            if bbox is not None:
                self.tracking_state.start_tracking(
                    __import__('detector_model').create_tracker(),
                    frame,
                    bbox
                )
            else:
                self.tracking_state.tracking = False

        # Tracking update (lightweight)
        if self.tracking_state.tracking:
            ok, bbox = self.tracking_state.update_tracking(frame)
            if ok:
                cent = centroid_from_bbox(bbox)
                self.tracking_state.add_centroid(cent)
                if SHOW_VIDEO:
                    x, y, bw, bh = bbox
                    cv2.rectangle(display, (x, y), (x + bw, y + bh), (0, 255, 255), 2)
                    cv2.circle(display, cent, 4, (0, 0, 255), -1)
            else:
                self.tracking_state.tracking = False

        # Movement detection
        event_data = None
        if len(self.tracking_state.centroid_history) > 0:
            smoothed = self.tracking_state.get_smoothed_centroid()
            if SHOW_VIDEO:
                cv2.circle(display, smoothed, 6, (255, 0, 0), 2)

            if self.tracking_state.last_reported_centroid is None:
                self.tracking_state.last_reported_centroid = smoothed

            dx, dy = compute_movement(self.tracking_state.last_reported_centroid, smoothed)
            horiz_exceeded = abs(dx) >= MOVEMENT_THRESHOLD
            vert_exceeded = abs(dy) >= MOVEMENT_THRESHOLD

            if ((horiz_exceeded or vert_exceeded) and 
                self.tracking_state.should_emit_event(frame_idx)):
                
                direction_cat = "middle"
                movement_cat = "middle"
                if horiz_exceeded:
                    direction_cat = "right" if dx > 0 else "left"
                if vert_exceeded:
                    movement_cat = "down" if dy > 0 else "up"

                event_data = {
                    'direction': direction_cat,
                    'movement': movement_cat,
                    'dx': dx,
                    'dy': dy,
                }

                self.tracking_state.mark_event_frame(frame_idx)
                self.tracking_state.last_reported_centroid = smoothed

                if SHOW_VIDEO:
                    overlay_text = f"Direction: {direction_cat.upper()} | Movement: {movement_cat.upper()}"
                    cv2.putText(display, overlay_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 0, 255), 2, cv2.LINE_AA)

        return display, event_data

    def render_display(self, display, frame_idx, start_time, should_display):
        """Optionally render display frame with FPS/status."""
        if not SHOW_VIDEO or not should_display:
            return

        if DISPLAY_STATUS:
            status_text = "TRACKING" if self.tracking_state.tracking else "DETECTING"
            cv2.putText(display, status_text, (20, display.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if DISPLAY_FPS:
            elapsed = (start_time - __import__('time').time())
            fps = frame_idx / max(1, -elapsed) if elapsed != 0 else 0
            cv2.putText(display, f"FPS: {fps:.1f}", (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Person Direction Detector (Optimized)", display)