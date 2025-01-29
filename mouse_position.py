import pyautogui
from Quartz import NSEvent
import logging

logger = logging.getLogger(__name__)

class MousePosition:
    @staticmethod
    def get_current_position():
        """Retourne la position actuelle du curseur sous forme de tuple (x, y)"""
        return pyautogui.position()

def get_mouse_position():
    """Retourne la position actuelle de la souris"""
    try:
        location = NSEvent.mouseLocation()
        logger.debug(f"Position de la souris : ({location.x}, {location.y})")
        return location.x, location.y
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la position de la souris : {e}")
        return 0, 0

# Pour la compatibilité avec l'ancien code
class MousePositionCompat:
    @staticmethod
    def get_mouse_position():
        return get_mouse_position()
