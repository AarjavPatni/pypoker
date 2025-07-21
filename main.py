import random
from enum import Enum, IntEnum, auto
from itertools import product, combinations
from collections import Counter
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


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
    
    # TODO: Use a draw method

    # TODO: Perhaps use an iterator? So that I don't have to do .cards


class Player:
    def __init__(self, name: str, chips: int):
        self.name: str = name
        self.chips: int = chips
        self.hand: list[Card] = []
        self.is_active: bool = True
        # TODO: do we need position?


class Table:
    def __init__(self, players: list[Player], small_blind: int, big_blind: int, deck: Deck):
        self.players: list[Player] = players
        self.pot_size: int = 0
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind
        self.dealer: int = -1
        self.flop_cards: list[Card] = []
        self.turn_card: Card
        self.river_card: Card
        self.current_bet: int = big_blind
        # self.current_round: dict[Player, int] = {p: 0 for p in self.players}
        self.last_player: Player
        self.deck: Deck = deck


    def handle_player_action(self, player: Player, action: str) -> bool:
        match action:
            case "call":
                self.pot_size += self.current_bet
                player.chips -= self.current_bet
                return True

            case "raise":
                raise_amt: int = int(input("Enter raise amount: ")) # TODO: handle valuerror

                if raise_amt < 2*self.current_bet:
                    print("Minimum raise has to be twice the current bet")
                    return False

                self.current_bet = raise_amt
                player.chips -= raise_amt
                self.pot_size += raise_amt
                return True

            case "fold":
                player.is_active = False
                return True

        return False


    def begin_game(self):
        self.pre_game()
        self.pre_flop()
        self.flop()
        self.turn()
        self.river()
        self.showdown()


    # TODO: set default to dealer
    def start_betting(self, first_player: Optional[int] = None):
        first_player = first_player or (self.dealer + 1)
        # loop through Table
        for i in range(len(self.players)):
            current_player = self.players[(first_player + i) % len(self.players)]
            # !! allow checking / initial bet
            action: str = input(f"{current_player.name}, choose an action (fold, call, raise). Current bet to call: {self.current_bet}: ")
            while not self.handle_player_action(current_player, action):
                action = input(f"{current_player.name}, choose an action (fold, call, raise). Current bet to call: {self.current_bet}: ")


    def pre_game(self):
        logging.info("=== Starting Pre-Game ===")
        deck: Deck = self.deck
        self.dealer += 1
        self.last_player = self.players[self.dealer + 1]

        logging.info(f"Dealer set to player {self.players[self.dealer].name}")

        # collect blinds
        self.players[self.dealer + 1].chips -= self.small_blind
        self.players[self.dealer + 2].chips -= self.big_blind

        logging.info(f"Small blind collected from {self.players[self.dealer + 1].name}")
        logging.info(f"Big blind collected from {self.players[self.dealer + 2].name}")

        # move to pot
        self.pot_size += (self.small_blind + self.big_blind)
        logging.info(f"Pot size updated to {self.pot_size}")

        # dealing hole cards
        for p in self.players:
            hole_cards: list[Card] = random.sample(deck.cards, 2)
            for card in hole_cards:
                deck.cards.remove(card)
                p.hand.append(card)
            logging.info(f"Dealt hole cards to {p.name}: {p.hand}")

        self.current_bet = self.big_blind



    def pre_flop(self):
        logging.info("\n=== Starting Pre-Flop ===")
        self.start_betting(self.dealer + 3)
        logging.info("=== Ending Pre-Flop ===")
        self.current_bet = self.big_blind


    def flop(self):
        logging.info("=== Starting Flop ===")
        deck: Deck = self.deck
        flop: list[Card] = random.sample(deck.cards, 3)
        for card in flop:
            self.deck.cards.remove(card)
            self.flop_cards.append(card)
        logging.info(f"Flop cards: {self.flop_cards}")
        self.start_betting()
        logging.info("=== Ending Flop ===")
        self.current_bet = self.big_blind

    def turn(self):
        logging.info("=== Starting Turn ===")
        deck: Deck = self.deck
        turn: Card = random.sample(deck.cards, 1)[0]
        self.deck.cards.remove(turn)
        self.turn_card = turn
        logging.info(f"Turn card: {self.turn_card}")
        self.start_betting()
        logging.info("=== Ending Turn ===")
        self.current_bet = self.big_blind

    def river(self):
        logging.info("=== Starting River ===")
        deck: Deck = self.deck
        river: Card = random.sample(deck.cards, 1)[0]
        self.deck.cards.remove(river)
        self.turn_card = river
        logging.info(f"River card: {self.river_card}")
        self.start_betting()
        logging.info("=== Ending River ===")
        self.current_bet = self.big_blind


    def deal_community_cards(self):
        community_cards: list[Card] = random.sample(deck.cards, 5)
        self.flop_cards = community_cards[:3]
        self.turn_card = community_cards[3]
        self.river_card = community_cards[4]

        for card in community_cards:
            self.deck.cards.remove(card)

        print(f"flop - {self.flop_cards}")
        self.start_betting()
        self.current_bet = self.big_blind

        print(f"turn - {self.turn_card}")
        self.start_betting()
        self.current_bet = self.big_blind

        print(f"river - {self.river_card}")
        self.start_betting()


    def showdown(self):
        logging.info("=== Starting Showdown ===")
        for p in self.players:
            logging.info(f"{p.name} - {p.hand}")

        player_ranks: dict[Player, HandRank] = evaluate_table(self)
        logging.info(f"Player ranks: {player_ranks}")

        player_chips: dict[Player, int] = {}
        player_chips = dict(sorted(player_chips.items(), key=lambda x: x[1]))

        for p in player_chips.items():
            logging.info(f"{p[0]} - {p[1]}")
        logging.info("=== Ending Showdown ===")


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
    community_cards: list[Card] = table.flop_cards + [table.river_card, table.turn_card]
    player_ranks: dict[Player, HandRank] = dict()

    for player in table.players:
        best_hand: HandRank = HandRank.HIGH_CARD

        for hand in combinations(player.hand + community_cards, 5):
            print(hand, evaluate_hand(list(hand)))
            best_hand = max(best_hand, evaluate_hand(list(hand)))

        player_ranks[player] = best_hand
        print(f"{player.name}: {best_hand}")

    # sort by ranks
    player_ranks = dict(sorted(player_ranks.items(), key=lambda x: x[1])) 
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


if __name__ == "__main__":
    p1: Player = Player("alice", 1000)
    p2: Player = Player("bob", 1000)
    p3: Player = Player("charlie", 1000)
    p4: Player = Player("tom", 1000)
    p5: Player = Player("aarjav", 1000)
    p6: Player = Player("stone", 1000)

    deck: Deck = Deck()

    table: Table = Table([p1, p2, p3, p4, p5, p6], 100, 200, deck)
    table.begin_game()

