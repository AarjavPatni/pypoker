# PyPoker

MVP - 6v6 poker played over the network

---

### Game logic
- [x] Deal cards
    - [x] Shuffling the deck
    - [x] Removing random cards from the deck
    - [x] Adding cards to players' hands
- [x] Manage rounds
    - [x] Pre-game
        - [x] Set last player as d+1
        - [x] Assign dealer position
        - [x] Collect small blind from player
        - [x] Collect big blind from player
        - [x] Add blinds to pot
        - [x] Distribute hole cards
    - [x] Pre Flop
        - [x] Allow betting
        - [x] Start betting from [d+3] player
    - [x] Flop
        - [x] Deal flop
        - [x] Output flop
        - [x] Allow betting
    - [x] Turn
        - [x] Deal turn
        - [x] Output turn
        - [x] Allow betting
    - [x] River
        - [x] Deal river
        - [x] Output river
        - [x] Allow betting
    - [x] Showdown
        - [x] Show all active hands
        - [x] Evaluate the table
        - [x] Output winner and final stats (chips, ranks, etc)
- [ ] Handle betting
    - [ ] Add deal method
    - [ ] Loop through table until last player reached
    - [ ] Prompt player for action (fold, call, raise)
    - [ ] Bets
        - [ ] Move current_bet chips from player to pot
        - current_bet = big_blind / latest raise
    - [ ] Folds - mark player inactive; move to next player
    - [ ] Raises
        - Min raise = 2*current_bet
        - [ ] Set current_bet = raise
        - [ ] Move current_bet from player to pot
        - [ ] Set last player = player who raised - 1
    - [ ] Check
        - [ ] TODO
    - [ ] All ins
        - [ ] Manage side pot
            - [ ] **TODO**
        - [ ] Move all chips from player to table. Set current_bet = max(all in value,
        min_raise)
        - [ ] (player.chips = 0 and active) implies all_in
            - [ ] Move to the next player
- [ ] Evaluate hands
    - [x] Distinct hand types
    - [ ] Handle tiebreakers
        - [ ] `evaluate_table()` - Get the best hand along with the rank
            - [ ] Loop through sorted hands, compare each card to find the
            best hand
            - [ ] Store best hand and rank as dict. dict[player] = (rank, best hand)
            - [ ] If two players have the same rank in the dict, compare their best_hand
            - [ ] Comparing `best_hand` - Sort, loop through, select the highest

---

### Refactor

- [ ] Deck
    - [ ] draw method
- [ ] Table
    - [ ] handle_player_action
        - [ ] handle raises
    - [ ] start_betting
        - [ ] accept an optional dict[player, actions] for each player
    - [ ] immutable dealing of cards
        - [ ] deal(no of cards, players) -> tuple[player, card]
    - [ ] community card dealing

---

### Terminal UI
- [ ] Game State
    - [ ] Hole cards
    - [ ] Community cards
    - [ ] Pot size
    - [ ] Player chips
    - [ ] Other players' chips
- [ ] Player actions (folded/called/raised)
- [ ] Handling input
    - [ ] Ask for action
        - [ ] Show valid actions based on game state

---

### Networking
- [ ] Playing over the network
    - [ ] Server setup
        - [ ] **TODO**
    - [ ] Client logic
        - [ ] **TODO**
    - [ ] Message protocol
        - [ ] **TODO**

