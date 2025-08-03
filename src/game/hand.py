from typing import List, Optional
from .card import Card


class Hand:
    """Represents a hand of cards in blackjack."""
    
    def __init__(self, cards: Optional[List[Card]] = None):
        self.cards = cards or []
        self._is_doubled = False
        self._is_surrendered = False
    
    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)
    
    def clear(self) -> None:
        """Clear all cards from the hand."""
        self.cards.clear()
        self._is_doubled = False
        self._is_surrendered = False
    
    @property
    def num_cards(self) -> int:
        """Get the number of cards in the hand."""
        return len(self.cards)
    
    @property
    def is_blackjack(self) -> bool:
        """Check if the hand is a blackjack (Ace + 10-value card)."""
        if self.num_cards != 2:
            return False
        return self.total == 21 and self.has_ace
    
    @property
    def has_ace(self) -> bool:
        """Check if the hand contains an Ace."""
        return any(card.is_ace for card in self.cards)
    
    @property
    def is_soft(self) -> bool:
        """Check if the hand is soft (contains an Ace counted as 11)."""
        if not self.has_ace:
            return False
        return self.total <= 21 and self._get_soft_total() + 10 <= 21
    
    @property
    def is_bust(self) -> bool:
        """Check if the hand is bust (total > 21)."""
        return self.total > 21
    
    @property
    def total(self) -> int:
        """Get the total value of the hand, optimizing Aces."""
        total = sum(card.get_soft_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.is_ace)
        
        # Add 10 for each Ace that can be counted as 11
        for _ in range(aces):
            if total + 10 <= 21:
                total += 10
            else:
                break
        
        return total
    
    def _get_soft_total(self) -> int:
        """Get the soft total (all Aces counted as 1)."""
        return sum(card.get_soft_value() for card in self.cards)
    
    @property
    def can_split(self) -> bool:
        """Check if the hand can be split (two cards of same rank)."""
        if self.num_cards != 2:
            return False
        return self.cards[0].rank == self.cards[1].rank
    
    @property
    def can_double(self) -> bool:
        """Check if the hand can be doubled (exactly 2 cards)."""
        return self.num_cards == 2
    
    @property
    def is_doubled(self) -> bool:
        """Check if the hand was doubled."""
        return self._is_doubled
    
    @property
    def is_surrendered(self) -> bool:
        """Check if the hand was surrendered."""
        return self._is_surrendered
    
    def mark_doubled(self) -> None:
        """Mark the hand as doubled."""
        self._is_doubled = True
    
    def mark_surrendered(self) -> None:
        """Mark the hand as surrendered."""
        self._is_surrendered = True
    
    def get_display_string(self, hide_first: bool = False) -> str:
        """Get a string representation of the hand."""
        if hide_first and self.cards:
            return f"[XX] {' '.join(str(card) for card in self.cards[1:])}"
        return ' '.join(str(card) for card in self.cards)
    
    def __str__(self) -> str:
        return f"Hand({self.get_display_string()}) - Total: {self.total}"
    
    def __repr__(self) -> str:
        return f"Hand(cards={self.cards}, total={self.total})" 