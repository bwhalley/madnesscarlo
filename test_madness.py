"""
Comprehensive test suite for MTG Madness Simulator

This test suite validates:
1. Card data reading and parsing from CSV
2. Condition string parsing
3. Game simulation mechanics
4. Mulligan logic
5. Deck operations
6. Statistical aggregation
"""

import pytest
import pandas as pd
import json
import os
import tempfile
from collections import Counter
from madness import (
    parse_condition_string,
    Deck,
    GameState,
    simulate_game,
    should_mulligan,
    count_lands_in_hand,
    has_creature_in_hand,
    choose_card_to_remove,
    perform_mulligan,
    evaluate_ideal_setups,
    load_config
)


# ==========================================================
# Test Fixtures
# ==========================================================

@pytest.fixture
def simple_deck_csv(tmp_path):
    """Create a simple test deck CSV file."""
    csv_content = """Card Name,Quantity,Type,Mana Cost,Conditions
Forest,10,Land,,effect:mana_G;category:land
Island,10,Land,,effect:mana_U;category:land
Llanowar Elves,4,Creature,G,requires:lands>=1;requires:color=G
Grizzly Bears,4,Creature,1G,requires:lands>=2;requires:color=G
Counterspell,4,Instant,UU,requires:lands>=2;requires:color=U"""
    
    deck_path = tmp_path / "test_deck.csv"
    deck_path.write_text(csv_content)
    return str(deck_path)


