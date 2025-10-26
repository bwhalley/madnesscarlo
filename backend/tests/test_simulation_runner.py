"""
Tests for the simulation runner module.

Tests simulation execution, aggregation, and statistics generation.
"""

import pytest
from app.simulation.runner import simulate_game, run_simulations


class TestSimulateGame:
    """Test single game simulation."""
    
    def test_simulate_game_returns_results(self, sample_deck_cards, sample_config):
        """simulate_game should return complete game results."""
        result = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        
        # Check all required fields are present
        assert "cards_seen" in result
        assert "cards_seen_by_turn" in result
        assert "key_seen" in result
        assert "setup_results" in result
        assert "spells_cast" in result
        assert "lands_in_play" in result
        assert "cards_drawn_total" in result
        assert "mana_colors" in result
        assert "mulligan_count" in result
        assert "graveyard" in result
        assert "battlefield" in result
        assert "madness_casts" in result
        assert "flashback_casts" in result
        assert "cards_tutored" in result
        assert "opening_hand_size" in result
    
    def test_simulate_game_tracks_key_cards(self, sample_deck_cards, sample_config):
        """simulate_game should track if key cards were seen."""
        result = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        
        # Should have key_seen dict with all configured key cards
        for key_card in sample_config["key_cards"]:
            assert key_card in result["key_seen"]
            assert isinstance(result["key_seen"][key_card], bool)
    
    def test_simulate_game_evaluates_setups(self, sample_deck_cards, sample_config):
        """simulate_game should evaluate all ideal setups."""
        result = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        
        # Should have setup_results dict with all configured setups
        for setup in sample_config["ideal_setups"]:
            assert setup["name"] in result["setup_results"]
            assert isinstance(result["setup_results"][setup["name"]], bool)
    
    def test_simulate_game_respects_turn_limit(self, sample_deck_cards, sample_config):
        """simulate_game should respect the turn limit."""
        result = simulate_game(sample_deck_cards, turns=3, config=sample_config)
        
        # Should have drawn opening 7 + 3 draws for turns (minimum)
        # Can be more due to card effects like Careful Study (+2 draw)
        assert result["cards_drawn_total"] >= 7
        assert result["cards_drawn_total"] <= 15  # 7 + 3 turns + card effects
    
    def test_simulate_game_tracks_mana_colors(self, sample_deck_cards, sample_config):
        """simulate_game should track mana colors produced."""
        result = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        
        # With UG deck, should have some combination of U and G
        # (might not have both if unlucky with draws)
        mana_colors = result["mana_colors"]
        assert isinstance(mana_colors, list)


