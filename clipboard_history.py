from AppKit import (NSPasteboard, NSStringPboardType, NSEvent,
                  NSCommandKeyMask, NSKeyDown, NSApplication,
                  NSPasteboardTypePNG, NSPasteboardTypeTIFF,
                  NSPasteboardTypeRTF, NSPasteboardTypeFileURL,
                  NSImage, NSPDFPboardType, NSData)
from Quartz import (CGEventCreateKeyboardEvent, CGEventPost,
                   kCGHIDEventTap, kCGEventFlagMaskCommand,
                   CGEventSetFlags)
import logging
import time
import subprocess
import os
from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ClipboardItem:
    """
    Represents an item in the clipboard history.

    Args:
        content: The actual content of the clipboard item.
        content_type: The type of content (e.g., 'text', 'image', 'file', etc.).
        timestamp: When the item was copied.
        preview: Optional preview text or thumbnail path for the item.
    """
    content: Any
    content_type: str
    timestamp: datetime
    preview: Optional[str] = None

class ClipboardHistory:
    """
    A class to manage clipboard history with support for multiple content types.
    
    This class maintains a history of clipboard contents including text, images,
    files, and other media types. It handles copying and pasting of these items.
    """

    SUPPORTED_TYPES = {
        NSStringPboardType: 'text',
        NSPasteboardTypePNG: 'image',
        NSPasteboardTypeTIFF: 'image',
        NSPasteboardTypeRTF: 'rtf',
        NSPasteboardTypeFileURL: 'file',
        NSPDFPboardType: 'pdf'
    }

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
        
        # Create cache directory for media files if it doesn't exist
        self.cache_dir = os.path.expanduser('~/.clipboard_cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _save_media_to_cache(self, data, extension):
        """
        Save media data to cache directory.

        Args:
            data: Binary data of the media file.
            extension: File extension to use (e.g., 'png', 'pdf').

        Returns:
            str: Path to the cached file.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'clip_{timestamp}.{extension}'
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(data)
        return filepath

    def _get_clipboard_content(self):
        """
        Get content from clipboard with type information.

        Returns:
            ClipboardItem: A ClipboardItem instance if content is found, None otherwise.
        """
        for pb_type, our_type in self.SUPPORTED_TYPES.items():
            if data := self.pasteboard.dataForType_(pb_type):
                if our_type == 'text':
                    content = self.pasteboard.stringForType_(pb_type)
                    return ClipboardItem(
                        content=content,
                        content_type='text',
                        timestamp=datetime.now(),
                        preview=content[:100] + "..." if len(content) > 100 else content
                    )
                elif our_type == 'image':
                    filepath = self._save_media_to_cache(data.bytes(), 'png')
                    return ClipboardItem(
                        content=data.bytes(),  # Store the actual image data
                        content_type='image',
                        timestamp=datetime.now(),
                        preview=filepath  # Use filepath only for preview
                    )
                elif our_type == 'file':
                    file_url = self.pasteboard.stringForType_(pb_type)
                    return ClipboardItem(
                        content=file_url,
                        content_type='file',
                        timestamp=datetime.now(),
                        preview=os.path.basename(file_url)
                    )
                elif our_type in ['pdf', 'rtf']:
                    binary_data = data.bytes()
                    filepath = self._save_media_to_cache(binary_data, our_type)
                    return ClipboardItem(
                        content=binary_data,  # Store the actual binary data
                        content_type=our_type,
                        timestamp=datetime.now(),
                        preview=filepath  # Use filepath only for preview
                    )
        return None

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
                
                if item := self._get_clipboard_content():
                    # Remove duplicate if exists (compare content for binary data)
                    if item.content_type in ['image', 'pdf', 'rtf']:
                        self.history = [h for h in self.history 
                                      if h.content_type != item.content_type or 
                                      h.content != item.content]
                    else:
                        self.history = [h for h in self.history if h.content != item.content]
                    
                    self.history.insert(0, item)
                    logger.info(f"Added to history: {item.content_type} content")
                    
                    if len(self.history) > self.max_items:
                        old_item = self.history.pop()
                        if old_item.content_type in ['image', 'pdf', 'rtf']:
                            try:
                                os.remove(old_item.preview)  # Remove preview file
                            except Exception as e:
                                logger.error(f"Error removing cached file: {e}")
                
                self.last_change_count = current_count
        except Exception as e:
            logger.error(f"Error updating history: {e}")

    def paste_item(self, item):
        """
        Copy an item to the current clipboard and simulate paste command.

        Args:
            item: ClipboardItem to paste.

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

            if item.content_type == 'text':
                self.pasteboard.setString_forType_(item.content, NSStringPboardType)
            elif item.content_type == 'image':
                # Create NSData from bytes
                ns_data = NSData.dataWithBytes_length_(item.content, len(item.content))
                self.pasteboard.setData_forType_(ns_data, NSPasteboardTypePNG)
            elif item.content_type == 'file':
                self.pasteboard.setString_forType_(item.content, NSPasteboardTypeFileURL)
            elif item.content_type in ['pdf', 'rtf']:
                # Create NSData from bytes
                ns_data = NSData.dataWithBytes_length_(item.content, len(item.content))
                pb_type = NSPDFPboardType if item.content_type == 'pdf' else NSPasteboardTypeRTF
                self.pasteboard.setData_forType_(ns_data, pb_type)

            logger.info(f"Item set to clipboard: {item.content_type}")
            
            try:
                v_keycode = 9
                v_down = CGEventCreateKeyboardEvent(None, v_keycode, True)
                CGEventSetFlags(v_down, kCGEventFlagMaskCommand)
                v_up = CGEventCreateKeyboardEvent(None, v_keycode, False)
                
                CGEventPost(kCGHIDEventTap, v_down)
                time.sleep(0.1)
                CGEventPost(kCGHIDEventTap, v_up)
                
                logger.info("Cmd+V simulation successful")
                return True
                
            except Exception as e:
                logger.error(f"Error simulating paste: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error during paste operation: {e}")
            return False

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
                logger.info(f"Item removed from history: {removed_item.content_type} content")
                
                # Clean up preview file for media types
                if removed_item.content_type in ['image', 'pdf', 'rtf']:
                    try:
                        os.remove(removed_item.preview)
                    except Exception as e:
                        logger.error(f"Error removing cached file: {e}")
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            return False
