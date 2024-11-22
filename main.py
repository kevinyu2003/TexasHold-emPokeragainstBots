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

def card_generator(ranks, suits):
  """Generates a card from a deck of cards - in the order of 
  suits and ranks lists"""
  for rank in ranks:
      for suit in suits:
          yield rank+suit

def suffle(deck):
  """Shuffles a deck of cards"""
  random.shuffle(deck)
  return deck

def personality():
  """随机电脑性格"""
  return random.uniform(-0.1,0.1)


def gameStart():
    """Start running the game"""
    players_amount = 5 # the number of players 
    if players_amount < 2 or players_amount > 12:
        print("The players amount is invalid.")
        return 0
    