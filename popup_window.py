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
    def initWithFrame_text_index_callback_deleteCallback_(self, frame, text, index, callback, delete_callback):
        self = super(HistoryItemView, self).initWithFrame_(frame)
        if self is not None:
            self.text = text
            self.index = index
            self.callback = callback
            self.delete_callback = delete_callback
            self.hovered = False
            self.delete_button_hovered = False
            
            # Configure mouse tracking
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
            
            # Enable layer for transparency
            self.setWantsLayer_(True)
            self.layer().setBackgroundColor_(CGColorCreateGenericRGB(1, 1, 1, 0))  # Transparent white background
            
            # Create delete button
            button_size = 20
            button_frame = NSMakeRect(
                frame.size.width - button_size - 10,  # 10 pixels of margin
                (frame.size.height - button_size) / 2,
                button_size,
                button_size
            )
            self.delete_button = NSButton.alloc().initWithFrame_(button_frame)
            self.delete_button.setTitle_("✕")  # Use a more visible ×
            self.delete_button.setBezelStyle_(NSBezelStyleRegularSquare)  # Square style
            self.delete_button.setButtonType_(NSMomentaryPushInButton)  # Button type
            self.delete_button.setBordered_(False)  # No border
            self.delete_button.setTarget_(self)
            self.delete_button.setAction_("deleteClicked:")
            self.delete_button.setFont_(NSFont.systemFontOfSize_(14))  # Larger font
            
            # Text color in gray
            attrs = {
                NSForegroundColorAttributeName: NSColor.secondaryLabelColor()
            }
            title_attrs = NSAttributedString.alloc().initWithString_attributes_("✕", attrs)
            self.delete_button.setAttributedTitle_(title_attrs)
            
            self.addSubview_(self.delete_button)
            
        return self
    
    def deleteClicked_(self, sender):
        self.delete_callback(self.index)
    
    def mouseEntered_(self, event):
        self.hovered = True
        self.setNeedsDisplay_(True)
        NSCursor.pointingHandCursor().set()
    
    def mouseExited_(self, event):
        self.hovered = False
        self.setNeedsDisplay_(True)
        NSCursor.arrowCursor().set()
    
    def mouseDown_(self, event):
        # Convert click point to local coordinates
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        
        # Check if click is on delete button
        if not NSPointInRect(point, self.delete_button.frame()):
            self.callback(self.index)
    
    def drawRect_(self, rect):
        # Draw background
        if self.hovered:
            NSColor.selectedTextBackgroundColor().setFill()  # Fill when hovered
        else:
            NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9).setFill()  # Semi-transparent otherwise
        NSBezierPath.fillRect_(self.bounds())
        
        # Draw text
        if self.hovered:
            text_color = NSColor.selectedTextColor()
        else:
            text_color = NSColor.textColor()
        
        attrs = {
            NSForegroundColorAttributeName: text_color,
            NSFontAttributeName: NSFont.systemFontOfSize_(13)
        }
        
        # Truncate text if necessary
        display_text = self.text
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."
        
        text = NSAttributedString.alloc().initWithString_attributes_(
            display_text, attrs
        )
        
        # Calculate text position to center vertically
        text_height = text.size().height
        y_pos = (self.bounds().size.height - text_height) / 2
        
        # Leave space for delete button
        text.drawAtPoint_(NSPoint(10, y_pos))

