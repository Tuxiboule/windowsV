# WindowsV

A clipboard manager for macOS inspired by Windows+V, allowing easy access to your clipboard history.
Fell free to comment any suggestion.

## Features

- 📋 Clipboard history  
- ⌨️ Customizable keyboard shortcut (default: Ctrl+Opt+Cmd+V)  
- 🖱️ Contextual user interface that appears at the cursor position  
- 🔄 Real-time updates  

## Requirements

- macOS 10.13 or later  
- Python 3.9+  
- Python packages listed in `requirements.txt`  

### Installing Python

   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python@3.9
   ```

After installing Python, make sure pip (Python package manager) is up to date:
```bash
python3 -m pip install --upgrade pip
```

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/Tuxiboule/WindowsV.git
   cd WindowsV
   ```  
2. Install dependencies:  
   ```bash
   pip3 install -r requirements.txt
   ```  
3. Run the application:  
   ```bash
   python3 main.py
   ```  

## Required Permissions

The application requires the following permissions to function properly:  
- **Accessibility**: To detect keyboard shortcuts  
- **Input Monitoring**: To monitor keyboard input  

These permissions can be granted in:  
**System Preferences > Security & Privacy > Privacy > Accessibility/Input Monitoring**  

## Usage

1. The app runs in the background in the menu bar (📋 icon)  
2. Use the shortcut Ctrl+Opt+Cmd+V to display the clipboard history  
3. Click on an item to past it in the current field

## Project Structure

- `main.py` : Application entry point  
- `popup_window.py` : Manages the popup window  
- `clipboard_history.py` : Handles clipboard history  
- `mac_keyboard_listener.py` : Manages keyboard shortcuts  
- `mouse_position.py` : Utility for retrieving cursor position