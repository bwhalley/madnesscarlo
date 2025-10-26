"""
Tests for the simulation engine module.

Tests card actions, activated abilities, mana detection, and ideal setup evaluation.
"""

import pytest
from collections import Counter
from app.simulation.engine import (
    Deck, GameState, evaluate_ideal_setups,
    CARD_ACTIONS, ACTIVATED_ABILITIES,
    play_careful_study, play_frantic_search,
    play_survival, activate_survival,
    play_wild_mongrel, activate_wild_mongrel,
    play_wonder, play_roar_flashback,
    is_creature, discard_random
)


class TestDeckInitialization:
    """Test Deck class initialization with AtomicCards.json."""
    
    def test_deck_loads_card_info(self, sample_deck_cards):
        """Deck should load card info from AtomicCards.json."""
        deck = Deck(sample_deck_cards)
        
        # Check that card info was loaded
        assert "Island" in deck.card_info
        assert "Survival of the Fittest" in deck.card_info
        
        # Check card types are detected
        assert "Land" in deck.card_info["Island"]["type"]
        assert "Enchantment" in deck.card_info["Survival of the Fittest"]["type"]
    
    def test_deck_creates_card_list(self):
        """Deck should expand cards based on count."""
        cards_data = [
            {"card_name": "Island", "count": 9},
            {"card_name": "Forest", "count": 7},
            {"card_name": "Mountain", "count": 4},
        ]
        
        deck = Deck(cards_data)
        
        # Should have created expanded card list with correct total
        assert len(deck.cards) == 20  # 9 + 7 + 4
        
        # Should have correct number of each card
        island_count = sum(1 for card in deck.cards if card == "Island")
        assert island_count == 9
        
        forest_count = sum(1 for card in deck.cards if card == "Forest")
        assert forest_count == 7


