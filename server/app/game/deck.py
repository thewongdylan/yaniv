import random
from app.models import Card

def generate_deck() -> list[Card]:
    suits = ['Diamonds', 'Clubs', 'Hearts', 'Spades']
    values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = []
    for suit in suits:
        for value in values:
            card_id = f"{suit}_{value}"
            deck.append(Card(id=card_id, suit=suit, value=value))

    deck.append(Card(id='Joker_1', suit='Joker', value='0'))
    deck.append(Card(id='Joker_2', suit='Joker', value='0'))

    random.shuffle(deck)
    return deck