from AppKit import (NSWindow, NSPanel, NSScreen, NSScrollView, NSTableView,
                  NSTableColumn, NSColor, NSRect, NSPoint, NSSize,
                  NSBackingStoreBuffered, NSWindowStyleMaskBorderless,
                  NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
                  NSWindowStyleMaskResizable, NSWindowStyleMaskMiniaturizable,
                  NSEventTypeKeyDown, NSEventTypeLeftMouseDown, NSEventMaskKeyDown,
                  NSEventMaskLeftMouseDown, NSPointInRect, NSEvent,
                  NSBezelBorder, NSFont, NSMakeRange, NSForegroundColorAttributeName,
                  NSAttributedString, NSCursor, NSTrackingArea, NSTrackingMouseEnteredAndExited,
                  NSTrackingActiveAlways, NSTrackingMouseMoved, NSBezierPath,
                  NSFontAttributeName, NSView, NSTextField, NSButton, NSTextView,
                  NSApp, NSFloatingWindowLevel, NSMakeRect, NSWindowStyleMaskNonactivatingPanel,
                  NSBezelStyleRegularSquare, NSMomentaryPushInButton, NSApplication)
from Quartz import CGColorCreateGenericRGB
from objc import super
import logging
from clipboard_history import ClipboardHistory

logger = logging.getLogger(__name__)

class HistoryItemView(NSView):
    """
    A custom NSView subclass that displays a single clipboard history item with a delete button.
    
    This view handles mouse interactions, hover effects, and click events for both
    the main text area and the delete button. It supports different content types
    including text, images, and files.
    """

    def initWithFrame_text_index_callback_deleteCallback_(self, frame, item, index, callback, delete_callback):
        """
        Initialize the history item view with the given parameters.

        Args:
            frame: NSRect defining the view's frame.
            item: ClipboardItem instance containing the content to display.
            index: Integer index of this item in the history.
            callback: Function to call when the item is clicked.
            delete_callback: Function to call when the delete button is clicked.

        Returns:
            The initialized HistoryItemView instance.
        """
        self = super(HistoryItemView, self).initWithFrame_(frame)
        if self is not None:
            self.item = item
            self.index = index
            self.callback = callback
            self.delete_callback = delete_callback
            self.hovered = False
            self.delete_button_hovered = False
            
            tracking_options = (NSTrackingMouseEnteredAndExited |
                              NSTrackingActiveAlways |
                              NSTrackingMouseMoved)
            tracking_area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
                self.bounds(),
                tracking_options,
                self,
                None
            )
            self.addTrackingArea_(tracking_area)
            
            self.setWantsLayer_(True)
            self.layer().setBackgroundColor_(CGColorCreateGenericRGB(1, 1, 1, 0))
            
            button_size = 20
            button_frame = NSMakeRect(
                frame.size.width - button_size - 10,
                (frame.size.height - button_size) / 2,
                button_size,
                button_size
            )
            self.delete_button = NSButton.alloc().initWithFrame_(button_frame)
            self.delete_button.setTitle_("✕")
            self.delete_button.setBezelStyle_(NSBezelStyleRegularSquare)
            self.delete_button.setButtonType_(NSMomentaryPushInButton)
            self.delete_button.setBordered_(False)
            self.delete_button.setTarget_(self)
            self.delete_button.setAction_("deleteClicked:")
            self.delete_button.setFont_(NSFont.systemFontOfSize_(14))
            
            attrs = {
                NSForegroundColorAttributeName: NSColor.secondaryLabelColor()
            }
            title_attrs = NSAttributedString.alloc().initWithString_attributes_("✕", attrs)
            self.delete_button.setAttributedTitle_(title_attrs)
            
            if self.item.content_type == 'image':
                self.image_view = NSImageView.alloc().initWithFrame_(
                    NSMakeRect(10, 5, frame.size.height - 10, frame.size.height - 10)
                )
                image = NSImage.alloc().initWithContentsOfFile_(self.item.content)
                if image:
                    self.image_view.setImage_(image)
                    self.addSubview_(self.image_view)
            
            self.addSubview_(self.delete_button)
            
        return self
    
    def deleteClicked_(self, sender):
        """
        Handle delete button click event.

        Args:
            sender: The NSButton that triggered the event.
        """
        self.delete_callback(self.index)
    
    def mouseEntered_(self, event):
        """
        Handle mouse enter event by updating hover state and cursor.

        Args:
            event: The NSEvent representing the mouse enter event.
        """
        self.hovered = True
        self.setNeedsDisplay_(True)
        NSCursor.pointingHandCursor().set()
    
    def mouseExited_(self, event):
        """
        Handle mouse exit event by updating hover state and cursor.

        Args:
            event: The NSEvent representing the mouse exit event.
        """
        self.hovered = False
        self.setNeedsDisplay_(True)
        NSCursor.arrowCursor().set()
    
    def mouseDown_(self, event):
        """
        Handle mouse click event by triggering the appropriate callback.

        Args:
            event: The NSEvent representing the mouse click event.
        """
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        
        if not NSPointInRect(point, self.delete_button.frame()):
            self.callback(self.index)
    
    def drawRect_(self, rect):
        """
        Draw the view's content including background and text.

        Args:
            rect: The NSRect defining the area to be drawn.
        """
        if self.hovered:
            NSColor.selectedTextBackgroundColor().setFill()
        else:
            NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9).setFill()
        NSBezierPath.fillRect_(self.bounds())
        
        if self.hovered:
            text_color = NSColor.selectedTextColor()
        else:
            text_color = NSColor.textColor()
        
        attrs = {
            NSForegroundColorAttributeName: text_color,
            NSFontAttributeName: NSFont.systemFontOfSize_(13)
        }
        
        # Display appropriate preview based on content type
        if self.item.content_type == 'text':
            display_text = self.item.content
            if len(display_text) > 100:
                display_text = display_text[:97] + "..."
        elif self.item.content_type == 'image':
            display_text = "📷 Image"
        elif self.item.content_type == 'file':
            display_text = f"📄 {self.item.preview}"
        elif self.item.content_type == 'pdf':
            display_text = "📑 PDF Document"
        elif self.item.content_type == 'rtf':
            display_text = "📝 Rich Text Document"
        else:
            display_text = f"Unknown type: {self.item.content_type}"
        
        text = NSAttributedString.alloc().initWithString_attributes_(
            display_text, attrs
        )
        
        # Position text to the right of the image if present
        if self.item.content_type == 'image':
            x_offset = self.bounds().size.height
        else:
            x_offset = 10
            
        text_height = text.size().height
        y_pos = (self.bounds().size.height - text_height) / 2
        text.drawAtPoint_(NSPoint(x_offset, y_pos))

