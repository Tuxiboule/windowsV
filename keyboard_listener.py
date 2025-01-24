from pynput import keyboard
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KeyboardListener:
    def __init__(self, callback):
        self.callback = callback
        self.current_keys = set()
        self.listener = None
        
        # Définition des touches à surveiller
        self.REQUIRED_KEYS = {
            keyboard.Key.shift,     # Shift
            keyboard.Key.alt,       # Option/Alt
            keyboard.Key.cmd,       # Command
            keyboard.KeyCode.from_char('v')  # V
        }

    def _on_press(self, key):
        """Appelé lorsqu'une touche est pressée"""
        try:
            logger.debug(f'Touche pressée: {key}')
            
            # Si c'est une des touches que nous surveillons
            if key in self.REQUIRED_KEYS:
                self.current_keys.add(key)
                
                # Vérifie si toutes les touches requises sont pressées
                if self.REQUIRED_KEYS.issubset(self.current_keys):
                    logger.info("Combinaison de touches détectée!")
                    self.callback()
                    
        except Exception as e:
            logger.error(f"Erreur lors de la détection de touche: {e}")

    def _on_release(self, key):
        """Appelé lorsqu'une touche est relâchée"""
        try:
            logger.debug(f'Touche relâchée: {key}')
            # Retire la touche de l'ensemble des touches pressées
            self.current_keys.discard(key)
        except Exception as e:
            logger.error(f"Erreur lors du relâchement de touche: {e}")

    def start(self):
        """Démarre l'écoute du clavier"""
        logger.info("Démarrage du listener clavier...")
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info("Listener clavier démarré avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du listener: {e}")
            raise

    def stop(self):
        """Arrête l'écoute du clavier"""
        logger.info("Arrêt du listener clavier...")
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            logger.info("Listener clavier arrêté avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du listener: {e}")
            raise
