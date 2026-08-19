"""
Game menu manager - orchestrates all menu screens and state transitions.
"""
import sys
from ursina import Ursina, window, camera, color, mouse
from menu_config import (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
                         BACKGROUND_COLOR, MENU_STATE_MAIN, MENU_STATE_SETTINGS,
                         MENU_STATE_PLAYING, MENU_STATE_QUIT)
from menu_main import MainMenuScreen
from menu_settings import SettingsMenuScreen


class GameMenuManager:
    """Manages game menu states and transitions."""
    
    def __init__(self):
        # Initialize Ursina
        self.app = Ursina()
        window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        window.title = WINDOW_TITLE
        
        # Set background color
        camera.background_color = color.rgb(*BACKGROUND_COLOR)
        
        # Game settings (persisted across menu)
        self.settings = {
            "Difficulty": 1,
            "Volume": 2,
            "Graphics": 1,
            "Show FPS": 0,
        }
        
        # Menu screens
        self.screens = {}
        self._init_screens()
        
        # Current state
        self.current_state = MENU_STATE_MAIN
        self.current_screen = self.screens[MENU_STATE_MAIN]
        
        # Input handling
        self.app.input = self._handle_input
        
        print("[MenuManager] Initialized", flush=True)

    def _init_screens(self):
        """Initialize all menu screens."""
        self.screens[MENU_STATE_MAIN] = MainMenuScreen(self._on_state_change)
        self.screens[MENU_STATE_SETTINGS] = SettingsMenuScreen(
            self._on_state_change,
            self.settings
        )

    def _on_state_change(self, new_state):
        """Handle state change request."""
        print(f"[MenuManager] State change: {self.current_state} -> {new_state}", flush=True)
        
        if self.current_state == new_state:
            return
        
        # Hide current screen
        if self.current_screen:
            self.current_screen.hide()
        
        # Handle state transition
        if new_state == MENU_STATE_QUIT:
            self.quit_game()
        elif new_state == MENU_STATE_PLAYING:
            self.start_game()
        elif new_state in self.screens:
            self.current_state = new_state
            self.current_screen = self.screens[new_state]
            self.current_screen.show()

    def start_game(self):
        """Start the game."""
        print("[MenuManager] Starting game with settings:", self.settings, flush=True)
        # TODO: Launch the actual game with these settings
        self.app.pause()

    def quit_game(self):
        """Quit the game."""
        print("[MenuManager] Quitting game", flush=True)
        sys.exit(0)

    def _handle_input(self, key):
        """Handle all keyboard input."""
        if self.current_screen:
            self.current_screen.handle_input(key)

    def update(self):
        """Main update loop."""
        if self.current_screen:
            self.current_screen.update(self.app.time_dt())

    def run(self):
        """Run the menu."""
        self.app.update = self.update
        
        # Handle mouse input
        def mouse_down():
            if self.current_screen and hasattr(self.current_screen, 'on_mouse_down'):
                self.current_screen.on_mouse_down()
        
        def mouse_up():
            if self.current_screen and hasattr(self.current_screen, 'on_mouse_up'):
                self.current_screen.on_mouse_up()
        
        # Bind mouse events
        mouse.left_click = mouse_down
        
        try:
            self.app.run()
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up all resources."""
        for screen in self.screens.values():
            screen.cleanup()
        print("[MenuManager] Cleanup complete", flush=True)


def main():
    """Entry point for the menu."""
    menu = GameMenuManager()
    menu.run()


if __name__ == '__main__':
    main()