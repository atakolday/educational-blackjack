"""
Card display component for showing hands of cards.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from ...game.card import Card, Suit, Rank
from ...game.hand import Hand
import os
from PIL import Image, ImageTk

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
        self.card_back_image = None
        self.face_card_images = {}  # Dictionary to store face card images
        
        self._create_widgets()
        self._load_card_back_image()
        self._load_face_card_images()
    
    def _create_widgets(self):
        """Create the widget layout."""
        # Set fixed dimensions for the entire card display to prevent resizing
        self.configure(width=800, height=300)
        self.pack_propagate(False)  # Prevent the main frame from resizing
        
        # Title
        self.title_label = ttk.Label(self, text=self.title, font=('Arial', 16, 'bold'))
        self.title_label.pack(pady=(0, 10))
        
        # Cards frame with fixed dimensions to prevent resizing glitches
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Set minimum dimensions to accommodate multiple cards
        # Each card is 120x160, so we need space for at least 6-8 cards horizontally
        self.cards_frame.configure(width=800, height=200)
        self.cards_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Total label
        self.total_label = ttk.Label(self, text="Total: 0", font=('Arial', 14))
        self.total_label.pack(pady=(10, 0))
        
        # Status label (for soft hands, bust, etc.)
        self.status_label = ttk.Label(self, text="", font=('Arial', 12))
        self.status_label.pack()
    
    def _load_card_back_image(self):
        """Load the card back image from assets."""
        try:
            # Get the path to the assets directory
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            assets_dir = os.path.join(current_dir, 'assets')
            image_path = os.path.join(assets_dir, 'card_back.png')
            
            # Load and resize the image to fit the card dimensions
            original_image = Image.open(image_path)
            resized_image = original_image.resize((116, 156), Image.Resampling.LANCZOS)  # Slightly smaller than card frame
            self.card_back_image = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            print(f"Failed to load card back image: {e}")
            self.card_back_image = None
    
    def _load_face_card_images(self):
        """Load all face card images from assets."""
        try:
            # Get the path to the assets directory
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            assets_dir = os.path.join(current_dir, 'assets', 'face_cards')
            
            # Define face card ranks and suits
            face_ranks = ['jack', 'queen', 'king']
            suits = ['clubs', 'diamonds', 'hearts', 'spades']
            
            # Load each face card image
            for rank in face_ranks:
                for suit in suits:
                    image_path = os.path.join(assets_dir, f'{rank}_of_{suit}.png')
                    
                    # Load and resize the image to fit the card dimensions
                    original_image = Image.open(image_path)
                    
                    # Scale the cropped content to fit the white background frame (118x158)
                    resized_image = original_image.resize((102, 148), Image.Resampling.LANCZOS)
                    
                    # Convert rank and suit names to enum values for lookup
                    rank_enum = getattr(Rank, rank.upper())
                    suit_enum = getattr(Suit, suit.upper())
                    
                    # Store the image with (rank, suit) tuple as key
                    self.face_card_images[(rank_enum, suit_enum)] = ImageTk.PhotoImage(resized_image)
                    
        except Exception as e:
            print(f"Failed to load face card images: {e}")
            self.face_card_images = {}
    
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
        if self.hide_first:
            # Show only visible cards total (exclude the face-down card)
            if len(self.cards) > 1:
                visible_cards = self.cards[1:]
                total = sum(card.get_soft_value() for card in visible_cards)
                aces = sum(1 for card in visible_cards if card.is_ace)
                for _ in range(aces):
                    if total + 10 <= 21:
                        total += 10
                self.total_label.config(text=f"Total: {total}")
            else:
                # Only one card and it's face-down
                self.total_label.config(text="Total: ?")
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
            
            self.status_label.config(text=", ".join(status_parts) if status_parts else "", font=('Courier', 24, 'bold') if hand.is_blackjack else ('Courier', 12, 'bold'))
    
    def _create_card_widget(self, card: Card) -> tk.Frame:
        """Create a widget for a single card using layered approach."""
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
        card_bg = '#ffffff'  # Pure white
        
        # Layer 1: White background
        bg_frame = tk.Frame(
            card_frame,
            relief=tk.FLAT,
            borderwidth=1,
            bg=card_bg
        )
        bg_frame.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # Layer 2: Corner rank/suit labels (absolute positioning) - only for non-face cards
        if not is_face_card:
            # Top-left corner
            top_left = tk.Label(
                bg_frame,
                text=f"{rank_text}\n{suit_symbol}",
                font=('Arial', 18, 'bold') if rank_text != '10' else ('Arial Narrow', 16, 'bold'),
                fg=fg_color,
                bg=card_bg,
                justify=tk.LEFT
            )
            top_left.place(x=2, y=2, anchor='nw')
            
            # Bottom-right corner (rotated)
            bottom_right = tk.Label(
                bg_frame,
                text=f"{suit_symbol}\n{rank_text}",
                font=('Arial', 18, 'bold') if rank_text != '10' else ('Arial Narrow', 16, 'bold'),
                fg=fg_color,
                bg=card_bg,
                justify=tk.RIGHT
            )
            bottom_right.place(x=110, y=150, anchor='se')
        
        # Layer 3: Center content
        if is_face_card:
            # Use PNG image for face cards if available, otherwise fall back to text
            if (card.rank, card.suit) in self.face_card_images:
                center_label = tk.Label(
                    bg_frame,
                    image=self.face_card_images[(card.rank, card.suit)],
                    bg=card_bg
                )
                center_label.place(x=59, y=79, anchor='center')  # Center the 105x150 image in 118x158 frame
            else:
                # Fallback to text if image not available
                center_label = tk.Label(
                    bg_frame,
                    text=rank_text,
                    font=('Arial', 36, 'bold'),
                    fg=fg_color,
                    bg=card_bg
                )
                center_label.place(x=55, y=75, anchor='center')
        else:
            self._create_suit_pattern_layered(
                parent=bg_frame,
                count=card.rank.card_value,
                suit_symbol=suit_symbol,
                fg_color=fg_color,
                bg_color=card_bg
            )
        
        return card_frame
    
    def _create_card_back(self) -> tk.Frame:
        """Create a widget for a card back."""
        # Create main card frame with shadow effect
        card_frame = tk.Frame(
            self.cards_frame, 
            relief=tk.RAISED, 
            borderwidth=2,
            bg='#1a1a1a',   # Darker shadow color
            width=120,      # Fixed width for better proportions
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
        
        # Use the loaded card back image if available, otherwise fall back to text pattern
        if self.card_back_image:
            # Create label with the image
            card_back_label = tk.Label(
                inner_frame,
                image=self.card_back_image,
                bg='#2c5530'
            )
            card_back_label.pack(expand=True, fill=tk.BOTH)
        else:
            # Fallback to text-based card back pattern
            # Top pattern
            top_pattern = tk.Label(
                inner_frame,
                text="♠ ♥ ♦ ♣",
                font=('Arial', 12, 'bold'),
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
    
    def _create_suit_pattern_layered(self, parent, count, suit_symbol, fg_color, bg_color):
        """Create suit symbols using absolute positioning for perfect layout."""

        # Traditional playing card patterns with absolute coordinates
        patterns = {
          1: [
            (55, 75),              # Center only (Ace)
          ],
          2: [
            (55, 40),              # Top center
            (55, 120),             # Bottom center
          ],
          3: [
            (55, 40),              # Top center
            (55, 80),              # Center
            (55, 120),             # Bottom center
          ],
          4: [
            (35, 40), (75, 40),    # Top left & right
            (35, 120), (75, 120),  # Bottom left & right
          ],
          5: [
            (35, 40), (75, 40),    # Top left & right
            (55, 80),              # Center
            (35, 120), (75, 120),  # Bottom left & right
          ],
          6: [
            (35, 40), (75, 40),    # Top left & right
            (35, 80), (75, 80),    # Middle left & right
            (35, 120), (75, 120),  # Bottom left & right
          ],
          7: [
            (35, 40), (75, 40),    # Top left & right
            (55, 60),              # Top center
            (35, 80), (75, 80),    # Middle left & right
            (35, 120), (75, 120),  # Bottom left & right
          ],
          8: [
            (35, 40), (75, 40),    # Top left & right
            (55, 60),              # Top center
            (35, 80), (75, 80),    # Middle left & right
            (55, 100),             # Bottom center
            (35, 120), (75, 120),  # Bottom left & right
          ],
           9: [
            (35, 40), (75, 40),   # Top left & right
            (35, 66), (75, 66),   # Upper middle left & right
            (35, 93), (75, 93),   # Lower middle left & right
            (35, 120), (75, 120), # Bottom left & right
            (55, 75)              # Center middle
          ],  # 4 on each side (two columns), one in the center middle
          10: [
            (35, 40), (75, 40),    # Top left & right
            (55, 53),              # Top center
            (35, 66), (75, 66),    # Upper middle left & right
            (35, 93), (75, 93),    # Lower middle left & right
            (55, 106),             # Bottom center
            (35, 120), (75, 120),  # Bottom left & right
          ],
          11: [
            (55, 75),              # Center only (Ace)
          ],
        }

        patterns = self._shift_patterns_x(patterns, 1)
        
        if count in patterns:
            font_size = 45 if count in [1, 11] else 26
            
            for x, y in patterns[count]:
                symbol_label = tk.Label(
                    parent,
                    text=suit_symbol,
                    font=('Courier', font_size, 'bold'),
                    fg=fg_color,
                    bg=bg_color
                )
                symbol_label.place(x=x, y=y, anchor='center')

    def _shift_patterns_x(self, patterns, shift_amount):
        return {
            key: [(x + shift_amount, y) for (x, y) in coords]
            for key, coords in patterns.items()
        }    