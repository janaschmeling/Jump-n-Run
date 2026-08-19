"""
Main menu screen - Start Game, Settings, Quit options.
"""
from ursina import Vec3, Text, color
from menu_screen import MenuScreen
from menu_button import MenuButton
from menu_config import (MENU_CENTER_X, MENU_TOP_Y, MENU_SPACING,
                         TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
                         COLOR_WHITE, COLOR_YELLOW, WINDOW_HEIGHT,
                         MENU_STATE_SETTINGS, MENU_STATE_PLAYING, MENU_STATE_QUIT)


class MainMenuScreen(MenuScreen):
    """The main menu with Start, Settings, and Quit options."""
    
    def __init__(self, on_state_change=None):
        super().__init__(on_state_change)
        self.input_cooldown = 0.0
        self._create_ui()

    def _create_ui(self):
        """Create main menu UI elements."""
        # Title
        title = Text(
            text="JUMP N RUN",
            position=Vec3(MENU_CENTER_X, MENU_TOP_Y, 0),
            font_size=TITLE_FONT_SIZE,
            color=COLOR_YELLOW,
            scale=1.0,
            origin=(0, 0)
        )
        self.elements.append(title)

        # Subtitle
        subtitle = Text(
            text="Move your body to play",
            position=Vec3(MENU_CENTER_X, MENU_TOP_Y - 80, 0),
            font_size=SUBTITLE_FONT_SIZE,
            color=COLOR_WHITE,
            scale=1.0,
            origin=(0, 0)
        )
        self.elements.append(subtitle)

        # Start Game button
        button_y = MENU_TOP_Y + 150
        start_btn = MenuButton(
            "START GAME",
            (MENU_CENTER_X, button_y),
            on_click=self._on_start_game
        )
        self.buttons = [start_btn]
        self.elements.append(start_btn.button_bg)
        self.elements.append(start_btn.text_entity)

        # Settings button
        settings_btn = MenuButton(
            "SETTINGS",
            (MENU_CENTER_X, button_y + MENU_SPACING),
            on_click=self._on_settings
        )
        self.buttons.append(settings_btn)
        self.elements.append(settings_btn.button_bg)
        self.elements.append(settings_btn.text_entity)

        # Quit button
        quit_btn = MenuButton(
            "QUIT",
            (MENU_CENTER_X, button_y + MENU_SPACING * 2),
            on_click=self._on_quit
        )
        self.buttons.append(quit_btn)
        self.elements.append(quit_btn.button_bg)
        self.elements.append(quit_btn.text_entity)

    def update(self, dt):
        """Update main menu logic."""
        if not self.active:
            return
        
        self.input_cooldown -= dt
        
        # Update all buttons
        for btn in self.buttons:
            btn.update(dt, self._get_mouse_pos())

    def handle_input(self, key):
        """Handle keyboard input."""
        if not self.active:
            return
        
        if self.input_cooldown > 0:
            return
        
        if key == 'escape':
            self._on_quit()
        elif key == 'up arrow':
            self._navigate(-1)
            self.input_cooldown = 0.2
        elif key == 'down arrow':
            self._navigate(1)
            self.input_cooldown = 0.2

    def on_mouse_down(self):
        """Handle mouse down on buttons."""
        for btn in self.buttons:
            btn.on_mouse_down()

    def on_mouse_up(self):
        """Handle mouse up on buttons."""
        for btn in self.buttons:
            btn.on_mouse_up()

    def _get_mouse_pos(self):
        """Get current mouse position."""
        from ursina import mouse
        if hasattr(mouse, 'position') and mouse.position is not None:
            return (mouse.position.x, mouse.position.y)
        return None

    def _navigate(self, direction):
        """Navigate between buttons."""
        # Find currently selected button (placeholder for now)
        pass

    def _on_start_game(self):
        """Start game button clicked."""
        print("[Menu] Starting game...", flush=True)
        self.change_state(MENU_STATE_PLAYING)

    def _on_settings(self):
        """Settings button clicked."""
        print("[Menu] Opening settings...", flush=True)
        self.change_state(MENU_STATE_SETTINGS)

    def _on_quit(self):
        """Quit button clicked."""
        print("[Menu] Quitting...", flush=True)
        self.change_state(MENU_STATE_QUIT)

    def cleanup(self):
        """Cleanup main menu."""
        for btn in self.buttons:
            btn.cleanup()
        super().cleanup()