class TestRunSimulations:
    """Test multiple simulation runs and aggregation."""
    
    def test_run_simulations_returns_aggregated_results(self, sample_deck_cards, sample_config):
        """run_simulations should return aggregated statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        # Check all required sections are present
        assert "summary" in results
        assert "card_stats" in results
        assert "key_card_stats" in results
        assert "setup_stats" in results
        assert "mulligan_stats" in results
        assert "graveyard_stats" in results
        assert "battlefield_stats" in results
        assert "madness_stats" in results
        assert "flashback_stats" in results
        assert "tutored_stats" in results
    
    def test_run_simulations_summary_stats(self, sample_deck_cards, sample_config):
        """run_simulations should calculate correct summary statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        summary = results["summary"]
        
        assert "simulations_run" in summary
        assert summary["simulations_run"] == 10
        assert "average_lands_in_play" in summary
        assert "average_cards_seen" in summary
        assert "average_mulligans" in summary  # Correct field name
        assert "average_graveyard_size" in summary
        assert "average_creatures_on_board" in summary
    
    def test_run_simulations_includes_all_setups(self, sample_deck_cards, sample_config):
        """run_simulations should include ALL configured setups, even if 0%."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        setup_stats = results["setup_stats"]
        
        # Should have one entry for each configured setup
        assert len(setup_stats) == len(sample_config["ideal_setups"])
        
        # Each setup should have name and percentage
        for stat in setup_stats:
            assert "setup_name" in stat
            assert "success_percentage" in stat
            assert isinstance(stat["success_percentage"], (int, float))
        
        # Check all configured setups are present
        setup_names = {stat["setup_name"] for stat in setup_stats}
        expected_names = {setup["name"] for setup in sample_config["ideal_setups"]}
        assert setup_names == expected_names
    
    def test_run_simulations_card_stats_format(self, sample_deck_cards, sample_config):
        """run_simulations should format card stats correctly."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        card_stats = results["card_stats"]
        
        # Should have stats for seen cards
        assert len(card_stats) > 0
        
        # Each stat should have proper format
        for stat in card_stats:
            assert "card" in stat
            assert "seen_percentage" in stat
            assert "cast_percentage" in stat
            assert 0 <= stat["seen_percentage"] <= 100
            assert 0 <= stat["cast_percentage"] <= 100
    
    def test_run_simulations_key_card_stats(self, sample_deck_cards, sample_config):
        """run_simulations should track key card statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        key_card_stats = results["key_card_stats"]
        
        # Should have stats for key cards that were seen
        for stat in key_card_stats:
            assert "card" in stat
            assert "seen_percentage" in stat
            assert stat["card"] in sample_config["key_cards"]
    
    def test_run_simulations_mulligan_stats(self, sample_deck_cards, sample_config):
        """run_simulations should track mulligan statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        mulligan_stats = results["mulligan_stats"]
        
        # Should have mulligan counts
        assert len(mulligan_stats) > 0
        
        for stat in mulligan_stats:
            assert "mulligan_count" in stat
            assert "games" in stat
            assert "percentage" in stat
    
    def test_run_simulations_graveyard_stats(self, sample_deck_cards, sample_config):
        """run_simulations should track graveyard statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        graveyard_stats = results["graveyard_stats"]
        
        # Should have graveyard stats (discards should happen)
        for stat in graveyard_stats:
            assert "card" in stat
            assert "avg_in_graveyard" in stat
            assert "percentage" in stat
    
    def test_run_simulations_battlefield_stats(self, sample_deck_cards, sample_config):
        """run_simulations should track battlefield statistics."""
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config
        )
        
        battlefield_stats = results["battlefield_stats"]
        
        # Should have battlefield stats (lands should be played)
        assert len(battlefield_stats) > 0
        
        for stat in battlefield_stats:
            assert "card" in stat
            assert "avg_on_battlefield" in stat
            assert "percentage" in stat
    
    def test_run_simulations_progress_callback(self, sample_deck_cards, sample_config):
        """run_simulations should call progress callback."""
        progress_calls = []
        
        def progress_callback(current, total, message):
            progress_calls.append((current, total, message))
        
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=sample_config,
            progress_callback=progress_callback
        )
        
        # Should have called progress callback
        assert len(progress_calls) > 0
        
        # Last call should be completion
        last_call = progress_calls[-1]
        assert last_call[0] == 10  # current
        assert last_call[1] == 10  # total
        assert "complete" in last_call[2].lower()


class TestSetupStatsAggregation:
    """Test that setup stats aggregation handles all cases correctly."""
    
    def test_setups_with_zero_success_included(self, sample_deck_cards):
        """Setups with 0% success should still appear in results."""
        # Create a config with an impossible setup
        config = {
            "key_cards": [],
            "mulligan_strategy": {"enabled": False},
            "ideal_setups": [
                {
                    "name": "Impossible Setup",
                    "turn_limit": 1,
                    "requires_cards": ["NonexistentCard"],
                    "requires_colors": ["Z"]  # Not a real color
                }
            ]
        }
        
        results = run_simulations(
            sample_deck_cards,
            runs=5,
            turns=4,
            config=config
        )
        
        # Should still have the setup in results
        setup_stats = results["setup_stats"]
        assert len(setup_stats) == 1
        assert setup_stats[0]["setup_name"] == "Impossible Setup"
        assert setup_stats[0]["success_percentage"] == 0.0
    
    def test_multiple_setups_with_mixed_results(self, sample_deck_cards):
        """Should handle mix of successful and unsuccessful setups."""
        config = {
            "key_cards": [],
            "mulligan_strategy": {"enabled": False},
            "ideal_setups": [
                {
                    "name": "Easy Setup",
                    "turn_limit": 4,
                    "requires_cards": [],  # No requirements
                    "requires_colors": []
                },
                {
                    "name": "Hard Setup",
                    "turn_limit": 1,
                    "requires_cards": ["Survival of the Fittest"],
                    "requires_colors": ["G"],
                    "requires_in_play": ["Survival of the Fittest"]
                }
            ]
        }
        
        results = run_simulations(
            sample_deck_cards,
            runs=10,
            turns=4,
            config=config
        )
        
        setup_stats = results["setup_stats"]
        assert len(setup_stats) == 2
        
        # Find each setup
        easy = next(s for s in setup_stats if s["setup_name"] == "Easy Setup")
        hard = next(s for s in setup_stats if s["setup_name"] == "Hard Setup")
        
        # Easy setup should succeed
        assert easy["success_percentage"] > 0
        
        # Hard setup might succeed but could be 0%
        assert hard["success_percentage"] >= 0


class TestSimulationDeterminism:
    """Test that simulations produce varied but reasonable results."""
    
    def test_multiple_runs_produce_different_results(self, sample_deck_cards, sample_config):
        """Multiple simulation runs should produce varied results (not deterministic)."""
        result1 = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        result2 = simulate_game(sample_deck_cards, turns=4, config=sample_config)
        
        # Results should be different (different random draws)
        assert result1["cards_seen"] != result2["cards_seen"] or \
               result1["lands_in_play"] != result2["lands_in_play"]
    
    def test_aggregated_results_converge(self, sample_deck_cards, sample_config):
        """Aggregated results over many runs should be stable."""
        results1 = run_simulations(sample_deck_cards, runs=50, turns=4, config=sample_config)
        results2 = run_simulations(sample_deck_cards, runs=50, turns=4, config=sample_config)
        
        # Average lands in play should be similar (within 10%)
        avg1 = results1["summary"]["average_lands_in_play"]
        avg2 = results2["summary"]["average_lands_in_play"]
        
        difference = abs(avg1 - avg2)
        relative_diff = difference / avg1 if avg1 > 0 else 0
        
        assert relative_diff < 0.2  # Within 20% (generous for 50 runs)

