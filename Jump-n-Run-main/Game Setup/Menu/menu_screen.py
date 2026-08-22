"""
Base menu screen - abstract base for menu implementations.
"""
from abc import ABC, abstractmethod
from ursina import destroy


class MenuScreen(ABC):
    """Abstract base class for menu screens."""
    
    def __init__(self, on_state_change=None):
        self.on_state_change = on_state_change
        self.active = True
        self.elements = []  # Track all UI elements for cleanup

    @abstractmethod
    def update(self, dt):
        """Update screen logic."""
        pass

    @abstractmethod
    def handle_input(self, key):
        """Handle keyboard/controller input."""
        pass

    def change_state(self, new_state):
        """Request state change (to main menu controller)."""
        if self.on_state_change:
            self.on_state_change(new_state)

    def cleanup(self):
        """Destroy all UI elements."""
        for elem in self.elements:
            try:
                destroy(elem)
            except Exception:
                pass
        self.elements.clear()

    def show(self):
        """Show this screen."""
        self.active = True

    def hide(self):
        """Hide this screen."""
        self.active = False