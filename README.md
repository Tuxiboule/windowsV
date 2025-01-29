# WindowsV

A clipboard manager for macOS inspired by Windows+V, allowing easy access to your clipboard history.

## Features

- 📋 Clipboard history  
- ⌨️ Customizable keyboard shortcut (default: Ctrl+Opt+Cmd+V)  
- 🖱️ Contextual user interface that appears at the cursor position  
- 🔄 Real-time updates  

## Requirements

- macOS 10.13 or later  
- Python 3.9+  
- Python packages listed in `requirements.txt`  

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-username/WindowsV.git
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

1. Launch the application  
2. The app runs in the background in the menu bar (📋 icon)  
3. Use the shortcut Ctrl+Opt+Cmd+V to display the clipboard history  
4. Click on an item to copy it to the clipboard and paste it in input field

## Project Structure

- `main.py` : Application entry point  
- `popup_window.py` : Manages the popup window  
- `clipboard_history.py` : Handles clipboard history  
- `mac_keyboard_listener.py` : Manages keyboard shortcuts  
- `mouse_position.py` : Utility for retrieving cursor position  

## Development

To contribute to the project:  
1. Fork the repository  
2. Create a branch for your feature  
3. Commit your changes  
4. Push to the branch  
5. Open a Pull Request  