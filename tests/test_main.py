from pypoker.main import Table, evaluate_table, Player, Card, Suit, Rank


def test_evaluate_table():
    p1: Player = Player("alice", 1000)
    p2: Player = Player("bob", 1000)
    p3: Player = Player("charlie", 1000)
    p4: Player = Player("jacob", 1000)
    p5: Player = Player("aarjav", 1000)
    p6: Player = Player("john", 1000)

    # Royal Flush – Alice: A♥ K♥ Q♥ J♥ 10♥
    p1.hand = [Card(Suit.HEARTS, Rank.TEN), Card(Suit.HEARTS, Rank.ACE)]

    # Straight Flush – Bob: 5♣ 6♣ 7♣ 8♣ 9♣
    p2.hand = [Card(Suit.CLUBS, Rank.SEVEN), Card(Suit.CLUBS, Rank.EIGHT)]

    # Four of a Kind – Charlie: A♣ A♦ A♥ A♠ 5♦
    p3.hand = [Card(Suit.CLUBS, Rank.ACE), Card(Suit.DIAMONDS, Rank.ACE)]

    # Full House – Jacob: Q♠ Q♣ Q♦ 6♠ 6♦
    p4.hand = [Card(Suit.SPADES, Rank.QUEEN), Card(Suit.CLUBS, Rank.QUEEN)]

    # Flush – Aarjav: 2♦ 4♦ 6♦ 8♦ 10♦
    p5.hand = [Card(Suit.DIAMONDS, Rank.SIX), Card(Suit.DIAMONDS, Rank.EIGHT)]

    # Straight – John: 3♠ 4♥ 5♦ 6♣ 7♥
    p6.hand = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.CLUBS, Rank.SIX)]

    table: Table = Table([p1, p2, p3, p4, p5, p6], 0, 0)
    table.flop = [Card(Suit.HEARTS, Rank.QUEEN), Card(Suit.HEARTS, Rank.JACK), Card(Suit.HEARTS, Rank.KING)]
    table.turn = Card(Suit.CLUBS, Rank.FIVE)
    table.river = Card(Suit.CLUBS, Rank.NINE)

    winner = evaluate_table(table)
    assert max(winner, key=winner.get).name == "alice"


def test_ace_low_straight():
    p1 = Player("lowstraight", 1000)
    p2 = Player("highcard", 1000)

    # A-2-3-4-5 straight
    p1.hand = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.TWO)]
    p2.hand = [Card(Suit.CLUBS, Rank.KING), Card(Suit.DIAMONDS, Rank.QUEEN)]

    table = Table([p1, p2], 0, 0)
    table.flop = [Card(Suit.HEARTS, Rank.THREE), Card(Suit.CLUBS, Rank.FOUR), Card(Suit.DIAMONDS, Rank.FIVE)]
    table.turn = Card(Suit.SPADES, Rank.SEVEN)
    table.river = Card(Suit.HEARTS, Rank.NINE)

    winner = evaluate_table(table)
    assert max(winner, key=winner.get).name == "lowstraight"


def test_full_house_beats_flush():
    p1 = Player("flushboy", 1000)
    p2 = Player("fullhousegirl", 1000)

    # Flush
    p1.hand = [Card(Suit.HEARTS, Rank.TWO), Card(Suit.HEARTS, Rank.FIVE)]
    # Full House
    p2.hand = [Card(Suit.CLUBS, Rank.QUEEN), Card(Suit.DIAMONDS, Rank.QUEEN)]

    table = Table([p1, p2], 0, 0)
    table.flop = [Card(Suit.HEARTS, Rank.SIX), Card(Suit.HEARTS, Rank.EIGHT), Card(Suit.HEARTS, Rank.JACK)]
    table.turn = Card(Suit.SPADES, Rank.SIX)
    table.river = Card(Suit.CLUBS, Rank.SIX)

    winner = evaluate_table(table)
    assert max(winner, key=winner.get).name == "fullhousegirl"


