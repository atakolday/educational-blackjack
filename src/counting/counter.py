from typing import Dict, List, Optional
from collections import defaultdict
from ..game.card import Card, Rank
from ..game.deck import Deck


class CardCounter:
    """Implements the Hi-Lo card counting system with running and true count tracking."""
    
    def __init__(self):
        """Initialize the card counter."""
        self.running_count = 0
        self.true_count = 0.0
        self._card_counts: Dict[Rank, int] = defaultdict(int)
        self._total_cards_seen = 0
        self._initial_deck_size = 0
    
    def reset(self, deck: Deck) -> None:
        """Reset the counter for a new deck."""
        self.running_count = 0
        self.true_count = 0.0
        self._card_counts.clear()
        self._total_cards_seen = 0
        self._initial_deck_size = deck.cards_remaining
        
        # Initialize card counts from the deck
        for card in deck.cards:
            self._card_counts[card.rank] += 1
    
    def update_count(self, card: Card) -> None:
        """
        Update the running count when a card is dealt.
        
        Args:
            card: The card that was dealt
        """
        self.running_count += card.count_value
        self._card_counts[card.rank] -= 1
        self._total_cards_seen += 1
        
        # Update true count
        self._update_true_count()
    
    def update_count_multiple(self, cards: List[Card]) -> None:
        """
        Update the count for multiple cards at once.
        
        Args:
            cards: List of cards that were dealt
        """
        for card in cards:
            self.update_count(card)
    
    def _update_true_count(self) -> None:
        """Update the true count based on current running count and decks remaining."""
        decks_remaining = self._get_decks_remaining()
        if decks_remaining > 0:
            self.true_count = self.running_count / decks_remaining
        else:
            self.true_count = 0.0
    
    def _get_decks_remaining(self) -> float:
        """Calculate the number of decks remaining."""
        if self._initial_deck_size == 0:
            return 0.0
        
        cards_remaining = self._initial_deck_size - self._total_cards_seen
        return cards_remaining / 52.0
    
    @property
    def decks_remaining(self) -> float:
        """Get the number of decks remaining."""
        return self._get_decks_remaining()
    
    @property
    def penetration(self) -> float:
        """Get the penetration percentage (cards dealt / total cards)."""
        if self._initial_deck_size == 0:
            return 0.0
        return self._total_cards_seen / self._initial_deck_size
    
    def get_card_count(self, rank: Rank) -> int:
        """Get the number of cards of a specific rank remaining."""
        return self._card_counts[rank]
    
    def get_probability(self, rank: Rank) -> float:
        """Get the probability of drawing a specific rank."""
        cards_remaining = self._initial_deck_size - self._total_cards_seen
        if cards_remaining == 0:
            return 0.0
        return self._card_counts[rank] / cards_remaining
    
    def get_probability_10_value(self) -> float:
        """Get the probability of drawing a 10-value card (10, J, Q, K)."""
        ten_value_ranks = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
        count = sum(self._card_counts[rank] for rank in ten_value_ranks)
        cards_remaining = self._initial_deck_size - self._total_cards_seen
        if cards_remaining == 0:
            return 0.0
        return count / cards_remaining
    
    def get_probability_ace(self) -> float:
        """Get the probability of drawing an Ace."""
        return self.get_probability(Rank.ACE)
    
    def get_probability_low_card(self) -> float:
        """Get the probability of drawing a low card (2-6)."""
        low_ranks = [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]
        count = sum(self._card_counts[rank] for rank in low_ranks)
        cards_remaining = self._initial_deck_size - self._total_cards_seen
        if cards_remaining == 0:
            return 0.0
        return count / cards_remaining
    
    def get_probability_high_card(self) -> float:
        """Get the probability of drawing a high card (10, J, Q, K, A)."""
        high_ranks = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
        count = sum(self._card_counts[rank] for rank in high_ranks)
        cards_remaining = self._initial_deck_size - self._total_cards_seen
        if cards_remaining == 0:
            return 0.0
        return count / cards_remaining
    
    def get_count_status(self) -> str:
        """Get a string representation of the current count status."""
        if self.true_count >= 2:
            return "Very Favorable"
        elif self.true_count >= 1:
            return "Favorable"
        elif self.true_count >= 0:
            return "Neutral"
        elif self.true_count >= -1:
            return "Unfavorable"
        else:
            return "Very Unfavorable"
    
    def get_betting_multiplier(self) -> float:
        """
        Get the recommended betting multiplier based on the true count.
        This is a simplified version - real card counters use more sophisticated systems.
        """
        if self.true_count <= 0:
            return 1.0  # Minimum bet
        elif self.true_count <= 2:
            return 1.0 + (self.true_count * 0.5)  # Linear increase
        else:
            return 2.0 + (self.true_count - 2) * 0.25  # Diminishing returns
    
    def __str__(self) -> str:
        return f"CardCounter(running={self.running_count}, true={self.true_count:.2f}, decks={self.decks_remaining:.2f})"
    
    def __repr__(self) -> str:
        return f"CardCounter(running_count={self.running_count}, true_count={self.true_count:.2f})" 