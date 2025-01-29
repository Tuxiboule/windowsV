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
                    # Si l'élément existe déjà dans l'historique, le supprimer d'abord
                    if content in self.history:
                        logger.info(f"Suppression du doublon existant : {content[:50]}...")
                        self.history.remove(content)
                    
                    # Ajoute le nouvel élément au début
                    self.history.insert(0, content)
                    logger.info(f"Ajout à l'historique : {content[:50]}...")
                    
                    # Limite la taille de l'historique
                    if len(self.history) > self.max_items:
                        self.history.pop()
                
                self.last_change_count = current_count
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'historique : {e}")
    
    def get_history(self):
        """Retourne l'historique actuel"""
        return self.history
    
    def check_accessibility_permissions(self):
        """Vérifie si l'application a les permissions d'accessibilité"""
        try:
            # Vérifie si on peut créer un événement de test
            test_event = CGEventCreateKeyboardEvent(None, 0, True)
            if test_event is None:
                logger.error("Impossible de créer des événements. Vérifiez les permissions d'accessibilité.")
                return False
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des permissions : {e}")
            return False

    def paste_item(self, item):
        """Colle un élément dans le presse-papier actuel et le colle"""
        try:
            # Vérifie d'abord les permissions
            if not self.check_accessibility_permissions():
                logger.error("Permissions d'accessibilité manquantes. Veuillez les activer dans Préférences Système > Sécurité et confidentialité > Confidentialité > Accessibilité")
                return False

            # Met à jour le presse-papier
            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(item, NSStringPboardType)
            logger.info(f"Élément mis dans le presse-papier : {item[:50]}...")
            
            # Utilise CGEvent pour une simulation plus fiable de Cmd+V
            try:
                # Crée les événements pour Cmd+V
                v_keycode = 9  # Code pour la touche V
                
                # Touche V pressée avec Cmd
                v_down = CGEventCreateKeyboardEvent(None, v_keycode, True)
                CGEventSetFlags(v_down, kCGEventFlagMaskCommand)
                
                # Touche V relâchée
                v_up = CGEventCreateKeyboardEvent(None, v_keycode, False)
                
                # Envoie les événements
                CGEventPost(kCGHIDEventTap, v_down)
                time.sleep(0.1)  # Petit délai pour assurer la stabilité
                CGEventPost(kCGHIDEventTap, v_up)
                
                logger.info("Simulation de Cmd+V effectuée avec succès")
                return True
                
            except Exception as e:
                logger.error(f"Erreur lors de la simulation du collage : {e}")
                # Essaie une méthode alternative avec pbpaste/pbcopy
                try:
                    subprocess.run(['pbcopy'], input=item.encode('utf-8'))
                    subprocess.run(['pbpaste'])
                    logger.info("Collage effectué via pbpaste")
                    return True
                except Exception as e2:
                    logger.error(f"Échec de la méthode alternative : {e2}")
                    return False
            
        except Exception as e:
            logger.error(f"Erreur lors du collage : {e}")
            return False

    def remove_item(self, index):
        """Supprime un élément de l'historique"""
        try:
            if 0 <= index < len(self.history):
                removed_item = self.history.pop(index)
                logger.info(f"Élément supprimé de l'historique : {removed_item[:50]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'élément : {e}")
            return False