class PopupWindow:
    def __init__(self):
        logger.info("Initializing PopupWindow")
        
        # Initialize clipboard history
        self.clipboard_history = ClipboardHistory(max_items=10)
        
        # Initialize NSApplication if needed
        if NSApp() is None:
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory
        
        # Create a simple borderless window
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 300),  # Initial position and size
            NSWindowStyleMaskBorderless | NSWindowStyleMaskTitled | NSWindowStyleMaskNonactivatingPanel,  # Borderless and non-activating
            NSBackingStoreBuffered,
            False
        )
        
        # Configure window
        background_color = NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9)  # More opaque
        self.window.setBackgroundColor_(background_color)
        self.window.setOpaque_(False)  # Required for transparency
        self.window.setHasShadow_(True)  # With shadow
        self.window.setLevel_(NSFloatingWindowLevel)  # Floating window
        self.window.setAcceptsMouseMovedEvents_(True)  # Enable mouse events
        self.window.setIgnoresMouseEvents_(False)  # Accept mouse events
        self.window.setCanHide_(True)  # Can be hidden
        self.window.setHidesOnDeactivate_(False)  # Don't hide when losing focus
        self.window.setBecomesKeyOnlyIfNeeded_(True)  # Only take focus when needed
        
        # Create scroll view
        scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 400, 300)
        )
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setAutohidesScrollers_(True)
        scroll_view.setBorderType_(NSBezelBorder)
        scroll_view.setDrawsBackground_(False)  # Make background transparent
        
        # Create content view with transparent background
        self.content_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 380, 300)
        )
        self.content_view.setWantsLayer_(True)
        
        scroll_view.setDocumentView_(self.content_view)
        
        # Add scroll view to window
        self.window.setContentView_(scroll_view)
        
        # Configure event monitors
        self.key_monitor = None
        self.click_monitor = None
        
        # Hide window at startup
        self.window.orderOut_(None)
        logger.info("PopupWindow successfully initialized")

    def _handle_key_event(self, event):
        # Handle keyboard events
        try:
            logger.info(f"Keyboard event received - type: {event.type()}, keyCode: {event.keyCode()}")
            if event.type() == NSEventTypeKeyDown:
                # If Esc key is pressed (keyCode 53)
                if event.keyCode() == 53:
                    logger.info("Esc key detected, closing window")
                    self.hide()
                    return None
            return event
        except Exception as e:
            logger.error(f"Error handling keyboard event: {e}")
            return event

    def _handle_click_event(self, event):
        # Handle click events
        try:
            # Check if click is within window
            click_location = NSEvent.mouseLocation()
            window_frame = self.window.frame()
            
            # Convert screen coordinates to window coordinates
            screen_frame = NSScreen.mainScreen().frame()
            adjusted_y = screen_frame.size.height - click_location.y
            
            # Check if click is within window
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
        # Handle history item click
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
        # Handle history item deletion
        try:
            if self.clipboard_history.remove_item(index):
                logger.info(f"Item {index} deleted successfully")
                self._update_history_view()
            else:
                logger.error(f"Failed to delete item {index}")
        except Exception as e:
            logger.error(f"Error handling item deletion: {e}")

    def _update_history_view(self):
        # Update view with current history
        try:
            # Remove all old views
            for subview in self.content_view.subviews():
                subview.removeFromSuperview()
            
            # Get history
            history = self.clipboard_history.get_history()
            if not history:
                logger.info("History is empty")
                return
                
            # Configure item size
            item_height = 30
            total_height = max(len(history) * item_height, self.content_view.frame().size.height)
            
            # Update content view size
            frame = self.content_view.frame()
            new_frame = NSMakeRect(
                frame.origin.x,
                frame.origin.y,
                frame.size.width,
                total_height
            )
            self.content_view.setFrame_(new_frame)
            
            # Create view for each item, starting from top
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
        # Show window at specified coordinates
        try:
            logger.info(f"Showing window at coordinates ({x}, {y})")
            
            # Update history
            self.clipboard_history.check_and_update()
            
            # Update view
            self._update_history_view()
            
            # Get main screen
            screen = NSScreen.mainScreen()
            if screen is None:
                logger.error("Failed to find main screen")
                return
            
            # Adjust coordinates for Mac screen (origin at bottom left)
            screen_frame = screen.frame()
            adjusted_y = screen_frame.size.height - y
            
            # Position window
            self.window.setFrameOrigin_((x, adjusted_y - self.window.frame().size.height))
            
            # Configure event monitors
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
            
            # Show window without taking focus
            self.window.orderFrontRegardless()
            
        except Exception as e:
            logger.error(f"Error showing window: {e}")

    def hide(self):
        # Hide window
        try:
            logger.info("Closing window")
            
            # Remove event monitors
            if self.key_monitor is not None:
                NSEvent.removeMonitor_(self.key_monitor)
                self.key_monitor = None
                logger.info("Keyboard event monitor removed")
            
            if self.click_monitor is not None:
                NSEvent.removeMonitor_(self.click_monitor)
                self.click_monitor = None
                logger.info("Click event monitor removed")
            
            # Hide window
            self.window.orderOut_(None)
            logger.info("Window hidden successfully")
            
        except Exception as e:
            logger.error(f"Error hiding window: {e}")
            import traceback
            logger.error(traceback.format_exc())
