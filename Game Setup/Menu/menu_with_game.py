"""
Menu integrated with game - allows transitioning between menu and game.

This script combines the menu system with the actual game.
"""
import sys
import subprocess
import argparse
from ursina import Ursina, window, camera, color
from menu_config import (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
                         BACKGROUND_COLOR, MENU_STATE_MAIN, MENU_STATE_SETTINGS,
                         MENU_STATE_PLAYING, MENU_STATE_QUIT)
from menu_main import MainMenuScreen
from menu_settings import SettingsMenuScreen


class IntegratedGameMenu:
    """Menu system integrated with the actual game."""
    
    def __init__(self, detector_cmd=None, pipe_mode=False, model_file=None):
        self.app = Ursina()
        window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        window.title = WINDOW_TITLE
        camera.background_color = color.rgb(*BACKGROUND_COLOR)
        
        self.settings = {
            "Difficulty": 1,
            "Volume": 2,
            "Graphics": 1,
            "Show FPS": 0,
        }
        
        self.detector_cmd = detector_cmd
        self.pipe_mode = pipe_mode
        self.model_file = model_file
        self.game_process = None
        
        self.screens = {}
        self._init_screens()
        
        self.current_state = MENU_STATE_MAIN
        self.current_screen = self.screens[MENU_STATE_MAIN]
        
        self.app.input = self._handle_input
        print("[IntegratedMenu] Initialized", flush=True)

    def _init_screens(self):
        """Initialize all menu screens."""
        self.screens[MENU_STATE_MAIN] = MainMenuScreen(self._on_state_change)
        self.screens[MENU_STATE_SETTINGS] = SettingsMenuScreen(
            self._on_state_change,
            self.settings
        )

    def _on_state_change(self, new_state):
        """Handle state change."""
        if self.current_state == new_state:
            return
        
        if self.current_screen:
            self.current_screen.hide()
        
        if new_state == MENU_STATE_QUIT:
            self.quit_game()
        elif new_state == MENU_STATE_PLAYING:
            self.launch_game()
        elif new_state in self.screens:
            self.current_state = new_state
            self.current_screen = self.screens[new_state]
            self.current_screen.show()

    def launch_game(self):
        """Launch the actual game."""
        print("[IntegratedMenu] Launching game with settings:", self.settings, flush=True)
        
        # Build game command
        cmd = [sys.executable, "game_main.py"]
        if self.pipe_mode:
            cmd.append("--pipe")
        if self.detector_cmd:
            cmd.extend(["--run", self.detector_cmd])
        if self.model_file:
            cmd.extend(["--model-file", self.model_file])
        
        try:
            # Launch game (this will block until game closes)
            self.game_process = subprocess.run(cmd)
            print("[IntegratedMenu] Game closed, returning to menu", flush=True)
            # Return to main menu
            self._on_state_change(MENU_STATE_MAIN)
        except Exception as e:
            print(f"[IntegratedMenu] Failed to launch game: {e}", flush=True)
            self._on_state_change(MENU_STATE_MAIN)

    def quit_game(self):
        """Quit the application."""
        print("[IntegratedMenu] Quitting", flush=True)
        sys.exit(0)

    def _handle_input(self, key):
        """Handle input."""
        if self.current_screen:
            self.current_screen.handle_input(key)

    def update(self):
        """Update loop."""
        if self.current_screen:
            self.current_screen.update(self.app.time_dt())

    def run(self):
        """Run the menu."""
        self.app.update = self.update
        
        def mouse_down():
            if self.current_screen and hasattr(self.current_screen, 'on_mouse_down'):
                self.current_screen.on_mouse_down()
        
        def mouse_up():
            if self.current_screen and hasattr(self.current_screen, 'on_mouse_up'):
                self.current_screen.on_mouse_up()
        
        try:
            self.app.run()
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup."""
        for screen in self.screens.values():
            screen.cleanup()
        if self.game_process:
            try:
                self.game_process.terminate()
            except Exception:
                pass
        print("[IntegratedMenu] Cleanup complete", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Jump N Run - Menu")
    parser.add_argument('--run', dest='command', type=str, default=None,
                        help='Command to run detector.')
    parser.add_argument('--pipe', action='store_true', help='Read detector JSON from stdin.')
    parser.add_argument('--model-file', type=str, default=None, help='Local GLB file.')
    args = parser.parse_args()

    menu = IntegratedGameMenu(
        detector_cmd=args.command,
        pipe_mode=args.pipe,
        model_file=args.model_file
    )
    menu.run()


if __name__ == '__main__':
    main()