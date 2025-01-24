# Fenêtre Contextuelle

Cette application crée une fenêtre contextuelle qui apparaît à côté du curseur lorsque vous appuyez sur la combinaison de touches Shift + Option + Cmd + V.

## Installation

1. Assurez-vous d'avoir Python 3.6 ou supérieur installé
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. Utilisez la combinaison de touches Shift + Option + Cmd + V pour faire apparaître la fenêtre
3. La fenêtre disparaîtra automatiquement si vous :
   - Cliquez en dehors de la fenêtre
   - Appuyez sur la touche Échap
   - Utilisez à nouveau le raccourci

## Structure du projet

- `main.py` : Point d'entrée de l'application
- `keyboard_listener.py` : Gestion des raccourcis clavier
- `popup_window.py` : Gestion de la fenêtre contextuelle
- `mouse_position.py` : Récupération de la position du curseur
- `requirements.txt` : Liste des dépendances
