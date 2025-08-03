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
        super().__init__(parent, bg='#2c5530')
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
            font=('Arial', 48, 'bold'),
            fg='#ffffff',
            bg='#2c5530'
        )
        title_label.pack(pady=(20, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="with Card Counting & Statistical Strategy",
            font=('Arial', 18),
            fg='#cccccc',
            bg='#2c5530'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Card icon/logo
        card_icon = tk.Label(
            title_frame,
            text="🂠 ♠ ♥ ♦ ♣",
            font=('Arial', 32),
            fg='#ffffff',
            bg='#2c5530'
        )
        card_icon.pack(pady=(0, 20))
        
        # Game options frame with simple styling
        options_frame = tk.Frame(self, bg='#3a3a3a', relief='flat', bd=2)
        options_frame.grid(row=2, column=1, sticky="ew", padx=20, pady=20)
        
        # Title for the frame
        title_label = tk.Label(options_frame, text="Game Setup", font=('Arial', 18, 'bold'), 
                              fg='#ffffff', bg='#3a3a3a')
        title_label.pack(anchor=tk.W, padx=20, pady=(20, 20))
        
        # Content frame
        content_frame = tk.Frame(options_frame, bg='#3a3a3a')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Bankroll selection
        bankroll_frame = ttk.Frame(content_frame)
        bankroll_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(bankroll_frame, text="Starting Bankroll:", font=('Arial', 16, 'bold')).pack(anchor=tk.W)
        
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
            font=('Arial', 14),
            width=25
        )
        self.bankroll_combo.pack(fill=tk.X, pady=(10, 0))
        self.bankroll_combo.bind('<<ComboboxSelected>>', self._on_bankroll_change)
        
        # Shoe size selection
        shoe_frame = ttk.Frame(content_frame)
        shoe_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(shoe_frame, text="Shoe Size (Number of Decks):", font=('Arial', 16, 'bold')).pack(anchor=tk.W)
        
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
            font=('Arial', 14),
            width=25
        )
        self.shoe_combo.pack(fill=tk.X, pady=(10, 0))
        self.shoe_combo.bind('<<ComboboxSelected>>', self._on_shoe_change)
        
        # Custom bankroll entry (hidden by default)
        self.custom_frame = ttk.Frame(content_frame)
        self.custom_var = tk.StringVar(value="1000")
        self.custom_entry = ttk.Entry(
            self.custom_frame,
            textvariable=self.custom_var,
            font=('Arial', 14),
            width=20
        )
        ttk.Label(self.custom_frame, text="Custom Amount ($):", font=('Arial', 14)).pack(anchor=tk.W)
        self.custom_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Game rules info
        rules_frame = tk.Frame(content_frame, bg='#3a3a3a')
        rules_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Rules title
        rules_title = tk.Label(
            rules_frame,
            text="Game Rules",
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#3a3a3a'
        )
        rules_title.pack(anchor=tk.W, pady=(0, 20))
        
        rules_text = """  • Dealer hits soft 17
  • Blackjack pays 3:2
  • Double after split allowed
  • Surrender available
  • Hi-Lo card counting system
  • Real-time strategy recommendations
  • ~75% penetration before shuffle"""
        
        rules_label = tk.Label(
            rules_frame,
            text=rules_text,
            font=('Arial', 14),
            justify=tk.LEFT,
            fg='#ffffff',
            bg='#3a3a3a'
        )
        rules_label.pack(anchor=tk.W)
        
        # Start game button with rounded corners
        button_frame = tk.Frame(self, bg='#2c5530')
        button_frame.grid(row=3, column=1, sticky="ew", padx=20, pady=20)
        
        # Create rounded button canvas
        button_canvas = tk.Canvas(button_frame, bg='#2c5530', highlightthickness=0, height=50)
        button_canvas.pack(fill=tk.X, pady=10)
        
        # Draw rounded rectangle for button
        button_canvas.create_rounded_rectangle = lambda x1, y1, x2, y2, radius, **kwargs: button_canvas.create_polygon(
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
            smooth=True, **kwargs
        )
        
        # Function to redraw button with proper centering
        def redraw_button():
            canvas_width = button_canvas.winfo_width()
            if canvas_width > 1:  # Only draw if canvas has proper width
                button_width = min(canvas_width - 20, 400)  # Leave 10px margin on each side
                button_x = (canvas_width - button_width) // 2
                
                # Clear previous drawings
                button_canvas.delete("all")
                
                # Draw the rounded button background
                button_canvas.create_rounded_rectangle(button_x, 0, button_x + button_width, 50, 10, 
                                                     fill='#555555', outline='#777777', width=2)
                
                # Create button text centered in the button
                button_text = tk.Label(button_canvas, text="START NEW GAME", font=('Arial', 16, 'bold'), 
                                      fg='#ffffff', bg='#555555')
                button_canvas.create_window(button_x + button_width//2, 25, anchor=tk.CENTER, window=button_text)
                
                # Rebind events to the new button text
                button_text.bind('<Button-1>', lambda e: self._start_game())
                button_text.bind('<Enter>', on_enter)
                button_text.bind('<Leave>', on_leave)
        
        # Initial draw
        button_canvas.after(10, redraw_button)
        
        # Bind canvas resize to redraw
        button_canvas.bind('<Configure>', lambda e: redraw_button())
        
        # Bind click events
        button_canvas.bind('<Button-1>', lambda e: self._start_game())
        
        # Hover effects
        def on_enter(e):
            canvas_width = button_canvas.winfo_width()
            if canvas_width > 1:
                button_width = min(canvas_width - 20, 400)
                button_x = (canvas_width - button_width) // 2
                button_canvas.delete("all")
                button_canvas.create_rounded_rectangle(button_x, 0, button_x + button_width, 50, 10, 
                                                     fill='#666666', outline='#888888', width=2)
                # Recreate text with new background
                button_text = tk.Label(button_canvas, text="START NEW GAME", font=('Arial', 16, 'bold'), 
                                      fg='#ffffff', bg='#666666')
                button_canvas.create_window(button_x + button_width//2, 25, anchor=tk.CENTER, window=button_text)
                button_text.bind('<Button-1>', lambda e: self._start_game())
                button_text.bind('<Enter>', on_enter)
                button_text.bind('<Leave>', on_leave)
            
        def on_leave(e):
            canvas_width = button_canvas.winfo_width()
            if canvas_width > 1:
                button_width = min(canvas_width - 20, 400)
                button_x = (canvas_width - button_width) // 2
                button_canvas.delete("all")
                button_canvas.create_rounded_rectangle(button_x, 0, button_x + button_width, 50, 10, 
                                                     fill='#555555', outline='#777777', width=2)
                # Recreate text with new background
                button_text = tk.Label(button_canvas, text="START NEW GAME", font=('Arial', 16, 'bold'), 
                                      fg='#ffffff', bg='#555555')
                button_canvas.create_window(button_x + button_width//2, 25, anchor=tk.CENTER, window=button_text)
                button_text.bind('<Button-1>', lambda e: self._start_game())
                button_text.bind('<Enter>', on_enter)
                button_text.bind('<Leave>', on_leave)
            
        button_canvas.bind('<Enter>', on_enter)
        button_canvas.bind('<Leave>', on_leave)
        
        # Credits/info
        credits_label = tk.Label(
            self,
            text="Educational Project - Card counting may be prohibited in some casinos | © Ata Kolday | GitHub: @atakolday",
            font=('Arial', 12),
            fg='#ffffff',
            bg='#2c5530'
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