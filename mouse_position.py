import pyautogui

class MousePosition:
    @staticmethod
    def get_current_position():
        """Retourne la position actuelle du curseur sous forme de tuple (x, y)"""
        return pyautogui.position()
