#!/usr/bin/env python3
"""
Blackjack Game with Card Counting and Statistical Strategy
Main entry point with console interface for testing.
"""

import sys
from src.game.game import BlackjackGame, GameState, GameResult


def print_game_state(game: BlackjackGame) -> None:
    """Print the current game state."""
    print("\n" + "="*50)
    print(f"Bankroll: ${game.player_bankroll:.2f}")
    print(f"Games Played: {game.games_played}")
    print(f"Win Rate: {game.get_win_rate():.2%}")
    print(f"Deck: {game.deck}")
    print(f"Count: {game.card_counter}")
    print(f"Count Status: {game.card_counter.get_count_status()}")
    print(f"State: {game.state.value}")
    
    # Show strategy recommendation if available
    strategy = game.get_strategy_recommendation()
    if strategy:
        print(f"\nStrategy Recommendation:")
        print(f"  Optimal Action: {strategy['optimal_action'].value.upper()}")
        print(f"  Expected Value: {strategy['optimal_ev']:.3f}")
        print(f"  Basic Strategy: {strategy['basic_action'].value.upper()}")
        print(f"  Basic Strategy EV: {strategy['basic_ev']:.3f}")
        if strategy['count_advantage']:
            print(f"  Count Advantage: +{strategy['ev_difference']:.3f} EV")
        else:
            print(f"  Count Disadvantage: {strategy['ev_difference']:.3f} EV")
    
    # Show insurance recommendation if available
    insurance = game.get_insurance_recommendation()
    if insurance:
        print(f"\nInsurance Recommendation:")
        print(f"  Take Insurance: {'YES' if insurance['should_take_insurance'] else 'NO'}")
        print(f"  Insurance EV: {insurance['insurance_ev']:.3f}")
        print(f"  Dealer Blackjack Probability: {insurance['dealer_blackjack_probability']:.1%}")
        if insurance['count_advantage']:
            print(f"  Count Advantage: +{insurance['insurance_ev']:.3f} EV")
        else:
            print(f"  Count Disadvantage: {insurance['insurance_ev']:.3f} EV")
    
    if game.current_bet > 0:
        print(f"Current Bet: ${game.current_bet:.2f}")
    
    if game.dealer_hand.cards:
        print(f"Dealer: {game.dealer_hand.get_display_string(hide_first=game.state != GameState.GAME_OVER)}")
        if game.state == GameState.GAME_OVER:
            print(f"Dealer Total: {game.dealer_hand.total}")
    
    if game.player_hands:
        for i, hand in enumerate(game.player_hands):
            marker = " → " if i == game.current_hand_index else "   "
            print(f"Player{marker}{hand}")
    
    print("="*50)


def print_available_actions(game: BlackjackGame) -> None:
    """Print available actions for the current state."""
    if game.state == GameState.BETTING:
        print("\nAvailable Actions:")
        print("  bet <amount> - Place a bet")
        print("  quit - Exit the game")
    
    elif game.state == GameState.INSURANCE:
        max_insurance = game.current_bet / 2
        print(f"\nInsurance Available (Dealer shows Ace)")
        print(f"Maximum insurance: ${max_insurance:.2f}")
        print("\nAvailable Actions:")
        print("  insurance <amount> - Take insurance")
        print("  decline - Decline insurance")
        print("  quit - Exit the game")
    
    elif game.state == GameState.PLAYER_TURN:
        current_hand = game.get_current_hand()
        if not current_hand:
            return
        
        print("\nAvailable Actions:")
        print("  hit - Take another card")
        print("  stand - Keep current hand")
        
        if current_hand.can_double and game.current_bet <= game.player_bankroll:
            print("  double - Double down")
        
        if current_hand.can_split and game.current_bet <= game.player_bankroll:
            print("  split - Split the hand")
        
        if game.surrender_allowed and current_hand.num_cards == 2:
            print("  surrender - Surrender hand")
    
    elif game.state == GameState.GAME_OVER:
        print("\nGame Over! Actions:")
        print("  new - Start new hand")
        print("  quit - Exit the game")


def print_results(results: list) -> None:
    """Print game results."""
    print("\n" + "="*50)
    print("GAME RESULTS")
    print("="*50)
    
    for i, (hand, result, payout) in enumerate(results):
        print(f"Hand {i+1}: {hand}")
        print(f"Result: {result.value.replace('_', ' ').title()}")
        if payout > 0:
            print(f"Payout: ${payout:.2f}")
        print()


def main():
    """Main game loop."""
    print("Welcome to Blackjack with Card Counting!")
    print("This game includes statistical strategy calculation based on the running count.")
    
    # Initialize game
    game = BlackjackGame(num_decks=6, min_bet=10.0, max_bet=1000.0)
    
    while True:
        print_game_state(game)
        print_available_actions(game)
        
        try:
            command = input("\nEnter action: ").strip().lower()
            
            if command == "quit":
                print("Thanks for playing!")
                break
            
            elif game.state == GameState.BETTING:
                if command.startswith("bet "):
                    try:
                        amount = float(command[4:])
                        if game.place_bet(amount):
                            print(f"Bet placed: ${amount:.2f}")
                            if game.deal_initial_cards():
                                print("Cards dealt!")
                            else:
                                print("Error dealing cards!")
                        else:
                            print("Invalid bet amount!")
                    except ValueError:
                        print("Invalid bet amount!")
                else:
                    print("Invalid command!")
            
            elif game.state == GameState.INSURANCE:
                if command.startswith("insurance "):
                    try:
                        amount = float(command[10:])
                        if game.place_insurance(amount):
                            print(f"Insurance bet placed: ${amount:.2f}")
                        else:
                            print("Invalid insurance amount!")
                    except ValueError:
                        print("Invalid insurance amount!")
                elif command == "decline":
                    if game.decline_insurance():
                        print("Insurance declined. Continuing with game...")
                    else:
                        print("Error declining insurance!")
                else:
                    print("Invalid command!")
            
            elif game.state == GameState.PLAYER_TURN:
                if command == "hit":
                    if game.hit():
                        print("Card dealt!")
                    else:
                        print("Cannot hit!")
                
                elif command == "stand":
                    if game.stand():
                        print("Standing...")
                    else:
                        print("Cannot stand!")
                
                elif command == "double":
                    if game.double_down():
                        print("Doubled down!")
                    else:
                        print("Cannot double down!")
                
                elif command == "split":
                    if game.split():
                        print("Hand split!")
                    else:
                        print("Cannot split!")
                
                elif command == "surrender":
                    if game.surrender():
                        print("Hand surrendered!")
                    else:
                        print("Cannot surrender!")
                
                else:
                    print("Invalid command!")
                
                # Check if we need to play dealer hand
                if game.state == GameState.DEALER_TURN:
                    print("Dealer's turn...")
                    game.play_dealer_hand()
                    results = game.determine_results()
                    print_results(results)
                    game.update_statistics(results)
            
            elif game.state == GameState.GAME_OVER:
                if command == "new":
                    game.start_new_hand()
                    print("New hand started!")
                else:
                    print("Invalid command!")
            
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main() 