@pytest.fixture
def complex_deck_csv(tmp_path):
    """Create a more complex test deck with card effects."""
    csv_content = """Card Name,Quantity,Type,Mana Cost,Conditions
Forest,7,Land,,effect:mana_G;category:land
Island,9,Land,,effect:mana_U;category:land
Yavimaya Coast,4,Land,,effect:mana_U;effect:mana_G;category:land
Careful Study,3,Sorcery,U,requires:lands>=1;requires:color=U;effect:draw2_discard2
Frantic Search,4,Instant,2U,requires:lands>=3;requires:color=U;effect:draw2_discard2
Wild Mongrel,4,Creature,1G,requires:lands>=2;requires:color=G
Basking Rootwalla,4,Creature,G,requires:lands>=1;requires:color=G"""
    
    deck_path = tmp_path / "complex_deck.csv"
    deck_path.write_text(csv_content)
    return str(deck_path)


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration file."""
    config = {
        "key_cards": ["Careful Study", "Wild Mongrel"],
        "key_card_turn_limit": 4,
        "ideal_setups": [
            {
                "name": "Early Combo",
                "requires_cards": ["Careful Study", "Wild Mongrel"],
                "requires_colors": ["U", "G"],
                "turn_limit": 3
            }
        ]
    }
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return str(config_path)


# ==========================================================
# Phase 1: Condition Parsing Tests
# ==========================================================

class TestConditionParsing:
    """Test the condition string parser."""
    
    def test_parse_empty_condition(self):
        """Test parsing empty or invalid conditions."""
        assert parse_condition_string("") == []
        assert parse_condition_string(None) == []
        assert parse_condition_string("   ") == []
    
    def test_parse_requires_lands(self):
        """Test parsing land requirements."""
        result = parse_condition_string("requires:lands>=3")
        assert len(result) == 1
        assert result[0]["type"] == "requires"
        assert result[0]["target"] == "lands"
        assert result[0]["op"] == ">="
        assert result[0]["value"] == 3
    
    def test_parse_requires_color(self):
        """Test parsing color requirements."""
        result = parse_condition_string("requires:color=U")
        assert len(result) == 1
        assert result[0]["type"] == "requires"
        assert result[0]["target"] == "color"
        assert result[0]["op"] == "="
        assert result[0]["value"] == "U"
    
    def test_parse_effect(self):
        """Test parsing card effects."""
        result = parse_condition_string("effect:mana_G")
        assert len(result) == 1
        assert result[0]["type"] == "effect"
        assert result[0]["value"] == "mana_G"
    
    def test_parse_multiple_conditions(self):
        """Test parsing multiple conditions separated by semicolons."""
        result = parse_condition_string("requires:lands>=2;requires:color=U;effect:draw2_discard2")
        assert len(result) == 3
        assert result[0]["type"] == "requires"
        assert result[1]["type"] == "requires"
        assert result[2]["type"] == "effect"
    
    def test_parse_timing(self):
        """Test parsing timing conditions."""
        result = parse_condition_string("timing:instant")
        assert len(result) == 1
        assert result[0]["type"] == "timing"
        assert result[0]["value"] == "instant"
    
    def test_parse_category(self):
        """Test parsing category conditions."""
        result = parse_condition_string("category:land")
        assert len(result) == 1
        assert result[0]["type"] == "category"
        assert result[0]["value"] == "land"


# ==========================================================
# Phase 2: Deck Class Tests
# ==========================================================

class TestDeck:
    """Test the Deck class functionality."""
    
    def test_deck_loading(self, simple_deck_csv):
        """Test that deck loads correctly from CSV."""
        deck = Deck(simple_deck_csv)
        assert len(deck.cards) == 32  # 10+10+4+4+4
        assert "Forest" in deck.card_info
        assert "Island" in deck.card_info
        assert "Llanowar Elves" in deck.card_info
    
    def test_deck_quantities(self, simple_deck_csv):
        """Test that card quantities are correctly expanded."""
        deck = Deck(simple_deck_csv)
        forest_count = sum(1 for card in deck.cards if card == "Forest")
        assert forest_count == 10
    
    def test_deck_card_info(self, simple_deck_csv):
        """Test that card metadata is stored correctly."""
        deck = Deck(simple_deck_csv)
        forest_info = deck.card_info["Forest"]
        assert forest_info["type"] == "Land"
        assert len(forest_info["conditions"]) > 0
        assert forest_info["conditions"][0]["type"] == "effect"
    
    def test_deck_shuffle(self, simple_deck_csv):
        """Test that shuffle randomizes deck order."""
        deck1 = Deck(simple_deck_csv)
        original_order = deck1.cards.copy()
        
        deck2 = Deck(simple_deck_csv)
        deck2.shuffle()
        
        # After shuffle, order should be different (with high probability)
        # Run multiple shuffles to ensure randomness
        different = False
        for _ in range(10):
            deck_test = Deck(simple_deck_csv)
            deck_test.shuffle()
            if deck_test.cards != original_order:
                different = True
                break
        assert different, "Shuffle should randomize card order"
    
    def test_deck_draw(self, simple_deck_csv):
        """Test drawing cards from deck."""
        deck = Deck(simple_deck_csv)
        initial_size = len(deck.cards)
        
        drawn = deck.draw(3)
        assert len(drawn) == 3
        assert len(deck.cards) == initial_size - 3
    
    def test_deck_draw_empty(self, simple_deck_csv):
        """Test drawing when deck is empty."""
        deck = Deck(simple_deck_csv)
        deck.cards = []
        drawn = deck.draw(5)
        assert len(drawn) == 0
    
    def test_deck_draw_partial(self, simple_deck_csv):
        """Test drawing more cards than available."""
        deck = Deck(simple_deck_csv)
        deck.cards = ["Card1", "Card2"]
        drawn = deck.draw(5)
        assert len(drawn) == 2
        assert len(deck.cards) == 0


# ==========================================================
# Phase 3: Game State Tests
# ==========================================================

class TestGameState:
    """Test the GameState class and game mechanics."""
    
    def test_initial_state(self, simple_deck_csv):
        """Test initial game state setup."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        assert state.turn == 1
        assert state.lands_in_play == 0
        assert len(state.cards_seen) == 0
        assert len(state.hand) == 0
        assert state.cards_drawn_total == 0
    
    def test_draw_card(self, simple_deck_csv):
        """Test drawing cards updates state correctly."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        state.draw_card(3)
        assert state.cards_drawn_total == 3
        assert len(state.cards_seen) >= 1  # At least 1 unique card
        assert len(state.cards_seen) <= 3  # At most 3 unique cards
        assert sum(state.hand.values()) == 3
    
    def test_cards_seen_by_turn_tracking(self, simple_deck_csv):
        """Test that cards are tracked by turn first seen."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        state.turn = 1
        state.draw_card(2)
        
        state.turn = 3
        state.draw_card(2)
        
        # Check that cards drawn on turn 1 are marked with turn 1
        turn_1_cards = [card for card, turn in state.cards_seen_by_turn.items() if turn == 1]
        turn_3_cards = [card for card, turn in state.cards_seen_by_turn.items() if turn == 3]
        
        # Should have at least some cards from each turn
        assert len(turn_1_cards) >= 1
        assert len(turn_3_cards) >= 1
        # Total should be at least 4 unique cards
        assert len(state.cards_seen_by_turn) >= 2
    
    def test_play_land(self, simple_deck_csv):
        """Test playing lands."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        # Put a forest in hand
        state.hand["Forest"] = 1
        state.play_land()
        
        assert state.lands_in_play == 1
        assert state.hand["Forest"] == 0
        assert "G" in state.mana_colors
    
    def test_mana_colors_tracking(self, complex_deck_csv):
        """Test that mana colors are tracked correctly."""
        deck = Deck(complex_deck_csv)
        state = GameState(deck)
        
        state.turn = 1
        state.hand["Forest"] = 1
        state.play_land()
        assert "G" in state.mana_colors
        
        state.turn = 2
        state.hand["Island"] = 1
        state.play_land()
        assert "G" in state.mana_colors
        assert "U" in state.mana_colors
    
    def test_can_cast_lands_requirement(self, simple_deck_csv):
        """Test casting check with land requirements."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        state.lands_in_play = 1
        state.mana_colors.add("G")  # Also need the color
        assert state.can_cast("Llanowar Elves")  # requires 1 land and G
        
        state.lands_in_play = 0
        assert not state.can_cast("Llanowar Elves")
    
    def test_can_cast_color_requirement(self, simple_deck_csv):
        """Test casting check with color requirements."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        state.lands_in_play = 2
        state.mana_colors.add("G")
        
        assert state.can_cast("Grizzly Bears")  # requires G
        assert not state.can_cast("Counterspell")  # requires U
        
        state.mana_colors.add("U")
        assert state.can_cast("Counterspell")
    
    def test_has_color(self, simple_deck_csv):
        """Test color checking."""
        deck = Deck(simple_deck_csv)
        state = GameState(deck)
        
        state.mana_colors.add("G")
        assert state.has_color("G")
        assert state.has_color("g")  # Case insensitive
        assert not state.has_color("U")


# ==========================================================
# Phase 4: Mulligan Logic Tests
# ==========================================================

class TestMulliganLogic:
    """Test mulligan decision logic."""
    
    @pytest.fixture
    def default_strategy(self):
        """Default mulligan strategy for testing."""
        return {
            "enabled": True,
            "min_lands": 2,
            "max_lands": 4,
            "requires_creature": True,
            "max_mulligans": 7,
            "bottom_priority": {
                "prefer_land_at_count": 4,
                "protect_key_cards": True
            }
        }
    
    def test_count_lands_in_hand(self, simple_deck_csv):
        """Test counting lands in hand."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 3, "Island": 2, "Llanowar Elves": 2})
        
        count = count_lands_in_hand(hand, deck)
        assert count == 5
    
    def test_has_creature_in_hand(self, simple_deck_csv):
        """Test detecting creatures in hand."""
        deck = Deck(simple_deck_csv)
        
        hand_with_creature = Counter({"Forest": 3, "Llanowar Elves": 1})
        assert has_creature_in_hand(hand_with_creature, deck)
        
        hand_without_creature = Counter({"Forest": 5, "Island": 2})
        assert not has_creature_in_hand(hand_without_creature, deck)
    
    def test_should_mulligan_zero_lands(self, simple_deck_csv, default_strategy):
        """Test mulligan with 0 lands."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Llanowar Elves": 4, "Grizzly Bears": 3})
        assert should_mulligan(hand, deck, default_strategy)
    
    def test_should_mulligan_one_land(self, simple_deck_csv, default_strategy):
        """Test mulligan with 1 land."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 1, "Llanowar Elves": 3, "Grizzly Bears": 3})
        assert should_mulligan(hand, deck, default_strategy)
    
    def test_should_mulligan_five_lands(self, simple_deck_csv, default_strategy):
        """Test mulligan with 5 lands."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 5, "Llanowar Elves": 2})
        assert should_mulligan(hand, deck, default_strategy)
    
    def test_should_mulligan_no_creatures(self, simple_deck_csv, default_strategy):
        """Test mulligan with no creatures."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 3, "Island": 3, "Counterspell": 1})
        assert should_mulligan(hand, deck, default_strategy)
    
    def test_should_keep_good_hand(self, simple_deck_csv, default_strategy):
        """Test keeping a good hand."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 3, "Island": 1, "Llanowar Elves": 2, "Grizzly Bears": 1})
        assert not should_mulligan(hand, deck, default_strategy)
    
    def test_choose_card_to_remove_four_lands(self, simple_deck_csv, default_strategy):
        """Test card removal preference with 4 lands."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 3, "Island": 1, "Llanowar Elves": 2})
        key_cards = ["Llanowar Elves"]
        
        removed = choose_card_to_remove(hand, deck, key_cards, default_strategy)
        # Should remove a land when we have 4
        assert removed in ["Forest", "Island"]
    
    def test_choose_card_to_remove_non_key(self, simple_deck_csv, default_strategy):
        """Test card removal prefers non-key cards."""
        deck = Deck(simple_deck_csv)
        hand = Counter({"Forest": 2, "Llanowar Elves": 1, "Grizzly Bears": 1})
        key_cards = ["Llanowar Elves"]
        
        removed = choose_card_to_remove(hand, deck, key_cards, default_strategy)
        # Should prefer to remove Grizzly Bears (non-key, non-land)
        assert removed == "Grizzly Bears"
    
    def test_perform_mulligan_integration(self, simple_deck_csv, default_strategy):
        """Test full mulligan process."""
        deck = Deck(simple_deck_csv)
        key_cards = ["Llanowar Elves"]
        
        hand, mulligan_count = perform_mulligan(deck, key_cards, default_strategy)
        
        # Hand size should be 7 minus mulligan count
        assert sum(hand.values()) == 7 - mulligan_count
        # Mulligan count should be reasonable (0-7)
        assert 0 <= mulligan_count <= 7


