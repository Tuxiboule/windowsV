from AppKit import NSPasteboard, NSStringPboardType
import logging

logger = logging.getLogger(__name__)

class ClipboardHistory:
    def __init__(self, max_items=10):
        self.max_items = max_items
        self.history = []
        self.pasteboard = NSPasteboard.generalPasteboard()
        self.last_change_count = self.pasteboard.changeCount()
        
    def check_and_update(self):
        """Vérifie si le presse-papier a changé et met à jour l'historique"""
        try:
            current_count = self.pasteboard.changeCount()
            
            if current_count > self.last_change_count:
                logger.info("Changement détecté dans le presse-papier")
                
                # Récupère le contenu du presse-papier
                if content := self.pasteboard.stringForType_(NSStringPboardType):
                    # Évite les doublons consécutifs
                    if not self.history or content != self.history[0]:
                        self.history.insert(0, content)
                        if len(self.history) > self.max_items:
                            self.history.pop()
                        logger.info(f"Ajout à l'historique : {content[:50]}...")
                
                self.last_change_count = current_count
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'historique : {e}")
    
    def get_history(self):
        """Retourne l'historique actuel"""
        return self.history
    
    def paste_item(self, item):
        """Colle un élément dans le presse-papier actuel"""
        try:
            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(item, NSStringPboardType)
            logger.info(f"Élément collé dans le presse-papier : {item[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du collage : {e}")
            return False
