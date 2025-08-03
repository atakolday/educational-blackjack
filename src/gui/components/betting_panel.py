"""
Betting panel component for placing bets and managing bankroll.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class BettingPanel(ttk.LabelFrame):
    """Component for betting interface."""
    
    def __init__(self, parent, min_bet: int, max_bet: int, initial_bankroll: int = 1000):
        """
        Initialize the betting panel.
        
        Args:
            parent: Parent widget
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
            initial_bankroll: Initial bankroll amount
        """
        super().__init__(parent, text="Betting", padding=(10, 20))
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.current_bankroll = initial_bankroll
        self.on_bet_placed: Optional[Callable[[int], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Bankroll display
        self.bankroll_frame = ttk.Frame(self)
        self.bankroll_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.bankroll_frame, text="Bankroll:", font=('Arial', 14, 'bold'),).pack(anchor=tk.W)
        self.bankroll_label = ttk.Label(self.bankroll_frame, text=f"${format(self.current_bankroll, ',')}", font=('Arial', 14, 'bold'), foreground='#ffffff')   
        self.bankroll_label.pack(anchor=tk.W)
        
        # Bet amount entry
        self.bet_frame = ttk.Frame(self)
        self.bet_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.bet_frame, text="Bet Amount:", font=('Arial', 14, 'bold')).pack(anchor=tk.W)
        
        self.bet_var = tk.StringVar(value=str(self.min_bet))  # Start with minimum bet
        self.bet_entry = ttk.Entry(self.bet_frame, textvariable=self.bet_var, font=('Arial', 12))
        self.bet_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Quick bet buttons (circular chips)
        self.quick_bet_frame = ttk.Frame(self)
        self.quick_bet_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Common bet amounts with chip colors
        bet_amounts = [10, 25, 50, 100, 250, 500]
        chip_colors = {
            10: "#FF6B6B",    # Red
            25: "#4ECDC4",    # Teal
            50: "#45B7D1",    # Blue
            100: "#96CEB4",   # Green
            250: "#FFEAA7",   # Yellow
            500: "#DDA0DD"    # Purple
        }
        
        self.chip_buttons = []
        for i, amount in enumerate(bet_amounts):
            if amount <= self.max_bet:
                # Create canvas for circular chip
                chip_canvas = tk.Canvas(
                    self.quick_bet_frame,
                    width=80,
                    height=80,
                    highlightthickness=0,
                    bg='#3a3a3a'  # Dark gray background to match ttk theme
                )
                chip_canvas.grid(row=i//3, column=i%3, padx=5, pady=5)
                
                # Draw circular chip
                chip_color = chip_colors.get(amount, "#CCCCCC")
                chip_canvas.create_oval(5, 5, 75, 75, fill=chip_color, outline="#333333", width=2)
                
                # Add inner circle for 3D effect
                chip_canvas.create_oval(10, 10, 70, 70, fill=chip_color, outline="#666666", width=1)
                
                # Add text with darker color for better visibility
                chip_canvas.create_text(40, 40, text=f"${amount}", font=('Arial', 12, 'bold'), fill='#333333')
                
                # Store canvas and amount for click handling
                chip_canvas.amount = amount
                chip_canvas.color = chip_color
                
                # Bind click events
                chip_canvas.bind('<Button-1>', lambda e, a=amount: self._add_to_bet_amount(a))
                chip_canvas.bind('<Enter>', lambda e, canvas=chip_canvas: self._on_chip_hover_enter(canvas))
                chip_canvas.bind('<Leave>', lambda e, canvas=chip_canvas: self._on_chip_hover_leave(canvas))
                
                self.chip_buttons.append(chip_canvas)
        
        # Configure grid weights
        for i in range(3):
            self.quick_bet_frame.grid_columnconfigure(i, weight=1)
        
        # Bet action buttons frame
        self.bet_actions_frame = ttk.Frame(self)
        self.bet_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Place bet button
        self.place_bet_btn = ttk.Button(
            self.bet_actions_frame,
            text="Place Bet",
            command=self._place_bet,
            style='Accent.TButton'
        )
        self.place_bet_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Clear bet button
        self.clear_bet_btn = ttk.Button(
            self.bet_actions_frame,
            text="Clear Bet",
            command=self._clear_bet,
            style='Secondary.TButton'
        )
        self.clear_bet_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Configure grid weights for the actions frame
        self.bet_actions_frame.grid_columnconfigure(0, weight=1)
        self.bet_actions_frame.grid_columnconfigure(1, weight=1)
        
        # Initialize clear button state
        self._update_clear_button_state()
    
    def _set_bet_amount(self, amount: int):
        """Set the bet amount in the entry field."""
        self.bet_var.set(str(amount))
        self._update_clear_button_state()
    
    def _add_to_bet_amount(self, amount: int):
        """Add to the current bet amount in the entry field."""
        try:
            current_bet = int(self.bet_var.get())
            new_bet = current_bet + amount
            # Check if new bet exceeds bankroll
            if new_bet <= self.current_bankroll:
                self.bet_var.set(str(new_bet))
            else:
                # Could add a warning message here
                pass
        except ValueError:
            # If current bet is invalid, just set to the chip amount
            self.bet_var.set(str(amount))
        self._update_clear_button_state()
    
    def _clear_bet(self):
        """Clear the bet amount to 0."""
        self.bet_var.set("0")
        self._update_clear_button_state()
    
    def _update_clear_button_state(self):
        """Update the clear bet button state based on current bet amount."""
        try:
            current_bet = int(self.bet_var.get())
            if current_bet > 0:
                self.clear_bet_btn.config(state='normal')
            else:
                self.clear_bet_btn.config(state='disabled')
        except ValueError:
            self.clear_bet_btn.config(state='disabled')
    
    def _on_chip_hover_enter(self, canvas):
        """Handle chip hover enter event."""
        # Redraw chip with brighter color and glow effect (no size change)
        canvas.delete("all")
        brighter_color = self._brighten_color(canvas.color)
        
        # Add glow effect (outer circle with lighter color)
        canvas.create_oval(3, 3, 77, 77, fill=brighter_color, outline="#666666", width=1)
        # Main chip
        canvas.create_oval(5, 5, 75, 75, fill=brighter_color, outline="#333333", width=2)
        # Inner circle for 3D effect
        canvas.create_oval(10, 10, 70, 70, fill=brighter_color, outline="#666666", width=1)
        # Text
        canvas.create_text(40, 40, text=f"${canvas.amount}", font=('Arial', 12, 'bold'), fill='#333333')
    
    def _on_chip_hover_leave(self, canvas):
        """Handle chip hover leave event."""
        # Redraw chip with original color (no size change)
        canvas.delete("all")
        # Main chip
        canvas.create_oval(5, 5, 75, 75, fill=canvas.color, outline="#333333", width=2)
        # Inner circle for 3D effect
        canvas.create_oval(10, 10, 70, 70, fill=canvas.color, outline="#666666", width=1)
        # Text
        canvas.create_text(40, 40, text=f"${canvas.amount}", font=('Arial', 12, 'bold'), fill='#333333')
    
    def _brighten_color(self, color):
        """Brighten a hex color for hover effect."""
        # Convert hex to RGB, brighten, then back to hex
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _place_bet(self):
        """Place the bet."""
        try:
            amount = int(self.bet_var.get())
            if self.on_bet_placed:
                self.on_bet_placed(amount)
        except ValueError:
            # Invalid bet amount
            pass
    
    def update_bankroll(self, bankroll: int):
        """
        Update the bankroll display.
        
        Args:
            bankroll: Current bankroll amount
        """
        self.current_bankroll = bankroll
        self.bankroll_label.config(text=f"${format(bankroll, ',')}")
        
        # Color code bankroll
        if bankroll > 1000:
            self.bankroll_label.config(foreground='#03C40A')
        elif bankroll < 500:
            self.bankroll_label.config(foreground='#FF6B6B')
        else:
            self.bankroll_label.config(foreground='#FFFFFF')
    
    def set_bet_placed_callback(self, callback: Callable[[int], None]):
        """
        Set the callback for when a bet is placed.
        
        Args:
            callback: Function to call when bet is placed
        """
        self.on_bet_placed = callback
    
    def disable_betting(self):
        """Disable betting controls."""
        self.bet_entry.config(state='disabled')
        self.place_bet_btn.config(state='disabled')
        
        # Disable chip buttons by making them gray
        for chip_canvas in self.chip_buttons:
            chip_canvas.delete("all")
            chip_canvas.create_oval(5, 5, 75, 75, fill="#CCCCCC", outline="#999999", width=2)
            chip_canvas.create_oval(10, 10, 70, 70, fill="#CCCCCC", outline="#999999", width=1)
            chip_canvas.create_text(40, 40, text=f"${chip_canvas.amount}", font=('Arial', 12, 'bold'), fill='#666666')
            # Unbind events
            chip_canvas.unbind('<Button-1>')
            chip_canvas.unbind('<Enter>')
            chip_canvas.unbind('<Leave>')
        
        # Disable clear bet button
        self.clear_bet_btn.config(state='disabled')
    
    def enable_betting(self):
        """Enable betting controls."""
        self.bet_entry.config(state='normal')
        self.place_bet_btn.config(state='normal')
        
        # Re-enable chip buttons by restoring their colors and events
        for chip_canvas in self.chip_buttons:
            chip_canvas.delete("all")
            chip_canvas.create_oval(5, 5, 75, 75, fill=chip_canvas.color, outline="#333333", width=2)
            chip_canvas.create_oval(10, 10, 70, 70, fill=chip_canvas.color, outline="#666666", width=1)
            chip_canvas.create_text(40, 40, text=f"${chip_canvas.amount}", font=('Arial', 12, 'bold'), fill='#333333')
            # Re-bind events
            chip_canvas.bind('<Button-1>', lambda e, a=chip_canvas.amount: self._add_to_bet_amount(a))
            chip_canvas.bind('<Enter>', lambda e, canvas=chip_canvas: self._on_chip_hover_enter(canvas))
            chip_canvas.bind('<Leave>', lambda e, canvas=chip_canvas: self._on_chip_hover_leave(canvas))
        
        # Update clear bet button state
        self._update_clear_button_state() 