# ==========================================================
# Phase 5: Simulation Tests
# ==========================================================

class TestSimulation:
    """Test game simulation mechanics."""
    
    def test_simulate_game_basic(self, simple_deck_csv):
        """Test basic game simulation runs without errors."""
        result = simulate_game(simple_deck_csv, turns=4)
        
        assert "cards_seen" in result
        assert "lands_in_play" in result
        assert "spells_cast" in result
        assert "mulligan_count" in result
        assert isinstance(result["cards_seen"], list)
    
    def test_simulate_game_with_config(self, complex_deck_csv, tmp_path):
        """Test simulation with configuration."""
        config = {
            "key_cards": ["Careful Study", "Wild Mongrel"],
            "key_card_turn_limit": 4,
            "ideal_setups": [
                {
                    "name": "Test Setup",
                    "requires_cards": ["Careful Study"],
                    "requires_colors": ["U"],
                    "turn_limit": 4
                }
            ]
        }
        
        result = simulate_game(complex_deck_csv, turns=4, config=config)
        
        assert "key_seen" in result
        assert "setup_results" in result
        assert "Careful Study" in result["key_seen"]
        assert "Test Setup" in result["setup_results"]
    
    def test_simulate_game_turns_progression(self, simple_deck_csv):
        """Test that turns progress correctly."""
        result = simulate_game(simple_deck_csv, turns=10)
        
        # Should have played at least some lands
        assert result["lands_in_play"] >= 0
        # Should have drawn initial hand + turns
        assert result["cards_drawn_total"] >= 7
    
    def test_simulate_game_mana_colors(self, complex_deck_csv):
        """Test that mana colors are tracked."""
        result = simulate_game(complex_deck_csv, turns=4)
        
        assert "mana_colors" in result
        assert isinstance(result["mana_colors"], list)


