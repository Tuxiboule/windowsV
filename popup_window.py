from AppKit import (NSWindow, NSScreen, NSColor, NSBorderlessWindowMask,
                  NSBackingStoreBuffered, NSMakeRect, NSApplication,
                  NSEventMaskKeyDown, NSEventTypeKeyDown, NSEvent,
                  NSApp, NSFloatingWindowLevel, NSEventMaskLeftMouseDown,
                  NSEventTypeLeftMouseDown, NSWindowStyleMaskTitled,
                  NSView, NSTextField, NSButton, NSTextView, NSScrollView,
                  NSBezelBorder, NSFont, NSMakeRange, NSForegroundColorAttributeName,
                  NSAttributedString, NSCursor, NSTrackingArea, NSTrackingMouseEnteredAndExited,
                  NSTrackingActiveAlways, NSTrackingMouseMoved, NSBezierPath,
                  NSFontAttributeName)
from Foundation import NSPoint, NSSize, NSRect
from objc import super
import logging
from clipboard_history import ClipboardHistory

logger = logging.getLogger(__name__)

class HistoryItemView(NSView):
    def initWithFrame_text_index_callback_(self, frame, text, index, callback):
        self = super(HistoryItemView, self).initWithFrame_(frame)
        if self is not None:
            self.text = text
            self.index = index
            self.callback = callback
            self.hovered = False
            
            # Configure le suivi de la souris
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
        return self
    
    def mouseEntered_(self, event):
        self.hovered = True
        self.setNeedsDisplay_(True)
        NSCursor.pointingHandCursor().set()
    
    def mouseExited_(self, event):
        self.hovered = False
        self.setNeedsDisplay_(True)
        NSCursor.arrowCursor().set()
    
    def mouseDown_(self, event):
        self.callback(self.index)
    
    def drawRect_(self, rect):
        # Dessine le fond
        if self.hovered:
            NSColor.selectedTextBackgroundColor().setFill()
        else:
            NSColor.clearColor().setFill()
        NSBezierPath.fillRect_(self.bounds())
        
        # Dessine le texte
        if self.hovered:
            text_color = NSColor.selectedTextColor()
        else:
            text_color = NSColor.textColor()
        
        attrs = {
            NSForegroundColorAttributeName: text_color,
            NSFontAttributeName: NSFont.systemFontOfSize_(13)
        }
        
        # Tronque le texte si nécessaire
        display_text = self.text
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."
        
        text = NSAttributedString.alloc().initWithString_attributes_(
            display_text, attrs
        )
        
        # Calcule la position du texte pour le centrer verticalement
        text_height = text.size().height
        y_pos = (self.bounds().size.height - text_height) / 2
        
        text.drawAtPoint_(NSPoint(10, y_pos))

