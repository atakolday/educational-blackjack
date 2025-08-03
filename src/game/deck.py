import random
from typing import List, Optional, Dict
from collections import defaultdict
from .card import Card, Suit, Rank


class Deck:
    """Represents a deck of cards with multi-deck support and card tracking."""
    
    def __init__(self, num_decks: int = 6):
        """
        Initialize a deck with multiple standard 52-card decks.
        
        Args:
            num_decks: Number of decks to use (typically 6-8 for casino blackjack)
        """
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.discarded_cards: List[Card] = []
        self._card_counts: Dict[Rank, int] = defaultdict(int)
        self._total_cards = 0
        
        self._build_deck()
        self.shuffle()
    
    def _build_deck(self) -> None:
        """Build the deck with the specified number of standard decks."""
        self.cards.clear()
        self._card_counts.clear()
        
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    card = Card(suit, rank)
                    self.cards.append(card)
                    self._card_counts[rank] += 1
        
        self._total_cards = len(self.cards)
    
    def shuffle(self) -> None:
        """Shuffle the deck and reset discarded cards."""
        random.shuffle(self.cards)
        self.discarded_cards.clear()
        self._card_counts = defaultdict(int)
        
        # Rebuild card counts
        for card in self.cards:
            self._card_counts[card.rank] += 1
    
    def deal_card(self) -> Optional[Card]:
        """
        Deal a card from the deck.
        
        Returns:
            The dealt card, or None if deck is empty
        """
        if not self.cards:
            return None
        
        card = self.cards.pop()
        self.discarded_cards.append(card)
        self._card_counts[card.rank] -= 1
        
        return card
    
    def burn_card(self) -> Optional[Card]:
        """Burn a card (remove from deck without dealing)."""
        if self.cards:
            card = self.cards.pop()
            self.discarded_cards.append(card)
            self._card_counts[card.rank] -= 1
            return card
        return None
    
    def cut_card_position(self) -> int:
        """Get the position where the cut card should be placed (typically 60-75 cards from bottom)."""
        return random.randint(60, 75)
    
    def should_shuffle(self) -> bool:
        """Check if the deck should be shuffled (cut card reached)."""
        return len(self.cards) <= self.cut_card_position()
    
    @property
    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the deck."""
        return len(self.cards)
    
    @property
    def decks_remaining(self) -> float:
        """Get the approximate number of decks remaining."""
        return self.cards_remaining / 52.0
    
    @property
    def penetration(self) -> float:
        """Get the penetration percentage (cards dealt / total cards)."""
        if self._total_cards == 0:
            return 0.0
        return (self._total_cards - self.cards_remaining) / self._total_cards
    
    def get_card_count(self, rank: Rank) -> int:
        """Get the number of cards of a specific rank remaining in the deck."""
        return self._card_counts[rank]
    
    def get_suit_count(self, suit: Suit) -> int:
        """Get the number of cards of a specific suit remaining in the deck."""
        return sum(1 for card in self.cards if card.suit == suit)
    
    def get_probability(self, rank: Rank) -> float:
        """Get the probability of drawing a specific rank."""
        if self.cards_remaining == 0:
            return 0.0
        return self._card_counts[rank] / self.cards_remaining
    
    def get_probability_10_value(self) -> float:
        """Get the probability of drawing a 10-value card (10, J, Q, K)."""
        ten_value_ranks = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
        count = sum(self._card_counts[rank] for rank in ten_value_ranks)
        if self.cards_remaining == 0:
            return 0.0
        return count / self.cards_remaining
    
    def get_probability_ace(self) -> float:
        """Get the probability of drawing an Ace."""
        return self.get_probability(Rank.ACE)
    
    def get_probability_low_card(self) -> float:
        """Get the probability of drawing a low card (2-6)."""
        low_ranks = [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]
        count = sum(self._card_counts[rank] for rank in low_ranks)
        if self.cards_remaining == 0:
            return 0.0
        return count / self.cards_remaining
    
    def get_probability_high_card(self) -> float:
        """Get the probability of drawing a high card (10, J, Q, K, A)."""
        high_ranks = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
        count = sum(self._card_counts[rank] for rank in high_ranks)
        if self.cards_remaining == 0:
            return 0.0
        return count / self.cards_remaining
    
    def __str__(self) -> str:
        return f"Deck({self.num_decks} decks, {self.cards_remaining} cards remaining)"
    
    def __repr__(self) -> str:
        return f"Deck(num_decks={self.num_decks}, cards_remaining={self.cards_remaining})" 