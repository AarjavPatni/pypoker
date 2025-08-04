from __future__ import annotations
import random
from enum import Enum, IntEnum, auto
from itertools import product, combinations
from collections import Counter
from typing import Optional, cast, Iterable
from dataclasses import dataclass, field
from copy import deepcopy
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
    Suit.DIAMONDS: "♦︎",
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
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
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
        self.cards: list[Card] = [
            Card(suit, rank)
            for suit, rank in product(
                cast(Iterable[Suit], Suit), cast(Iterable[Rank], Rank)
            )
        ]  # pyrefly: ignore

    def draw(self, count: int) -> list[Card]:
        # Shuffle isn't required because sample already returns random elements from the list
        cards_drawn = random.sample(self.cards, count)
        for card in cards_drawn:
            self.cards.remove(card)

        return cards_drawn

    # TODO: Perhaps use an iterator? So that I don't have to do .cards


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

    def __repr__(self):
        return self.name


class Player:
    def __init__(self, name: str, chips: int):
        self.name: str = name
        self.chips: int = chips
        self.hand: list[Card] = []
        self.is_active: bool = True

    def __repr__(self):
        return self.name


@dataclass
class Action:
    code: int
    value: Optional[int] = None

    def __post_init__(self):
        if self.code not in (1, 2, 3, 4):
            raise ValueError("Action can only be one of check, call, raise, or fold.")

        if self.code == 3:
            if not self.value:
                raise ValueError("You've raised without specifying an amount.")


@dataclass
class Table:
    small_blind: int
    big_blind: int
    last_player: Player = field(init=False)
    turn_card: Optional[Card] = None
    river_card: Optional[Card] = None
    players: list[Player] = field(default_factory=list)
    deck: Deck = field(default_factory=Deck)
    pot_size: int = 0
    dealer: int = -1
    flop_cards: list[Card] = field(default_factory=list)
    player_actions: Optional[list[list[Action]]] = None

    def __post_init__(self):
        self.current_bet = self.big_blind
        if self.players:
            self.last_player = self.players[0]

    def begin_game(self):
        return self.pre_game().pre_flop().flop().turn().river().showdown().players

    def start_betting(self, first_player: Optional[int] = None) -> Table:
        """
        Goes around the table asking players for actions until the current round is over. Then, returns
        a new table instance.
        """
        mod_table: Table = deepcopy(self)
        first_player = first_player or (self.dealer + 1)
        test_action: Optional[list[Action]] = None

        if mod_table.player_actions:
            test_action = mod_table.player_actions.pop(0)

        if test_action is not None:
            for i in range(len(self.players)):
                current_player_idx = (first_player + i) % len(self.players)
                current_action: Action = test_action.pop(0)

                if (
                    handle_player_action(mod_table, current_player_idx, current_action)
                    is None
                ):
                    raise ValueError(f"Incorrect action: {current_action}")
        else:
            for i in range(len(self.players)):
                current_player_idx = (first_player + i) % len(self.players)
                action: int = int(
                    input(
                        f"{self.players[current_player_idx].name}, choose an action (check (0), call (1), raise (2), fold (3). Current bet to call: {self.current_bet}: "
                    )
                )
                if action == 2:
                    raise_amt: int = int(input("enter raise amount: "))
                    action_arg: Action = Action(2, raise_amt)
                else:
                    action_arg: Action = Action(action)

                while not handle_player_action(
                    mod_table, current_player_idx, action_arg
                ):
                    action: int = int(
                        input(
                            f"{self.players[current_player_idx].name}, choose an action (check (0), call (1), raise (2), fold (3). Current bet to call: {self.current_bet}: "
                        )
                    )
                    if action == "raise":
                        raise_amt: int = int(input("enter raise amount: "))
                        action_arg: Action = Action(2, raise_amt)
                    else:
                        action_arg: Action = Action(action)

        return mod_table

    def pre_game(self):
        mod_table: Table = deepcopy(self)
        # set dealer, move blinds, dealing hole cards
        mod_players: list[Player] = mod_table.players

        logging.info("=== Starting Pre-Game ===")
        mod_pot: int = mod_table.pot_size

        # collect blinds
        mod_players[self.dealer + 1].chips -= self.small_blind
        mod_players[self.dealer + 2].chips -= self.big_blind

        # move to pot
        mod_pot += mod_table.small_blind + mod_table.big_blind

        # dealing hole cards
        for p in mod_players:
            hole_cards: list[Card] = mod_table.deck.draw(2)
            p.hand = hole_cards

        mod_table.current_bet = mod_table.big_blind

        return mod_table

    def pre_flop(self):
        logging.info("=== Starting Pre-Flop ===")
        mod_table: Table = deepcopy(self)
        mod_table.start_betting(mod_table.dealer + 3)
        logging.info("=== Ending Pre-Flop ===")
        mod_table.current_bet = 0

        return mod_table

    def flop(self):
        logging.info("=== Starting Flop ===")
        mod_table: Table = deepcopy(self)
        flop: list[Card] = mod_table.deck.draw(3)
        mod_table.flop_cards = flop

        logging.info(f"Flop cards: {mod_table.flop_cards}")
        mod_table.start_betting()
        logging.info("=== Ending Flop ===")

        mod_table.current_bet = 0

        return mod_table

    def turn(self):
        logging.info("=== Starting Turn ===")
        mod_table: Table = deepcopy(self)
        turn: Card = mod_table.deck.draw(1)[0]
        mod_table.turn_card = turn

        logging.info(f"Turn card: {mod_table.turn_card}")
        mod_table.start_betting()
        logging.info("=== Ending Turn ===")

        mod_table.current_bet = 0

        return mod_table

    def river(self):
        logging.info("=== Starting River ===")
        mod_table: Table = deepcopy(self)
        river: Card = mod_table.deck.draw(1)[0]
        mod_table.river_card = river

        logging.info(f"River card: {mod_table.river_card}")
        mod_table.start_betting()
        logging.info("=== Ending River ===")

        mod_table.current_bet = 0

        return mod_table

    def deal_community_cards(self):
        raise NotImplementedError

        """
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
        """

    def showdown(self):
        mod_table: Table = deepcopy(self)

        logging.info("=== Starting Showdown ===")
        for p in mod_table.players:
            logging.info(f"{p.name} - {p.hand}")

        player_ranks: dict[Player, tuple[HandRank, list[Card]]] = evaluate_table(
            mod_table
        )

        for p in player_ranks:
            print(f"{p} - {player_ranks[p]}")
        player_chips: dict[Player, int] = {}
        player_chips = dict(sorted(player_chips.items(), key=lambda x: x[1]))

        for p in player_chips.items():
            logging.info(f"{p[0]} - {p[1]}")
        logging.info("=== Ending Showdown ===\n")

        return mod_table


