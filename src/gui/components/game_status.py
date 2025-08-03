"""
Game status component for displaying current game information.
"""

import tkinter as tk
from tkinter import ttk
from ...game.game import BlackjackGame, GameState


class GameStatus(ttk.Frame):
    """Component for displaying game status information."""
    
    def __init__(self, parent):
        """
        Initialize the game status component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Main status frame
        self.status_frame = ttk.LabelFrame(self, text="Game Status", padding=10)
        self.status_frame.pack(fill=tk.X)
        
        # Game state
        self.state_frame = ttk.Frame(self.status_frame)
        self.state_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.state_frame, text="State:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.state_label = ttk.Label(self.state_frame, text="Betting", font=('Arial', 12))
        self.state_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Current bet
        self.bet_frame = ttk.Frame(self.status_frame)
        self.bet_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.bet_frame, text="Current Bet:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.bet_label = ttk.Label(self.bet_frame, text="$0.00", font=('Arial', 12))
        self.bet_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Games played
        self.games_frame = ttk.Frame(self.status_frame)
        self.games_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.games_frame, text="Games Played:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.games_label = ttk.Label(self.games_frame, text="0", font=('Arial', 12))
        self.games_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Win rate
        self.winrate_frame = ttk.Frame(self.status_frame)
        self.winrate_frame.pack(fill=tk.X)
        
        ttk.Label(self.winrate_frame, text="Win Rate:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.winrate_label = ttk.Label(self.winrate_frame, text="0.0%", font=('Arial', 12))
        self.winrate_label.pack(side=tk.LEFT, padx=(5, 0))
    
    def update_status(self, game: BlackjackGame):
        """
        Update the game status display.
        
        Args:
            game: The current game state
        """
        # Update game state
        state_text = game.state.value.replace('_', ' ').title()
        self.state_label.config(text=state_text)
        
        # Color code the state
        if game.state == GameState.BETTING:
            self.state_label.config(foreground='blue')
        elif game.state == GameState.PLAYER_TURN:
            self.state_label.config(foreground='green')
        elif game.state == GameState.DEALER_TURN:
            self.state_label.config(foreground='orange')
        elif game.state == GameState.GAME_OVER:
            self.state_label.config(foreground='red')
        else:
            self.state_label.config(foreground='black')
        
        # Update current bet
        if game.current_bet > 0:
            self.bet_label.config(text=f"${game.current_bet:.2f}")
        else:
            self.bet_label.config(text="$0.00")
        
        # Update games played
        self.games_label.config(text=str(game.games_played))
        
        # Update win rate
        win_rate = game.get_win_rate()
        self.winrate_label.config(text=f"{win_rate:.1%}")
        
        # Color code win rate
        if win_rate > 0.5:
            self.winrate_label.config(foreground='green')
        elif win_rate < 0.4:
            self.winrate_label.config(foreground='red')
        else:
            self.winrate_label.config(foreground='black') 