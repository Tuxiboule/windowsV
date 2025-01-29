from AppKit import (NSPasteboard, NSStringPboardType, NSEvent,
                  NSCommandKeyMask, NSKeyDown, NSApplication,
                  NSPasteboardTypePNG, NSPasteboardTypeTIFF,
                  NSPasteboardTypeRTF, NSPasteboardTypeFileURL,
                  NSImage, NSPDFPboardType, NSData, NSFilenamesPboardType, NSURL)
from Quartz import (CGEventCreateKeyboardEvent, CGEventPost,
                   kCGHIDEventTap, kCGEventFlagMaskCommand,
                   CGEventSetFlags)
import logging
import time
import subprocess
import os
from dataclasses import dataclass
from typing import Optional, Any, Union
from datetime import datetime
import shutil
import tempfile
from Foundation import NSArray

logger = logging.getLogger(__name__)

class ClipboardItem:
    def __init__(self, content, content_type, raw_data=None, timestamp=None, preview=None):
        """
        Initialize a clipboard item.
        
        Args:
            content: The content of the clipboard item (text, file path, etc.)
            content_type: The type of content (NSStringPboardType, etc.)
            raw_data: Optional NSData object for binary content
            timestamp: When the item was created
            preview: Preview text or path for display
        """
        self.content = content
        self.content_type = content_type
        self.raw_data = raw_data
        self.timestamp = timestamp or datetime.now()
        self.preview = preview

