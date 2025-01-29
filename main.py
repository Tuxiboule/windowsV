import logging
from mac_keyboard_listener import MacKeyboardListener
from popup_window import PopupWindow
from mouse_position import get_mouse_position
from AppKit import NSApplication, NSApp
from Foundation import NSObject, NSTimer
from objc import super

# Configure le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ClipboardChecker(NSObject):
    def initWithWindow_(self, window):
        self = super(ClipboardChecker, self).init()
        if self is not None:
            self.window = window
        return self
    
    def checkClipboard_(self, timer):
        """Vérifie régulièrement le presse-papier"""
        try:
            self.window.clipboard_history.check_and_update()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du presse-papier : {e}")

def main():
    try:
        logger.info("Démarrage de l'application...")
        
        # Initialise NSApplication si nécessaire
        if NSApp() is None:
            app = NSApplication.sharedApplication()
        
        # Crée la fenêtre popup
        logger.info("Création de la fenêtre popup...")
        global popup_window
        popup_window = PopupWindow()
        
        # Crée et configure le checker de presse-papier
        checker = ClipboardChecker.new()
        checker.initWithWindow_(popup_window)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0,  # Intervalle en secondes
            checker,  # Target
            'checkClipboard:',  # Selector
            None,  # User info
            True  # Repeats
        )
        
        # Configure le listener de clavier
        keyboard = MacKeyboardListener()
        keyboard.set_callback(lambda: popup_window.show(*get_mouse_position()))
        keyboard.start()
        
        # Lance la boucle principale
        NSApplication.sharedApplication().run()
        
    except Exception as e:
        logger.error(f"Erreur dans la boucle principale : {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        logger.info("Application arrêtée proprement")

if __name__ == "__main__":
    main()