class PopupWindow:
    """
    A floating window that displays clipboard history items.
    
    This class manages a transparent, borderless window that shows clipboard history
    items and handles keyboard and mouse events for interaction with the history items.
    """

    def __init__(self):
        """
        Initialize the popup window with a transparent background and clipboard history.
        
        Sets up the window appearance, scroll view, content view, and event monitors.
        The window is initially hidden.
        """
        logger.info("Initializing PopupWindow")
        
        self.clipboard_history = ClipboardHistory(max_items=50)
        
        if NSApp() is None:
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(1)  
        
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 300),  
            NSWindowStyleMaskBorderless | NSWindowStyleMaskTitled | NSWindowStyleMaskNonactivatingPanel,  
            NSBackingStoreBuffered,
            False
        )
        
        background_color = NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9)  
        self.window.setBackgroundColor_(background_color)
        self.window.setOpaque_(False)  
        self.window.setHasShadow_(True)  
        self.window.setLevel_(NSFloatingWindowLevel)  
        self.window.setAcceptsMouseMovedEvents_(True)  
        self.window.setIgnoresMouseEvents_(False)  
        self.window.setCanHide_(True)  
        self.window.setHidesOnDeactivate_(False)  
        self.window.setBecomesKeyOnlyIfNeeded_(True)  
        
        scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 400, 300)
        )
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setAutohidesScrollers_(True)
        scroll_view.setBorderType_(NSBezelBorder)
        scroll_view.setDrawsBackground_(False)  
        
        self.content_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 380, 300)
        )
        self.content_view.setWantsLayer_(True)
        
        scroll_view.setDocumentView_(self.content_view)
        
        self.window.setContentView_(scroll_view)
        
        self.key_monitor = None
        self.click_monitor = None
        
        self.window.orderOut_(None)
        logger.info("PopupWindow successfully initialized")

    def _handle_key_event(self, event):
        """
        Handle keyboard events for the window.

        Args:
            event: NSEvent representing the keyboard event.

        Returns:
            The event object if not handled, None if handled.

        Raises:
            Exception: If there's an error handling the keyboard event.
        """
        try:
            logger.info(f"Keyboard event received - type: {event.type()}, keyCode: {event.keyCode()}")
            if event.type() == NSEventTypeKeyDown:
                if event.keyCode() == 53:
                    logger.info("Esc key detected, closing window")
                    self.hide()
                    return None
            return event
        except Exception as e:
            logger.error(f"Error handling keyboard event: {e}")
            return event

    def _handle_click_event(self, event):
        """
        Handle mouse click events outside the window.

        Args:
            event: NSEvent representing the mouse click event.

        Returns:
            The event object if not handled, None if handled.

        Raises:
            Exception: If there's an error handling the click event.
        """
        try:
            click_location = NSEvent.mouseLocation()
            window_frame = self.window.frame()
            
            screen_frame = NSScreen.mainScreen().frame()
            adjusted_y = screen_frame.size.height - click_location.y
            
            in_window = (
                window_frame.origin.x <= click_location.x <= window_frame.origin.x + window_frame.size.width and
                adjusted_y - window_frame.size.height <= click_location.y <= adjusted_y
            )
            
            if not in_window:
                logger.info("Click detected outside window")
                self.hide()
                return None
            
            return event
            
        except Exception as e:
            logger.error(f"Error handling click event: {e}")
            return event

    def _handle_item_click(self, index):
        """
        Handle clicks on clipboard history items.

        Args:
            index: Integer index of the clicked history item.

        Raises:
            Exception: If there's an error handling the item click.
        """
        try:
            history = self.clipboard_history.get_history()
            if 0 <= index < len(history):
                item = history[index]
                if self.clipboard_history.paste_item(item):
                    logger.info(f"Item {index} pasted successfully")
                    self.hide()
        except Exception as e:
            logger.error(f"Error handling item click: {e}")

    def _handle_item_delete(self, index):
        """
        Handle deletion of clipboard history items.

        Args:
            index: Integer index of the history item to delete.

        Raises:
            Exception: If there's an error handling the item deletion.
        """
        try:
            if self.clipboard_history.remove_item(index):
                logger.info(f"Item {index} deleted successfully")
                self._update_history_view()
            else:
                logger.error(f"Failed to delete item {index}")
        except Exception as e:
            logger.error(f"Error handling item deletion: {e}")

    def _update_history_view(self):
        """
        Update the window's content view with current clipboard history items.
        
        Creates and positions HistoryItemView instances for each history item.

        Raises:
            Exception: If there's an error updating the history view.
        """
        try:
            for subview in self.content_view.subviews():
                subview.removeFromSuperview()
            
            history = self.clipboard_history.get_history()
            if not history:
                logger.info("History is empty")
                return
                
            item_height = 30
            total_height = max(len(history) * item_height, self.content_view.frame().size.height)
            
            frame = self.content_view.frame()
            new_frame = NSMakeRect(
                frame.origin.x,
                frame.origin.y,
                frame.size.width,
                total_height
            )
            self.content_view.setFrame_(new_frame)
            
            for i, item in enumerate(history):
                frame = NSMakeRect(0, total_height - ((i + 1) * item_height), 380, item_height)
                item_view = HistoryItemView.alloc().initWithFrame_text_index_callback_deleteCallback_(
                    frame, item, i, self._handle_item_click, self._handle_item_delete
                )
                self.content_view.addSubview_(item_view)
                
            logger.info(f"View updated with {len(history)} items")
            
        except Exception as e:
            logger.error(f"Error updating history view: {e}")

    def show(self, x=0, y=0):
        """
        Show the window at specified coordinates.

        Args:
            x: Integer x-coordinate for window position (default: 0).
            y: Integer y-coordinate for window position (default: 0).

        Raises:
            Exception: If there's an error showing the window.
        """
        try:
            logger.info(f"Showing window at coordinates ({x}, {y})")
            
            self.clipboard_history.check_and_update()
            
            self._update_history_view()
            
            screen = NSScreen.mainScreen()
            if screen is None:
                logger.error("Failed to find main screen")
                return
            
            screen_frame = screen.frame()
            adjusted_y = screen_frame.size.height - y
            
            self.window.setFrameOrigin_((x, adjusted_y - self.window.frame().size.height))
            
            if self.key_monitor is None:
                logger.info("Configuring keyboard event monitor")
                self.key_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskKeyDown,
                    self._handle_key_event
                )
            
            if self.click_monitor is None:
                self.click_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskLeftMouseDown,
                    self._handle_click_event
                )
            
            self.window.orderFrontRegardless()
            
        except Exception as e:
            logger.error(f"Error showing window: {e}")

    def hide(self):
        """
        Hide the window and clean up event monitors.

        Raises:
            Exception: If there's an error hiding the window.
        """
        try:
            logger.info("Closing window")
            
            if self.key_monitor is not None:
                NSEvent.removeMonitor_(self.key_monitor)
                self.key_monitor = None
                logger.info("Keyboard event monitor removed")
            
            if self.click_monitor is not None:
                NSEvent.removeMonitor_(self.click_monitor)
                self.click_monitor = None
                logger.info("Click event monitor removed")
            
            self.window.orderOut_(None)
            logger.info("Window hidden successfully")
            
        except Exception as e:
            logger.error(f"Error hiding window: {e}")
            import traceback
            logger.error(traceback.format_exc())