class ClipboardHistory:
    """
    A class to manage clipboard history with support for multiple content types.
    
    This class maintains a history of clipboard contents including text, images,
    files, and other media types. It handles copying and pasting of these items.
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
        
        # Create cache directory for media files if it doesn't exist
        self.cache_dir = os.path.join(tempfile.gettempdir(), "clipboard_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _save_media_to_cache(self, data_bytes, ext):
        """
        Save binary data to a temporary file.
        
        Args:
            data_bytes: Binary data to save
            ext: File extension without dot
            
        Returns:
            str: Path to saved file
        """
        try:
            filename = f"clip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            filepath = os.path.join(self.cache_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data_bytes)
                
            return filepath
        except Exception as e:
            logger.error(f"Error saving media to cache: {e}")
            return None

    def _get_clipboard_content(self):
        """
        Get content from clipboard with type information.
        """
        pb = self.pasteboard
        types = pb.types()
        
        if not types:
            return None
            
        # Check for files first (prioritize this over text)
        if NSFilenamesPboardType in types:
            filenames = pb.propertyListForType_(NSFilenamesPboardType)
            if filenames and len(filenames) > 0:
                file_path = filenames[0]  # Get first file
                return ClipboardItem(
                    content=file_path,  # Store the actual file path
                    content_type=NSPasteboardTypeFileURL,
                    raw_data=None,  # We don't need raw data for files
                    timestamp=datetime.now(),
                    preview=os.path.basename(file_path)
                )
        
        # Then check for text content
        if "public.utf8-plain-text" in types:
            content = pb.stringForType_("public.utf8-plain-text")
            if content and not content.startswith('file://'):  # Ignore if it's a file URL
                return ClipboardItem(
                    content=content,
                    content_type=NSStringPboardType,
                    raw_data=None,
                    timestamp=datetime.now(),
                    preview=content[:100] + "..." if len(content) > 100 else content
                )
        
        # Handle images and other binary content
        for content_type in types:
            if content_type in (NSPasteboardTypePNG, NSPasteboardTypeTIFF):
                data = pb.dataForType_(content_type)
                if not data:
                    continue
                    
                filepath = self._save_media_to_cache(data.bytes().tobytes(), 'png')
                if filepath:
                    return ClipboardItem(
                        content=filepath,
                        content_type=content_type,
                        raw_data=data,
                        timestamp=datetime.now(),
                        preview=filepath
                    )
                    
            elif content_type in (NSPDFPboardType, NSPasteboardTypeRTF):
                data = pb.dataForType_(content_type)
                if not data:
                    continue
                    
                filepath = self._save_media_to_cache(data.bytes().tobytes(), 
                    'pdf' if content_type == NSPDFPboardType else 'rtf')
                if filepath:
                    return ClipboardItem(
                        content=filepath,
                        content_type=content_type,
                        raw_data=data,
                        timestamp=datetime.now(),
                        preview=filepath
                    )
        
        return None

    def paste_item(self, item):
        """
        Copy an item to the current clipboard and simulate paste command.
        """
        try:
            if not self.check_accessibility_permissions():
                logger.error("Missing accessibility permissions")
                return False

            self.pasteboard.clearContents()

            if item.content_type == NSStringPboardType:
                # For text content
                self.pasteboard.setString_forType_(item.content, "public.utf8-plain-text")
                logger.info("Set text content to clipboard")
                
            elif item.content_type == NSPasteboardTypeFileURL:
                # For files, set both the filename list and URL
                try:
                    file_path = item.content  # We stored the actual path
                    if os.path.exists(file_path):
                        # Set the filenames list
                        filenames = NSArray.arrayWithObject_(file_path)
                        success = self.pasteboard.setPropertyList_forType_(filenames, NSFilenamesPboardType)
                        if not success:
                            logger.error("Failed to set filenames")
                            return False
                            
                        # Set the file URL
                        file_url = NSURL.fileURLWithPath_(file_path).absoluteString()
                        success = self.pasteboard.setString_forType_(file_url, NSPasteboardTypeFileURL)
                        if not success:
                            logger.error("Failed to set file URL")
                            return False
                            
                        logger.info(f"Set file to clipboard: {file_path}")
                        
                    else:
                        logger.error(f"File does not exist: {file_path}")
                        return False
                        
                except Exception as e:
                    logger.error(f"Error setting file to clipboard: {e}")
                    return False
                
            elif item.raw_data is not None:
                # For binary content (images, PDFs, RTF)
                success = self.pasteboard.setData_forType_(item.raw_data, item.content_type)
                if not success:
                    logger.error(f"Failed to set {item.content_type} data")
                    return False
                    
                # For images, also set both PNG and TIFF types
                if item.content_type in (NSPasteboardTypePNG, NSPasteboardTypeTIFF):
                    self.pasteboard.setData_forType_(item.raw_data, NSPasteboardTypePNG)
                    self.pasteboard.setData_forType_(item.raw_data, NSPasteboardTypeTIFF)
                
                logger.info(f"Set binary content to clipboard: {item.content_type}")

            # Simulate Cmd+V
            from Quartz import (CGEventCreateKeyboardEvent,
                              CGEventPost,
                              kCGHIDEventTap,
                              kCGEventFlagMaskCommand)
            import time

            try:
                v_keycode = 9  # 'v' key
                v_down = CGEventCreateKeyboardEvent(None, v_keycode, True)
                CGEventSetFlags(v_down, kCGEventFlagMaskCommand)
                v_up = CGEventCreateKeyboardEvent(None, v_keycode, False)
                
                CGEventPost(kCGHIDEventTap, v_down)
                time.sleep(0.1)
                CGEventPost(kCGHIDEventTap, v_up)
                
                logger.info("Paste command simulated")
                return True
                
            except Exception as e:
                logger.error(f"Error simulating paste: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error during paste operation: {e}")
            return False

    def check_and_update(self):
        """
        Check if clipboard has changed and update history accordingly.
        """
        try:
            current_count = self.pasteboard.changeCount()
            
            if current_count > self.last_change_count:
                logger.info("Change detected in clipboard")
                
                if item := self._get_clipboard_content():
                    # Remove duplicate if exists
                    if item.raw_data is not None:
                        # For binary content, compare raw data
                        self.history = [h for h in self.history 
                                      if h.content_type != item.content_type or 
                                      h.raw_data.bytes().tobytes() != item.raw_data.bytes().tobytes()]
                    else:
                        # For text content, compare the actual content
                        self.history = [h for h in self.history if h.content != item.content]
                    
                    self.history.insert(0, item)
                    logger.info(f"Added to history: {item.content_type}")
                    
                    # Clean up old items
                    while len(self.history) > self.max_items:
                        old_item = self.history.pop()
                        if old_item.raw_data is not None and old_item.preview:
                            try:
                                if os.path.exists(old_item.preview):
                                    os.remove(old_item.preview)
                            except Exception as e:
                                logger.error(f"Error removing cached file: {e}")
                
                self.last_change_count = current_count
        except Exception as e:
            logger.error(f"Error updating history: {e}")

    def get_history(self):
        """
        Get the current clipboard history.

        Returns:
            list: List of ClipboardItem objects
        """
        return self.history
    
    def check_accessibility_permissions(self):
        """
        Check if the app has the required accessibility permissions.

        Returns:
            bool: True if permissions are granted, False otherwise
        """
        from AppKit import NSDictionary
        from ApplicationServices import AXIsProcessTrusted
        
        return bool(AXIsProcessTrusted())

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
                if removed_item.raw_data is not None:
                    try:
                        os.remove(removed_item.preview)
                    except Exception as e:
                        logger.error(f"Error removing cached file: {e}")
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            return False

    def clear_history(self):
        """
        Clear the clipboard history and remove cached files.
        """
        try:
            # Remove all cached files
            for item in self.history:
                if item.preview and os.path.exists(item.preview):
                    try:
                        os.remove(item.preview)
                    except Exception as e:
                        logger.error(f"Error removing cached file: {e}")
            
            # Clear history list
            self.history.clear()
            logger.info("Clipboard history cleared")
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")

    def __del__(self):
        """
        Clean up cached files when the object is destroyed.
        """
        self.clear_history()
        try:
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
        except Exception as e:
            logger.error(f"Error cleaning up cache directory: {e}")
