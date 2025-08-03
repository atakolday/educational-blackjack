"""
Strategy display component for showing optimal actions and expected values.
"""

import tkinter as tk
from tkinter import ttk
import traceback
from typing import Optional, Dict, Any
from ...game.card import Card
from ...game.hand import Hand
from ...strategy.calculator import StrategyCalculator, Action


class StrategyDisplay(ttk.LabelFrame):
    """Component for displaying strategy recommendations."""
    
    def __init__(self, parent, strategy_calculator: StrategyCalculator):
        """
        Initialize the strategy display.
        
        Args:
            parent: Parent widget
            strategy_calculator: The strategy calculator
        """
        super().__init__(parent, text="Strategy", padding=10)
        self.strategy_calculator = strategy_calculator
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Optimal action
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.action_frame, text="Optimal Action:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.action_label = ttk.Label(self.action_frame, text="", font=('Arial', 14, 'bold'))
        self.action_label.pack(anchor=tk.W)
        
        # Expected value
        self.ev_frame = ttk.Frame(self)
        self.ev_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.ev_frame, text="Expected Value:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.ev_label = ttk.Label(self.ev_frame, text="", font=('Arial', 14))
        self.ev_label.pack(anchor=tk.W)
        
        # Basic strategy comparison
        self.basic_frame = ttk.Frame(self)
        self.basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.basic_frame, text="Basic Strategy:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.basic_label = ttk.Label(self.basic_frame, text="", font=('Arial', 14))
        self.basic_label.pack(anchor=tk.W)
        
        # EV difference
        self.diff_frame = ttk.Frame(self)
        self.diff_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.diff_frame, text="Count Advantage:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.diff_label = ttk.Label(self.diff_frame, text="", font=('Arial', 14))
        self.diff_label.pack(anchor=tk.W)
        
        # Player bust probability
        self.player_bust_frame = ttk.Frame(self)
        self.player_bust_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.player_bust_frame, text="Player Bust:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.player_bust_label = ttk.Label(self.player_bust_frame, text="", font=('Arial', 14))
        self.player_bust_label.pack(anchor=tk.W)
        
        # Dealer bust probability
        self.dealer_bust_frame = ttk.Frame(self)
        self.dealer_bust_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.dealer_bust_frame, text="Dealer Bust:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        self.dealer_bust_label = ttk.Label(self.dealer_bust_frame, text="", font=('Arial', 14))
        self.dealer_bust_label.pack(anchor=tk.W)
        
        # Insurance recommendation (hidden by default)
        self.insurance_frame = ttk.Frame(self)
        self.insurance_label = ttk.Label(self.insurance_frame, text="", font=('Arial', 14))
        self.insurance_label.pack(anchor=tk.W)
    
    def update_strategy(self, player_hand: Hand, dealer_up_card: Card, dealer_hand: Hand = None):
        """
        Update the strategy display.
        
        Args:
            player_hand: The player's current hand
            dealer_up_card: The dealer's up card
            dealer_hand: The dealer's full hand (optional, for bust probability calculation)
        """
        try:
            # Get strategy comparison
            strategy = self.strategy_calculator.get_strategy_comparison(player_hand, dealer_up_card)
            
            # Update optimal action
            optimal_action = strategy['optimal_action'].value.upper()
            self.action_label.config(text=optimal_action)
            
            # Color code the action
            if optimal_action in ['HIT', 'STAND']:
                self.action_label.config(foreground='#90D5FF')
            elif optimal_action in ['DOUBLE', 'SPLIT']:
                self.action_label.config(foreground='#03C40A')
            elif optimal_action == 'SURRENDER':
                self.action_label.config(foreground='#FF6B6B')
            else:
                self.action_label.config(foreground='#000000')
            
            # Update expected value
            optimal_ev = strategy['optimal_ev']
            self.ev_label.config(text=f"{optimal_ev:.3f}")
            
            # Color code EV
            if optimal_ev > 0:
                self.ev_label.config(foreground='#03C40A')
            elif optimal_ev < 0:
                self.ev_label.config(foreground='#FF6B6B')
            else:
                self.ev_label.config(foreground='#000000')
            
            # Update basic strategy
            basic_action = strategy['basic_action'].value.upper()
            basic_ev = strategy['basic_ev']
            self.basic_label.config(text=f"{basic_action} ({basic_ev:.3f})")
            
            # Update count advantage
            ev_difference = strategy['ev_difference']
            count_advantage = strategy['count_advantage']
            
            if count_advantage:
                self.diff_label.config(text=f"+{ev_difference:.3f} EV", foreground='#03C40A')
            else:
                self.diff_label.config(text=f"{ev_difference:.3f} EV", foreground='#FF6B6B')
            
            # Update player bust probability
            try:
                player_bust_prob = self.strategy_calculator.get_bust_probability(player_hand.total, 'player')
                player_bust_percentage = player_bust_prob * 100
                self.player_bust_label.config(text=f"{player_bust_percentage:.1f}%")
                
                # Color code player bust probability
                if player_bust_prob < 0.3:
                    self.player_bust_label.config(foreground='#03C40A')
                elif player_bust_prob < 0.5:
                    self.player_bust_label.config(foreground='#E89149')
                else:
                    self.player_bust_label.config(foreground='#FF6B6B')
            except Exception as e:
                print("ERROR: Bust probability calculation failed")
                print(f'{e}: {traceback.format_exc()}')
                self.player_bust_label.config(text="Error", foreground='#FF6B6B')
            
            # Update dealer bust probability
            try:
                if dealer_hand:
                    # Calculate dealer's current total (excluding hidden card)
                    dealer_visible_total = sum(card.get_soft_value() for card in dealer_hand.cards[1:])
                    dealer_aces = sum(1 for card in dealer_hand.cards[1:] if card.is_ace)
                    for _ in range(dealer_aces):
                        if dealer_visible_total + 10 <= 21:
                            dealer_visible_total += 10
                    
                    dealer_bust_prob = self.strategy_calculator.get_bust_probability(dealer_visible_total, 'dealer')
                    dealer_bust_percentage = dealer_bust_prob * 100
                    self.dealer_bust_label.config(text=f"{dealer_bust_percentage:.1f}%")
                else:
                    # Fallback to just the up card
                    dealer_bust_prob = self.strategy_calculator.get_bust_probability(dealer_up_card.value, 'dealer')
                    dealer_bust_percentage = dealer_bust_prob * 100
                    self.dealer_bust_label.config(text=f"{dealer_bust_percentage:.1f}%")
                
                # Color code dealer bust probability
                if dealer_bust_prob < 0.3:
                    self.dealer_bust_label.config(foreground='#03C40A')
                elif dealer_bust_prob < 0.5:
                    self.dealer_bust_label.config(foreground='#E89149')
                else:
                    self.dealer_bust_label.config(foreground='#FF6B6B')
            except Exception as e:
                self.dealer_bust_label.config(text="Error", foreground='#FF6B6B')
            
            # Show the insurance frame if needed
            self.insurance_frame.pack(fill=tk.X, pady=(0, 10))
            
        except Exception as e:
            # Handle any errors in strategy calculation
            self.action_label.config(text="Error", foreground='#FF6B6B')
            self.ev_label.config(text="")   
            self.basic_label.config(text="")
            self.diff_label.config(text="")
    
    def update_insurance_recommendation(self):
        """Update the insurance recommendation display."""
        try:
            insurance = self.strategy_calculator.get_insurance_recommendation()
            
            if insurance['should_take_insurance']:
                self.insurance_label.config(
                    text=f"Take Insurance (+{insurance['insurance_ev']:.3f} EV)",
                    foreground='#03C40A'
                )
            else:
                self.insurance_label.config(
                    text=f"Decline Insurance ({insurance['insurance_ev']:.3f} EV)",
                    foreground='#FF6B6B'
                )
            
            # Show the insurance frame
            self.insurance_frame.pack(fill=tk.X, pady=(0, 10))
            
        except Exception as e:
            self.insurance_label.config(text="Insurance: Error", foreground='#FF6B6B')
    
    def clear_strategy(self):
        """Clear the strategy display."""
        self.action_label.config(text="")
        self.ev_label.config(text="")
        self.basic_label.config(text="")
        self.diff_label.config(text="")
        self.player_bust_label.config(text="")
        self.dealer_bust_label.config(text="")
        self.insurance_label.config(text="")
        
        # Hide insurance frame
        self.insurance_frame.pack_forget() 