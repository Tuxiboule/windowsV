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
            
            # Active le layer pour la transparence
            self.setWantsLayer_(True)
            self.layer().setBackgroundColor_(CGColorCreateGenericRGB(1, 1, 1, 0))  # Fond blanc transparent
            
            # Crée le bouton de suppression
            button_size = 20
            button_frame = NSMakeRect(
                frame.size.width - button_size - 10,  # 10 pixels de marge
                (frame.size.height - button_size) / 2,
                button_size,
                button_size
            )
            self.delete_button = NSButton.alloc().initWithFrame_(button_frame)
            self.delete_button.setTitle_("✕")  # Utilisation d'un × plus visible
            self.delete_button.setBezelStyle_(NSBezelStyleRegularSquare)  # Style carré
            self.delete_button.setButtonType_(NSMomentaryPushInButton)  # Type de bouton
            self.delete_button.setBordered_(False)  # Pas de bordure
            self.delete_button.setTarget_(self)
            self.delete_button.setAction_("deleteClicked:")
            self.delete_button.setFont_(NSFont.systemFontOfSize_(14))  # Police plus grande
            
            # Couleur du texte en gris
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
        # Convertit le point de clic en coordonnées locales
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        
        # Vérifie si le clic est sur le bouton de suppression
        if not NSPointInRect(point, self.delete_button.frame()):
            self.callback(self.index)
    
    def drawRect_(self, rect):
        # Dessine le fond
        if self.hovered:
            NSColor.selectedTextBackgroundColor().setFill()  # Plein quand survolé
        else:
            NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9).setFill()  # Semi-transparent sinon
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
        
        # Laisse de l'espace pour le bouton de suppression
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
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 300),  # Position et taille initiales
            NSWindowStyleMaskBorderless | NSWindowStyleMaskTitled | NSWindowStyleMaskNonactivatingPanel,  # Sans bordure et non-activating
            NSBackingStoreBuffered,
            False
        )
        
        # Configure la fenêtre
        background_color = NSColor.windowBackgroundColor().colorWithAlphaComponent_(0.9)  # Plus opaque
        self.window.setBackgroundColor_(background_color)
        self.window.setOpaque_(False)  # Nécessaire pour la transparence
        self.window.setHasShadow_(True)  # Avec une ombre
        self.window.setLevel_(NSFloatingWindowLevel)  # Fenêtre flottante
        self.window.setAcceptsMouseMovedEvents_(True)  # Active les événements de souris
        self.window.setIgnoresMouseEvents_(False)  # Accepte les événements de souris
        self.window.setCanHide_(True)  # Peut être cachée
        self.window.setHidesOnDeactivate_(False)  # Ne se cache pas quand elle perd le focus
        self.window.setBecomesKeyOnlyIfNeeded_(True)  # Ne prend le focus que si nécessaire
        
        # Crée la vue de défilement
        scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 400, 300)
        )
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setAutohidesScrollers_(True)
        scroll_view.setBorderType_(NSBezelBorder)
        scroll_view.setDrawsBackground_(False)  # Rend le fond transparent
        
        # Crée la vue de contenu avec un fond transparent
        self.content_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 380, 300)
        )
        self.content_view.setWantsLayer_(True)
        
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
            logger.info(f"Événement clavier reçu - type: {event.type()}, keyCode: {event.keyCode()}")
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
            # Vérifie si le clic est dans la fenêtre
            click_location = NSEvent.mouseLocation()
            window_frame = self.window.frame()
            
            # Convertit les coordonnées de l'écran en coordonnées de fenêtre
            screen_frame = NSScreen.mainScreen().frame()
            adjusted_y = screen_frame.size.height - click_location.y
            
            # Vérifie si le clic est dans la fenêtre
            in_window = (
                window_frame.origin.x <= click_location.x <= window_frame.origin.x + window_frame.size.width and
                adjusted_y - window_frame.size.height <= click_location.y <= adjusted_y
            )
            
            if not in_window:
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

    def _handle_item_delete(self, index):
        """Gère la suppression d'un élément de l'historique"""
        try:
            if self.clipboard_history.remove_item(index):
                logger.info(f"Élément {index} supprimé avec succès")
                self._update_history_view()
            else:
                logger.error(f"Impossible de supprimer l'élément {index}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'élément : {e}")

    def _update_history_view(self):
        """Met à jour la vue avec l'historique actuel"""
        try:
            # Supprime toutes les anciennes vues
            for subview in self.content_view.subviews():
                subview.removeFromSuperview()
            
            # Récupère l'historique
            history = self.clipboard_history.get_history()
            if not history:
                logger.info("Historique vide")
                return
                
            # Configure la taille des éléments
            item_height = 30
            total_height = max(len(history) * item_height, self.content_view.frame().size.height)
            
            # Met à jour la taille de la vue de contenu
            frame = self.content_view.frame()
            new_frame = NSMakeRect(
                frame.origin.x,
                frame.origin.y,
                frame.size.width,
                total_height
            )
            self.content_view.setFrame_(new_frame)
            
            # Crée une vue pour chaque élément, en commençant par le haut
            for i, item in enumerate(history):
                frame = NSMakeRect(0, total_height - ((i + 1) * item_height), 380, item_height)
                item_view = HistoryItemView.alloc().initWithFrame_text_index_callback_deleteCallback_(
                    frame, item, i, self._handle_item_click, self._handle_item_delete
                )
                self.content_view.addSubview_(item_view)
                
            logger.info(f"Vue mise à jour avec {len(history)} éléments")
            
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
            screen_frame = screen.frame()
            adjusted_y = screen_frame.size.height - y
            
            # Positionne la fenêtre
            self.window.setFrameOrigin_((x, adjusted_y - self.window.frame().size.height))
            
            # Configure les moniteurs d'événements
            if self.key_monitor is None:
                logger.info("Configuration du moniteur d'événements clavier")
                self.key_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskKeyDown,
                    self._handle_key_event
                )
            
            if self.click_monitor is None:
                self.click_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                    NSEventMaskLeftMouseDown,
                    self._handle_click_event
                )
            
            # Affiche la fenêtre sans prendre le focus
            self.window.orderFrontRegardless()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la fenêtre : {e}")

    def hide(self):
        """Cache la fenêtre"""
        try:
            logger.info("Fermeture de la fenêtre")
            
            # Supprime les moniteurs d'événements
            if self.key_monitor is not None:
                NSEvent.removeMonitor_(self.key_monitor)
                self.key_monitor = None
                logger.info("Moniteur clavier supprimé")
            
            if self.click_monitor is not None:
                NSEvent.removeMonitor_(self.click_monitor)
                self.click_monitor = None
                logger.info("Moniteur de clic supprimé")
            
            # Cache la fenêtre
            self.window.orderOut_(None)
            logger.info("Fenêtre cachée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la fenêtre : {e}")
            import traceback
            logger.error(traceback.format_exc())
