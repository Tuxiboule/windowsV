import pyautogui
from Quartz import NSEvent
import logging

logger = logging.getLogger(__name__)

class MousePosition:
    """
    A utility class for getting the current mouse cursor position using pyautogui.
    """

    @staticmethod
    def get_current_position():
        """
        Get the current cursor position using pyautogui.

        Returns:
            tuple: A tuple containing (x, y) coordinates of the mouse cursor.
        """
        return pyautogui.position()

def get_mouse_position():
    """
    Get the current mouse position using NSEvent.

    Returns:
        tuple: A tuple containing (x, y) coordinates of the mouse cursor.
               Returns (0, 0) if there's an error getting the position.

    Raises:
        Exception: If there's an error getting the mouse position.
    """
    try:
        location = NSEvent.mouseLocation()
        #logger.debug(f"Mouse position: ({location.x}, {location.y})")
        return location.x, location.y
    except Exception as e:
        logger.error(f"Error getting mouse position: {e}")
        return 0, 0

class MousePositionCompat:
    """
    Compatibility class that provides the same interface as the old code.
    Uses NSEvent to get mouse position.
    """

    @staticmethod
    def get_mouse_position():
        """
        Get the current mouse position using NSEvent.

        Returns:
            tuple: A tuple containing (x, y) coordinates of the mouse cursor.
        """
        return get_mouse_position()
