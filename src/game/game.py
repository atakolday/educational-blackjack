from typing import List, Optional, Tuple, Dict
from enum import Enum
from .card import Card
from .hand import Hand
from .deck import Deck
from ..counting.counter import CardCounter
from ..strategy.calculator import StrategyCalculator, Action


class GameState(Enum):
    """Game state enumeration."""
    BETTING = "betting"
    DEALING = "dealing"
    INSURANCE = "insurance"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    GAME_OVER = "game_over"


class GameResult(Enum):
    """Game result enumeration."""
    PLAYER_WIN = "player_win"
    DEALER_WIN = "dealer_win"
    PUSH = "push"
    PLAYER_BLACKJACK = "player_blackjack"
    DEALER_BLACKJACK = "dealer_blackjack"
    PLAYER_SURRENDER = "player_surrender"


class BlackjackGame:
    """Main blackjack game engine."""
    
    def __init__(self, num_decks: int = 6, min_bet: float = 10.0, max_bet: float = 1000.0):
        """
        Initialize a new blackjack game.
        
        Args:
            num_decks: Number of decks to use
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
        """
        self.deck = Deck(num_decks)
        self.min_bet = min_bet
        self.max_bet = max_bet
        
        # Game state
        self.state = GameState.BETTING
        self.current_bet = 0.0
        self.insurance_bet = 0.0
        self.player_hands: List[Hand] = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        
        # Game statistics
        self.player_bankroll = 1000.0
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.games_pushed = 0
        
        # Game rules
        self.dealer_hits_soft_17 = True
        self.double_after_split = True
        self.surrender_allowed = True
        self.blackjack_pays_3_to_2 = True
        
        # Card counting
        self.card_counter = CardCounter()
        self.card_counter.reset(self.deck)
        
        # Strategy calculator
        self.strategy_calculator = StrategyCalculator(self.card_counter)
    
    def place_bet(self, amount: float) -> bool:
        """
        Place a bet for the current hand.
        
        Args:
            amount: Bet amount
            
        Returns:
            True if bet was placed successfully, False otherwise
        """
        if self.state != GameState.BETTING:
            return False
        
        if amount < self.min_bet or amount > self.max_bet:
            return False
        
        if amount > self.player_bankroll:
            return False
        
        self.current_bet = amount
        self.player_bankroll -= amount
        self.state = GameState.DEALING
        return True
    
    def deal_initial_cards(self) -> bool:
        """
        Deal the initial two cards to player and dealer.
        
        Returns:
            True if dealing was successful, False otherwise
        """
        if self.state != GameState.DEALING:
            return False
        
        # Check if deck needs shuffling
        if self.deck.should_shuffle():
            self.deck.shuffle()
            self.card_counter.reset(self.deck)
        
        # Burn a card (casino practice)
        burned_card = self.deck.burn_card()
        if burned_card:
            self.card_counter.update_count(burned_card)
        
        # Clear previous hands
        self.player_hands = [Hand()]
        self.dealer_hand.clear()
        self.current_hand_index = 0
        
        # Deal initial cards
        for _ in range(2):
            for hand in self.player_hands:
                card = self.deck.deal_card()
                if card:
                    hand.add_card(card)
                    self.card_counter.update_count(card)
            
            card = self.deck.deal_card()
            if card:
                self.dealer_hand.add_card(card)
                self.card_counter.update_count(card)
        
        # Check if dealer has Ace up card (insurance opportunity)
        if len(self.dealer_hand.cards) >= 2 and self.dealer_hand.cards[1].is_ace:
            self.state = GameState.INSURANCE
            return True
        
        # Check for dealer blackjack
        if self.dealer_hand.is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for dealer blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        # Check for player blackjack
        if self.player_hands[0].is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for player blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        self.state = GameState.PLAYER_TURN
        return True
    
    def hit(self) -> bool:
        """
        Hit the current player hand.
        
        Returns:
            True if hit was successful, False otherwise
        """
        if self.state != GameState.PLAYER_TURN:
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        if current_hand.is_bust or current_hand.is_doubled:
            return False
        
        card = self.deck.deal_card()
        if not card:
            return False
        
        current_hand.add_card(card)
        self.card_counter.update_count(card)
        
        # If hand is bust or doubled, move to next hand
        if current_hand.is_bust or current_hand.is_doubled:
            if self.current_hand_index < len(self.player_hands) - 1:
                self.current_hand_index += 1
            else:
                self.state = GameState.DEALER_TURN
        
        return True
    
    def stand(self) -> bool:
        """
        Stand on the current player hand.
        
        Returns:
            True if stand was successful, False otherwise
        """
        if self.state != GameState.PLAYER_TURN:
            return False
        
        if self.current_hand_index < len(self.player_hands) - 1:
            self.current_hand_index += 1
        else:
            self.state = GameState.DEALER_TURN
        
        return True
    
    def double_down(self) -> bool:
        """
        Double down on the current player hand.
        
        Returns:
            True if double down was successful, False otherwise
        """
        if self.state != GameState.PLAYER_TURN:
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_double:
            return False
        
        if self.current_bet > self.player_bankroll:
            return False
        
        # Double the bet
        self.player_bankroll -= self.current_bet
        self.current_bet *= 2
        
        # Deal one more card
        card = self.deck.deal_card()
        if not card:
            return False
        
        current_hand.add_card(card)
        self.card_counter.update_count(card)
        current_hand.mark_doubled()
        
        # Move to next hand or dealer turn
        if self.current_hand_index < len(self.player_hands) - 1:
            self.current_hand_index += 1
        else:
            self.state = GameState.DEALER_TURN
        
        return True
    
    def split(self) -> bool:
        """
        Split the current player hand.
        
        Returns:
            True if split was successful, False otherwise
        """
        if self.state != GameState.PLAYER_TURN:
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_split:
            return False
        
        if self.current_bet > self.player_bankroll:
            return False
        
        # Create new hand
        split_card = current_hand.cards.pop()
        new_hand = Hand([split_card])
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        
        # Deduct bet for new hand
        self.player_bankroll -= self.current_bet
        
        # Deal cards to both hands
        for i in range(2):
            hand_index = self.current_hand_index + i
            if hand_index < len(self.player_hands):
                card = self.deck.deal_card()
                if card:
                    self.player_hands[hand_index].add_card(card)
                    self.card_counter.update_count(card)
        
        return True
    
    def place_insurance(self, amount: float) -> bool:
        """
        Place an insurance bet.
        
        Args:
            amount: Insurance bet amount (typically half the original bet)
            
        Returns:
            True if insurance bet was placed successfully, False otherwise
        """
        if self.state != GameState.INSURANCE:
            return False
        
        if amount > self.player_bankroll:
            return False
        
        if amount > self.current_bet / 2:
            return False  # Insurance is typically limited to half the original bet
        
        self.insurance_bet = amount
        self.player_bankroll -= amount
        
        # After placing insurance, proceed with the game
        # Check for dealer blackjack
        if self.dealer_hand.is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for dealer blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        # Check for player blackjack
        if self.player_hands[0].is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for player blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        self.state = GameState.PLAYER_TURN
        return True
    
    def decline_insurance(self) -> bool:
        """
        Decline insurance and continue with the game.
        
        Returns:
            True if successful, False otherwise
        """
        if self.state != GameState.INSURANCE:
            return False
        
        # Check for dealer blackjack
        if self.dealer_hand.is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for dealer blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        # Check for player blackjack
        if self.player_hands[0].is_blackjack:
            self.state = GameState.GAME_OVER
            # Process payouts immediately for player blackjack
            results = self.determine_results()
            self.update_statistics(results)
            return True
        
        self.state = GameState.PLAYER_TURN
        return True
    
    def surrender(self) -> bool:
        """
        Surrender the current player hand.
        
        Returns:
            True if surrender was successful, False otherwise
        """
        if self.state != GameState.PLAYER_TURN:
            return False
        
        if not self.surrender_allowed:
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        if current_hand.num_cards != 2:
            return False
        
        current_hand.mark_surrendered()
        
        # Move to next hand or dealer turn
        if self.current_hand_index < len(self.player_hands) - 1:
            self.current_hand_index += 1
        else:
            self.state = GameState.DEALER_TURN
        
        return True
    
    def play_dealer_hand(self) -> None:
        """Play out the dealer's hand according to house rules."""
        if self.state != GameState.DEALER_TURN:
            return
        
        # Check if any player hands are still in play (not busted)
        active_hands = [hand for hand in self.player_hands if not hand.is_bust and not hand.is_surrendered]
        
        # If all hands are busted or surrendered, dealer doesn't need to play
        if not active_hands:
            self.state = GameState.GAME_OVER
            return
        
        # Dealer plays according to house rules
        while self.dealer_hand.total < 17 or (self.dealer_hits_soft_17 and self.dealer_hand.is_soft and self.dealer_hand.total == 17):
            card = self.deck.deal_card()
            if not card:
                break
            self.dealer_hand.add_card(card)
            self.card_counter.update_count(card)
        
        self.state = GameState.GAME_OVER
    
    def determine_results(self) -> List[Tuple[Hand, GameResult, float]]:
        """
        Determine the results for all player hands.
        
        Returns:
            List of tuples containing (hand, result, payout)
        """
        if self.state != GameState.GAME_OVER:
            return []
        
        results = []
        base_bet = self.current_bet / len(self.player_hands)
        
        for hand in self.player_hands:
            if hand.is_surrendered:
                results.append((hand, GameResult.PLAYER_SURRENDER, base_bet * 0.5))
                continue
            
            if hand.is_bust:
                results.append((hand, GameResult.DEALER_WIN, 0.0))
                continue
            
            if hand.is_blackjack:
                if self.dealer_hand.is_blackjack:
                    results.append((hand, GameResult.PUSH, base_bet))
                else:
                    payout = base_bet * (2.5 if self.blackjack_pays_3_to_2 else 2.0)  # Already includes bet + winnings
                    results.append((hand, GameResult.PLAYER_BLACKJACK, payout))
                continue
            
            if self.dealer_hand.is_blackjack:
                results.append((hand, GameResult.DEALER_BLACKJACK, 0.0))
                continue
            
            if self.dealer_hand.is_bust:
                payout = base_bet * (2.0 if hand.is_doubled else 2.0)  # 2x for win (bet + winnings)
                results.append((hand, GameResult.PLAYER_WIN, payout))
                continue
            
            if hand.total > self.dealer_hand.total:
                payout = base_bet * (2.0 if hand.is_doubled else 2.0)  # 2x for win (bet + winnings)
                results.append((hand, GameResult.PLAYER_WIN, payout))
            elif hand.total < self.dealer_hand.total:
                results.append((hand, GameResult.DEALER_WIN, 0.0))
            else:
                results.append((hand, GameResult.PUSH, base_bet))
        
        return results
    
    def update_statistics(self, results: List[Tuple[Hand, GameResult, float]]) -> None:
        """Update game statistics based on results."""
        total_payout = 0.0
        
        # Handle insurance payout
        if self.insurance_bet > 0:
            if self.dealer_hand.is_blackjack:
                # Insurance pays 2:1
                insurance_payout = self.insurance_bet * 3  # bet + 2x winnings
                total_payout += insurance_payout
            # If dealer doesn't have blackjack, insurance bet is lost (no payout)
        
        for hand, result, payout in results:
            total_payout += payout
            
            if result in [GameResult.PLAYER_WIN, GameResult.PLAYER_BLACKJACK]:
                self.games_won += 1
            elif result == GameResult.DEALER_WIN:
                self.games_lost += 1
            elif result == GameResult.PUSH:
                self.games_pushed += 1
        
        self.player_bankroll += total_payout
        self.games_played += 1
        self.insurance_bet = 0.0  # Reset insurance bet
    
    def start_new_hand(self) -> None:
        """Start a new hand, resetting game state."""
        self.state = GameState.BETTING
        self.current_bet = 0.0
        self.insurance_bet = 0.0
        self.player_hands.clear()
        self.dealer_hand.clear()
        self.current_hand_index = 0
    
    def get_current_hand(self) -> Optional[Hand]:
        """Get the current player hand being played."""
        if not self.player_hands or self.current_hand_index >= len(self.player_hands):
            return None
        return self.player_hands[self.current_hand_index]
    
    def get_win_rate(self) -> float:
        """Get the player's win rate."""
        if self.games_played == 0:
            return 0.0
        return self.games_won / self.games_played
    
    def get_strategy_recommendation(self) -> Optional[Dict[str, any]]:
        """Get strategy recommendation for the current situation."""
        if self.state != GameState.PLAYER_TURN:
            return None
        
        current_hand = self.get_current_hand()
        if not current_hand or not self.dealer_hand.cards:
            return None
        
        dealer_up_card = self.dealer_hand.cards[1]
        return self.strategy_calculator.get_strategy_comparison(current_hand, dealer_up_card)
    
    def get_insurance_recommendation(self) -> Optional[Dict[str, any]]:
        """Get insurance recommendation for the current situation."""
        if self.state != GameState.INSURANCE:
            return None
        
        return self.strategy_calculator.get_insurance_recommendation()
    
    def __str__(self) -> str:
        return f"BlackjackGame(state={self.state.value}, bankroll=${self.player_bankroll:.2f})" 