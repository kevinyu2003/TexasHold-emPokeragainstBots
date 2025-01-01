import holdem_calc
import random
suits = u'shdc' #spade heart diamond club 
ranks = u'AKQJT98765432' # T is 10
Sequence = {"2":1,
            '3':2,
            "4":3,
            "5":4,
            "6":5,
            '7':6,
            '8':7,
            '9':8,
            'T':9,
            "J":10,
            "Q":11,
            'K':12,
            "A":13}

def card_generator(ranks = ranks, suits = suits):
  """Generates a card from a deck of cards - in the order of 
  suits and ranks lists"""
  for rank in ranks:
      for suit in suits:
          yield rank+suit
def deck_generator(cards = card_generator()):
  deck = []
  for card in cards:
    deck.append(card)
  return deck


def suffle(deck):
  """Shuffles a deck of cards"""
  random.shuffle(deck)
  return deck

def personality():
  """随机电脑性格"""
  return random.uniform(-0.1,0.1)

def handvalue(hand):
  """计算手牌的概率"""
  probability=holdem_calc.calculate(None,False, 1, None, [hand[0], hand[1], "?", "?"], False)
  prob = list(probability) # type: ignore
  return prob[1]



def find_first_player_index(big_blind_index):
  for i in  range(big_blind_index+1, players_amount):
    if players_in_game[i] == 1: 
        return i
  return 0 #  if all the bot after big blind is out the player is the first one to action
    
   

def game_loop():
    while True:
        # Deal cards
        deal_cards()

        # Pre-flop betting round
        betting_round("Pre-Flop")

        # Flop
        deal_community_cards(3)
        betting_round("Post-Flop")

        # Turn
        deal_community_cards(1)
        betting_round("Post-Turn")

        # River
        deal_community_cards(1)
        betting_round("Post-River")

        # Showdown
        showdown()

        # Reset for next hand
        reset_game()
    
def deal_cards():
    for player in range(players_amount):
        players_hands[player] = [playing_cards.pop(0), playing_cards.pop(0)]

def deal_community_cards(num_cards):
    for _ in range(num_cards):
        community_cards.append(playing_cards.pop(0))

def betting_round(round_name):
    current_bet = small_blind_amount if round_name == "Pre-Flop" else 0
    current_player = find_first_player_index(big_blind_index)

    while True:
        if players_in_game[current_player]:
            if current_player == 0:  # Human player
                # Get user input for action
                action = get_user_action()
            else:  # Computer player
                action = computer_action(current_player, current_bet, pot_size, community_cards)

            # Process the action
            if action == "fold":
                players_in_game[current_player] = 0
            elif action == "check" or action == "call":
                pot_size += current_bet
            elif action == "raise":
                raise_amount = get_raise_amount(current_player, current_bet)
                pot_size += raise_amount
                current_bet = raise_amount

        current_player = (current_player + 1) % players_amount

        # Check if betting round is over
        if all(player_in_game == 0 or player_bet == current_bet for player_in_game, player_bet in zip(players_in_game, player_bets)):
            break

def get_user_action():
    while True:
        action = input("Enter your action (fold/check/call/raise): ").lower()
        if action in ["fold", "check", "call","raise"]:
            return action
        # elif action == "raise":
        #     while True:
        #         try:
        #             raise_amount = int(input("Enter raise amount: "))
        #             if raise_amount > 0:
        #                 return "raise", raise_amount
        #             else:
        #                 print("Raise amount must be positive.")
        #         except ValueError:
        #             print("Invalid input. Please enter a number.")
        else:
            print("Invalid action. Please try again.")

def get_raise_amount(current_player, current_bet):
    if current_player != 0:
      return get_computer_raise_amount(current_player, current_bet, pot_size, community_cards)
    while True:
        try:
            raise_amount = int(input(f"Player {current_player}, enter your raise amount: "))
            if raise_amount > current_bet:
                return raise_amount
            else:
                print("Raise amount must be greater than the current bet.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
def showdown():
    # Find the best hand among active players
    best_hand_value = 0
    best_hand_player = None
    for player in range(players_amount):
        if players_in_game[player]:
            hand_value = handvalue(players_hands[player], community_cards)
            if hand_value > best_hand_value:
                best_hand_value = hand_value
                best_hand_player = player
    chip_stack[best_hand_player] += pot
    
    # Distribute the pot to the winner(s)
    # ...
                
def computer_action(player_index, current_bet, pot_size, community_cards):
    hand_strength = handvalue(players_hands[player_index], community_cards)
    personality = personalities[player_index]
    if hand_strength + personality >= .30:
        return check

    # Implement decision-making logic based on hand strength, personality, pot odds, and other factors
    # ...
    if hand_strength + personality <= .2:
        action = "fold"
    elif hand_strength + personality <= .4
    return action  # "fold", "check", "call", or "raise"

def get_computer_raise_amount(player_index, current_bet, pot_size, community_cards):
    hand_strength = handvalue(players_hands[player_index], community_cards)
    personality = personalities[player_index]
    if hand_strength + personality >= 0.5:
        return chip_stack[player_index]
    elif hand_strength + personality >= 0.4:
        return current_bet + random.randint(1,10)*100
    else:
        return current_bet + 100
    
def reset_game():
    playing = 0

playing = 1
while playing: 
  """define global values"""
  players_amount = 5
  if players_amount < 2 or players_amount > 12:
      print("The players amount is invalid.")
      break
  print(players_amount)
  players_in_game = [1] * players_amount # an array to represent each player still in the game or not players_in_game[0] is the user
  rounds_played = 0 #used to keep track of how many games played
  small_blind_index = rounds_played / players_amount #the player index of the small blind should increment evertime game ends. 
  big_blind_index = small_blind_index + 1
  deck = deck_generator()
  suffled_deck = suffle(deck)
  playing_cards = suffled_deck[0 : 2 * players_amount + 5]
  players_hands = {}
  community_cards = []
  personalities = []
  for i in range(1,players_amount):
    personalities[i] = personality()  
  chip_stack = [10000] * players_amount
  pot_size = 0
  game_loop()
