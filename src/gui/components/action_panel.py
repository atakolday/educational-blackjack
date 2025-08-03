"""
Action panel component for game actions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from ...game.game import BlackjackGame, GameState


class ActionPanel(ttk.LabelFrame):
    """Component for game actions."""
    
    def __init__(self, parent):
        """
        Initialize the action panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="Actions", padding=10)
        
        # Callbacks
        self.on_hit: Optional[Callable[[], None]] = None
        self.on_stand: Optional[Callable[[], None]] = None
        self.on_double: Optional[Callable[[], None]] = None
        self.on_split: Optional[Callable[[], None]] = None
        self.on_surrender: Optional[Callable[[], None]] = None
        self.on_insurance: Optional[Callable[[float], None]] = None
        self.on_decline_insurance: Optional[Callable[[], None]] = None
        self.on_new_hand: Optional[Callable[[], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Main action buttons
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill=tk.BOTH, expand=True)
        
        # Hit button
        self.hit_btn = ttk.Button(
            self.action_frame,
            text="Hit",
            command=self._on_hit,
            style='Action.TButton'
        )
        self.hit_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Stand button
        self.stand_btn = ttk.Button(
            self.action_frame,
            text="Stand",
            command=self._on_stand,
            style='Action.TButton'
        )
        self.stand_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Double button
        self.double_btn = ttk.Button(
            self.action_frame,
            text="Double",
            command=self._on_double,
            style='Action.TButton'
        )
        self.double_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Split button
        self.split_btn = ttk.Button(
            self.action_frame,
            text="Split",
            command=self._on_split,
            style='Action.TButton'
        )
        self.split_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Surrender button
        self.surrender_btn = ttk.Button(
            self.action_frame,
            text="Surrender",
            command=self._on_surrender,
            style='Action.TButton'
        )
        self.surrender_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # New hand button
        self.new_hand_btn = ttk.Button(
            self.action_frame,
            text="New Hand",
            command=self._on_new_hand,
            style='Action.TButton'
        )
        self.new_hand_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        
        # Insurance frame (hidden by default)
        self.insurance_frame = ttk.Frame(self)
        self.insurance_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.insurance_frame, text="Insurance Available", font=('Arial', 10, 'bold')).pack()
        
        # Insurance amount entry
        self.insurance_var = tk.StringVar(value="0")
        self.insurance_entry = ttk.Entry(self.insurance_frame, textvariable=self.insurance_var, font=('Arial', 10))
        self.insurance_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Insurance buttons
        insurance_btn_frame = ttk.Frame(self.insurance_frame)
        insurance_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.insurance_btn = ttk.Button(
            insurance_btn_frame,
            text="Take Insurance",
            command=self._on_insurance,
            style='Action.TButton'
        )
        self.insurance_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.decline_insurance_btn = ttk.Button(
            insurance_btn_frame,
            text="Decline",
            command=self._on_decline_insurance,
            style='Action.TButton'
        )
        self.decline_insurance_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Hide insurance frame initially
        self.insurance_frame.pack_forget()
    
    def _on_hit(self):
        """Handle hit action."""
        if self.on_hit:
            self.on_hit()
    
    def _on_stand(self):
        """Handle stand action."""
        if self.on_stand:
            self.on_stand()
    
    def _on_double(self):
        """Handle double action."""
        if self.on_double:
            self.on_double()
    
    def _on_split(self):
        """Handle split action."""
        if self.on_split:
            self.on_split()
    
    def _on_surrender(self):
        """Handle surrender action."""
        if self.on_surrender:
            self.on_surrender()
    
    def _on_insurance(self):
        """Handle insurance action."""
        if self.on_insurance:
            try:
                amount = float(self.insurance_var.get())
                self.on_insurance(amount)
            except ValueError:
                # Invalid insurance amount
                pass
    
    def _on_decline_insurance(self):
        """Handle decline insurance action."""
        if self.on_decline_insurance:
            self.on_decline_insurance()
    
    def _on_new_hand(self):
        """Handle new hand action."""
        if self.on_new_hand:
            self.on_new_hand()
    
    def update_actions(self, game: BlackjackGame):
        """
        Update action buttons based on game state.
        
        Args:
            game: The current game state
        """
        # Hide insurance frame by default
        self.insurance_frame.pack_forget()
        
        if game.state == GameState.BETTING:
            # Disable all action buttons during betting
            self._disable_all_actions()
            self.new_hand_btn.config(state='normal')
            
        elif game.state == GameState.INSURANCE:
            # Show insurance options
            self._disable_all_actions()
            self.insurance_frame.pack(fill=tk.X, pady=(10, 0))
            
        elif game.state == GameState.PLAYER_TURN:
            # Enable appropriate actions based on current hand
            current_hand = game.get_current_hand()
            if not current_hand:
                self._disable_all_actions()
                return
            
            # Enable basic actions
            self.hit_btn.config(state='normal')
            self.stand_btn.config(state='normal')
            
            # Enable double if allowed
            if current_hand.can_double and game.current_bet <= game.player_bankroll:
                self.double_btn.config(state='normal')
            else:
                self.double_btn.config(state='disabled')
            
            # Enable split if allowed
            if current_hand.can_split and game.current_bet <= game.player_bankroll:
                self.split_btn.config(state='normal')
            else:
                self.split_btn.config(state='disabled')
            
            # Enable surrender if allowed
            if game.surrender_allowed and current_hand.num_cards == 2:
                self.surrender_btn.config(state='normal')
            else:
                self.surrender_btn.config(state='disabled')
            
            # Disable new hand button during play
            self.new_hand_btn.config(state='disabled')
            
        elif game.state == GameState.DEALER_TURN:
            # Disable all actions during dealer turn
            self._disable_all_actions()
            
        elif game.state == GameState.GAME_OVER:
            # Only allow new hand
            self._disable_all_actions()
            self.new_hand_btn.config(state='normal')
    
    def show_insurance_options(self, max_insurance: float):
        """
        Show insurance options.
        
        Args:
            max_insurance: Maximum insurance amount
        """
        self.insurance_var.set(str(max_insurance))
        self.insurance_frame.pack(fill=tk.X, pady=(10, 0))
    
    def _disable_all_actions(self):
        """Disable all action buttons."""
        self.hit_btn.config(state='disabled')
        self.stand_btn.config(state='disabled')
        self.double_btn.config(state='disabled')
        self.split_btn.config(state='disabled')
        self.surrender_btn.config(state='disabled')
        self.new_hand_btn.config(state='disabled') 