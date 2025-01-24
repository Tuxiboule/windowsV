import tkinter as tk
from tkinter import ttk
import pyperclip
from pynput import keyboard
import json
import os
from datetime import datetime
from PIL import ImageGrab, ImageTk
import io

class ClipboardItem:
    def __init__(self, content, timestamp, is_image=False, pinned=False):
        self.content = content
        self.timestamp = timestamp
        self.is_image = is_image
        self.pinned = pinned

class ClipboardManager:
    def __init__(self):
        # Initialiser l'historique du presse-papiers
        self.clipboard_history = []
        self.max_history = 25
        self.current_keys = set()
        
        # Charger l'historique
        self.load_history()
        
        # Configurer l'écouteur de clavier
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.keyboard_listener.start()
        
        # Créer la fenêtre principale (cachée)
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Démarrer la surveillance du presse-papiers
        self.last_clipboard = pyperclip.paste()
        self.check_clipboard()
        
        # Configurer le style
        self.setup_style()

    def setup_style(self):
        style = ttk.Style()
        style.configure('Clipboard.TFrame', background='#2D2D2D')
        style.configure('ClipboardItem.TFrame', background='#3D3D3D', padding=5)
        style.configure('ClipboardText.TLabel', 
                       background='#3D3D3D',
                       foreground='white',
                       wraplength=300)
        style.configure('Pinned.ClipboardItem.TFrame', 
                       background='#4D4D4D')

    def create_popup(self):
        # Créer une nouvelle fenêtre popup
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        
        # Positionner la fenêtre près du curseur
        x = popup.winfo_pointerx()
        y = popup.winfo_pointery()
        popup.geometry(f"+{x}+{y}")
        
        # Créer le conteneur principal
        main_frame = ttk.Frame(popup, style='Clipboard.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer le canvas avec scrollbar
        canvas = tk.Canvas(main_frame, bg='#2D2D2D', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Clipboard.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ajouter les éléments de l'historique
        for item in self.clipboard_history:
            self.create_item_frame(scrollable_frame, item, popup)
        
        # Packer les widgets
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurer la taille
        popup.update_idletasks()
        width = min(400, popup.winfo_screenwidth() - x)
        height = min(600, popup.winfo_screenheight() - y)
        popup.geometry(f"{width}x{height}")
        
        # Gérer la fermeture au clic en dehors
        popup.bind('<FocusOut>', lambda e: popup.destroy())
        
        return popup

    def create_item_frame(self, parent, item, popup):
        # Créer le cadre pour l'élément
        style = 'Pinned.ClipboardItem.TFrame' if item.pinned else 'ClipboardItem.TFrame'
        frame = ttk.Frame(parent, style=style)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Ajouter le contenu
        if item.is_image:
            try:
                image = ImageTk.PhotoImage(item.content)
                label = ttk.Label(frame, image=image)
                label.image = image  # Garder une référence
            except:
                label = ttk.Label(frame, text="[Image]", style='ClipboardText.TLabel')
        else:
            # Tronquer le texte si nécessaire
            display_text = item.content
            if len(display_text) > 100:
                display_text = display_text[:97] + "..."
            label = ttk.Label(frame, text=display_text, style='ClipboardText.TLabel')
        
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ajouter les boutons
        pin_text = "📌" if not item.pinned else "🔓"
        pin_btn = ttk.Button(frame, text=pin_text, 
                            command=lambda: self.toggle_pin(item))
        pin_btn.pack(side=tk.RIGHT, padx=2)
        
        delete_btn = ttk.Button(frame, text="🗑", 
                               command=lambda: self.delete_item(item))
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
        # Ajouter le comportement de clic
        label.bind('<Button-1>', lambda e: self.use_item(item, popup))
        
        # Ajouter un séparateur
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=5)

    def toggle_pin(self, item):
        item.pinned = not item.pinned
        self.save_history()
        self.show_history()  # Rafraîchir l'affichage

    def delete_item(self, item):
        if item in self.clipboard_history:
            self.clipboard_history.remove(item)
            self.save_history()
            self.show_history()  # Rafraîchir l'affichage

    def use_item(self, item, popup):
        if item.is_image:
            # Copier l'image dans le presse-papiers
            output = io.BytesIO()
            item.content.save(output, 'BMP')
            data = output.getvalue()[14:]  # Le format BMP a un en-tête de 14 octets
            output.close()
            pyperclip.copy(data)
        else:
            pyperclip.copy(item.content)
        popup.destroy()

    def check_clipboard(self):
        try:
            # Vérifier d'abord si une image est disponible
            image = ImageGrab.grabclipboard()
            if image:
                current = image
                is_image = True
            else:
                current = pyperclip.paste()
                is_image = False

            if (is_image or current != self.last_clipboard):
                self.last_clipboard = current if not is_image else "image"
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Créer un nouvel élément
                new_item = ClipboardItem(current, timestamp, is_image)
                
                # Ajouter au début de l'historique
                self.clipboard_history.insert(0, new_item)
                
                # Supprimer les éléments non épinglés si on dépasse max_history
                unpinned = [item for item in self.clipboard_history if not item.pinned]
                if len(unpinned) > self.max_history:
                    for item in unpinned[self.max_history:]:
                        if item in self.clipboard_history:
                            self.clipboard_history.remove(item)
                
                self.save_history()
        except:
            pass
        finally:
            # Vérifier toutes les 500ms
            self.root.after(500, self.check_clipboard)

    def on_press(self, key):
        try:
            if hasattr(key, 'char'):
                self.current_keys.add(key.char.lower())
            else:
                self.current_keys.add(key)
            
            # Vérifier si la combinaison Command + Shift + V est pressée
            if (keyboard.Key.cmd in self.current_keys and 
                keyboard.Key.shift in self.current_keys and 
                'v' in self.current_keys):
                self.show_history()
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if hasattr(key, 'char'):
                self.current_keys.discard(key.char.lower())
            else:
                self.current_keys.discard(key)
        except KeyError:
            pass

    def show_history(self):
        self.create_popup()

    def load_history(self):
        history_file = os.path.expanduser('~/.clipboard_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.clipboard_history = []
                    for item in data:
                        if item['is_image']:
                            # Les images ne sont pas sauvegardées entre les sessions
                            continue
                        self.clipboard_history.append(
                            ClipboardItem(
                                item['content'],
                                item['timestamp'],
                                item['is_image'],
                                item.get('pinned', False)
                            )
                        )
            except:
                self.clipboard_history = []

    def save_history(self):
        history_file = os.path.expanduser('~/.clipboard_history.json')
        with open(history_file, 'w') as f:
            # Sauvegarder seulement les éléments texte
            data = []
            for item in self.clipboard_history:
                if not item.is_image:
                    data.append({
                        'content': item.content,
                        'timestamp': item.timestamp,
                        'is_image': item.is_image,
                        'pinned': item.pinned
                    })
            json.dump(data, f)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClipboardManager()
    app.run()
