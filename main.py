import logging
from mac_keyboard_listener import MacKeyboardListener
from popup_window import PopupWindow
from mouse_position import get_mouse_position
from AppKit import (
    NSApplication, 
    NSApp, 
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSImage
)
from Foundation import NSObject, NSTimer
from objc import super

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ClipboardChecker(NSObject):
    """
    A class that periodically checks the clipboard for changes.
    
    This class extends NSObject to work with the macOS timer system and
    monitors clipboard changes at regular intervals.
    """

    def initWithWindow_(self, window):
        """
        Initialize the clipboard checker with a window reference.

        Args:
            window: PopupWindow instance to update when clipboard changes.

        Returns:
            The initialized ClipboardChecker instance.
        """
        self = super(ClipboardChecker, self).init()
        if self is not None:
            self.window = window
        return self
    
    def checkClipboard_(self, timer):
        """
        Check clipboard contents and update history if changed.
        
        This method is called periodically by NSTimer to monitor clipboard changes.

        Args:
            timer: NSTimer instance that triggered this check.

        Raises:
            Exception: If there's an error checking the clipboard.
        """
        try:
            self.window.clipboard_history.check_and_update()
        except Exception as e:
            logger.error(f"Error while checking clipboard: {e}")

def create_menu():
    """
    Create the status bar menu for the application.

    Returns:
        NSMenu: The configured menu with quit option.
    """
    menu = NSMenu.alloc().init()
    
    quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "Quit", "terminate:", "q"
    )
    menu.addItem_(quit_item)
    
    return menu

def main():
    """
    Main entry point of the application.
    
    Sets up the clipboard monitoring system, keyboard listener, and status bar icon.
    Initializes all necessary components and starts the main application loop.

    Raises:
        Exception: If there's an error during application startup or execution.
    """
    try:
        logger.info("Starting application...")
        
        if NSApp() is None:
            app = NSApplication.sharedApplication()
        
        logger.info("Creating popup window...")
        global popup_window
        popup_window = PopupWindow()
        
        checker = ClipboardChecker.new()
        checker.initWithWindow_(popup_window)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0,
            checker,
            'checkClipboard:',
            None,
            True
        )
        
        def show_popup():
            try:
                x, y = get_mouse_position()
                popup_window.show(x, y)
            except Exception as e:
                logger.error(f"Error while showing popup: {e}")
        
        keyboard = MacKeyboardListener(show_popup)
        keyboard.start()
        
        statusbar = NSStatusBar.systemStatusBar()
        statusitem = statusbar.statusItemWithLength_(-1)
        statusitem.setMenu_(create_menu())
        statusitem.setTitle_("📋")
        
        NSApplication.sharedApplication().run()
        
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        logger.info("Application properly stopped")

if __name__ == "__main__":
    main()
