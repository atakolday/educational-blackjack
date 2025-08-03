"""
Card display component for showing hands of cards.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from ...game.card import Card, Suit, Rank
from ...game.hand import Hand


class CardDisplay(ttk.Frame):
    """Component for displaying cards in a hand."""
    
    def __init__(self, parent, title: str):
        """
        Initialize the card display.
        
        Args:
            parent: Parent widget
            title: Title for this display (e.g., "Dealer", "Player")
        """
        super().__init__(parent)
        self.title = title
        self.cards: List[Card] = []
        self.hide_first = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Title
        self.title_label = ttk.Label(self, text=self.title, font=('Arial', 14, 'bold'))
        self.title_label.pack(pady=(0, 10))
        
        # Cards frame
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Total label
        self.total_label = ttk.Label(self, text="Total: 0", font=('Arial', 12))
        self.total_label.pack(pady=(10, 0))
        
        # Status label (for soft hands, bust, etc.)
        self.status_label = ttk.Label(self, text="", font=('Arial', 10))
        self.status_label.pack()
    
    def update_hand(self, hand: Hand, hide_first: bool = False):
        """
        Update the display with a single hand.
        
        Args:
            hand: The hand to display
            hide_first: Whether to hide the first card
        """
        self.cards = hand.cards.copy()
        self.hide_first = hide_first
        self._update_display()
    
    def update_hands(self, hands: List[Hand], current_index: int = 0):
        """
        Update the display with multiple hands (for splits).
        
        Args:
            hands: List of hands to display
            current_index: Index of the current hand being played
        """
        if not hands:
            self.cards = []
            self._update_display()
            return
        
        # For now, show the current hand
        # TODO: Implement multi-hand display for splits
        current_hand = hands[current_index]
        self.cards = current_hand.cards.copy()
        self.hide_first = False
        self._update_display()
        
        # Update title to show current hand
        if len(hands) > 1:
            self.title_label.config(text=f"{self.title} (Hand {current_index + 1}/{len(hands)})")
        else:
            self.title_label.config(text=self.title)
    
    def _update_display(self):
        """Update the card display."""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        if not self.cards:
            # Show empty state
            empty_label = ttk.Label(self.cards_frame, text="No cards", font=('Arial', 12))
            empty_label.pack(expand=True)
            self.total_label.config(text="Total: 0")
            self.status_label.config(text="")
            return
        
        # Create card widgets with slight overlap for realistic hand appearance
        for i, card in enumerate(self.cards):
            if i == 0 and self.hide_first:
                # Show card back
                card_widget = self._create_card_back()
            else:
                card_widget = self._create_card_widget(card)
            
            # Position cards with slight overlap for realistic hand appearance
            if i == 0:
                card_widget.pack(side=tk.LEFT, padx=(5, 0))
            else:
                card_widget.pack(side=tk.LEFT, padx=(0, 0))  # Minimal spacing for overlap effect
        
        # Update total and status
        if self.hide_first and len(self.cards) > 1:
            # Show only visible cards total
            visible_cards = self.cards[1:]
            total = sum(card.get_soft_value() for card in visible_cards)
            aces = sum(1 for card in visible_cards if card.is_ace)
            for _ in range(aces):
                if total + 10 <= 21:
                    total += 10
            self.total_label.config(text=f"Total: {total}")
            self.status_label.config(text="(First card hidden)")
        else:
            # Show full hand
            hand = Hand(self.cards)
            self.total_label.config(text=f"Total: {hand.total}")
            
            # Status text
            status_parts = []
            if hand.is_blackjack:
                status_parts.append("BLACKJACK!")
            elif hand.is_bust:
                status_parts.append("BUST!")
            elif hand.is_soft:
                status_parts.append("Soft")
            if hand.is_doubled:
                status_parts.append("Doubled")
            if hand.is_surrendered:
                status_parts.append("Surrendered")
            
            self.status_label.config(text=", ".join(status_parts) if status_parts else "")
    
    def _create_card_widget(self, card: Card) -> tk.Frame:
        """Create a widget for a single card."""
        # Create main card frame with shadow effect
        card_frame = tk.Frame(
            self.cards_frame, 
            relief=tk.RAISED, 
            borderwidth=2,
            bg='#1a1a1a',  # Darker shadow color
            width=120,     # Fixed width for better proportions
            height=160      # Fixed height for better proportions
        )
        card_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Card dimensions - make cards wider for better proportions
        card_width = 12
        card_height = 4
        
        # Card content
        rank_text = card.rank.display
        suit_symbol = card.suit.value
        
        # Color scheme
        if card.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            fg_color = '#d40000'  # Darker red for better contrast
        else:
            fg_color = '#000000'  # Black for clubs and spades
        
        # Special styling for face cards
        is_face_card = card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]
        if is_face_card:
            # Use a slightly different background for face cards
            card_bg = '#f8f8f8'  # Slightly off-white
        else:
            card_bg = '#ffffff'  # Pure white
        
        # Inner card frame for the white card face
        inner_frame = tk.Frame(
            card_frame,
            relief=tk.FLAT,
            borderwidth=1,
            bg=card_bg  # Dynamic card background
        )
        inner_frame.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # Create card content
        # Top-left corner
        top_left = tk.Label(
            inner_frame,
            text=f"{rank_text}\n{suit_symbol}",
            font=('Arial', 16, 'bold'),
            fg=fg_color,
            bg=card_bg,
            justify=tk.LEFT,
            anchor='nw'
        )
        top_left.pack(anchor='nw', padx=3, pady=3)
        
        # Center suit (larger)
        center_suit = tk.Label(
            inner_frame,
            text=suit_symbol,
            font=('Arial', 24, 'bold'),
            fg=fg_color,
            bg=card_bg
        )
        center_suit.pack(expand=True)
        
        # Bottom-right corner (rotated)
        bottom_right = tk.Label(
            inner_frame,
            text=f"{suit_symbol}\n{rank_text}",
            font=('Arial', 16, 'bold'),
            fg=fg_color,
            bg=card_bg,
            justify=tk.RIGHT,
            anchor='se'
        )
        bottom_right.pack(anchor='se', padx=3, pady=3)
        
        return card_frame
    
    def _create_card_back(self) -> tk.Frame:
        """Create a widget for a card back."""
        # Create main card frame with shadow effect
        card_frame = tk.Frame(
            self.cards_frame, 
            relief=tk.RAISED, 
            borderwidth=2,
            bg='#1a1a1a',  # Darker shadow color
            width=120,     # Fixed width for better proportions
            height=160      # Fixed height for better proportions
        )
        card_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Inner card frame for the card back design
        inner_frame = tk.Frame(
            card_frame,
            relief=tk.FLAT,
            borderwidth=1,
            bg='#2c5530'  # Dark green background
        )
        inner_frame.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # Card back pattern
        # Top pattern
        top_pattern = tk.Label(
            inner_frame,
            text="♠ ♥ ♦ ♣",
            font=('Arial', 8, 'bold'),
            fg='#ffffff',
            bg='#2c5530'
        )
        top_pattern.pack(anchor='n', pady=(5, 0))
        
        # Center design
        center_design = tk.Label(
            inner_frame,
            text="🂠",
            font=('Arial', 24, 'bold'),
            fg='#ffffff',
            bg='#2c5530'
        )
        center_design.pack(expand=True)
        
        # Bottom pattern
        bottom_pattern = tk.Label(
            inner_frame,
            text="♣ ♦ ♥ ♠",
            font=('Arial', 8, 'bold'),
            fg='#ffffff',
            bg='#2c5530'
        )
        bottom_pattern.pack(anchor='s', pady=(0, 5))
        
        return card_frame 