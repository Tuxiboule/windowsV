import tkinter as tk

class PopupWindow:
    def __init__(self):
        self.window = None

    def show(self, x, y):
        """Affiche la fenêtre contextuelle aux coordonnées spécifiées"""
        if self.window:
            self.hide()

        # Création de la fenêtre principale
        self.window = tk.Tk()
        self.window.withdraw()  # Cache la fenêtre pendant la configuration
        self.window.overrideredirect(True)  # Supprime la barre de titre
        
        # Configuration de la fenêtre
        width = 300
        height = 200
        
        # Ajustement de la position pour éviter que la fenêtre ne sorte de l'écran
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = min(x, screen_width - width)
        y = min(y, screen_height - height)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.configure(bg='white')

        # Création d'un cadre avec bordure
        frame = tk.Frame(
            self.window,
            bg='white',
            highlightbackground='#CCCCCC',
            highlightthickness=1
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Ajout du contenu
        label = tk.Label(
            frame,
            text="Presse-papiers ici",
            bg='white',
            fg='#333333',
            font=('Arial', 12)
        )
        label.pack(expand=True)

        # Gestion des événements
        self.window.bind('<Escape>', lambda e: self.hide())
        self.window.bind('<FocusOut>', lambda e: self.hide())
        self.window.bind('<Button-1>', lambda e: self.hide())  # Clic gauche
        
        # Affiche la fenêtre
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def hide(self):
        """Cache et détruit la fenêtre contextuelle"""
        if self.window:
            self.window.destroy()
            self.window = None