class TestManaColorDetection:
    """Test mana color detection from lands."""
    
    def test_basic_land_mana_detection(self):
        """Basic lands should produce correct mana colors."""
        cards_data = [
            {"card_name": "Island", "count": 1},
            {"card_name": "Forest", "count": 1},
            {"card_name": "Mountain", "count": 1},
            {"card_name": "Plains", "count": 1},
            {"card_name": "Swamp", "count": 1},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        
        # Manually set hand to ensure we have all basic land types
        state.hand = Counter({
            "Island": 1,
            "Forest": 1,
            "Mountain": 1,
            "Plains": 1,
            "Swamp": 1
        })
        
        # Play each basic land
        for turn in range(1, 6):
            state.turn = turn
            state.play_land()
        
        # Should have all five colors
        assert "U" in state.mana_colors  # Island -> Blue
        assert "G" in state.mana_colors  # Forest -> Green
        assert "R" in state.mana_colors  # Mountain -> Red
        assert "W" in state.mana_colors  # Plains -> White
        assert "B" in state.mana_colors  # Swamp -> Black
    
    def test_mana_colors_tracked_by_turn(self):
        """Mana colors should be tracked per turn."""
        cards_data = [
            {"card_name": "Island", "count": 10},
            {"card_name": "Forest", "count": 10},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        
        # Turn 1: Play Island
        state.hand = Counter({"Island": 1})
        state.turn = 1
        state.play_land()
        assert state.mana_colors_by_turn[1] == {"U"}
        
        # Turn 2: Play Forest - colors should accumulate
        state.hand = Counter({"Forest": 1})
        state.turn = 2
        state.play_land()
        # Should have accumulated both colors
        assert state.mana_colors_by_turn[2] == {"U", "G"}
    
    def test_lands_added_to_battlefield(self):
        """Played lands should be added to battlefield."""
        cards_data = [{"card_name": "Island", "count": 10}]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.draw_card(3)
        
        state.turn = 1
        state.play_land()
        
        assert state.battlefield["Island"] == 1
        assert state.lands_in_play == 1


class TestCardActions:
    """Test card action implementations."""
    
    def test_careful_study_draws_and_discards(self):
        """Careful Study should draw 2 and discard 2."""
        cards_data = [
            {"card_name": "Careful Study", "count": 1},
            {"card_name": "Island", "count": 20},
            {"card_name": "Forest", "count": 20},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.hand = Counter({"Careful Study": 1})
        state.mana_colors = {"U"}
        
        initial_deck_size = len(state.deck.cards)
        
        play_careful_study(state)
        
        # Should have cast the spell
        assert state.spells_cast["Careful Study"] == 1
        # Careful Study should be in graveyard (the spell itself)
        assert state.graveyard["Careful Study"] >= 1
        # Should have drawn 2 cards from deck
        assert len(state.deck.cards) == initial_deck_size - 2
        # Total cards in graveyard should be 3 (spell + 2 discards)
        assert sum(state.graveyard.values()) == 3
    
    def test_survival_enters_battlefield(self):
        """Survival of the Fittest should enter battlefield when cast."""
        cards_data = [
            {"card_name": "Survival of the Fittest", "count": 4},
            {"card_name": "Forest", "count": 20},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.hand = Counter({"Survival of the Fittest": 1})
        state.mana_colors = {"G"}
        
        play_survival(state)
        
        assert state.battlefield["Survival of the Fittest"] == 1
        assert state.spells_cast["Survival of the Fittest"] == 1
        # Counter keeps keys with 0 count, so check count is 0
        assert state.hand.get("Survival of the Fittest", 0) == 0
    
    def test_wild_mongrel_enters_battlefield(self):
        """Wild Mongrel should enter battlefield when cast."""
        cards_data = [
            {"card_name": "Wild Mongrel", "count": 4},
            {"card_name": "Forest", "count": 20},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.hand = Counter({"Wild Mongrel": 1})
        state.mana_colors = {"G"}
        
        play_wild_mongrel(state)
        
        assert state.battlefield["Wild Mongrel"] == 1
        assert state.spells_cast["Wild Mongrel"] == 1


class TestActivatedAbilities:
    """Test activated ability implementations."""
    
    def test_survival_tutors_creature(self):
        """Survival should discard creature and tutor another."""
        cards_data = [
            {"card_name": "Survival of the Fittest", "count": 1},
            {"card_name": "Squee, Goblin Nabob", "count": 4},
            {"card_name": "Basking Rootwalla", "count": 4},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.battlefield = Counter({"Survival of the Fittest": 1})
        state.hand = Counter({"Squee, Goblin Nabob": 1})
        
        initial_hand_size = sum(state.hand.values())
        
        activate_survival(state)
        
        # Should still have 1 card (discarded 1, tutored 1)
        assert sum(state.hand.values()) == initial_hand_size
        # Squee should be in graveyard or madness-cast
        assert state.graveyard.get("Squee, Goblin Nabob", 0) >= 1 or \
               state.madness_casts.get("Squee, Goblin Nabob", 0) >= 1
        # Should have tutored something
        assert sum(state.cards_tutored.values()) == 1
    
    def test_wild_mongrel_discards_card(self):
        """Wild Mongrel should discard a card."""
        cards_data = [
            {"card_name": "Wild Mongrel", "count": 1},
            {"card_name": "Basking Rootwalla", "count": 4},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.battlefield = Counter({"Wild Mongrel": 1})
        state.hand = Counter({"Basking Rootwalla": 1})
        
        activate_wild_mongrel(state)
        
        # Hand should be empty
        assert sum(state.hand.values()) == 0
        # Rootwalla should be discarded (graveyard or madness)
        assert state.graveyard.get("Basking Rootwalla", 0) + \
               state.madness_casts.get("Basking Rootwalla", 0) == 1
    
    def test_roar_flashback(self):
        """Roar of the Wurm should be castable from graveyard."""
        cards_data = [
            {"card_name": "Roar of the Wurm", "count": 4},
            {"card_name": "Forest", "count": 20},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.graveyard = Counter({"Roar of the Wurm": 1})
        state.mana_colors = {"G"}
        
        play_roar_flashback(state)
        
        # Roar should be removed from graveyard
        assert state.graveyard["Roar of the Wurm"] == 0
        # Wurm token should be on battlefield
        assert state.battlefield["Wurm Token"] == 1
        # Should track flashback cast
        assert state.flashback_casts["Roar of the Wurm"] == 1


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_is_creature_detection(self):
        """is_creature should correctly identify creatures."""
        cards_data = [
            {"card_name": "Wild Mongrel", "count": 4},
            {"card_name": "Island", "count": 4},
            {"card_name": "Careful Study", "count": 4},
        ]
        
        deck = Deck(cards_data)
        
        assert is_creature("Wild Mongrel", deck) == True
        assert is_creature("Island", deck) == False
        assert is_creature("Careful Study", deck) == False
    
    def test_discard_random(self):
        """discard_random should discard cards from hand."""
        cards_data = [
            {"card_name": "Island", "count": 20},
        ]
        
        deck = Deck(cards_data)
        state = GameState(deck)
        state.hand = Counter({"Island": 3})
        
        discard_random(state, 2)
        
        assert sum(state.hand.values()) == 1
        assert state.graveyard["Island"] == 2


class TestIdealSetupEvaluation:
    """Test ideal setup evaluation with all condition types."""
    
    def test_requires_cards_check(self, mock_game_state, sample_config):
        """Should check if required cards were seen by turn limit."""
        # Counterspell was seen on turn 2
        setup = {
            "name": "Test",
            "turn_limit": 2,
            "requires_cards": ["Counterspell"]
        }
        
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == True
        
        # But not by turn 1
        setup["turn_limit"] = 1
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == False
    
    def test_requires_colors_check(self, mock_game_state):
        """Should check if required mana colors are available."""
        setup = {
            "name": "Test",
            "turn_limit": 4,
            "requires_cards": [],
            "requires_colors": ["U", "G"]
        }
        
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == True
        
        # Red not available
        setup["requires_colors"] = ["R"]
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == False
    
    def test_requires_min_lands_check(self, mock_game_state):
        """Should check minimum lands in play."""
        setup = {
            "name": "Test",
            "turn_limit": 4,
            "requires_cards": [],
            "requires_colors": [],
            "requires_min_lands": 3
        }
        
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == True
        
        setup["requires_min_lands"] = 4
        result = evaluate_ideal_setups(mock_game_state, {"ideal_setups": [setup]})
        assert result["Test"] == False
    
    def test_requires_in_play_check(self):
        """Should check if cards are on battlefield."""
        cards_data = [{"card_name": "Survival of the Fittest", "count": 4}]
        deck = Deck(cards_data)
        state = GameState(deck)
        state.battlefield = Counter({"Survival of the Fittest": 1})
        state.cards_seen_by_turn = {"Survival of the Fittest": 1}
        state.mana_colors = {"G"}
        state.lands_in_play = 2
        state.mana_colors_by_turn = {1: {"G"}}
        
        setup = {
            "name": "Test",
            "turn_limit": 4,
            "requires_cards": ["Survival of the Fittest"],
            "requires_colors": ["G"],
            "requires_min_lands": 2,
            "requires_in_play": ["Survival of the Fittest"]
        }
        
        result = evaluate_ideal_setups(state, {"ideal_setups": [setup]})
        assert result["Test"] == True
    
    def test_requires_in_graveyard_check(self):
        """Should check if cards are in graveyard."""
        cards_data = [{"card_name": "Wonder", "count": 4}]
        deck = Deck(cards_data)
        state = GameState(deck)
        state.graveyard = Counter({"Wonder": 1})
        state.cards_seen_by_turn = {"Wonder": 1}
        state.lands_in_play = 1
        
        setup = {
            "name": "Test",
            "turn_limit": 4,
            "requires_cards": ["Wonder"],
            "requires_colors": [],
            "requires_in_graveyard": ["Wonder"]
        }
        
        result = evaluate_ideal_setups(state, {"ideal_setups": [setup]})
        assert result["Test"] == True
    
    def test_requires_any_creature_in_hand_check(self):
        """Should check if any creature is in hand."""
        cards_data = [
            {"card_name": "Squee, Goblin Nabob", "count": 4},
            {"card_name": "Island", "count": 4}
        ]
        deck = Deck(cards_data)
        state = GameState(deck)
        state.hand = Counter({"Squee, Goblin Nabob": 1})
        state.cards_seen_by_turn = {"Squee, Goblin Nabob": 0}
        state.lands_in_play = 1
        
        setup = {
            "name": "Test",
            "turn_limit": 4,
            "requires_cards": [],
            "requires_colors": [],
            "requires_any_creature_in_hand": True
        }
        
        result = evaluate_ideal_setups(state, {"ideal_setups": [setup]})
        assert result["Test"] == True
        
        # Only lands in hand
        state.hand = Counter({"Island": 1})
        result = evaluate_ideal_setups(state, {"ideal_setups": [setup]})
        assert result["Test"] == False
    
    def test_all_conditions_combined(self):
        """Should check all conditions together (AND logic)."""
        cards_data = [
            {"card_name": "Survival of the Fittest", "count": 4},
            {"card_name": "Squee, Goblin Nabob", "count": 4},
            {"card_name": "Forest", "count": 20}
        ]
        deck = Deck(cards_data)
        state = GameState(deck)
        state.battlefield = Counter({"Survival of the Fittest": 1, "Forest": 2})
        state.hand = Counter({"Squee, Goblin Nabob": 1})
        state.cards_seen_by_turn = {"Survival of the Fittest": 1, "Squee, Goblin Nabob": 0}
        state.mana_colors = {"G"}
        state.mana_colors_by_turn = {1: {"G"}, 2: {"G"}}
        state.lands_in_play = 2
        
        setup = {
            "name": "Survival Engine",
            "turn_limit": 4,
            "requires_cards": ["Survival of the Fittest"],
            "requires_colors": ["G"],
            "requires_in_play": ["Survival of the Fittest"],
            "requires_min_lands": 2,
            "requires_any_creature_in_hand": True
        }
        
        result = evaluate_ideal_setups(state, {"ideal_setups": [setup]})
        assert result["Survival Engine"] == True


class TestCardActionsRegistry:
    """Test that all card actions are registered."""
    
    def test_all_card_actions_registered(self):
        """Should have all 8 card actions registered."""
        expected_actions = [
            "Careful Study",
            "Frantic Search",
            "Survival of the Fittest",
            "Wild Mongrel",
            "Waterfront Bouncer",
            "Basking Rootwalla",
            "Arrogant Wurm",
            "Wonder"
        ]
        
        for action in expected_actions:
            assert action in CARD_ACTIONS, f"{action} not registered"
    
    def test_all_activated_abilities_registered(self):
        """Should have all 4 activated abilities registered."""
        expected_abilities = [
            "Survival of the Fittest",
            "Wild Mongrel",
            "Waterfront Bouncer",
            "Roar of the Wurm"
        ]
        
        for ability in expected_abilities:
            assert ability in ACTIVATED_ABILITIES, f"{ability} not registered"

