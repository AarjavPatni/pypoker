# PyPoker

MVP - 6v6 poker played over the network

---

### Game logic
- [x] Deal cards
    - [x] Shuffling the deck
    - [x] Removing random cards from the deck
    - [x] Adding cards to players' hands
- [ ] Manage rounds
    - [ ] Pre-game
        - [ ] Set last player as d+1
        - [ ] Assign dealer position
        - [ ] Collect small blind from player
        - [ ] Collect big blind from player
        - [ ] Add blinds to pot
        - [ ] Distribute hole cards
    - [ ] Pre Flop
        - [ ] Allow betting
        - [ ] Start betting from [d+3] player
    - [ ] Flop
        - [ ] Deal flop
        - [ ] Output flop
        - [ ] Allow betting
    - [ ] Turn
        - [ ] Deal turn
        - [ ] Output turn
        - [ ] Allow betting
    - [ ] River
        - [ ] Deal river
        - [ ] Output river
        - [ ] Allow betting
    - [ ] Showdown
        - [ ] Show all active hands
        - [ ] Evaluate the table
        - [ ] Output winner and final stats (chips, ranks, etc)
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