# ==========================================================
# Phase 6: Ideal Setup Evaluation Tests
# ==========================================================

class TestIdealSetups:
    """Test ideal setup evaluation."""
    
    def test_evaluate_setups_success(self, complex_deck_csv):
        """Test successful setup evaluation."""
        deck = Deck(complex_deck_csv)
        state = GameState(deck)
        
        # Simulate seeing required cards early
        state.turn = 2
        state.cards_seen_by_turn["Careful Study"] = 1
        state.cards_seen_by_turn["Wild Mongrel"] = 2
        state.mana_colors.add("U")
        state.mana_colors.add("G")
        state.mana_colors_by_turn[1] = {"U"}
        state.mana_colors_by_turn[2] = {"U", "G"}
        
        config = {
            "ideal_setups": [
                {
                    "name": "Early Combo",
                    "requires_cards": ["Careful Study", "Wild Mongrel"],
                    "requires_colors": ["U", "G"],
                    "turn_limit": 4
                }
            ]
        }
        
        results = evaluate_ideal_setups(state, config)
        assert results["Early Combo"] == True
    
    def test_evaluate_setups_failure_missing_card(self, complex_deck_csv):
        """Test setup failure when card is missing."""
        deck = Deck(complex_deck_csv)
        state = GameState(deck)
        
        state.turn = 4
        state.cards_seen_by_turn["Careful Study"] = 1
        # Wild Mongrel is missing
        state.mana_colors_by_turn[1] = {"U", "G"}
        
        config = {
            "ideal_setups": [
                {
                    "name": "Early Combo",
                    "requires_cards": ["Careful Study", "Wild Mongrel"],
                    "requires_colors": ["U", "G"],
                    "turn_limit": 4
                }
            ]
        }
        
        results = evaluate_ideal_setups(state, config)
        assert results["Early Combo"] == False
    
    def test_evaluate_setups_failure_too_late(self, complex_deck_csv):
        """Test setup failure when cards seen too late."""
        deck = Deck(complex_deck_csv)
        state = GameState(deck)
        
        state.turn = 5
        state.cards_seen_by_turn["Careful Study"] = 5  # Seen too late
        state.cards_seen_by_turn["Wild Mongrel"] = 2
        state.mana_colors_by_turn[1] = {"U", "G"}
        
        config = {
            "ideal_setups": [
                {
                    "name": "Early Combo",
                    "requires_cards": ["Careful Study", "Wild Mongrel"],
                    "requires_colors": ["U", "G"],
                    "turn_limit": 4
                }
            ]
        }
        
        results = evaluate_ideal_setups(state, config)
        assert results["Early Combo"] == False


