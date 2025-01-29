from setuptools import setup

APP = ['../main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pynput'],
    'includes': ['pynput'],
    'frameworks': ['Cocoa'],
    'plist': {
        'LSUIElement': True,  # Pour que l'app soit uniquement dans la barre de menu
        'CFBundleName': 'WindowsV',
        'CFBundleDisplayName': 'WindowsV',
        'CFBundleIdentifier': 'com.windowsv.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
}

setup(
    name="WindowsV",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
