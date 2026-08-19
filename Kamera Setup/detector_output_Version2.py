"""
Output handling - JSON event serialization and threading.
"""
import json
import sys
import threading
import time
from collections import OrderedDict
from queue import Queue, Empty


class OutputManager:
    """Non-blocking JSON output via background thread."""
    
    def __init__(self, queue_size=10):
        self.queue = Queue(maxsize=queue_size)
        self.running = True
        self._start_worker()

    def _start_worker(self):
        """Start background thread that writes to stdout."""
        t = threading.Thread(target=self._output_worker, daemon=True)
        t.start()

    def _output_worker(self):
        """Background thread for printing JSON to avoid blocking video processing."""
        while self.running:
            try:
                event = self.queue.get(timeout=1.0)
                if event is None:
                    break
                print(json.dumps(event, ensure_ascii=False, separators=(",", ":"), sort_keys=False), flush=True)
            except Empty:
                continue
            except Exception as e:
                print(f"Output error: {e}", file=sys.stderr)

    def send_event(self, timestamp, direction, movement, dx, dy, frame_idx, tracking):
        """Queue an event for output (non-blocking)."""
        if self.queue.full():
            # Drop oldest event if queue is full (prefer recent events)
            try:
                self.queue.get_nowait()
            except Empty:
                pass
        
        event = OrderedDict([
            ("timestamp", timestamp),
            ("Direction", direction),
            ("Movement", movement),
            ("dx", int(dx)),
            ("dy", int(dy)),
            ("frame", frame_idx),
            ("tracking", bool(tracking))
        ])
        
        try:
            self.queue.put_nowait(event)
        except Exception:
            pass  # Queue full, skip this event

    def shutdown(self):
        """Stop output worker thread."""
        self.running = False
        self.queue.put(None)