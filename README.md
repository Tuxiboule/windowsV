# Gestionnaire de Presse-papiers pour macOS

Cette application est un gestionnaire de presse-papiers inspiré de la fonctionnalité Windows + V de Windows 10/11, mais adapté pour macOS.

## Fonctionnalités

- Historique des 10 derniers éléments copiés
- Interface dans la barre de menu macOS (menu bar)
- Raccourci clavier Command + Shift + V pour accéder rapidement à l'historique
- Sauvegarde persistante de l'historique
- Horodatage des éléments copiés

## Installation

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```bash
python clipboard_manager.py             
```

2. Une icône 📋 apparaîtra dans votre barre de menu
3. Utilisez Command + Shift + V pour accéder rapidement à l'historique
4. Cliquez sur un élément dans le menu pour le copier dans le presse-papiers

Note : Pour que l'application fonctionne correctement, vous devrez probablement autoriser l'accès aux "Fonctionnalités d'assistance" dans les Préférences Système > Sécurité et confidentialité > Confidentialité.

## Arrêt de l'application

Cliquez sur l'icône 📋 dans la barre de menu et sélectionnez "Quit"
