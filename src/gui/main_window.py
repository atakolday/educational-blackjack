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
from ..utils.utils import draw_rounded_rect

class BlackjackGUI:
    """Main GUI window for the Blackjack game."""
    
    def __init__(self, num_decks: int = 6, min_bet: int = 10, max_bet: int = 1000):
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
        self.root.geometry("1600x1200")
        self.root.configure(bg='#2c5530')  # Dark green background

        # Set up ttk style
        self.style = ttk.Style()
        
        # Configure custom styles for the application
        self.style.configure("TLabelframe", 
                           background="#3a3a3a", 
                           bordercolor="#555555",
                           lightcolor="#555555",
                           darkcolor="#555555")
        
        self.style.configure("TLabelframe.Label", 
                           background="#3a3a3a", 
                           foreground="white",
                           font=('Arial', 16, 'bold'))
        
        self.style.configure("TFrame", 
                           background="#3a3a3a")
        
        self.style.configure("TLabel", 
                           background="#3a3a3a", 
                           foreground="white")
        
        self.style.configure("TButton", 
                           background="#555555", 
                           foreground="white",
                           bordercolor="#777777",
                           lightcolor="#777777",
                           darkcolor="#333333")
        
        self.style.configure("Accent.TButton", 
                           background="#4CAF50", 
                           foreground="white",
                           bordercolor="#45a049",
                           lightcolor="#45a049",
                           darkcolor="#3d8b40")
        
        self.style.configure("Secondary.TButton", 
                           background="#f44336", 
                           foreground="white",
                           bordercolor="#da190b",
                           lightcolor="#da190b",
                           darkcolor="#c62828")
        
        # Map styles for different states
        self.style.map("TButton",
                      background=[('active', '#666666'), ('pressed', '#444444')],
                      foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')])
        
        self.style.map("Accent.TButton",
                      background=[('active', '#45a049'), ('pressed', '#3d8b40')],
                      foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')])
        
        self.style.map("Secondary.TButton",
                      background=[('active', '#da190b'), ('pressed', '#c62828')],
                      foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')])
        
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
                            break
                        else:
                            # For other formats, use iconbitmap
                            self.root.iconbitmap(icon_path)
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
        self.betting_panel = BettingPanel(self.right_frame, self.min_bet, self.max_bet, self.game.player_bankroll)
        self.action_panel = ActionPanel(self.right_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready to play", relief=tk.SUNKEN)
    
    def _layout_components(self):
        """Layout all components in the window."""
        # Left panel (Count and Strategy) - positioned below the menu button
        self.left_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=10, pady=(10, 10))
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.count_display.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        self.strategy_display.pack(fill=tk.BOTH, expand=True)
        
        # Center panel (Game area)
        self.center_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(3, weight=1)
        
        self.game_status.pack(fill=tk.X, pady=(10, 10))
        self.dealer_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.player_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Right panel (Betting and Actions)
        self.right_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        self.betting_panel.pack(fill=tk.X, pady=(10, 10))
        self.action_panel.pack(fill=tk.BOTH, expand=True)
        
        # Menu button with rounded corners - positioned above the left panel
        menu_btn_canvas = tk.Canvas(self.root, width=160, height=44, highlightthickness=0, bg=self.root.cget("bg"))
        menu_btn_canvas.grid(row=0, column=0, sticky="nw", padx=10, pady=(10, 0))
        
        # Store references to canvas items for hover effects
        menu_btn_canvas.background_shape = None
        menu_btn_canvas.button_text = None
        
        # Draw the rounded rectangle background
        menu_btn_canvas.background_shape = draw_rounded_rect(menu_btn_canvas, 2, 2, 158, 42, 16, fill="#e0e0e0", outline="#b0b0b0", width=2)
        
        # Create button text as a canvas item instead of a separate button
        menu_btn_canvas.button_text = menu_btn_canvas.create_text(80, 22, text="← Back to Menu", font=('Arial', 12, 'bold'), fill='#333333')
        
        # Bind click events to the canvas
        def on_click(event):
            self._back_to_menu()
        
        def on_enter(event):
            # Update background color without redrawing
            menu_btn_canvas.itemconfig(menu_btn_canvas.background_shape, fill="#d0d0d0", outline="#a0a0a0")
            menu_btn_canvas.itemconfig(menu_btn_canvas.button_text, fill='#222222')
        
        def on_leave(event):
            # Update background color without redrawing
            menu_btn_canvas.itemconfig(menu_btn_canvas.background_shape, fill="#e0e0e0", outline="#b0b0b0")
            menu_btn_canvas.itemconfig(menu_btn_canvas.button_text, fill='#333333')
        
        menu_btn_canvas.bind('<Button-1>', on_click)
        menu_btn_canvas.bind('<Enter>', on_enter)
        menu_btn_canvas.bind('<Leave>', on_leave)
        
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
    
    def _on_start_game(self, bankroll: int, num_decks: int):
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
        self.root.grid_rowconfigure(0, weight=0)  # Menu button row (fixed height)
        self.root.grid_rowconfigure(1, weight=1)  # Top section
        self.root.grid_rowconfigure(2, weight=2)  # Middle section (game area)
        self.root.grid_rowconfigure(3, weight=1)  # Bottom section
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)  # Game area
        self.root.grid_columnconfigure(2, weight=1)
        
        # Initialize game components
        self._create_components()
        self._layout_components()
        self._bind_events()
        
        # Update display
        self._update_display()
    
    def _on_bet_placed(self, amount: int):
        """Handle bet placement."""
        if self.game.place_bet(amount):
            self._update_display()
            # Start the animated dealing process
            self._deal_cards_with_animation()
        else:
            messagebox.showerror("Error", "Invalid bet amount!")
    
    def _on_hit(self):
        """Handle hit action."""
        if self.game.hit():
            self._update_display()
            # Add a small delay before checking if dealer should play
            self.root.after(500, self._check_dealer_turn)
        else:
            messagebox.showerror("Error", "Cannot hit!")
    
    def _check_dealer_turn(self):
        """Check if it's the dealer's turn after player action."""
        if self.game.state == GameState.DEALER_TURN:
            self._play_dealer_hand()
    
    def _on_stand(self):
        """Handle stand action."""
        if self.game.stand():
            self._update_display()
            # Add a small delay before dealer plays
            self.root.after(500, self._check_dealer_turn)
        else:
            messagebox.showerror("Error", "Cannot stand!")
    
    def _on_double(self):
        """Handle double down action."""
        if self.game.double_down():
            self._update_display()
            # Add a small delay before dealer plays
            self.root.after(500, self._check_dealer_turn)
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
            # Add a small delay before dealer plays
            self.root.after(500, self._check_dealer_turn)
        else:
            messagebox.showerror("Error", "Cannot surrender!")
    
    def _on_insurance(self, amount: int):
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
    
    def _deal_cards_with_animation(self):
        """Deal cards with animation delays for a more natural feel."""
        # First, prepare the game state for dealing
        if self.game.state != GameState.DEALING:
            return
        
        # Check if deck needs shuffling
        if self.game.deck.should_shuffle():
            self.game.deck.shuffle()
            self.game.card_counter.reset(self.game.deck)
        
        # Burn a card (casino practice)
        burned_card = self.game.deck.burn_card()
        if burned_card:
            self.game.card_counter.update_count(burned_card)
        
        # Clear previous hands
        self.game.player_hands = [Hand()]
        self.game.dealer_hand.clear()
        self.game.current_hand_index = 0
        
        # Start the animated dealing sequence
        self._deal_next_card(0, 0)
    
    def _deal_next_card(self, round_num: int, card_in_round: int):
        """Deal the next card in the sequence with animation."""
        if round_num >= 2:  # All cards dealt
            # Check for insurance opportunity
            if len(self.game.dealer_hand.cards) >= 2 and self.game.dealer_hand.cards[1].is_ace:
                self.game.state = GameState.INSURANCE
                self._update_display()
                self._check_insurance()
                return
            
            # Check for dealer blackjack
            if self.game.dealer_hand.is_blackjack:
                self.game.state = GameState.GAME_OVER
                results = self.game.determine_results()
                self.game.update_statistics(results)
                self._update_display()
                return
            
            # Check for player blackjack
            if self.game.player_hands[0].is_blackjack:
                self.game.state = GameState.GAME_OVER
                results = self.game.determine_results()
                self.game.update_statistics(results)
                self._update_display()
                return
            
            self.game.state = GameState.PLAYER_TURN
            self._update_display()
            return
        
        # Deal the current card
        if card_in_round == 0:  # First card in this round
            # Deal to player
            card = self.game.deck.deal_card()
            if card:
                self.game.player_hands[0].add_card(card)
                self.game.card_counter.update_count(card)
                self._update_display()
                # Schedule next card (dealer's card in this round)
                self.root.after(800, lambda: self._deal_next_card(round_num, 1))
        else:  # Second card in this round (dealer's card)
            # Deal to dealer
            card = self.game.deck.deal_card()
            if card:
                self.game.dealer_hand.add_card(card)
                self.game.card_counter.update_count(card)
                self._update_display()
                # Schedule next round
                self.root.after(800, lambda: self._deal_next_card(round_num + 1, 0))
    
    def _check_insurance(self):
        """Check if insurance is available."""
        if self.game.state == GameState.INSURANCE:
            max_insurance = self.game.current_bet / 2
            self.action_panel.show_insurance_options(max_insurance)
    
    def _play_dealer_hand(self):
        """Play out the dealer's hand with step-by-step animation."""
        # Check if any player hands are still in play (not busted)
        active_hands = [hand for hand in self.game.player_hands if not hand.is_bust and not hand.is_surrendered]
        
        # If all hands are busted or surrendered, dealer doesn't need to play
        if not active_hands:
            self.game.state = GameState.GAME_OVER
            self._show_results()
            return
        
        # Set game state to dealer turn and start with revealing the face-down card
        self.game.state = GameState.DEALER_TURN
        self._dealer_play_step(reveal_hole_card=True)
    
    def _dealer_play_step(self, reveal_hole_card=False):
        """Play one step of the dealer's hand."""
        if reveal_hole_card:
            # First step: reveal the face-down card
            self._update_display()
            
            # Schedule the actual dealer play after a delay
            self.root.after(1500, lambda: self._dealer_play_step(reveal_hole_card=False))
            return
        
        # Use the exact same logic as the original play_dealer_hand method
        should_hit = (self.game.dealer_hand.total < 17 or 
                     (self.game.dealer_hits_soft_17 and self.game.dealer_hand.is_soft and self.game.dealer_hand.total == 17))
        
        if should_hit:
            # Deal one card to dealer
            card = self.game.deck.deal_card()
            if card:
                self.game.dealer_hand.add_card(card)
                self.game.card_counter.update_count(card)
                
                # Update display to show the new card
                self._update_display()
                
                # Schedule next step after a delay
                self.root.after(2000, lambda: self._dealer_play_step(reveal_hole_card=False))
            else:
                # No more cards in deck
                self.game.state = GameState.GAME_OVER
                self._show_results()
        else:
            # Dealer stands
            self.game.state = GameState.GAME_OVER
            self._show_results()
    
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
            hide_first=(self.game.state not in [GameState.GAME_OVER, GameState.DEALER_TURN])
        )
        
        # Update player display
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
                self.strategy_display.update_strategy(current_hand, dealer_up, self.game.dealer_hand)
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