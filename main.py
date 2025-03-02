import sys
import time
sys.path.append('.')
from holdem_calc import holdem_calc
import random

class TexasHoldemGame:
    def __init__(self, num_bots=4, starting_chips=10000, small_blind=50):
        self.num_players = num_bots + 1  # +1 for human player
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.reset_game()
        self.initialize_players()

    def initialize_players(self):
        # Initialize chips and personalities for all players
        self.chips = [self.starting_chips] * self.num_players
        self.personalities = [0]  # Human player has no personality modifier
        for _ in range(self.num_players - 1):
            self.personalities.append(random.uniform(-0.2, 0.2))  # Bot personalities

    def reset_game(self):
        # Reset game state for a new hand
        self.pot = 0
        self.community_cards = []
        self.player_hands = {}
        self.players_in_hand = [True] * self.num_players
        self.current_dealer = 0
        self.deck = self.create_deck()
        random.shuffle(self.deck)

    @staticmethod
    def create_deck():
        suits = 'shdc'  # spades, hearts, diamonds, clubs
        ranks = 'AKQJT98765432'
        # Create cards in the format that holdem_calc expects (e.g., 'As' for Ace of spades)
        return [rank + suit for rank in ranks for suit in suits]

    def get_hand_strength(self, player_index):
        if not self.players_in_hand[player_index]:
            return 0
        # Format hole cards and known opponent cards
        board = self.community_cards if self.community_cards else None
        hole_cards = [self.player_hands[player_index][0], self.player_hands[player_index][1], "?", "?"]
        # Calculate probability against known opponent hands
        probability = holdem_calc.calculate(board, False, 1, None, hole_cards , False)
        prob = list(probability)  # type: ignore
        return prob[0]  # Use win probability

    def get_bot_action(self, player_index, current_bet, to_call, round_name):
        # Validate bet amounts
        if to_call < 0 or to_call > self.chips[player_index]:
            return 'fold', 0

        hand_strength = self.get_hand_strength(player_index)
        personality = self.personalities[player_index]
        adjusted_strength = hand_strength + personality

        # Calculate pot odds
        pot_odds = to_call / (self.pot + to_call) if to_call > 0 else 0

        # Adjust aggression based on round
        round_multiplier = {
            'pre-flop': 0.7,  # Less conservative
            'flop': 0.8,     # Less conservative
            'turn': 0.9,     # Same
            'river': 1.0     # Normal
        }.get(round_name, 1.0)

        # Very strong hand
        if adjusted_strength >= 0.35:  # Adjusted threshold
            raise_threshold = 0.4 * round_multiplier
            if random.random() < raise_threshold:
                max_raise = min(
                    self.chips[player_index],
                    current_bet * 2.5,
                    self.pot * 2
                )
                return 'raise', max_raise
            return 'call', min(to_call, self.chips[player_index])

        # Strong hand
        elif adjusted_strength >= 0.25:  # Adjusted threshold
            raise_threshold = 0.3 * round_multiplier
            if random.random() < raise_threshold:
                max_raise = min(
                    self.chips[player_index],
                    current_bet * 2,
                    self.pot * 1.5
                )
                return 'raise', max_raise
            return 'call', min(to_call, self.chips[player_index])

        # Medium hand
        elif adjusted_strength >= 0.15:  # Adjusted threshold
            required_pot_odds = adjusted_strength - (0.05 * round_multiplier)
            if pot_odds <= required_pot_odds:
                return 'call', min(to_call, self.chips[player_index])
            return 'fold', 0

        # Weak hand
        else:
            bluff_threshold = 0.05 * round_multiplier
            if pot_odds < 0.1 and random.random() < bluff_threshold:
                return 'call', min(to_call, self.chips[player_index])
            return 'fold', 0

    def display_game_state(self, show_all_cards=False, debug=True):
        print('\n' + '-'*50)
        print('Community Cards:', ' '.join(self.format_cards(self.community_cards)))
        print(f'Pot: {self.pot}')
        
        # Show player's cards and strength
        player_cards = self.format_cards(self.player_hands.get(0, []))
        player_strength = self.get_hand_strength(0) if self.players_in_hand[0] else 0
        print(f'Your cards: {" ".join(player_cards)} (strength: {player_strength:.2%})')
        print(f'Your chips: {self.chips[0]}')
        
        # Show other players' information, cards and strengths if in debug mode
        for i in range(1, self.num_players):
            if self.players_in_hand[i]:
                bot_strength = self.get_hand_strength(i)
                if show_all_cards or debug:
                    bot_cards = self.format_cards(self.player_hands[i])
                    print(f'Bot {i} cards: {" ".join(bot_cards)} (strength: {bot_strength:.2%}, chips: {self.chips[i]})')
                else:
                    print(f'Bot {i} chips: {self.chips[i]}')

    def get_hand_rank(self, player_index):
        if not self.players_in_hand[player_index]:
            return -1
        cards = self.player_hands[player_index] + self.community_cards
        ranks = [card[0] for card in cards]
        suits = [card[1] for card in cards]
        rank_values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        numeric_ranks = [rank_values[r] for r in ranks]
        numeric_ranks.sort(reverse=True)
        
        # Check for flush
        is_flush = any(suits.count(s) >= 5 for s in 'shdc')
        
        # Check for straight
        straight_ranks = list(set(numeric_ranks))  # Remove duplicates
        straight_ranks.sort(reverse=True)
        
        # Check for regular straight
        is_straight = False
        for i in range(len(straight_ranks) - 4):
            if straight_ranks[i] - straight_ranks[i+4] == 4:
                is_straight = True
                break
                
        # Check for Ace-low straight (A,2,3,4,5)
        if not is_straight and 14 in straight_ranks:  # If we have an Ace
            ace_low = [14, 2, 3, 4, 5]
            if all(r in straight_ranks for r in ace_low):
                is_straight = True
                # Move Ace to the end for proper ranking
                straight_ranks.remove(14)
                straight_ranks.append(1)
        
        # Count frequencies
        rank_counts = {}
        for r in numeric_ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        frequencies = sorted(rank_counts.values(), reverse=True)
        
        # Determine hand rank
        if is_straight and is_flush:
            return 8  # Straight flush
        elif 4 in frequencies:
            return 7  # Four of a kind
        elif frequencies[:2] == [3, 2]:
            return 6  # Full house
        elif is_flush:
            return 5  # Flush
        elif is_straight:
            return 4  # Straight
        elif frequencies[0] == 3:
            return 3  # Three of a kind
        elif frequencies[:2] == [2, 2]:
            return 2  # Two pair
        elif frequencies[0] == 2:
            return 1  # One pair
        else:
            return 0  # High card

    def get_kickers(self, player_index):
        if not self.players_in_hand[player_index]:
            return []
        cards = self.player_hands[player_index] + self.community_cards
        rank_values = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        return sorted([rank_values[card[0]] for card in cards], reverse=True)

    def showdown(self):
        print('\n' + '='*50)
        print('SHOWDOWN')
        print('='*50)
        
        # Display all cards
        self.display_game_state(show_all_cards=True)
        
        best_rank = -1
        winners = []
        
        # First compare hand ranks
        for player in range(self.num_players):
            if self.players_in_hand[player]:
                hand_rank = self.get_hand_rank(player)
                if hand_rank > best_rank:
                    best_rank = hand_rank
                    winners = [player]
                elif hand_rank == best_rank:
                    # If same rank, compare kickers
                    if winners:
                        winner_kickers = self.get_kickers(winners[0])
                        player_kickers = self.get_kickers(player)
                        for w_kick, p_kick in zip(winner_kickers, player_kickers):
                            if p_kick > w_kick:
                                winners = [player]
                                break
                            elif p_kick < w_kick:
                                break
                        else:
                            winners.append(player)  # Exactly equal hands
                    else:
                        winners.append(player)
        
        # Split pot among winners
        split_amount = self.pot // len(winners)
        for winner in winners:
            self.chips[winner] += split_amount
            hand_names = ['High Card', 'One Pair', 'Two Pair', 'Three of a Kind', 
                         'Straight', 'Flush', 'Full House', 'Four of a Kind', 'Straight Flush']
            if winner == 0:
                print(f'You win {split_amount} with {hand_names[best_rank]}')
            else:
                print(f'Bot {winner} wins {split_amount} with {hand_names[best_rank]}')
        self.pot = 0

    @staticmethod
    def format_cards(cards):
        return [card.replace('s', '♠').replace('h', '♥')
                    .replace('d', '♦').replace('c', '♣') for card in cards]

    def betting_round(self, round_name):
        # Display initial state at the start of each round
        print('\n' + '-'*20 + f' {round_name.upper()} ' + '-'*20)
        self.display_game_state()
        
        current_bet = self.big_blind if round_name == 'pre-flop' else 0
        player_bets = [0] * self.num_players
        players_acted = [False] * self.num_players
        active_players = sum(self.players_in_hand)

        # Handle blinds in pre-flop
        if round_name == 'pre-flop':
            sb_pos = (self.current_dealer + 1) % self.num_players
            bb_pos = (self.current_dealer + 2) % self.num_players
            
            # Post small blind
            sb_amount = min(self.small_blind, self.chips[sb_pos])
            self.chips[sb_pos] -= sb_amount
            player_bets[sb_pos] = sb_amount
            self.pot += sb_amount
            
            # Post big blind
            bb_amount = min(self.big_blind, self.chips[bb_pos])
            self.chips[bb_pos] -= bb_amount
            player_bets[bb_pos] = bb_amount
            self.pot += bb_amount
            current_bet = bb_amount

        # Continue betting until all players have acted and bets are equal
        current_player = (bb_pos + 1) % self.num_players if round_name == 'pre-flop' else (self.current_dealer + 1) % self.num_players

        while True:
            if not self.players_in_hand[current_player]:
                current_player = (current_player + 1) % self.num_players
                continue

            to_call = current_bet - player_bets[current_player]

            if current_player == 0:  # Human player
                self.display_game_state()
                print(f'\nTo call: {to_call}')
                action = input('Your action (fold/call/raise): ').lower()
                
                if action == 'fold':
                    self.players_in_hand[current_player] = False
                    active_players -= 1
                elif action in ['call', 'check']:
                    if to_call > 0:
                        call_amount = min(to_call, self.chips[current_player])
                        self.chips[current_player] -= call_amount
                        player_bets[current_player] += call_amount
                        self.pot += call_amount
                elif action == 'raise':
                    try:
                        raise_amount = int(input('Raise to: '))
                        if raise_amount <= 0:
                            print('Raise amount must be positive')
                            continue
                        if raise_amount <= current_bet:
                            print('Raise amount must be greater than current bet')
                            continue
                        if raise_amount > self.chips[current_player] + player_bets[current_player]:
                            print('Not enough chips')
                            continue
                            
                        # Limit raise based on round and pot size
                        max_raise_multiplier = {
                            'pre-flop': 2,   # Max 2x current bet in pre-flop
                            'flop': 2.5,     # Max 2.5x in flop
                            'turn': 3,       # Max 3x in turn
                            'river': 4       # Max 4x in river
                        }.get(round_name, 2)
                        
                        max_raise = min(
                            self.chips[current_player] + player_bets[current_player],
                            max(current_bet * max_raise_multiplier, self.big_blind),  # Ensure minimum raise is at least big blind
                            self.pot * 2  # Limit raise to 2x pot
                        )
                        
                        if raise_amount > max_raise:
                            print(f'Maximum raise allowed is {max_raise}')
                            continue
                            
                        additional = raise_amount - player_bets[current_player]
                        self.chips[current_player] -= additional
                        player_bets[current_player] += additional
                        self.pot += additional
                        current_bet = raise_amount
                        players_acted = [False] * self.num_players
                        players_acted[current_player] = True
                    except ValueError:
                        print('Please enter a valid number')
                        continue
            else:  # Bot players
                action, amount = self.get_bot_action(current_player, current_bet, to_call, round_name)
                time.sleep(1)  # Add delay for readability
                
                if action == 'fold':
                    self.players_in_hand[current_player] = False
                    active_players -= 1
                    print(f'Bot {current_player} folds')
                elif action == 'call':
                    call_amount = min(to_call, self.chips[current_player])
                    self.chips[current_player] -= call_amount
                    player_bets[current_player] += call_amount
                    self.pot += call_amount
                    print(f'Bot {current_player} calls {call_amount}')
                else:  # raise
                    additional = amount - player_bets[current_player]
                    self.chips[current_player] -= additional
                    player_bets[current_player] += additional
                    self.pot += additional
                    current_bet = amount
                    players_acted = [False] * self.num_players
                    players_acted[current_player] = True
                    print(f'Bot {current_player} raises to {amount}')

            players_acted[current_player] = True
            time.sleep(1)  # Add delay after each action
            
            # Check if betting round is complete
            if active_players == 1:
                return
                
            all_acted = True
            for p in range(self.num_players):
                if self.players_in_hand[p] and not players_acted[p]:
                    all_acted = False
                    break
                    
            if all_acted and all(not self.players_in_hand[p] or player_bets[p] == current_bet 
                                for p in range(self.num_players)):
                return
                
            current_player = (current_player + 1) % self.num_players

    def play_hand(self):
        self.reset_game()
        self.deal_hole_cards()
        
        print('\n' + '='*50)
        print('NEW HAND STARTING')
        print('='*50 + '\n')
        time.sleep(1)
        
        # Pre-flop
        print('\n' + '-'*20 + ' PRE-FLOP ' + '-'*20)
        self.betting_round('pre-flop')
        if sum(self.players_in_hand) == 1:
            return self.award_pot()
            
        # Flop
        print('\n' + '-'*20 + ' FLOP ' + '-'*20)
        self.deal_community_cards(3)
        self.betting_round('flop')
        if sum(self.players_in_hand) == 1:
            return self.award_pot()
            
        # Turn
        print('\n' + '-'*20 + ' TURN ' + '-'*20)
        self.deal_community_cards(1)
        self.betting_round('turn')
        if sum(self.players_in_hand) == 1:
            return self.award_pot()
            
        # River
        print('\n' + '-'*20 + ' RIVER ' + '-'*20)
        self.deal_community_cards(1)
        self.betting_round('river')
        if sum(self.players_in_hand) == 1:
            return self.award_pot()
            
        print('\n' + '-'*20 + ' SHOWDOWN ' + '-'*20)
        self.showdown()

    def award_pot(self):
        for i in range(self.num_players):
            if self.players_in_hand[i]:
                self.chips[i] += self.pot
                print(f'Player {i} wins {self.pot}')
                break
        self.pot = 0

    def deal_hole_cards(self):
        # Deal two cards to each player
        for i in range(self.num_players):
            # Take two cards from the top of the deck
            player_cards = [self.deck.pop(), self.deck.pop()]
            self.player_hands[i] = player_cards

    def deal_community_cards(self, num_cards):
        # Deal specified number of community cards
        for _ in range(num_cards):
            self.community_cards.append(self.deck.pop())

def main():
    # Get number of bots from user
    while True:
        try:
            num_bots = int(input('Enter number of bots (1-9): '))
            if 1 <= num_bots <= 9:
                break
            print('Please enter a number between 1 and 9')
        except ValueError:
            print('Please enter a valid number')
    
    # Initialize and start the game
    game = TexasHoldemGame(num_bots=num_bots)
    
    while True:
        game.play_hand()
        
        # Ask to continue
        if input('\nPlay another hand? (y/n): ').lower() != 'y':
            break

if __name__ == '__main__':
    main()
