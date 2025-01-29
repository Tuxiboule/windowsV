#!/bin/bash

# Se déplace dans le dossier installer
cd "$(dirname "$0")"

# Nettoie les builds précédents
rm -rf build dist
rm -f *.dmg

# Installation des dépendances nécessaires
pip3 install py2app
pip3 install -r ../requirements.txt

# Construction de l'application
python3 setup.py py2app

# Création d'un dossier temporaire pour le DMG
TMP_DMG="tmp_dmg"
rm -rf "$TMP_DMG"
mkdir -p "$TMP_DMG"

# Copie l'application dans le dossier temporaire
cp -r "dist/WindowsV.app" "$TMP_DMG/"

# Création du DMG
create-dmg \
  --volname "WindowsV" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "WindowsV.app" 200 200 \
  --app-drop-link 400 200 \
  "WindowsV.dmg" \
  "$TMP_DMG"

# Nettoyage
rm -rf "$TMP_DMG"
