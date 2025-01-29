from Quartz import (CFMachPortCreateRunLoopSource, CFRunLoopGetCurrent,
                   kCFRunLoopDefaultMode, CGEventTapCreate,
                   kCGSessionEventTap, kCGHeadInsertEventTap,
                   CGEventMaskBit, kCGEventKeyDown, CGEventGetFlags,
                   kCGEventFlagMaskCommand, kCGEventFlagMaskAlternate,
                   kCGEventFlagMaskShift, kCGEventFlagMaskControl, CGEventGetIntegerValueField,
                   kCGKeyboardEventKeycode, CFRunLoopAddSource,
                   CGEventTapEnable)
import logging

# Utilise le logger configuré dans main.py
logger = logging.getLogger(__name__)

class MacKeyboardListener:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.tap = None
        self.run_loop_source = None
        
        # Dictionnaire pour convertir les codes de touches en noms lisibles
        self.KEY_CODES = {
            0: 'a', 1: 's', 2: 'd', 3: 'f', 4: 'h', 5: 'g', 6: 'z', 7: 'x',
            8: 'c', 9: 'v', 10: '§', 11: 'b', 12: 'q', 13: 'w', 14: 'e',
            15: 'r', 16: 'y', 17: 't', 18: '1', 19: '2', 20: '3', 21: '4',
            22: '6', 23: '5', 24: '=', 25: '9', 26: '7', 27: '-', 28: '8',
            29: '0', 30: ']', 31: 'o', 32: 'u', 33: '[', 34: 'i', 35: 'p',
            36: 'RETURN', 37: 'l', 38: 'j', 39: "'", 40: 'k', 41: ';',
            42: '\\', 43: ',', 44: '/', 45: 'n', 46: 'm', 47: '.',
            48: 'TAB', 49: 'SPACE', 50: '`', 51: 'DELETE', 52: 'ENTER',
            53: 'ESCAPE', 54: 'COMMAND', 55: 'SHIFT', 56: 'CAPSLOCK',
            57: 'OPTION', 58: 'CONTROL', 59: 'RIGHT_SHIFT', 60: 'RIGHT_OPTION',
            61: 'RIGHT_CONTROL', 62: 'FUNCTION', 63: 'F17', 64: 'F18',
            65: 'F19', 66: 'F20', 67: 'F5', 68: 'F6', 69: 'F7', 70: 'F3',
            71: 'F8', 72: 'F9', 73: 'F11', 74: 'F13', 75: 'F16', 76: 'F14',
            77: 'F10', 78: 'F12', 79: 'F15', 80: 'HELP', 81: 'HOME',
            82: 'PAGE_UP', 83: 'DELETE_FORWARD', 84: 'F4', 85: 'END',
            86: 'F2', 87: 'PAGE_DOWN', 88: 'F1', 89: 'LEFT_ARROW',
            90: 'RIGHT_ARROW', 91: 'DOWN_ARROW', 92: 'UP_ARROW'
        }

    def _event_callback(self, proxy, event_type, event, refcon):
        """Callback appelé pour chaque événement clavier"""
        try:
            # Vérifie si c'est un événement de type touche pressée
            if event_type == kCGEventKeyDown:
                # Obtient le code de la touche et les flags
                key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                flags = CGEventGetFlags(event)
                
                # Vérifie les modificateurs
                cmd_pressed = (flags & kCGEventFlagMaskCommand) != 0
                alt_pressed = (flags & kCGEventFlagMaskAlternate) != 0
                ctrl_pressed = (flags & kCGEventFlagMaskControl) != 0
                
                # Convertit le code en nom de touche
                key_name = self.KEY_CODES.get(key_code, f'Unknown({key_code})')
                '''
                # Log de la touche pressée
                modifiers = []
                if cmd_pressed:
                    modifiers.append('Command')
                if alt_pressed:
                    modifiers.append('Option')
                if ctrl_pressed:
                    modifiers.append('Control')
                
                if modifiers:
                    logger.info(f"Touche pressée: {' + '.join(modifiers)} + {key_name} (code: {key_code})")
                else:
                    logger.info(f"Touche pressée: {key_name} (code: {key_code})")
                '''
                # Vérifie si c'est la combinaison qu'on cherche (Command + Control + Option + V)
                if key_code == 9 and cmd_pressed and alt_pressed and ctrl_pressed:  # V
                    logger.info("Combinaison de touches détectée: Command + Control + Option + V!")
                    self.callback()
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'événement: {e}")
        
        return event

    def start(self):
        """Démarre l'écoute du clavier"""
        try:
            logger.info("Démarrage du listener clavier...")
            self.running = True
            
            # Crée un tap pour intercepter les événements clavier
            mask = CGEventMaskBit(kCGEventKeyDown)
            self.tap = CGEventTapCreate(
                kCGSessionEventTap,  # Tap au niveau de la session
                kCGHeadInsertEventTap,  # Insère au début de la chaîne
                0,  # Options par défaut
                mask,  # Masque d'événements
                self._event_callback,  # Notre callback
                None  # Pas de données utilisateur
            )
            
            if self.tap is None:
                raise Exception("Impossible de créer le tap d'événements. Vérifiez les permissions d'accessibilité.")
            
            # Active le tap
            CGEventTapEnable(self.tap, True)
            
            # Crée une source pour la boucle d'événements
            self.run_loop_source = CFMachPortCreateRunLoopSource(
                None, self.tap, 0
            )
            
            # Ajoute la source à la boucle d'événements courante
            run_loop = CFRunLoopGetCurrent()
            CFRunLoopAddSource(
                run_loop,
                self.run_loop_source,
                kCFRunLoopDefaultMode
            )
            
            logger.info("Listener clavier démarré avec succès")
            logger.info("En attente des événements clavier...")
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du listener: {e}")
            self.running = False
            raise

    def stop(self):
        """Arrête l'écoute du clavier"""
        try:
            logger.info("Arrêt du listener clavier...")
            if self.tap:
                CGEventTapEnable(self.tap, False)  # Désactive le tap
                self.tap = None
            if self.run_loop_source:
                self.run_loop_source = None
            
            self.running = False
            logger.info("Listener clavier arrêté avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du listener: {e}")
            raise
