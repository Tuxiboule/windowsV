from keyboard_listener import KeyboardListener
from popup_window import PopupWindow
from mouse_position import MousePosition
import sys
import logging
import os
import platform
import signal
import threading

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.popup = PopupWindow()
        self.keyboard_listener = None
        self.running = False
        
        # Configuration du gestionnaire de signaux
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour un arrêt propre"""
        logger.info(f"Signal reçu: {signum}")
        self.stop()
        
    def check_permissions(self):
        """Vérifie si l'application a les autorisations nécessaires"""
        if platform.system() != 'Darwin':
            return True
            
        try:
            test_listener = KeyboardListener(lambda: None)
            test_listener.start()
            test_listener.stop()
            return True
        except Exception as e:
            logger.error(f"Erreur d'autorisation : {e}")
            return False

    def show_popup(self):
        """Callback appelé lorsque la combinaison de touches est détectée"""
        try:
            x, y = MousePosition.get_current_position()
            x += 20  # Décalage pour éviter que la fenêtre soit sous le curseur
            self.popup.show(x, y)
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du popup : {e}")

    def start(self):
        """Démarre l'application"""
        try:
            self.running = True
            self.keyboard_listener = KeyboardListener(self.show_popup)
            self.keyboard_listener.start()
            
            logger.info("\nApplication démarrée avec succès!")
            print("\nAppuyez sur Shift + Option + Cmd + V pour afficher la fenêtre")
            print("Appuyez sur Ctrl+C pour quitter\n")
            
            # Boucle principale
            while self.running:
                try:
                    if threading.main_thread().is_alive():
                        threading.Event().wait(1)
                    else:
                        break
                except (KeyboardInterrupt, SystemExit):
                    break
                    
        except Exception as e:
            logger.error(f"Erreur lors du démarrage : {e}")
        finally:
            self.stop()

    def stop(self):
        """Arrête proprement l'application"""
        self.running = False
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if self.popup:
                self.popup.hide()
            logger.info("Application arrêtée proprement")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt : {e}")
        finally:
            sys.exit(0)

    def run(self):
        """Point d'entrée principal de l'application"""
        logger.info("Démarrage de l'application...")
        
        if not self.check_permissions():
            print("\n" + "="*80)
            print("ATTENTION : Autorisations requises")
            print("Cette application nécessite des autorisations d'accessibilité pour fonctionner.")
            print("\nPour autoriser l'application :")
            print("1. Allez dans Préférences Système > Sécurité et confidentialité > Confidentialité")
            print("2. Sélectionnez 'Accessibilité' dans la liste de gauche")
            print("3. Cliquez sur le cadenas en bas à gauche pour déverrouiller")
            print("4. Ajoutez Terminal (ou votre éditeur de code) à la liste")
            print("\nUne fois les autorisations accordées, relancez l'application.")
            print("="*80 + "\n")
            sys.exit(1)
        
        self.start()

if __name__ == "__main__":
    app = Application()
    app.run()
