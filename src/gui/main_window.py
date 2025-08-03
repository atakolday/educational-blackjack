"""
Main GUI window for the Blackjack game.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import threading
import time
import os

from ..game.game import BlackjackGame, GameState, GameResult
from ..game.card import Card, Suit, Rank
from ..game.hand import Hand
from .components.card_display import CardDisplay
from .components.count_display import CountDisplay
from .components.strategy_display import StrategyDisplay
from .components.betting_panel import BettingPanel
from .components.action_panel import ActionPanel
from .components.game_status import GameStatus
from .start_screen import StartScreen


class BlackjackGUI:
    """Main GUI window for the Blackjack game."""
    
    def __init__(self, num_decks: int = 6, min_bet: float = 10.0, max_bet: float = 1000.0):
        """
        Initialize the GUI.
        
        Args:
            num_decks: Number of decks to use
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
        """
        self.num_decks = num_decks
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.game = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Blackjack with Card Counting")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c5530')  # Dark green background
        
        # Set window icon
        self._set_window_icon()
        
        # Initialize UI state
        self.current_screen = "start"
        self.game_components = {}
        
        # Show start screen
        self._show_start_screen()
    
    def _set_window_icon(self):
        """Set the window icon."""
        try:
            # Try to set icon from various possible locations
            icon_paths = [
                "src/gui/assets/icon.png",                 # Your PNG icon file (preferred)
                "src/gui/assets/BlackjackIconGreen.icns",  # Your specific icon file
                "src/gui/assets/icon.icns",                # Standard name
                "src/gui/assets/icon.ico",                 # Windows
                "assets/icon.png",                         # Fallback locations
                "assets/icon.icns",
                "assets/icon.ico"
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        if icon_path.endswith('.icns') or icon_path.endswith('.png'):
                            # For .icns and .png files, use iconphoto method
                            from PIL import Image, ImageTk
                            img = Image.open(icon_path)
                            photo = ImageTk.PhotoImage(img)
                            self.root.iconphoto(True, photo)
                            print(f"Icon loaded successfully from: {icon_path}")
                            break
                        else:
                            # For other formats, use iconbitmap
                            self.root.iconbitmap(icon_path)
                            print(f"Icon loaded successfully from: {icon_path}")
                            break
                    except Exception as icon_error:
                        print(f"Failed to load icon from {icon_path}: {icon_error}")
                        continue
        except Exception as e:
            print(f"Icon setting failed: {e}")
            # Icon setting failed, continue without icon
            pass
    
    def _create_components(self):
        """Create all GUI components."""
        # Create frames first
        self.left_frame = ttk.Frame(self.root)
        self.center_frame = ttk.Frame(self.root)
        self.right_frame = ttk.Frame(self.root)
        
        # Left panel - Count and Strategy
        self.count_display = CountDisplay(self.left_frame, self.game.card_counter)
        self.strategy_display = StrategyDisplay(self.left_frame, self.game.strategy_calculator)
        
        # Center panel - Game area
        self.game_status = GameStatus(self.center_frame)
        self.dealer_display = CardDisplay(self.center_frame, "Dealer")
        self.player_display = CardDisplay(self.center_frame, "Player")
        
        # Right panel - Betting and Actions
        self.betting_panel = BettingPanel(self.right_frame, self.min_bet, self.max_bet)
        self.action_panel = ActionPanel(self.right_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready to play", relief=tk.SUNKEN)
        
        # Menu button
        self.menu_button = ttk.Button(self.root, text="← Back to Menu", command=self._back_to_menu)
    
    def _layout_components(self):
        """Layout all components in the window."""
        # Left panel (Count and Strategy)
        self.left_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.count_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.strategy_display.pack(fill=tk.BOTH, expand=True)
        
        # Center panel (Game area)
        self.center_frame.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=1)
        
        self.game_status.pack(fill=tk.X, pady=(0, 10))
        self.dealer_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.player_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Right panel (Betting and Actions)
        self.right_frame.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        self.betting_panel.pack(fill=tk.X, pady=(0, 10))
        self.action_panel.pack(fill=tk.BOTH, expand=True)
        
        # Menu button
        self.menu_button.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # Status bar
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
    
    def _bind_events(self):
        """Bind events between components."""
        # Betting panel events
        self.betting_panel.set_bet_placed_callback(self._on_bet_placed)
        
        # Action panel events
        self.action_panel.on_hit = self._on_hit
        self.action_panel.on_stand = self._on_stand
        self.action_panel.on_double = self._on_double
        self.action_panel.on_split = self._on_split
        self.action_panel.on_surrender = self._on_surrender
        self.action_panel.on_insurance = self._on_insurance
        self.action_panel.on_decline_insurance = self._on_decline_insurance
        self.action_panel.on_new_hand = self._on_new_hand
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _back_to_menu(self):
        """Return to the start screen."""
        if messagebox.askyesno("Back to Menu", "Are you sure you want to return to the menu? Current game progress will be lost."):
            self._show_start_screen()
    
    def _show_start_screen(self):
        """Show the start screen."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create and show start screen
        self.start_screen = StartScreen(self.root, self._on_start_game)
        self.start_screen.pack(fill=tk.BOTH, expand=True)
    
    def _on_start_game(self, bankroll: float, num_decks: int):
        """Handle start game button click."""
        # Update number of decks based on selection
        self.num_decks = num_decks
        
        # Initialize game with selected bankroll and deck count
        self.game = BlackjackGame(self.num_decks, self.min_bet, self.max_bet)
        self.game.player_bankroll = bankroll
        
        # Switch to game screen
        self._show_game_screen()
    
    def _show_game_screen(self):
        """Show the main game screen."""
        # Clear start screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configure grid weights for game layout
        self.root.grid_rowconfigure(0, weight=1)  # Top section
        self.root.grid_rowconfigure(1, weight=2)  # Middle section (game area)
        self.root.grid_rowconfigure(2, weight=1)  # Bottom section
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)  # Game area
        self.root.grid_columnconfigure(2, weight=1)
        
        # Initialize game components
        self._create_components()
        self._layout_components()
        self._bind_events()
        
        # Update display
        self._update_display()
    
    def _on_bet_placed(self, amount: float):
        """Handle bet placement."""
        if self.game.place_bet(amount):
            self._update_display()
            if self.game.deal_initial_cards():
                self._update_display()
                self._check_insurance()
            else:
                messagebox.showerror("Error", "Failed to deal cards!")
        else:
            messagebox.showerror("Error", "Invalid bet amount!")
    
    def _on_hit(self):
        """Handle hit action."""
        if self.game.hit():
            self._update_display()
            if self.game.state == GameState.DEALER_TURN:
                self._play_dealer_hand()
        else:
            messagebox.showerror("Error", "Cannot hit!")
    
    def _on_stand(self):
        """Handle stand action."""
        if self.game.stand():
            self._update_display()
            if self.game.state == GameState.DEALER_TURN:
                self._play_dealer_hand()
        else:
            messagebox.showerror("Error", "Cannot stand!")
    
    def _on_double(self):
        """Handle double down action."""
        if self.game.double_down():
            self._update_display()
            if self.game.state == GameState.DEALER_TURN:
                self._play_dealer_hand()
        else:
            messagebox.showerror("Error", "Cannot double down!")
    
    def _on_split(self):
        """Handle split action."""
        if self.game.split():
            self._update_display()
        else:
            messagebox.showerror("Error", "Cannot split!")
    
    def _on_surrender(self):
        """Handle surrender action."""
        if self.game.surrender():
            self._update_display()
            if self.game.state == GameState.DEALER_TURN:
                self._play_dealer_hand()
        else:
            messagebox.showerror("Error", "Cannot surrender!")
    
    def _on_insurance(self, amount: float):
        """Handle insurance bet."""
        if self.game.place_insurance(amount):
            self._update_display()
            if self.game.state == GameState.GAME_OVER:
                self._show_results()
        else:
            messagebox.showerror("Error", "Invalid insurance amount!")
    
    def _on_decline_insurance(self):
        """Handle declining insurance."""
        if self.game.decline_insurance():
            self._update_display()
            if self.game.state == GameState.GAME_OVER:
                self._show_results()
        else:
            messagebox.showerror("Error", "Failed to decline insurance!")
    
    def _on_new_hand(self):
        """Handle starting a new hand."""
        self.game.start_new_hand()
        self._update_display()
    
    def _check_insurance(self):
        """Check if insurance is available."""
        if self.game.state == GameState.INSURANCE:
            max_insurance = self.game.current_bet / 2
            self.action_panel.show_insurance_options(max_insurance)
    
    def _play_dealer_hand(self):
        """Play out the dealer's hand with animation."""
        def dealer_play():
            self.root.after(1000, self.game.play_dealer_hand)
            self.root.after(1100, self._update_display)
            self.root.after(1200, self._show_results)
        
        threading.Thread(target=dealer_play, daemon=True).start()
    
    def _show_results(self):
        """Show game results."""
        results = self.game.determine_results()
        self.game.update_statistics(results)
        self._update_display()
        
        # Show results dialog
        result_text = "Game Results:\n\n"
        for i, (hand, result, payout) in enumerate(results):
            result_text += f"Hand {i+1}: {result.value.replace('_', ' ').title()}\n"
            if payout > 0:
                result_text += f"Payout: ${payout:.2f}\n"
            result_text += "\n"
        
        messagebox.showinfo("Game Results", result_text)
    
    def _update_display(self):
        """Update all display components."""
        # Update game status
        self.game_status.update_status(self.game)
        
        # Update dealer display
        self.dealer_display.update_hand(
            self.game.dealer_hand,
            hide_first=(self.game.state != GameState.GAME_OVER)
        )
        
        # Update player display
        if self.game.player_hands:
            self.player_display.update_hands(
                self.game.player_hands,
                self.game.current_hand_index
            )
        
        # Update count display
        self.count_display.update_count(self.game.card_counter)
        
        # Update strategy display
        if self.game.state == GameState.PLAYER_TURN:
            current_hand = self.game.get_current_hand()
            if current_hand and self.game.dealer_hand.cards:
                dealer_up = self.game.dealer_hand.cards[1]
                self.strategy_display.update_strategy(current_hand, dealer_up)
        else:
            self.strategy_display.clear_strategy()
        
        # Update betting panel
        self.betting_panel.update_bankroll(self.game.player_bankroll)
        
        # Update action panel
        self.action_panel.update_actions(self.game)
        
        # Update status bar
        status_text = f"State: {self.game.state.value.title()}"
        if self.game.current_bet > 0:
            status_text += f" | Bet: ${self.game.current_bet:.2f}"
        status_text += f" | Games: {self.game.games_played} | Win Rate: {self.game.get_win_rate():.1%}"
        self.status_bar.config(text=status_text)
    
    def _on_close(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup when the GUI is destroyed."""
        try:
            if hasattr(self, 'root') and self.root:
                self.root.destroy()
        except:
            pass  # Ignore errors during cleanup 