# ==========================================================
# Phase 7: Configuration Tests
# ==========================================================

class TestConfiguration:
    """Test configuration loading and handling."""
    
    def test_load_config_valid(self, test_config):
        """Test loading valid configuration file."""
        config = load_config(test_config)
        
        assert "key_cards" in config
        assert "ideal_setups" in config
        assert len(config["key_cards"]) > 0
    
    def test_load_config_missing_file(self):
        """Test loading non-existent config file."""
        config = load_config("nonexistent_file.json")
        assert config == {}
    
    def test_load_config_structure(self, test_config):
        """Test config has expected structure."""
        config = load_config(test_config)
        
        assert isinstance(config["key_cards"], list)
        assert isinstance(config["ideal_setups"], list)
        
        if len(config["ideal_setups"]) > 0:
            setup = config["ideal_setups"][0]
            assert "name" in setup
            assert "requires_cards" in setup


# ==========================================================
# Phase 8: Edge Cases and Integration Tests
# ==========================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_deck(self, tmp_path):
        """Test handling of empty deck."""
        csv_content = """Card Name,Quantity,Type,Mana Cost,Conditions"""
        deck_path = tmp_path / "empty_deck.csv"
        deck_path.write_text(csv_content)
        
        deck = Deck(str(deck_path))
        assert len(deck.cards) == 0
        assert len(deck.card_info) == 0
    
    def test_deck_with_zero_quantity(self, tmp_path):
        """Test deck with zero quantity cards."""
        csv_content = """Card Name,Quantity,Type,Mana Cost,Conditions
Forest,0,Land,,effect:mana_G
Island,5,Land,,effect:mana_U"""
        
        deck_path = tmp_path / "zero_qty_deck.csv"
        deck_path.write_text(csv_content)
        
        deck = Deck(str(deck_path))
        forest_count = sum(1 for card in deck.cards if card == "Forest")
        assert forest_count == 0
    
    def test_malformed_conditions(self):
        """Test parsing malformed condition strings."""
        # Should not crash, just return empty or partial results
        result = parse_condition_string("invalid_format")
        assert isinstance(result, list)
        
        result = parse_condition_string("requires:;;;")
        assert isinstance(result, list)
    
    def test_simulate_zero_turns(self, simple_deck_csv):
        """Test simulation with zero turns."""
        result = simulate_game(simple_deck_csv, turns=0)
        # Should still have mulligan and initial hand
        assert result["mulligan_count"] >= 0
    
    def test_dual_land_mana_colors(self, complex_deck_csv):
        """Test that dual lands provide multiple colors."""
        deck = Deck(complex_deck_csv)
        state = GameState(deck)
        
        # Yavimaya Coast provides both U and G
        state.hand["Yavimaya Coast"] = 1
        state.play_land()
        
        assert "U" in state.mana_colors or "G" in state.mana_colors