def handle_player_action(
    table: Table, player_idx: int, action: Action
) -> Optional[Table]:
    """
    Returns a new table with modified states based on player actions
    """
    mod_table: Table = deepcopy(table)

    match action.code:
        case 1:
            if mod_table.current_bet > 0:
                print("Cannot check. Minimum bet placed.")
                return None

            return mod_table

        case 2:
            mod_table.pot_size += mod_table.current_bet
            mod_table.players[player_idx].chips -= mod_table.current_bet
            return mod_table

        case 3:
            assert action.value is not None
            raise_amt: int = action.value
            
            if raise_amt >= mod_table.players[player_idx].chips:
                print("Error: Raise is greater than available chips")
                return None

            if raise_amt < 2 * table.current_bet:
                print("Minimum raise has to be twice the current bet")
                return None

            mod_table.current_bet = raise_amt
            mod_table.players[player_idx].chips -= raise_amt
            mod_table.pot_size += raise_amt
            mod_table.last_player = mod_table.players[player_idx]
            return mod_table

        case 4:
            mod_table.players[player_idx].is_active = False
            return mod_table

    return None


def evaluate_table(table: Table) -> dict[Player, tuple[HandRank, list[Card]]]:
    community_cards: list[Card] = cast(
        list[Card], table.flop_cards + [table.river_card, table.turn_card]
    )
    player_ranks: dict[Player, tuple[HandRank, list[Card]]] = dict()

    for player in table.players:
        all_hand_combos = list(combinations(player.hand + community_cards, 5))

        best_hand_cards: list[Card] = list(all_hand_combos[0])
        best_hand_rank: HandRank = evaluate_hand(best_hand_cards)

        for hand in all_hand_combos:
            # print(hand, evaluate_hand(list(hand)))
            hand_eval: HandRank = evaluate_hand(list(hand))

            if hand_eval > best_hand_rank:
                best_hand_cards = list(hand)
                best_hand_rank = hand_eval

        player_ranks[player] = (best_hand_rank, best_hand_cards)

    # sort by ranks
    player_ranks = dict(
        sorted(player_ranks.items(), key=lambda x: x[1][0], reverse=True)
    )
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
        if list(card.rank for card in cards) == [12, 0, 1, 2, 3]:
            return True

        # iterate through all elements. i = 0 -> n-1. check if [i+1] - [i] = 1
        for i in range(len(cards) - 1):
            if cards[i + 1].rank - cards[i].rank != 1:
                return False

        return True

    if is_suited(hand):
        if list(i.rank for i in hand) == [8, 9, 10, 11, 12]:
            return HandRank.ROYAL_FLUSH
        elif is_sequence(hand):
            return HandRank.STRAIGHT_FLUSH

        return HandRank.FLUSH
    else:
        # check for straight first
        # keep a dict of occurences for each element in the hand
        # 4 occurences?
        # 3 occurences?
        # 2 occurences twice?
        # 2 occurences once?
        # 2 occurences and 3 occurences?
        # else high card

        if is_sequence(hand):
            return HandRank.STRAIGHT

        hand_counter: Counter = Counter(list(card.rank for card in hand))

        match hand_counter.most_common(1)[0][1]:
            case 4:
                return HandRank.FOUR_OF_A_KIND
            case 3:
                if hand_counter.most_common(2)[1][1] == 2:
                    # [KKK, 2, 2]
                    # [(K, 3), (2, 2)]
                    return HandRank.FULL_HOUSE

                return HandRank.THREE_OF_A_KIND
            case 2:
                # if there are two pairs
                if tuple(o for _, o in hand_counter.most_common(2)) == (2, 2):
                    return HandRank.TWO_PAIR
                else:
                    return HandRank.PAIR

        return HandRank.HIGH_CARD


if __name__ == "__main__":
    raise NotImplementedError
