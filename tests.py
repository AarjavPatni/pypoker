import unittest
from main import Player, Action, Table
from dataclasses import dataclass

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


"""
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

    def test_call_more_than_chips(self):
        players = [Player("Caller", 50), Player("Raiser", 1000)]
        rounds = [
            [Action(3, 100), Action(2)],
        ]
        table = Table(small_blind=10, big_blind=20, players=players)
        game = GameTest(initial_player_chips=1000, rounds=rounds, table=table)

        with self.assertRaises(ValueError):
            game.simulate_game()
"""


"""
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
        winner = list(results.keys())[-1]
        self.assertEqual(results[winner], HandRank.ROYAL_FLUSH)
        self.assertEqual(winner.name, "Alice")

    def test_full_house_beats_flush(self):
        players = [Player("Alice", 1000), Player("Bob", 1000)]
        players[0].hand = [Card(Suit.DIAMONDS, Rank.KING), Card(Suit.CLUBS, Rank.KING)]
        players[1].hand = [Card(Suit.SPADES, Rank.TWO), Card(Suit.SPADES, Rank.FOUR)]

        table = Table(small_blind=10, big_blind=20, players=players)
        table.flop_cards = [
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.THREE),
            Card(Suit.SPADES, Rank.SIX),
        ]
        table.turn_card = Card(Suit.SPADES, Rank.JACK)
        table.river_card = Card(Suit.SPADES, Rank.ACE)

        results = evaluate_table(table)
        winner = list(results.keys())[-1]
        self.assertEqual(results[winner], HandRank.FULL_HOUSE)
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
        winner = list(results.keys())[-1]
        self.assertEqual(results[winner], HandRank.PAIR)
        self.assertEqual(winner.name, "Alice")
"""

"""
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
            game = GameTest(1000, copy.deepcopy(self.base_rounds), table)
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
            game = GameTest(1000, copy.deepcopy(self.base_rounds), table)
            result = game.simulate_game()
            for p in result:
                self.assertLessEqual(p.chips, 1000)
                self.assertGreaterEqual(p.chips, 0)

    def test_action_stack_not_mutated(self):
        for _ in range(self.runs):
            rounds = copy.deepcopy(self.base_rounds)
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
            game = GameTest(1000, copy.deepcopy(self.base_rounds), table)
            game.simulate_game()
            seen_card_counts.append(len(table.deck.cards))
        self.assertTrue(all(n <= 52 for n in seen_card_counts), "Deck not properly reset between runs")
"""

if __name__ == "__main__":
    unittest.main