class PopupWindow:
    def __init__(self):
        logger.info("Initialisation de PopupWindow")
        
        # Initialise l'historique du presse-papier
        self.clipboard_history = ClipboardHistory(max_items=10)
        
        # Initialise NSApplication si nécessaire
        if NSApp() is None:
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory
        
        # Crée une fenêtre simple sans bordure
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 300),  # Position et taille initiales
            NSBorderlessWindowMask | NSWindowStyleMaskTitled,  # Sans bordure mais peut avoir le focus
            NSBackingStoreBuffered,
            False
        )
        
        # Configure la fenêtre
        self.window.setBackgroundColor_(NSColor.windowBackgroundColor())
        self.window.setOpaque_(True)
        self.window.setLevel_(NSFloatingWindowLevel)  # Fenêtre flottante
        self.window.setHasShadow_(True)  # Avec une ombre
        self.window.setAcceptsMouseMovedEvents_(True)  # Active les événements de souris
        
        # Crée la vue de défilement
        scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 400, 300)
        )
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setAutohidesScrollers_(True)
        scroll_view.setBorderType_(NSBezelBorder)
        
        # Crée la vue de contenu
        self.content_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 380, 300)
        )
        scroll_view.setDocumentView_(self.content_view)
        
        # Ajoute la vue de défilement à la fenêtre
        self.window.setContentView_(scroll_view)
        
        # Configure les moniteurs d'événements
        self.key_monitor = None
        self.click_monitor = None
        
        # Cache la fenêtre au démarrage
        self.window.orderOut_(None)
        logger.info("PopupWindow initialisée avec succès")

    def _handle_key_event(self, event):
        """Gère les événements clavier"""
        try:
            if event.type() == NSEventTypeKeyDown:
                # Si la touche Echap est pressée (keyCode 53)
                if event.keyCode() == 53:
                    logger.info("Touche Echap détectée, fermeture de la fenêtre")
                    self.hide()
                    return None
            return event
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'événement clavier : {e}")
            return event

    def _handle_click_event(self, event):
        """Gère les événements de clic"""
        try:
            if event.type() == NSEventTypeLeftMouseDown:
                # Si la fenêtre n'est pas la première répondeur, on la ferme
                if not self.window.isKeyWindow():
                    logger.info("Clic détecté en dehors de la fenêtre")
                    self.hide()
                    return None
            return event
        except Exception as e:
            logger.error(f"Erreur lors du traitement du clic : {e}")
            return event
    
    def _handle_item_click(self, index):
        """Gère le clic sur un élément de l'historique"""
        try:
            history = self.clipboard_history.get_history()
            if 0 <= index < len(history):
                item = history[index]
                if self.clipboard_history.paste_item(item):
                    logger.info(f"Élément {index} collé avec succès")
                    self.hide()
        except Exception as e:
            logger.error(f"Erreur lors du clic sur l'élément : {e}")

    def _update_history_view(self):
        """Met à jour la vue avec l'historique actuel"""
        try:
            # Supprime les anciennes vues
            for subview in self.content_view.subviews():
                subview.removeFromSuperview()
            
            # Récupère l'historique
            history = self.clipboard_history.get_history()
            
            # Calcule la hauteur totale nécessaire
            item_height = 40
            total_height = max(300, len(history) * item_height)
            
            # Ajuste la taille de la vue de contenu
            self.content_view.setFrame_(NSMakeRect(0, 0, 380, total_height))
            
            # Crée une vue pour chaque élément
            for i, item in enumerate(history):
                frame = NSMakeRect(0, total_height - (i + 1) * item_height, 380, item_height)
                item_view = HistoryItemView.alloc().initWithFrame_text_index_callback_(
                    frame, item, i, self._handle_item_click
                )
                self.content_view.addSubview_(item_view)
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la vue : {e}")

    def show(self, x=0, y=0):
        """Affiche la fenêtre aux coordonnées spécifiées"""
        try:
            logger.info(f"Tentative d'affichage de la fenêtre aux coordonnées ({x}, {y})")
            
            # Met à jour l'historique
            self.clipboard_history.check_and_update()
            
            # Met à jour la vue
            self._update_history_view()
            
            # Obtient l'écran principal
            screen = NSScreen.mainScreen()
            if screen is None:
                logger.error("Impossible de trouver l'écran principal")
                return
            
            # Ajuste les coordonnées pour l'écran Mac (origine en bas à gauche)
            frame = screen.frame()
            adjusted_y = frame.size.height - y - 300  # Soustrait la hauteur de la fenêtre
            
            logger.debug(f"Dimensions de l'écran : {frame.size.width}x{frame.size.height}")
            logger.debug(f"Position ajustée : ({x}, {adjusted_y})")
            
            # Configure les moniteurs d'événements
            if self.key_monitor is None:
                self.key_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskKeyDown,
                    self._handle_key_event
                )
            if self.click_monitor is None:
                self.click_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskLeftMouseDown,
                    self._handle_click_event
                )
            
            # Positionne et affiche la fenêtre
            self.window.setFrameOrigin_((x, adjusted_y))
            self.window.makeKeyAndOrderFront_(None)  # Donne le focus à la fenêtre
            
            logger.info("Fenêtre affichée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la fenêtre : {e}")
            import traceback
            logger.error(traceback.format_exc())

    def hide(self):
        """Cache la fenêtre"""
        try:
            logger.info("Tentative de masquage de la fenêtre")
            
            # Retire les moniteurs d'événements
            if self.key_monitor is not None:
                NSEvent.removeMonitor_(self.key_monitor)
                self.key_monitor = None
            if self.click_monitor is not None:
                NSEvent.removeMonitor_(self.click_monitor)
                self.click_monitor = None
            
            # Cache la fenêtre
            self.window.orderOut_(None)
            logger.info("Fenêtre masquée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du masquage de la fenêtre : {e}")
            import traceback
            logger.error(traceback.format_exc())
