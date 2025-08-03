"""
Betting panel component for placing bets and managing bankroll.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class BettingPanel(ttk.LabelFrame):
    """Component for betting interface."""
    
    def __init__(self, parent, min_bet: float, max_bet: float):
        """
        Initialize the betting panel.
        
        Args:
            parent: Parent widget
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
        """
        super().__init__(parent, text="Betting", padding=10)
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.on_bet_placed: Optional[Callable[[float], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Bankroll display
        self.bankroll_frame = ttk.Frame(self)
        self.bankroll_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.bankroll_frame, text="Bankroll:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.bankroll_label = ttk.Label(self.bankroll_frame, text="$1000.00", font=('Arial', 14, 'bold'))
        self.bankroll_label.pack(anchor=tk.W)
        
        # Bet amount entry
        self.bet_frame = ttk.Frame(self)
        self.bet_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.bet_frame, text="Bet Amount:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.bet_var = tk.StringVar(value=str(self.min_bet))
        self.bet_entry = ttk.Entry(self.bet_frame, textvariable=self.bet_var, font=('Arial', 12))
        self.bet_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Quick bet buttons
        self.quick_bet_frame = ttk.Frame(self)
        self.quick_bet_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Common bet amounts
        bet_amounts = [10, 25, 50, 100, 250, 500]
        for i, amount in enumerate(bet_amounts):
            if amount <= self.max_bet:
                btn = ttk.Button(
                    self.quick_bet_frame,
                    text=f"${amount}",
                    command=lambda a=amount: self._set_bet_amount(a)
                )
                btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            self.quick_bet_frame.grid_columnconfigure(i, weight=1)
        
        # Place bet button
        self.place_bet_btn = ttk.Button(
            self,
            text="Place Bet",
            command=self._place_bet,
            style='Accent.TButton'
        )
        self.place_bet_btn.pack(fill=tk.X, pady=(10, 0))
    
    def _set_bet_amount(self, amount: float):
        """Set the bet amount in the entry field."""
        self.bet_var.set(str(amount))
    
    def _place_bet(self):
        """Place the bet."""
        try:
            amount = float(self.bet_var.get())
            if self.on_bet_placed:
                self.on_bet_placed(amount)
        except ValueError:
            # Invalid bet amount
            pass
    
    def update_bankroll(self, bankroll: float):
        """
        Update the bankroll display.
        
        Args:
            bankroll: Current bankroll amount
        """
        self.bankroll_label.config(text=f"${bankroll:.2f}")
        
        # Color code bankroll
        if bankroll > 1000:
            self.bankroll_label.config(foreground='green')
        elif bankroll < 500:
            self.bankroll_label.config(foreground='red')
        else:
            self.bankroll_label.config(foreground='black')
    
    def set_bet_placed_callback(self, callback: Callable[[float], None]):
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
        
        # Disable quick bet buttons
        for child in self.quick_bet_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state='disabled')
    
    def enable_betting(self):
        """Enable betting controls."""
        self.bet_entry.config(state='normal')
        self.place_bet_btn.config(state='normal')
        
        # Enable quick bet buttons
        for child in self.quick_bet_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state='normal') 