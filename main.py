import random
from enum import Enum, IntEnum, auto
from itertools import product, combinations
from collections import Counter


class Suit(Enum):
    SPADES = auto()
    HEARTS = auto()
    CLUBS = auto()
    DIAMONDS = auto()


suit_symbols: dict[Suit, str] = {
    Suit.SPADES: "♠︎",
    Suit.HEARTS: "♥︎",
    Suit.CLUBS: "♣︎",
    Suit.DIAMONDS: "♦︎"
}


class Rank(IntEnum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12


rank_symbols = {
    Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
    Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
    Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A"
}


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit: Suit = suit
        self.rank: Rank = rank

    def __str__(self):
        return f"{suit_symbols[self.suit]} {rank_symbols[self.rank]}"

    def __repr__(self):
        return self.__str__()


class Deck:
    def __init__(self):
        # Create all combinations of suits and ranks using itertools.product
        self.cards: list[Card] = [Card(suit, rank) for suit, rank in product(Suit, Rank)]   # pyrefly: ignore

    def shuffle(self):
        random.shuffle(self.cards)

    # TODO: Perhaps use an iterator? So that I don't have to do .cards


class Player:
    def __init__(self, name: str, chips: int):
        self.name: str = name
        self.chips: int = chips
        self.hand: list[Card] = []
        self.current_bet: int = 0
        self.is_active: bool = True
        # TODO: do we need position?


class Table:
    def __init__(self, players: list[Player], small_blind: int, big_blind: int):
        self.players: list[Player] = players
        self.pot_size: int = 0
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind
        self.dealer: int = 0
        self.flop: list[Card]
        self.turn: Card
        self.river: Card


class HandRank(IntEnum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


def evaluate_table(table: Table) -> dict[Player, HandRank]:
    community_cards: list[Card] = table.flop + [table.river, table.turn]
    player_ranks: dict[Player, HandRank] = dict()

    for player in table.players:
        best_hand: HandRank = HandRank.HIGH_CARD

        for hand in combinations(player.hand + community_cards, 5):
            print(hand, evaluate_hand(list(hand)))
            best_hand = max(best_hand, evaluate_hand(list(hand)))

        player_ranks[player] = best_hand
        print(f"{player.name}: {best_hand}")
        
    return player_ranks



def evaluate_hand(hand: list[Card]) -> HandRank:
    """
    if suited -> royal flush, straight flush, flush
    else -> four of a kind, full house, straight, three of a kind, two pair, pair, high card
    """

    hand.sort(key=lambda c: c.rank)


    def is_suited(cards: list[Card]) -> bool:
        return len(set(i.suit for i in cards)) == 1

    def is_sequence(cards: list[Card]) -> bool:
        if (list(card.rank for card in cards) == [12, 0, 1, 2, 3]):
            return True

        # iterate through all elements. i = 0 -> n-1. check if [i+1] - [i] = 1
        for i in range(len(cards) - 1):
            if cards[i+1].rank - cards[i].rank != 1:
                return False
    
        return True

    if (is_suited(hand)):
        if (list(i.rank for i in hand) == [8, 9, 10, 11, 12]):
            return HandRank.ROYAL_FLUSH
        elif (is_sequence(hand)):
            return HandRank.STRAIGHT_FLUSH
        
        return HandRank.FLUSH
    else:
        # print("not suited...")
        # check for straight first
        # keep a dict of occurences for each element in the hand
        # 4 occurences?
        # 3 occurences?
        # 2 occurences twice?
        # 2 occurences once?
        # 2 occurences and 3 occurences?
        # else high card

        """
        - [x] find a way to map Ace to both 0 and 12. or find a better solution to sort the cards
          because A = 12 and at the end of the 2 3 4 5 A card combination
        - [x] stress test evaluate_table function for all 21 combinations
        """

        if (is_sequence(hand)):
            return HandRank.STRAIGHT

        hand_counter: Counter = Counter(list(card.rank for card in hand))

        match hand_counter.most_common(1)[0][1]:
            case 4:
                return HandRank.FOUR_OF_A_KIND
            case 3:
                if (hand_counter.most_common(2)[1][1] == 2):
                    # [KKK, 2, 2]
                    # [(K, 3), (2, 2)]
                    return HandRank.FULL_HOUSE

                return HandRank.THREE_OF_A_KIND
            case 2:
                # if there are two pairs
                if (tuple(o for _, o in hand_counter.most_common(2)) == (2, 2)):
                    return HandRank.TWO_PAIR
                else:
                    return HandRank.PAIR

        
        return HandRank.HIGH_CARD



deck: Deck = Deck()

# Naive player simulation
p1: Player = Player("alice", 1000)
p2: Player = Player("bob", 1000)
p3: Player = Player("charlie", 1000)
p4: Player = Player("jacob", 1000)
p5: Player = Player("aarjav", 1000)
p6: Player = Player("john", 1000)

t: Table = Table([p1, p2, p3, p4, p5, p6], 100, 200)

deck.shuffle()

# TODO: use generator here instead
# for i in deck.cards:
#     print(i)

print(f"Deck contains {len(deck.cards)} cards")

# dealer is already set to 0
# give each player two cards

# for each player, distribute two random cards from the deck
# find random cards
# add to player's hands. remove from deck.

print()

# Dealing Cards
for i, p in enumerate(t.players):
    # select two numbers from the number of cards in the deck
    # add these cards to the players' hands
    # remove from the deck
    card_indices: list[int] = random.sample([i for i in range(len(deck.cards))], 2)
    p.hand += [deck.cards[i] for i in card_indices]
    deck.cards = [card for i, card in enumerate(deck.cards) if i not in card_indices]
    print(f"{i+1}. {p.name}: ", p.hand)

assert (len(deck.cards) == 40)
print()

# now for the community cards, where should they be added? should they be created when the table is
# initiated or when the deck is dealt? i think the table should have the community cards
# undefined and when the card is dealt the attributes are set

# simply remove two cards from the deck and set them as attributes for table flop, turn, and river

community_card_indices: list[int] = random.sample([i for i in range(40)], 5)
t.flop = [deck.cards[community_card_indices[i]] for i in range(3)]
t.turn = deck.cards[community_card_indices[3]]
t.river = deck.cards[community_card_indices[4]]

print(f"Flop: {[str(i) for i in t.flop]}")
print(f"Turn: {t.turn}")
print(f"River: {t.river}")

print(evaluate_table(t))

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
