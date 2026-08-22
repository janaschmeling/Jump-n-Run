"""
Menu button - interactive UI element.
"""
from ursina import Entity, color, Text, Vec3, camera, mouse, lerp
from menu_config import (BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_CORNER_RADIUS,
                         BUTTON_HOVER_SCALE, BUTTON_PRESS_SCALE,
                         COLOR_BLUE, COLOR_DARK_GRAY, COLOR_HIGHLIGHT, COLOR_WHITE,
                         BUTTON_FONT_SIZE)


class MenuButton:
    """An interactive menu button with hover and press states."""
    
    def __init__(self, text, position, on_click=None, width=BUTTON_WIDTH, height=BUTTON_HEIGHT):
        self.text_str = text
        self.position = position
        self.on_click = on_click
        self.width = width
        self.height = height
        
        # State
        self.hovered = False
        self.pressed = False
        self.active = True
        
        # Create button background (rounded rectangle effect with cube)
        self.button_bg = Entity(
            model='quad',
            color=COLOR_BLUE,
            scale=(width, height, 1),
            position=Vec3(position[0], position[1], 0.1),
            collider='box'
        )
        
        # Create button text
        self.text_entity = Text(
            text=text,
            position=Vec3(position[0], position[1], 0.05),
            font_size=BUTTON_FONT_SIZE,
            color=COLOR_WHITE,
            scale=1.0
        )
        
        # Target scale for smooth transitions
        self.target_scale = 1.0
        self.current_scale = 1.0

    def update(self, dt, mouse_pos):
        """Update button state (hover, press)."""
        if not self.active:
            return
        
        # Check if mouse is over button
        self.hovered = self._is_mouse_over(mouse_pos)
        
        # Set target scale based on state
        if self.pressed:
            self.target_scale = BUTTON_PRESS_SCALE
        elif self.hovered:
            self.target_scale = BUTTON_HOVER_SCALE
        else:
            self.target_scale = 1.0
        
        # Smooth scale transition
        self.current_scale = lerp(self.current_scale, self.target_scale, 15 * dt)
        self.button_bg.scale = (self.width * self.current_scale, 
                               self.height * self.current_scale, 1)
        
        # Update button color based on state
        if self.pressed:
            self.button_bg.color = COLOR_HIGHLIGHT
        elif self.hovered:
            self.button_bg.color = COLOR_HIGHLIGHT
        else:
            self.button_bg.color = COLOR_BLUE

    def on_mouse_down(self):
        """Handle mouse down event."""
        if self.hovered and self.active:
            self.pressed = True
            return True
        return False

    def on_mouse_up(self):
        """Handle mouse up event."""
        if self.pressed and self.hovered and self.active:
            self.pressed = False
            if self.on_click:
                self.on_click()
            return True
        self.pressed = False
        return False

    def _is_mouse_over(self, mouse_pos):
        """Check if mouse is over this button."""
        if mouse_pos is None:
            return False
        x, y = mouse_pos
        button_x, button_y = self.position
        half_w = (self.width * self.current_scale) / 2
        half_h = (self.height * self.current_scale) / 2
        
        return (button_x - half_w <= x <= button_x + half_w and
                button_y - half_h <= y <= button_y + half_h)

    def set_active(self, active):
        """Enable/disable button."""
        self.active = active
        if not active:
            self.button_bg.color = COLOR_DARK_GRAY
        else:
            self.button_bg.color = COLOR_BLUE

    def cleanup(self):
        """Destroy button entities."""
        try:
            from ursina import destroy
            destroy(self.button_bg)
            destroy(self.text_entity)
        except Exception:
            pass