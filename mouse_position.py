import pyautogui
from Quartz import NSEvent
import logging

logger = logging.getLogger(__name__)

class MousePosition:
    @staticmethod
    def get_current_position():
        """Return the current cursor position as a tuple (x, y)"""
        return pyautogui.position()

def get_mouse_position():
    """Get the current mouse position"""
    try:
        location = NSEvent.mouseLocation()
        logger.debug(f"Mouse position: ({location.x}, {location.y})")
        return location.x, location.y
    except Exception as e:
        logger.error(f"Error getting mouse position: {e}")
        return 0, 0

# For compatibility with old code
class MousePositionCompat:
    @staticmethod
    def get_mouse_position():
        return get_mouse_position()
