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
    
   

def gameStart():
    """Start running the game"""
    suffled_deck = suffle(deck)
    playing_cards = suffled_deck[0 : 2 * players_amount + 5] #the cards that will be used for the game. 
    

    




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
  gameStart()
  playing = 0