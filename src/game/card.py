from enum import Enum
from typing import Optional


class Suit(Enum):
    """Card suits enumeration."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks enumeration with values and counting values."""
    ACE = ("A", 11, -1)  # (display, value, count_value)
    TWO = ("2", 2, 1)
    THREE = ("3", 3, 1)
    FOUR = ("4", 4, 1)
    FIVE = ("5", 5, 1)
    SIX = ("6", 6, 1)
    SEVEN = ("7", 7, 0)
    EIGHT = ("8", 8, 0)
    NINE = ("9", 9, 0)
    TEN = ("10", 10, -1)
    JACK = ("J", 10, -1)
    QUEEN = ("Q", 10, -1)
    KING = ("K", 10, -1)

    def __init__(self, display: str, card_value: int, count_value: int):
        self.display = display
        self.card_value = card_value
        self.count_value = count_value


class Card:
    """Represents a playing card with suit, rank, and card counting properties."""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self._is_ace = rank == Rank.ACE
    
    @property
    def value(self) -> int:
        """Get the card's value (Ace is 11 by default)."""
        return self.rank.card_value
    
    @property
    def count_value(self) -> int:
        """Get the card's counting value for Hi-Lo system."""
        return self.rank.count_value
    
    @property
    def is_ace(self) -> bool:
        """Check if the card is an Ace."""
        return self._is_ace
    
    @property
    def display_name(self) -> str:
        """Get the card's display name (e.g., 'A♠', '10♥')."""
        return f"{self.rank.display}{self.suit.value}"
    
    def get_soft_value(self) -> int:
        """Get the soft value of the card (Ace as 1)."""
        if self.is_ace:
            return 1
        return self.value
    
    def __str__(self) -> str:
        return self.display_name
    
    def __repr__(self) -> str:
        return f"Card({self.suit.name}, {self.rank.name})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self) -> int:
        return hash((self.suit, self.rank)) 