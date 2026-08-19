"""
Input handling - detector communication and mapping.
"""
import json
import subprocess
import threading
import time
import sys
from queue import Queue, Empty
from game_config import INPUT_TIMEOUT


class InputManager:
    """Handles detector communication and input state."""
    
    def __init__(self, detector_cmd=None, pipe_mode=False):
        self.input_state = {'Direction': 'middle', 'Movement': 'middle', 'last_update': 0.0}
        self.state_lock = threading.Lock()
        self.line_queue = Queue()
        self.stop_event = threading.Event()
        
        # Start detector reader threads
        if pipe_mode:
            self._start_stdin_reader()
        elif detector_cmd:
            self._start_command_reader(detector_cmd)

        # Start JSON parser thread
        self._start_parser_thread()

    def _start_stdin_reader(self):
        """Read detector output from stdin."""
        t = threading.Thread(target=self._read_stdin, daemon=True)
        t.start()

    def _start_command_reader(self, cmd):
        """Launch detector command and read its stdout."""
        t = threading.Thread(target=self._run_and_enqueue, args=(cmd,), daemon=True)
        t.start()

    def _start_parser_thread(self):
        """Parse JSON lines from detector output."""
        t = threading.Thread(target=self._parser_thread, daemon=True)
        t.start()

    def _read_stdin(self):
        """Read lines from stdin."""
        try:
            for raw in sys.stdin:
                if raw is None:
                    continue
                self.line_queue.put(raw.rstrip('\n'))
        except Exception:
            pass

    def _run_and_enqueue(self, cmd):
        """Run shell command and enqueue stdout lines."""
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        try:
            for raw in p.stdout:
                if raw is None:
                    continue
                self.line_queue.put(raw.rstrip('\n'))
        except Exception:
            pass
        finally:
            try:
                p.stdout.close()
            except Exception:
                pass

    def _parser_thread(self):
        """Parse JSON and update input state."""
        while not self.stop_event.is_set():
            try:
                line = self.line_queue.get(timeout=0.1)
            except Empty:
                continue
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            dir_val = obj.get('Direction', None)
            mov_val = obj.get('Movement', None)
            with self.state_lock:
                updated = False
                if dir_val in ('left', 'right', 'middle'):
                    self.input_state['Direction'] = dir_val
                    updated = True
                # Remove/ignore 'up' (jump). Only accept down (crouch) or middle.
                if mov_val in ('down', 'middle'):
                    self.input_state['Movement'] = mov_val
                    updated = True
                if updated:
                    self.input_state['last_update'] = time.time()

    def get_input(self):
        """Get latest input, reset on timeout."""
        with self.state_lock:
            now = time.time()
            if now - self.input_state['last_update'] > INPUT_TIMEOUT:
                self.input_state['Direction'] = 'middle'
                self.input_state['Movement'] = 'middle'
            return self.input_state['Direction'], self.input_state['Movement']

    def reset_direction(self):
        """Reset Direction to middle (one-shot)."""
        with self.state_lock:
            self.input_state['Direction'] = 'middle'

    def reset_movement(self):
        """Reset Movement to middle (one-shot)."""
        with self.state_lock:
            self.input_state['Movement'] = 'middle'

    def shutdown(self):
        """Stop input threads."""
        self.stop_event.set()
