"""
Start screen for the Blackjack game.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class StartScreen(tk.Frame):
    """Start screen component for the Blackjack game."""
    
    def __init__(self, parent, on_start_game: Callable[[float, int], None]):
        """
        Initialize the start screen.
        
        Args:
            parent: Parent widget
            on_start_game: Callback function when game starts (takes bankroll and num_decks as parameters)
        """
        super().__init__(parent)
        self.on_start_game = on_start_game
        self.selected_bankroll = 1000.0
        self.selected_decks = 6
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the start screen widgets."""
        # Configure grid weights for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Title and branding
        title_frame = tk.Frame(self, bg='#2c5530')
        title_frame.grid(row=1, column=1, sticky="ew", padx=20, pady=20)
        
        # Game title
        title_label = tk.Label(
            title_frame,
            text="BLACKJACK",
            font=('Arial', 36, 'bold'),
            fg='#ffffff',
            bg='#2c5530'
        )
        title_label.pack(pady=(20, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="with Card Counting & Statistical Strategy",
            font=('Arial', 14),
            fg='#cccccc',
            bg='#2c5530'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Card icon/logo
        card_icon = tk.Label(
            title_frame,
            text="🂠 ♠ ♥ ♦ ♣",
            font=('Arial', 24),
            fg='#ffffff',
            bg='#2c5530'
        )
        card_icon.pack(pady=(0, 20))
        
        # Game options frame
        options_frame = ttk.LabelFrame(self, text="Game Setup", padding=20)
        options_frame.grid(row=2, column=1, sticky="ew", padx=20, pady=20)
        
        # Bankroll selection
        bankroll_frame = ttk.Frame(options_frame)
        bankroll_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(bankroll_frame, text="Starting Bankroll:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Bankroll options
        bankroll_options = [
            ("$500 - Conservative", 500.0),
            ("$1,000 - Standard", 1000.0),
            ("$2,500 - Aggressive", 2500.0),
            ("$5,000 - High Roller", 5000.0),
            ("Custom Amount", -1.0)
        ]
        
        self.bankroll_var = tk.StringVar(value=bankroll_options[1][0])
        self.bankroll_combo = ttk.Combobox(
            bankroll_frame,
            textvariable=self.bankroll_var,
            values=[option[0] for option in bankroll_options],
            state="readonly",
            font=('Arial', 12),
            width=25
        )
        self.bankroll_combo.pack(fill=tk.X, pady=(10, 0))
        self.bankroll_combo.bind('<<ComboboxSelected>>', self._on_bankroll_change)
        
        # Shoe size selection
        shoe_frame = ttk.Frame(options_frame)
        shoe_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(shoe_frame, text="Shoe Size (Number of Decks):", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Shoe size options
        shoe_options = [
            ("1 Deck - Single Deck", 1),
            ("2 Decks - Double Deck", 2),
            ("4 Decks - Small Shoe", 4),
            ("6 Decks - Standard Casino", 6),
            ("8 Decks - Large Shoe", 8)
        ]
        
        self.shoe_var = tk.StringVar(value=shoe_options[3][0])  # Default to 6 decks
        self.shoe_combo = ttk.Combobox(
            shoe_frame,
            textvariable=self.shoe_var,
            values=[option[0] for option in shoe_options],
            state="readonly",
            font=('Arial', 12),
            width=25
        )
        self.shoe_combo.pack(fill=tk.X, pady=(10, 0))
        self.shoe_combo.bind('<<ComboboxSelected>>', self._on_shoe_change)
        
        # Custom bankroll entry (hidden by default)
        self.custom_frame = ttk.Frame(options_frame)
        self.custom_var = tk.StringVar(value="1000")
        self.custom_entry = ttk.Entry(
            self.custom_frame,
            textvariable=self.custom_var,
            font=('Arial', 12),
            width=20
        )
        ttk.Label(self.custom_frame, text="Custom Amount ($):").pack(anchor=tk.W)
        self.custom_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Game rules info
        rules_frame = ttk.LabelFrame(options_frame, text="Game Rules", padding=10)
        rules_frame.pack(fill=tk.X, pady=(20, 0))
        
        rules_text = """
• Dealer hits soft 17
• Blackjack pays 3:2
• Double after split allowed
• Surrender available
• Hi-Lo card counting system
• Real-time strategy recommendations
• ~75% penetration before shuffle
        """
        
        rules_label = tk.Label(
            rules_frame,
            text=rules_text,
            font=('Arial', 10),
            justify=tk.LEFT,
            fg='#ffffff',
            bg='#2c5530'
        )
        rules_label.pack(anchor=tk.W)
        
        # Start game button
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=1, sticky="ew", padx=20, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="START NEW GAME",
            command=self._start_game,
            style='Accent.TButton'
        )
        self.start_button.pack(fill=tk.X, pady=10)
        
        # Credits/info
        credits_label = tk.Label(
            self,
            text="Educational Project - Card counting may be prohibited in some casinos",
            font=('Arial', 8),
            fg='#666666'
        )
        credits_label.grid(row=5, column=1, pady=(0, 10))
    
    def _on_bankroll_change(self, event):
        """Handle bankroll selection change."""
        selected = self.bankroll_var.get()
        
        if "Custom Amount" in selected:
            # Show custom entry
            self.custom_frame.pack(fill=tk.X, pady=(10, 0))
            self.custom_entry.focus()
        else:
            # Hide custom entry
            self.custom_frame.pack_forget()
            
            # Extract amount from selection
            for option, amount in [
                ("$500 - Conservative", 500.0),
                ("$1,000 - Standard", 1000.0),
                ("$2,500 - Aggressive", 2500.0),
                ("$5,000 - High Roller", 5000.0)
            ]:
                if option in selected:
                    self.selected_bankroll = amount
                    break
    
    def _on_shoe_change(self, event):
        """Handle shoe size selection change."""
        selected = self.shoe_var.get()
        
        # Extract number of decks from selection
        for option, decks in [
            ("1 Deck - Single Deck", 1),
            ("2 Decks - Double Deck", 2),
            ("4 Decks - Small Shoe", 4),
            ("6 Decks - Standard Casino", 6),
            ("8 Decks - Large Shoe", 8)
        ]:
            if option in selected:
                self.selected_decks = decks
                break
    
    def _start_game(self):
        """Start the game with selected bankroll and shoe size."""
        # Get bankroll amount
        if "Custom Amount" in self.bankroll_var.get():
            try:
                amount = float(self.custom_var.get())
                if amount < 100:
                    tk.messagebox.showerror("Invalid Amount", "Minimum bankroll is $100")
                    return
                if amount > 10000:
                    tk.messagebox.showerror("Invalid Amount", "Maximum bankroll is $10,000")
                    return
                self.selected_bankroll = amount
            except ValueError:
                tk.messagebox.showerror("Invalid Amount", "Please enter a valid number")
                return
        
        # Start the game with both bankroll and number of decks
        self.on_start_game(self.selected_bankroll, self.selected_decks) 