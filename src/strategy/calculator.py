import copy
from typing import Dict, List, Tuple, Optional, Union, Literal
from enum import Enum
from collections import defaultdict
from ..game.card import Card, Rank
from ..game.hand import Hand
from ..counting.counter import CardCounter
from ..game.deck import Deck


class Action(Enum):
    """Possible actions in blackjack."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"


class StrategyCalculator:
    """Calculates optimal strategy based on current count and deck composition."""
    
    def __init__(self, card_counter: CardCounter):
        """
        Initialize the strategy calculator.
        
        Args:
            card_counter: The card counter tracking the current deck state
        """
        self.card_counter = card_counter
    
    def get_optimal_action(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[Action, float, Dict[str, float]]:
        """
        Get the optimal action for the current situation.
        
        Args:
            player_hand: The player's current hand
            dealer_up_card: The dealer's up card
            
        Returns:
            Tuple of (optimal_action, expected_value, action_probabilities)
        """
        if player_hand.is_bust:
            return Action.STAND, -1.0, {}
        
        if player_hand.is_blackjack:
            return Action.STAND, 1.5, {}
        
        # Calculate expected values for all possible actions
        action_evs = {}
        action_probs = {}
        
        # Hit EV
        hit_ev, hit_probs = self._calculate_hit_ev(player_hand, dealer_up_card)
        action_evs[Action.HIT] = hit_ev
        action_probs[Action.HIT] = hit_probs
        
        # Stand EV
        stand_ev, stand_probs = self._calculate_stand_ev(player_hand, dealer_up_card)
        action_evs[Action.STAND] = stand_ev
        action_probs[Action.STAND] = stand_probs
        
        # Double EV (only if allowed)
        if player_hand.can_double:
            double_ev, double_probs = self._calculate_double_ev(player_hand, dealer_up_card)
            action_evs[Action.DOUBLE] = double_ev
            action_probs[Action.DOUBLE] = double_probs
        
        # Split EV (only if allowed)
        if player_hand.can_split:
            split_ev, split_probs = self._calculate_split_ev(player_hand, dealer_up_card)
            action_evs[Action.SPLIT] = split_ev
            action_probs[Action.SPLIT] = split_probs
        
        # Surrender EV (only if allowed and first two cards)
        if player_hand.num_cards == 2:
            surrender_ev = -0.5  # Always -50% of bet
            action_evs[Action.SURRENDER] = surrender_ev
            action_probs[Action.SURRENDER] = {"surrender": 1.0}
        
        # Find the best action
        best_action = max(action_evs.keys(), key=lambda action: action_evs[action])
        best_ev = action_evs[best_action]
        
        return best_action, best_ev, action_probs[best_action]
    
    def _calculate_hit_ev(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[float, Dict[str, float]]:
        """Calculate expected value of hitting."""
        total_ev = 0.0
        probabilities = {}
        
        # Calculate probability of each possible card
        for rank in Rank:
            prob = self.card_counter.get_probability(rank)
            if prob > 0:
                # Create a new hand with this card
                new_hand = Hand(player_hand.cards.copy())
                new_hand.add_card(Card(dealer_up_card.suit, rank))  # Suit doesn't matter for EV
                
                if new_hand.is_bust:
                    # Bust - lose the bet
                    ev = -1.0
                    probabilities[f"bust_{rank.display}"] = prob
                else:
                    # Continue playing - recursive call
                    ev, _ = self._calculate_stand_ev(new_hand, dealer_up_card)
                    probabilities[f"hit_{rank.display}"] = prob
                
                total_ev += prob * ev
        
        return total_ev, probabilities
    
    def _calculate_stand_ev(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[float, Dict[str, float]]:
        """Calculate expected value of standing."""
        player_total = player_hand.total
        probabilities = {}
        
        # Calculate dealer's final hand distribution
        dealer_probs = self._calculate_dealer_final_hand_probs(dealer_up_card)
        
        total_ev = 0.0
        
        for dealer_total, prob in dealer_probs.items():
            if dealer_total > 21:
                # Dealer busts - player wins
                ev = 1.0
                probabilities[f"dealer_bust_{dealer_total}"] = prob
            elif player_total > dealer_total:
                # Player wins
                ev = 1.0
                probabilities[f"player_win_{dealer_total}"] = prob
            elif player_total < dealer_total:
                # Dealer wins
                ev = -1.0
                probabilities[f"dealer_win_{dealer_total}"] = prob
            else:
                # Push
                ev = 0.0
                probabilities[f"push_{dealer_total}"] = prob
            
            total_ev += prob * ev
        
        return total_ev, probabilities
    
    def _calculate_double_ev(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[float, Dict[str, float]]:
        """Calculate expected value of doubling down."""
        # Double down means exactly one more card
        total_ev = 0.0
        probabilities = {}
        
        for rank in Rank:
            prob = self.card_counter.get_probability(rank)
            if prob > 0:
                # Create a new hand with this card
                new_hand = Hand(player_hand.cards.copy())
                new_hand.add_card(Card(dealer_up_card.suit, rank))
                
                if new_hand.is_bust:
                    # Bust - lose double the bet
                    ev = -2.0
                    probabilities[f"double_bust_{rank.display}"] = prob
                else:
                    # Stand with the doubled hand
                    ev, _ = self._calculate_stand_ev(new_hand, dealer_up_card)
                    ev *= 2  # Double the bet
                    probabilities[f"double_{rank.display}"] = prob
                
                total_ev += prob * ev
        
        return total_ev, probabilities
    
    def _calculate_split_ev(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[float, Dict[str, float]]:
        """Calculate expected value of splitting."""
        # For simplicity, we'll calculate the EV of one split hand and multiply by 2
        # This is an approximation - the actual EV is more complex due to card removal effects
        
        split_card = player_hand.cards[0]  # Both cards are the same rank
        
        total_ev = 0.0
        probabilities = {}
        
        # Calculate EV for one split hand
        for rank in Rank:
            prob = self.card_counter.get_probability(rank)
            if prob > 0:
                # Create a new hand with split card + new card
                new_hand = Hand([split_card])
                new_hand.add_card(Card(dealer_up_card.suit, rank))
                
                if new_hand.is_bust:
                    ev = -1.0
                    probabilities[f"split_bust_{rank.display}"] = prob
                else:
                    ev, _ = self._calculate_stand_ev(new_hand, dealer_up_card)
                    probabilities[f"split_{rank.display}"] = prob
                
                total_ev += prob * ev
        
        # Multiply by 2 for the second split hand (approximation)
        total_ev *= 2
        
        return total_ev, probabilities
    
    def _calculate_dealer_final_hand_probs(self, dealer_up_card: Card) -> Dict[int, float]:
        """
        Accurately simulate the dealer's final hand probabilities given an upcard
        using recursive enumeration.
        """
        from collections import defaultdict

        memo = {}

        def recurse(total, soft, deck_counts):
            key = (total, soft, tuple(deck_counts.values()))
            if key in memo:
                return memo[key].copy()
            
            probs = defaultdict(float)
            
            # Dealer stands on 17+ (including soft 17)
            if total >= 17:
                probs[total] = 1.0
                memo[key] = probs.copy()
                return probs
            
            # Otherwise, dealer must hit
            total_cards = sum(deck_counts.values())
            for rank in Rank:
                count = deck_counts[rank]
                if count == 0:
                    continue
                prob = count / total_cards
                
                # Prepare the new deck state
                new_deck_counts = deck_counts.copy()
                new_deck_counts[rank] -= 1
                
                # Determine card value
                card_value = rank.card_value
                # Handle Ace as 11 if it doesn't bust, else as 1
                if rank == Rank.ACE:
                    if total + 11 <= 21:
                        new_total = total + 11
                        new_soft = True
                    else:
                        new_total = total + 1
                        new_soft = soft
                else:
                    new_total = total + card_value
                    new_soft = soft

                # If soft 17+ is reached and hand is soft, treat as stand (S17 rules)
                if new_total > 21 and new_soft:
                    new_total -= 10
                    new_soft = False
                if new_total > 21:
                    probs[22] += prob  # bust
                else:
                    subprobs = recurse(new_total, new_soft, new_deck_counts)
                    for t, p in subprobs.items():
                        probs[t] += prob * p

            memo[key] = probs.copy()
            return probs

        # Build the deck count (simulate one card missing for upcard)
        from collections import Counter
        deck_counts = Counter()
        for rank in Rank:
            deck_counts[rank] = self.card_counter.get_card_count(rank)
        # Remove the upcard
        deck_counts[dealer_up_card.rank] -= 1

        # Start dealer total/soft
        total = dealer_up_card.value
        soft = (dealer_up_card.rank == Rank.ACE)

        final_probs = recurse(total, soft, deck_counts)
        return dict(final_probs)
    
    def _calculate_dealer_bust_probability(self, dealer_up_card: Card) -> float:
        """Calculate the probability that the dealer will bust."""
        dealer_total = dealer_up_card.value
        
        if dealer_total >= 17:
            return 0.0  # Dealer stands
        
        # Calculate probability of going over 21
        bust_prob = 0.0
        
        for rank in Rank:
            prob = self.card_counter.get_probability(rank)
            if prob > 0:
                new_total = dealer_total + rank.card_value
                
                # Adjust for Aces
                if rank == Rank.ACE and new_total > 21:
                    new_total = dealer_total + 1  # Use Ace as 1
                
                if new_total > 21:
                    bust_prob += prob
                elif new_total < 17:
                    # Dealer must hit again - recursive calculation
                    # For simplicity, we'll use an approximation
                    bust_prob += prob * self._estimate_bust_probability(new_total)
        
        return bust_prob
    
    def _estimate_bust_probability(self, current_total: int) -> float:
        """Estimate bust probability for a given total (simplified)."""
        if current_total >= 17:
            return 0.0
        
        # Simple approximation based on remaining cards
        high_card_prob = self.card_counter.get_probability_high_card()
        
        # Rough estimate: if we need more than 4 points, high probability of bust
        points_needed = 21 - current_total
        if points_needed <= 4:
            return 0.1  # Low probability
        elif points_needed <= 6:
            return 0.3  # Medium probability
        else:
            return 0.6  # High probability
    
    def get_basic_strategy_action(self, player_hand: Hand, dealer_up_card: Card) -> Action:
        """Get the basic strategy action (for comparison)."""
        # This is a simplified basic strategy - in practice, this would be more comprehensive
        
        player_total = player_hand.total
        dealer_up_value = dealer_up_card.value
        
        # Check for splits first (pairs)
        if player_hand.can_split:
            split_rank = player_hand.cards[0].rank
            
            # Always split Aces and 8s
            if split_rank == Rank.ACE or split_rank == Rank.EIGHT:
                return Action.SPLIT
            
            # Split 10s (10, J, Q, K) vs dealer 5-6
            if split_rank in [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]:
                if dealer_up_value in [5, 6]:
                    return Action.SPLIT
            
            # Split 9s vs dealer 2-6, 8-9
            if split_rank == Rank.NINE:
                if dealer_up_value in [2, 3, 4, 5, 6, 8, 9]:
                    return Action.SPLIT
            
            # Split 7s vs dealer 2-7
            if split_rank == Rank.SEVEN:
                if dealer_up_value in [2, 3, 4, 5, 6, 7]:
                    return Action.SPLIT
            
            # Split 6s vs dealer 2-6
            if split_rank == Rank.SIX:
                if dealer_up_value in [2, 3, 4, 5, 6]:
                    return Action.SPLIT
            
            # Split 5s vs dealer 2-9
            if split_rank == Rank.FIVE:
                if dealer_up_value in [2, 3, 4, 5, 6, 7, 8, 9]:
                    return Action.SPLIT
            
            # Split 4s vs dealer 5-6
            if split_rank == Rank.FOUR:
                if dealer_up_value in [5, 6]:
                    return Action.SPLIT
            
            # Split 3s vs dealer 2-7
            if split_rank == Rank.THREE:
                if dealer_up_value in [2, 3, 4, 5, 6, 7]:
                    return Action.SPLIT
            
            # Split 2s vs dealer 2-7
            if split_rank == Rank.TWO:
                if dealer_up_value in [2, 3, 4, 5, 6, 7]:
                    return Action.SPLIT
        
        # Soft hands (containing Ace counted as 11)
        if player_hand.is_soft:
            if player_total >= 19:
                return Action.STAND
            elif player_total == 18:
                if dealer_up_value in [9, 10, 11]:  # 11 = Ace
                    return Action.HIT
                else:
                    return Action.STAND
            else:
                return Action.HIT
        
        # Hard hands
        if player_total >= 17:
            return Action.STAND
        elif player_total == 16:
            if dealer_up_value in [7, 8, 9, 10, 11]:
                return Action.HIT
            else:
                return Action.STAND
        elif player_total == 15:
            if dealer_up_value in [10, 11]:
                return Action.HIT
            else:
                return Action.STAND
        elif player_total == 13 or player_total == 14:
            if dealer_up_value in [2, 3, 4, 5, 6]:
                return Action.STAND
            else:
                return Action.HIT
        elif player_total == 12:
            if dealer_up_value in [4, 5, 6]:
                return Action.STAND
            else:
                return Action.HIT
        else:
            return Action.HIT
    
    def get_insurance_recommendation(self) -> Dict[str, any]:
        """Get insurance recommendation based on current count."""
        # Insurance pays 2:1 if dealer has blackjack
        # Basic strategy: Never take insurance (house edge ~7.7%)
        # Count-based strategy: Take insurance when count is very high
        
        # Calculate probability of dealer having blackjack
        # Dealer has Ace up, needs 10-value card for blackjack
        ten_value_prob = self.card_counter.get_probability_10_value()
        
        # Insurance EV = (prob_blackjack * 2) - (1 - prob_blackjack) * 1
        # = 2*prob_blackjack - 1 + prob_blackjack = 3*prob_blackjack - 1
        insurance_ev = 3 * ten_value_prob - 1
        
        # Basic strategy: never take insurance
        basic_ev = 0.0  # Not taking insurance has 0 EV
        
        # Recommendation: take insurance if EV > 0
        should_take_insurance = insurance_ev > 0
        
        return {
            "should_take_insurance": should_take_insurance,
            "insurance_ev": insurance_ev,
            "basic_ev": basic_ev,
            "dealer_blackjack_probability": ten_value_prob,
            "count_advantage": insurance_ev > basic_ev
        }
    
    def get_strategy_comparison(self, player_hand: Hand, dealer_up_card: Card) -> Dict[str, any]:
        """Get a comparison between basic strategy and count-based strategy."""
        optimal_action, optimal_ev, optimal_probs = self.get_optimal_action(player_hand, dealer_up_card)

        basic_action = self.get_basic_strategy_action(player_hand, dealer_up_card)
        
        # Calculate EV for basic strategy action
        basic_ev = 0.0
        if basic_action == Action.HIT:
            basic_ev, _ = self._calculate_hit_ev(player_hand, dealer_up_card)
        elif basic_action == Action.STAND:
            basic_ev, _ = self._calculate_stand_ev(player_hand, dealer_up_card)
        elif basic_action == Action.DOUBLE and player_hand.can_double:
            basic_ev, _ = self._calculate_double_ev(player_hand, dealer_up_card)
        elif basic_action == Action.SPLIT and player_hand.can_split:
            basic_ev, _ = self._calculate_split_ev(player_hand, dealer_up_card)
        elif basic_action == Action.SURRENDER and player_hand.num_cards == 2:
            basic_ev = -0.5
        
        return {
            "optimal_action": optimal_action,
            "optimal_ev": optimal_ev,
            "optimal_probabilities": optimal_probs,
            "basic_action": basic_action,
            "basic_ev": basic_ev,
            "ev_difference": optimal_ev - basic_ev,
            "count_advantage": optimal_ev > basic_ev
        }
    
    def get_bust_probability(self, hand_total: int, role: str = 'player') -> float:
        """
        Calculate bust probability for the current deck state.
        
        Args:
            hand_total: Current hand total
            role: 'dealer' or 'player' to determine stand threshold
            
        Returns:
            Probability of busting (0.0 to 1.0)
        """
        # Create a mock deck with current card counts for bust probability calculation
        class MockDeck:
            def __init__(self, card_counts, total_cards):
                self._card_counts = card_counts.copy()
                self.cards_remaining = total_cards
        
        total_cards = self.card_counter._initial_deck_size - self.card_counter._total_cards_seen
        mock_deck = MockDeck(self.card_counter._card_counts, total_cards)
        
        return self._calculate_bust_probability(hand_total, mock_deck, role)

    def _calculate_bust_probability(
        self,
        hand_total: int, 
        deck: Deck, 
        role: Union[Literal['dealer'], Literal['player']]
    ) -> float:
        """
        Calculate the bust probability for a given hand total and deck state.
        
        For players: calculates probability of busting on the next draw only
        For dealers: calculates probability of busting following dealer rules (recursive)
        
        Args:
            hand_total: Current hand total
            deck: Current deck state
            role: 'dealer' or 'player' to determine calculation method
            
        Returns:
            Probability of busting (0.0 to 1.0)
        """
        if hand_total > 21:
            return 1.0
        
        # For players: calculate bust probability on next draw only
        if role == 'player':
            bust_prob = 0.0
            total_deck_count = deck.cards_remaining
            
            for rank in list(deck._card_counts.keys()):
                if deck._card_counts[rank] == 0:
                    continue
                    
                card_prob = deck._card_counts[rank] / total_deck_count
                
                # Handle Ace specially - it can be 1 or 11
                if rank == Rank.ACE:
                    # Use Ace optimally (as 1 if 11 would bust)
                    if hand_total + 11 > 21:
                        # Ace as 1 - check if it busts
                        if hand_total + 1 > 21:
                            bust_prob += card_prob
                    else:
                        # Ace as 11 - check if it busts  
                        if hand_total + 11 > 21:
                            bust_prob += card_prob
                else:
                    # Regular card - check if it busts
                    if hand_total + rank.card_value > 21:
                        bust_prob += card_prob
            
            return bust_prob
        
        # For dealers: recursive calculation following dealer rules
        if hand_total >= 17:
            return 0.0  # Dealer stands

        total_prob = 0.0
        total_deck_count = deck.cards_remaining

        for rank in list(deck._card_counts.keys()):
            if deck._card_counts[rank] == 0:
                continue
                
            # Copy deck and remove 1 card
            new_deck = copy.deepcopy(deck)
            new_deck._card_counts[rank] -= 1
            
            card_prob = deck._card_counts[rank] / total_deck_count
            
            # Handle Ace specially - it can be 1 or 11
            if rank == Rank.ACE:
                # Try Ace as 11 first, then as 1 if it would bust
                if hand_total + 11 > 21:
                    # Must use Ace as 1
                    new_total = hand_total + 1
                    total_prob += card_prob * self._calculate_bust_probability(new_total, new_deck, role)
                else:
                    # Can use Ace as 11, so use it optimally (as 11 unless it causes immediate bust)
                    new_total = hand_total + 11
                    total_prob += card_prob * self._calculate_bust_probability(new_total, new_deck, role)
            else:
                # Regular card
                new_total = hand_total + rank.card_value
                total_prob += card_prob * self._calculate_bust_probability(new_total, new_deck, role)

        return total_prob 