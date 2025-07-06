from enum import Enum, auto
from itertools import product
import random 


class Suit(Enum):
    SPADES = auto()
    HEARTS = auto()
    CLUBS = auto()
    DIAMONDS = auto()


class Rank(Enum):
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()
    ACE = auto()


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank


class Deck:
    def __init__(self):
        # Create all combinations of suits and ranks using itertools.product
        self.cards = [Card(suit, rank) for suit, rank in product(Suit, Rank)]   # pyrefly: ignore

    # TODO: Perhaps use an iterator? So that I don't have to do .cards


class Player:
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.is_active = True
        # TODO: do we need position?


class Table:
    def __init__(self, players: list[Player], small_blind: int, big_blind: int):
        self.players = players
        self.pot_size = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer = 0


deck: Deck = Deck()

# Naive player simulation
p1: Player = Player("alice", 1000)
p2: Player = Player("bob", 1000)
p3: Player = Player("charlie", 1000)
p4: Player = Player("jacob", 1000)
p5: Player = Player("aarjav", 1000)
p6: Player = Player("john", 1000)

t: Table = Table([p1, p2, p3, p4, p5, p6], 100, 200)

random.shuffle(deck.cards)

for c in deck.cards:
    print(f"Rank: {c.rank}. Suit: {c.suit}")

print(f"Deck contains {len(deck.cards)} cards")

# dealer is already set to 0
# give each player two cards

# for each player, distribute two random cards from the deck
# find random cards
# add to player's hands. remove from deck. 

for p in t.players:
    # select two numbers from the number of cards in the deck
    # add these cards to the players' hands
    # remove from the deck
    card_indices: list[int] = random.sample([i for i in range(len(deck.cards))], 2)
    p.hand += [deck.cards[i] for i in card_indices]
    deck.cards = [card for i, card in enumerate(deck.cards) if i not in card_indices]
    print(vars(p)['name'], vars(p.hand[0]), vars(p.hand[1]))

assert(len(deck.cards) == 40)


# Game Iteration
# TODO: Use circular list

"""
0. shuffle the deck
1. dealer = 0 (! not for every game)
2. dealing mechanism. each player gets 2 cards.
3. 3 cards are opened in the center. removed from the deck.
4. round 1
    a. small_blind and big_blind are played
    b. rest of the players match the big_blind
    c. dealer matches the big_blind
    d. small_blind matches the big_blind
    e. added to pot
5. (burned card)
6. card revealed. removed from the deck.
7. round 2
    a. everybody just plays 200
    b. add to pot
8. (burned card)
9. card revealed. removed from deck.
10. round 3
    a. everybody bets 200
    b. add to pot
11. show of hands
12. ranks calculated
13. player.chips += pot. pot = 0.
14. dealer incremented
"""

