import unittest
from main import ( Player, Action, Table, Card, Suit, HandRank, Rank, Deck, evaluate_table,
                  evaluate_hand, handle_player_action, suit_symbols, rank_symbols )
from dataclasses import dataclass
import logging
import random
from copy import deepcopy


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@dataclass
class GameTest:
    initial_player_chips: int
    rounds: list[list[Action]]
    table: Table
    runs: int = 1

    def simulate_game(self) -> list[Player]:
        """
        1. Start the round (0 = preflop, 3 = river)
        2. Go around the table and run the action for each corresponding player
        3. Return the modified table
        """
        self.table.player_actions = self.rounds
        return self.table.begin_game()


class TestPokerValid(unittest.TestCase):
    def test_raise_call_then_check(self):
        players = [Player("Alice", 1000), Player("Bob", 1000)]
        rounds: list[list[Action]] = [
            [Action(3, 100), Action(2)],
            [Action(1), Action(1)],
            [Action(1), Action(1)],
            [Action(1), Action(1)],
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=1000, rounds=rounds, table=table)
        game.simulate_game()

    def test_raises_every_street(self):
        players = [Player("A", 2000), Player("B", 2000)]
        rounds = [
            [Action(3, 300), Action(2)],
            [Action(3, 400), Action(2)],
            [Action(3, 500), Action(2)],
            [Action(3, 600), Action(2)],
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=2000, rounds=rounds, table=table)
        game.simulate_game()

    def test_fold_on_turn(self):
        players = [Player("Hero", 1500), Player("Villain", 1500)]
        rounds = [
            [Action(3, 100), Action(2)],
            [Action(3, 200), Action(2)],
            [Action(3, 300), Action(4)],
            [Action(1)],
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=1500, rounds=rounds, table=table)
        game.simulate_game()


class TestPokerInvalid(unittest.TestCase):
    def test_raise_below_minimum(self):
        players = [Player("A", 1000), Player("B", 1000)]
        rounds = [
            [Action(3, 30), Action(2)],  # assuming current bet is 20, should be ≥40
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=1000, rounds=rounds, table=table)

        with self.assertRaises(ValueError):
            game.simulate_game()

    def test_raise_with_insufficient_chips(self):
        players = [Player("Shorty", 50), Player("BigStack", 1000)]
        rounds = [
            [Action(3, 100), Action(2)],
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=1000, rounds=rounds, table=table)

        with self.assertRaises(ValueError):
            game.simulate_game()


class TestPokerHandEvaluation(unittest.TestCase):
    def test_royal_flush_beats_straight(self):
        players = [Player("Alice", 1000), Player("Bob", 1000)]
        players[0].hand = [Card(Suit.SPADES, Rank.ACE), Card(Suit.SPADES, Rank.KING)]
        players[1].hand = [Card(Suit.CLUBS, Rank.NINE), Card(Suit.DIAMONDS, Rank.EIGHT)]

        table = Table(small_blind=10, big_blind=20, players=players)
        table.flop_cards = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.SPADES, Rank.TEN),
        ]
        table.turn_card = Card(Suit.HEARTS, Rank.TWO)
        table.river_card = Card(Suit.CLUBS, Rank.THREE)

        results = evaluate_table(table)
        winner = list(results.keys())[0]
        self.assertEqual(results[winner][0], HandRank.ROYAL_FLUSH)
        self.assertEqual(winner.name, "Alice")

    def test_full_house_beats_flush(self):
        players = [Player("Alice", 1000), Player("Bob", 1000)]
        players[0].hand = [Card(Suit.DIAMONDS, Rank.KING), Card(Suit.CLUBS, Rank.KING)]
        players[1].hand = [Card(Suit.SPADES, Rank.TWO), Card(Suit.SPADES, Rank.FOUR)]

        table = Table(small_blind=10, big_blind=20, players=players)
        table.flop_cards = [
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.THREE),
            Card(Suit.SPADES, Rank.THREE),
        ]
        table.turn_card = Card(Suit.SPADES, Rank.JACK)
        table.river_card = Card(Suit.SPADES, Rank.ACE)

        results = evaluate_table(table)
        winner = list(results.keys())[0]
        print(results)
        self.assertEqual(results[winner][0], HandRank.FULL_HOUSE)
        self.assertEqual(winner.name, "Alice")

    def test_pair_beats_high_card(self):
        players = [Player("Alice", 1000), Player("Bob", 1000)]
        players[0].hand = [Card(Suit.HEARTS, Rank.QUEEN), Card(Suit.CLUBS, Rank.SEVEN)]
        players[1].hand = [Card(Suit.SPADES, Rank.ACE), Card(Suit.DIAMONDS, Rank.TEN)]

        table = Table(small_blind=10, big_blind=20, players=players)
        table.flop_cards = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.FOUR),
            Card(Suit.DIAMONDS, Rank.SIX),
        ]
        table.turn_card = Card(Suit.HEARTS, Rank.NINE)
        table.river_card = Card(Suit.CLUBS, Rank.JACK)

        results = evaluate_table(table)
        winner = list(results.keys())[0]
        print(results)
        self.assertEqual(results[winner][0], HandRank.PAIR)
        self.assertEqual(winner.name, "Alice")