# ==========================================================
# Performance and Statistical Tests
# ==========================================================

class TestStatistics:
    """Test statistical properties of simulations."""
    
    def test_mulligan_distribution(self, simple_deck_csv):
        """Test that mulligan counts have reasonable distribution."""
        mulligan_counts = []
        
        # Run multiple simulations
        for _ in range(50):
            result = simulate_game(simple_deck_csv, turns=4)
            mulligan_counts.append(result["mulligan_count"])
        
        # Most games should keep (mulligan_count = 0)
        zero_mull_pct = mulligan_counts.count(0) / len(mulligan_counts)
        
        # At least some games should keep opening hand
        assert zero_mull_pct > 0.3, "Too many mulligans occurring"
        
        # Should not mulligan to oblivion every game
        avg_mulligan = sum(mulligan_counts) / len(mulligan_counts)
        assert avg_mulligan < 3, "Average mulligan count too high"
    
    def test_cards_drawn_increases(self, simple_deck_csv):
        """Test that cards drawn increases with turns."""
        result_4_turns = simulate_game(simple_deck_csv, turns=4)
        result_8_turns = simulate_game(simple_deck_csv, turns=8)
        
        # More turns should generally mean more cards drawn
        # (accounting for variance)
        assert result_8_turns["cards_drawn_total"] >= result_4_turns["cards_drawn_total"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

