"""
Count display component for showing card counting information.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from ...counting.counter import CardCounter


class CountDisplay(ttk.LabelFrame):
    """Component for displaying card counting information."""
    
    def __init__(self, parent, card_counter: CardCounter):
        """
        Initialize the count display.
        
        Args:
            parent: Parent widget
            card_counter: The card counter to display
        """
        super().__init__(parent, text="Card Count", padding=(10, 20))
        self.card_counter = card_counter
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Running count
        self.running_frame = ttk.Frame(self)
        self.running_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.running_frame, text="Running Count:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.running_label = ttk.Label(self.running_frame, text="0", font=('Arial', 16, 'bold'))
        self.running_label.pack(anchor=tk.W)
        
        # True count
        self.true_frame = ttk.Frame(self)
        self.true_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.true_frame, text="True Count:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.true_label = ttk.Label(self.true_frame, text="0.00", font=('Arial', 16, 'bold'))
        self.true_label.pack(anchor=tk.W)
        
        # Count status
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.status_frame, text="Status:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.status_label = ttk.Label(self.status_frame, text="Neutral", font=('Arial', 14))
        self.status_label.pack(anchor=tk.W)
        
        # Decks remaining
        self.decks_frame = ttk.Frame(self)
        self.decks_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.decks_frame, text="Decks Remaining:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.decks_label = ttk.Label(self.decks_frame, text="6.00", font=('Arial', 14))
        self.decks_label.pack(anchor=tk.W)
        
        # Penetration
        self.penetration_frame = ttk.Frame(self)
        self.penetration_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.penetration_frame, text="Penetration:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.penetration_label = ttk.Label(self.penetration_frame, text="0.0%", font=('Arial', 14))
        self.penetration_label.pack(anchor=tk.W)
        
        # Betting multiplier
        self.betting_frame = ttk.Frame(self)
        self.betting_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.betting_frame, text="Bet Multiplier:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.betting_label = ttk.Label(self.betting_frame, text="1.0x", font=('Arial', 14))
        self.betting_label.pack(anchor=tk.W)
    
    def update_count(self, card_counter: CardCounter):
        """
        Update the count display.
        
        Args:
            card_counter: The updated card counter
        """
        self.card_counter = card_counter
        
        # Update running count
        running_count = card_counter.running_count
        self.running_label.config(text=str(running_count))
        
        # Color code running count
        if running_count > 0:
            self.running_label.config(foreground='#03C40A')
        elif running_count < 0:
            self.running_label.config(foreground='#FF6B6B')
        else:
            self.running_label.config(foreground='#000000')
        
        # Update true count
        true_count = card_counter.true_count
        self.true_label.config(text=f"{true_count:.2f}")
        
        # Color code true count
        if true_count > 0:
            self.true_label.config(foreground='#03C40A')
        elif true_count < 0:
            self.true_label.config(foreground='#FF6B6B')
        else:
            self.true_label.config(foreground='#000000')
        
        # Update status
        status = card_counter.get_count_status()
        self.status_label.config(text=status)
        
        # Color code status
        if "Favorable" in status:
            self.status_label.config(foreground='#03C40A')
        elif "Unfavorable" in status:
            self.status_label.config(foreground='#FF6B6B')
        else:
            self.status_label.config(foreground='#000000')
        
        # Update decks remaining
        decks_remaining = card_counter.decks_remaining
        self.decks_label.config(text=f"{decks_remaining:.2f}")
        
        # Update penetration
        penetration = card_counter.penetration * 100
        self.penetration_label.config(text=f"{penetration:.1f}%")
        
        # Update betting multiplier
        multiplier = card_counter.get_betting_multiplier()
        self.betting_label.config(text=f"{multiplier:.1f}x")
        
        # Color code betting multiplier
        if multiplier > 1.0:
            self.betting_label.config(foreground='#03C40A')
        else:
            self.betting_label.config(foreground='#000000') 