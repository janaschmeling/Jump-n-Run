"""
Settings menu screen - Adjust game settings.
"""
from ursina import Vec3, Text, color
from menu_screen import MenuScreen
from menu_button import MenuButton
from menu_config import (MENU_CENTER_X, MENU_TOP_Y, MENU_SPACING,
                         TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
                         COLOR_WHITE, COLOR_YELLOW, SETTINGS_OPTIONS,
                         BUTTON_WIDTH, MENU_STATE_MAIN)


class SettingsMenuScreen(MenuScreen):
    """Settings menu for adjusting game options."""
    
    def __init__(self, on_state_change=None, settings_dict=None):
        super().__init__(on_state_change)
        self.settings = settings_dict or {}
        self.selected_option = 0
        self.options = SETTINGS_OPTIONS
        self._create_ui()

    def _create_ui(self):
        """Create settings menu UI."""
        # Title
        title = Text(
            text="SETTINGS",
            position=Vec3(MENU_CENTER_X, MENU_TOP_Y, 0),
            font_size=TITLE_FONT_SIZE,
            color=COLOR_YELLOW,
            scale=1.0,
            origin=(0, 0)
        )
        self.elements.append(title)

        # Settings options
        self.option_displays = []
        button_y = MENU_TOP_Y + 150
        
        for i, opt in enumerate(self.options):
            y = button_y + i * MENU_SPACING
            
            # Option name
            name_text = Text(
                text=opt["name"] + ":",
                position=Vec3(MENU_CENTER_X - 300, y, 0),
                font_size=1.2,
                color=COLOR_WHITE,
                origin=(1, 0)
            )
            self.elements.append(name_text)
            
            # Option value display
            value_idx = self.settings.get(opt["name"], opt["default"])
            value_text = Text(
                text=opt["values"][value_idx],
                position=Vec3(MENU_CENTER_X, y, 0),
                font_size=1.2,
                color=COLOR_YELLOW,
                origin=(0, 0)
            )
            self.elements.append(value_text)
            self.option_displays.append(value_text)
            
            # Left button (decrease)
            left_btn = MenuButton(
                "-",
                (MENU_CENTER_X - 200, y),
                on_click=lambda opt_name=opt["name"]: self._decrease_option(opt_name),
                width=50,
                height=50
            )
            self.elements.append(left_btn.button_bg)
            self.elements.append(left_btn.text_entity)
            
            # Right button (increase)
            right_btn = MenuButton(
                "+",
                (MENU_CENTER_X + 200, y),
                on_click=lambda opt_name=opt["name"]: self._increase_option(opt_name),
                width=50,
                height=50
            )
            self.elements.append(right_btn.button_bg)
            self.elements.append(right_btn.text_entity)

        # Back button
        back_y = button_y + len(self.options) * MENU_SPACING + 100
        back_btn = MenuButton(
            "BACK",
            (MENU_CENTER_X, back_y),
            on_click=self._on_back
        )
        self.back_btn = back_btn
        self.elements.append(back_btn.button_bg)
        self.elements.append(back_btn.text_entity)

    def update(self, dt):
        """Update settings menu."""
        if not self.active:
            return
        
        self.back_btn.update(dt, self._get_mouse_pos())

    def handle_input(self, key):
        """Handle keyboard input."""
        if not self.active:
            return
        
        if key == 'escape':
            self._on_back()

    def on_mouse_up(self):
        """Handle mouse up."""
        self.back_btn.on_mouse_up()

    def _get_mouse_pos(self):
        """Get current mouse position."""
        from ursina import mouse
        if hasattr(mouse, 'position') and mouse.position is not None:
            return (mouse.position.x, mouse.position.y)
        return None

    def _increase_option(self, option_name):
        """Increase setting value."""
        opt = next((o for o in self.options if o["name"] == option_name), None)
        if opt:
            current_idx = self.settings.get(option_name, opt["default"])
            new_idx = (current_idx + 1) % len(opt["values"])
            self.settings[option_name] = new_idx
            self._update_display()
            print(f"[Settings] {option_name} = {opt['values'][new_idx]}", flush=True)

    def _decrease_option(self, option_name):
        """Decrease setting value."""
        opt = next((o for o in self.options if o["name"] == option_name), None)
        if opt:
            current_idx = self.settings.get(option_name, opt["default"])
            new_idx = (current_idx - 1) % len(opt["values"])
            self.settings[option_name] = new_idx
            self._update_display()
            print(f"[Settings] {option_name} = {opt['values'][new_idx]}", flush=True)

    def _update_display(self):
        """Update displayed values."""
        for i, opt in enumerate(self.options):
            if i < len(self.option_displays):
                value_idx = self.settings.get(opt["name"], opt["default"])
                self.option_displays[i].text = opt["values"][value_idx]

    def _on_back(self):
        """Back button clicked."""
        print("[Settings] Returning to main menu...", flush=True)
        self.change_state(MENU_STATE_MAIN)

    def cleanup(self):
        """Cleanup settings menu."""
        self.back_btn.cleanup()
        super().cleanup()