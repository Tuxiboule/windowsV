from AppKit import (NSPasteboard, NSStringPboardType, NSEvent,
                  NSCommandKeyMask, NSKeyDown, NSApplication)
from Quartz import (CGEventCreateKeyboardEvent, CGEventPost,
                   kCGHIDEventTap, kCGEventFlagMaskCommand,
                   CGEventSetFlags)
import logging
import time
import subprocess

logger = logging.getLogger(__name__)

class ClipboardHistory:
    """
    A class to manage clipboard history with copy and paste functionality.
    
    This class maintains a history of clipboard contents, allows pasting previous items,
    and handles clipboard change monitoring.
    """

    def __init__(self, max_items=10):
        """
        Initialize the clipboard history manager.

        Args:
            max_items: Maximum number of items to keep in history (default: 10).
        """
        self.max_items = max_items
        self.history = []
        self.pasteboard = NSPasteboard.generalPasteboard()
        self.last_change_count = self.pasteboard.changeCount()
        
    def check_and_update(self):
        """
        Check if clipboard has changed and update history accordingly.
        
        Monitors the system clipboard for changes and adds new content to the history,
        removing duplicates and maintaining the maximum history size.

        Raises:
            Exception: If there's an error updating the history.
        """
        try:
            current_count = self.pasteboard.changeCount()
            
            if current_count > self.last_change_count:
                logger.info("Change detected in clipboard")
                
                if content := self.pasteboard.stringForType_(NSStringPboardType):
                    if content in self.history:
                        logger.info(f"Removing existing duplicate: {content[:50]}...")
                        self.history.remove(content)
                    
                    self.history.insert(0, content)
                    logger.info(f"Added to history: {content[:50]}...")
                    
                    if len(self.history) > self.max_items:
                        self.history.pop()
                
                self.last_change_count = current_count
        except Exception as e:
            logger.error(f"Error updating history: {e}")
    
    def get_history(self):
        """
        Get the current clipboard history.

        Returns:
            list: List of clipboard history items, most recent first.
        """
        return self.history
    
    def check_accessibility_permissions(self):
        """
        Check if the application has accessibility permissions.

        Returns:
            bool: True if accessibility permissions are granted, False otherwise.

        Raises:
            Exception: If there's an error checking permissions.
        """
        try:
            test_event = CGEventCreateKeyboardEvent(None, 0, True)
            if test_event is None:
                logger.error("Cannot create events. Check accessibility permissions.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False

    def paste_item(self, item):
        """
        Copy an item to the current clipboard and simulate paste command.

        Args:
            item: String content to paste.

        Returns:
            bool: True if paste was successful, False otherwise.

        Raises:
            Exception: If there's an error during the paste operation.
        """
        try:
            if not self.check_accessibility_permissions():
                logger.error("Missing accessibility permissions. Please enable them in System Preferences > Security & Privacy > Privacy > Accessibility")
                return False

            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(item, NSStringPboardType)
            logger.info(f"Item set to clipboard: {item[:50]}...")
            
            try:
                v_keycode = 9  # V key code
                
                v_down = CGEventCreateKeyboardEvent(None, v_keycode, True)
                CGEventSetFlags(v_down, kCGEventFlagMaskCommand)
                
                v_up = CGEventCreateKeyboardEvent(None, v_keycode, False)
                
                CGEventPost(kCGHIDEventTap, v_down)
                time.sleep(0.1)  # Small delay for stability
                CGEventPost(kCGHIDEventTap, v_up)
                
                logger.info("Cmd+V simulation successful")
                return True
                
            except Exception as e:
                logger.error(f"Error simulating paste: {e}")
                try:
                    subprocess.run(['pbcopy'], input=item.encode('utf-8'))
                    subprocess.run(['pbpaste'])
                    logger.info("Paste completed via pbpaste")
                    return True
                except Exception as e2:
                    logger.error(f"Alternative method failed: {e2}")
                    return False
            
        except Exception as e:
            logger.error(f"Error during paste operation: {e}")
            return False

    def remove_item(self, index):
        """
        Remove an item from the history.

        Args:
            index: Integer index of the item to remove.

        Returns:
            bool: True if item was successfully removed, False otherwise.

        Raises:
            Exception: If there's an error removing the item.
        """
        try:
            if 0 <= index < len(self.history):
                removed_item = self.history.pop(index)
                logger.info(f"Item removed from history: {removed_item[:50]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            return False
