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

# Configure logging
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
        """Regularly checks the clipboard"""
        try:
            self.window.clipboard_history.check_and_update()
        except Exception as e:
            logger.error(f"Error while checking clipboard: {e}")

def create_menu():
    # Create menu
    menu = NSMenu.alloc().init()
    
    # Add Quit option
    quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "Quit", "terminate:", "q"
    )
    menu.addItem_(quit_item)
    
    return menu

def main():
    try:
        logger.info("Starting application...")
        
        # Initialize NSApplication if needed
        if NSApp() is None:
            app = NSApplication.sharedApplication()
        
        # Create popup window
        logger.info("Creating popup window...")
        global popup_window
        popup_window = PopupWindow()
        
        # Create and configure clipboard checker
        checker = ClipboardChecker.new()
        checker.initWithWindow_(popup_window)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0,  # Interval in seconds
            checker,  # Target
            'checkClipboard:',  # Selector
            None,  # User info
            True  # Repeats
        )
        
        # Configure keyboard listener
        def show_popup():
            try:
                x, y = get_mouse_position()
                popup_window.show(x, y)
            except Exception as e:
                logger.error(f"Error while showing popup: {e}")
        
        keyboard = MacKeyboardListener(show_popup)
        keyboard.start()
        
        # Create menu bar icon
        statusbar = NSStatusBar.systemStatusBar()
        statusitem = statusbar.statusItemWithLength_(-1)  # -1 for variable length
        statusitem.setMenu_(create_menu())
        statusitem.setTitle_("📋")  # Use clipboard icon
        
        # Start main loop
        NSApplication.sharedApplication().run()
        
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        logger.info("Application properly stopped")

if __name__ == "__main__":
    main()