class TestExtendedCoverage(unittest.TestCase):
    def setUp(self):
        random.seed(0)  # deterministic where randomness is involved

    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        unique = {(c.suit, c.rank) for c in deck.cards}
        self.assertEqual(len(unique), 52)

    def test_draw_removes_cards_and_no_duplicates(self):
        deck = Deck()
        drawn = deck.draw(5)
        self.assertEqual(len(drawn), 5)
        self.assertEqual(len(deck.cards), 47)
        drawn_set = {(c.suit, c.rank) for c in drawn}
        remain_set = {(c.suit, c.rank) for c in deck.cards}
        self.assertTrue(drawn_set.isdisjoint(remain_set))

    def test_draw_too_many_raises(self):
        deck = Deck()
        with self.assertRaises(ValueError):
            deck.draw(53)  # more than 52

    def test_card_str_and_repr(self):
        card = Card(Suit.SPADES, Rank.ACE)
        s = str(card)
        self.assertIn(suit_symbols[Suit.SPADES], s)
        self.assertIn(rank_symbols[Rank.ACE], s)
        self.assertEqual(repr(card), s)

    def test_action_validation_errors(self):
        with self.assertRaises(ValueError):
            Action(0)  # invalid code
        with self.assertRaises(ValueError):
            Action(3, None)  # raise without amount

    def test_handle_player_action_check_with_bet(self):
        table = Table(10, 20, players=[Player("P", 1000), Player("Q", 1000)])
        table.current_bet = 100
        result = handle_player_action(table, 0, Action(1))
        self.assertIsNone(result)  # cannot check when bet exists

    def test_handle_player_action_call_raise_fold(self):
        table = Table(10, 20, players=[Player("P", 1000), Player("Q", 1000)])
        table.current_bet = 50
        # call
        before = table.players[0].chips
        result = handle_player_action(table, 0, Action(2))
        self.assertIsNotNone(result)
        self.assertEqual(result.pot_size, 50)
        self.assertEqual(result.players[0].chips, before - 50)

        # raise below minimum (min is 2 * current_bet)
        table.current_bet = 20
        res = handle_player_action(table, 0, Action(3, 30))
        self.assertIsNone(res)

        # raise exceeding chips
        table.current_bet = 10
        table.players[0].chips = 15
        res2 = handle_player_action(table, 0, Action(3, 20))  # 20 >= 15 triggers error
        self.assertIsNone(res2)

        # valid raise
        table = Table(10, 20, players=[Player("P", 1000), Player("Q", 1000)])
        table.current_bet = 30
        valid = handle_player_action(table, 0, Action(3, 60))  # exactly 2x
        self.assertIsNotNone(valid)
        self.assertEqual(valid.current_bet, 60)
        self.assertEqual(valid.pot_size, 60)
        self.assertEqual(valid.players[0].chips, 1000 - 60)

        # fold
        folded = handle_player_action(table, 1, Action(4))
        self.assertIsNotNone(folded)
        self.assertFalse(folded.players[1].is_active)

    def test_evaluate_hand_rankings(self):
        def mk(rank, suit): return Card(suit, rank)

        # High card
        hand = [
            mk(Rank.TWO, Suit.SPADES),
            mk(Rank.FIVE, Suit.HEARTS),
            mk(Rank.SEVEN, Suit.CLUBS),
            mk(Rank.NINE, Suit.DIAMONDS),
            mk(Rank.JACK, Suit.HEARTS),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.HIGH_CARD)

        # Pair
        hand = [
            mk(Rank.NINE, Suit.SPADES),
            mk(Rank.NINE, Suit.HEARTS),
            mk(Rank.TWO, Suit.CLUBS),
            mk(Rank.THREE, Suit.DIAMONDS),
            mk(Rank.FOUR, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.PAIR)

        # Two Pair
        hand = [
            mk(Rank.TEN, Suit.SPADES),
            mk(Rank.TEN, Suit.HEARTS),
            mk(Rank.JACK, Suit.CLUBS),
            mk(Rank.JACK, Suit.DIAMONDS),
            mk(Rank.THREE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.TWO_PAIR)

        # Three of a Kind
        hand = [
            mk(Rank.FOUR, Suit.SPADES),
            mk(Rank.FOUR, Suit.HEARTS),
            mk(Rank.FOUR, Suit.CLUBS),
            mk(Rank.SEVEN, Suit.DIAMONDS),
            mk(Rank.NINE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.THREE_OF_A_KIND)

        # Straight (5-9)
        hand = [
            mk(Rank.FIVE, Suit.SPADES),
            mk(Rank.SIX, Suit.HEARTS),
            mk(Rank.SEVEN, Suit.CLUBS),
            mk(Rank.EIGHT, Suit.DIAMONDS),
            mk(Rank.NINE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.STRAIGHT)

        # Flush
        hand = [
            mk(Rank.TWO, Suit.HEARTS),
            mk(Rank.FIVE, Suit.HEARTS),
            mk(Rank.SEVEN, Suit.HEARTS),
            mk(Rank.NINE, Suit.HEARTS),
            mk(Rank.KING, Suit.HEARTS),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.FLUSH)

        # Full House
        hand = [
            mk(Rank.KING, Suit.SPADES),
            mk(Rank.KING, Suit.HEARTS),
            mk(Rank.KING, Suit.CLUBS),
            mk(Rank.THREE, Suit.DIAMONDS),
            mk(Rank.THREE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.FULL_HOUSE)

        # Four of a Kind
        hand = [
            mk(Rank.ACE, Suit.SPADES),
            mk(Rank.ACE, Suit.HEARTS),
            mk(Rank.ACE, Suit.CLUBS),
            mk(Rank.ACE, Suit.DIAMONDS),
            mk(Rank.FIVE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.FOUR_OF_A_KIND)

        # Straight Flush (6-10 hearts)
        hand = [
            mk(Rank.SIX, Suit.HEARTS),
            mk(Rank.SEVEN, Suit.HEARTS),
            mk(Rank.EIGHT, Suit.HEARTS),
            mk(Rank.NINE, Suit.HEARTS),
            mk(Rank.TEN, Suit.HEARTS),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.STRAIGHT_FLUSH)

        # Royal Flush
        hand = [
            mk(Rank.TEN, Suit.SPADES),
            mk(Rank.JACK, Suit.SPADES),
            mk(Rank.QUEEN, Suit.SPADES),
            mk(Rank.KING, Suit.SPADES),
            mk(Rank.ACE, Suit.SPADES),
        ]
        self.assertEqual(evaluate_hand(hand), HandRank.ROYAL_FLUSH)

        # Wheel straight is NOT treated as straight in current implementation
        hand = [
            mk(Rank.ACE, Suit.SPADES),
            mk(Rank.TWO, Suit.HEARTS),
            mk(Rank.THREE, Suit.CLUBS),
            mk(Rank.FOUR, Suit.DIAMONDS),
            mk(Rank.FIVE, Suit.SPADES),
        ]
        self.assertNotEqual(evaluate_hand(hand), HandRank.STRAIGHT)

    @unittest.skip("TODO: known bug")
    def test_evaluate_table_ordering_and_ties(self):
        # Straight vs Pair
        p1 = Player("P1", 1000)
        p2 = Player("P2", 1000)
        p1.hand = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.SIX)]
        p2.hand = [Card(Suit.CLUBS, Rank.NINE), Card(Suit.DIAMONDS, Rank.NINE)]
        table = Table(10, 20, players=[p1, p2])
        table.flop_cards = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.TEN),
        ]
        table.turn_card = Card(Suit.DIAMONDS, Rank.JACK)
        table.river_card = Card(Suit.SPADES, Rank.NINE)
        results = evaluate_table(table)
        ranks = list(results.values())
        print(results)
        self.assertTrue(ranks[0][0] > ranks[1][0])

        # Tie scenario: both have pair of 2s
        q1 = Player("Q1", 1000)
        q2 = Player("Q2", 1000)
        q1.hand = [Card(Suit.SPADES, Rank.TWO), Card(Suit.HEARTS, Rank.THREE)]
        q2.hand = [Card(Suit.CLUBS, Rank.TWO), Card(Suit.DIAMONDS, Rank.FOUR)]
        table2 = Table(10, 20, players=[q1, q2])
        table2.flop_cards = [
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.SEVEN),
        ]
        table2.turn_card = Card(Suit.DIAMONDS, Rank.NINE)
        table2.river_card = Card(Suit.SPADES, Rank.JACK)
        results2 = evaluate_table(table2)
        self.assertEqual(len(results2), 2)
        ranks2 = list(results2.values())
        self.assertEqual(ranks2[0][0], ranks2[1][0])

    def test_tables_do_not_share_deck_by_default(self):
        # known issue: default Deck is shared via mutable default
        t1 = Table(10, 20, players=[Player("A", 1000), Player("B", 1000)])
        t2 = Table(10, 20, players=[Player("C", 1000), Player("D", 1000)])
        self.assertIsNot(t1.deck, t2.deck, "Tables should have independent decks")

    def test_pre_game_blinds_and_deal(self):
        table = Table(10, 20, players=[Player("X", 1000), Player("Y", 1000)])
        table.dealer = -1  # default
        new_table = table.pre_game()
        # small blind from player 0, big blind from player 1
        self.assertEqual(new_table.players[0].chips, 1000 - table.small_blind)
        self.assertEqual(new_table.players[1].chips, 1000 - table.big_blind)
        self.assertEqual(len(new_table.players[0].hand), 2)
        self.assertEqual(len(new_table.players[1].hand), 2)


@unittest.skip("TODO: test later")
class TestPokerMultipleRuns(unittest.TestCase):
    def setUp(self):
        self.players = [Player("P1", 1000), Player("P2", 1000)]
        self.base_rounds = [
            [Action(3, 100), Action(2)],
            [Action(1), Action(1)],
            [Action(1), Action(1)],
            [Action(1), Action(1)],
        ]
        self.runs = 20

    def test_no_duplicate_cards(self):
        for _ in range(self.runs):
            players_copy = [Player(p.name, p.chips) for p in self.players]
            table = Table(10, 20, players=players_copy)
            game = GameTest(1000, deepcopy(self.base_rounds), table)
            result = game.simulate_game()

            all_cards = [c for p in result for c in p.hand] + table.flop_cards
            if table.turn_card:
                all_cards.append(table.turn_card)
            if table.river_card:
                all_cards.append(table.river_card)

            self.assertEqual(len(all_cards), len(set(all_cards)), "Duplicate cards detected")

    def test_chip_reset_each_run(self):
        for _ in range(self.runs):
            players_copy = [Player(p.name, p.chips) for p in self.players]
            table = Table(10, 20, players=players_copy)
            game = GameTest(1000, deepcopy(self.base_rounds), table)
            result = game.simulate_game()
            for p in result:
                self.assertLessEqual(p.chips, 1000)
                self.assertGreaterEqual(p.chips, 0)

    def test_action_stack_not_mutated(self):
        for _ in range(self.runs):
            rounds = deepcopy(self.base_rounds)
            table = Table(10, 20, players=[Player(p.name, p.chips) for p in self.players])
            game = GameTest(1000, rounds, table)
            try:
                game.simulate_game()
            except IndexError:
                self.fail("Action stack was exhausted. Likely due to mutation between runs.")

    def test_deck_refills_every_run(self):
        seen_card_counts = []
        for _ in range(self.runs):
            table = Table(10, 20, players=[Player(p.name, p.chips) for p in self.players])
            game = GameTest(1000, deepcopy(self.base_rounds), table)
            game.simulate_game()
            seen_card_counts.append(len(table.deck.cards))
        self.assertTrue(all(n <= 52 for n in seen_card_counts), "Deck not properly reset between runs")

if __name__ == "__main__":
    unittest.main
