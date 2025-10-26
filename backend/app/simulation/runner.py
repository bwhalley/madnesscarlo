"""
Simulation Runner

Executes Monte Carlo simulations and aggregates results.
"""

from typing import Dict, List, Any, Optional
from collections import Counter
from .engine import (
    Deck, GameState, perform_mulligan, evaluate_ideal_setups,
    CARD_ACTIONS, ACTIVATED_ABILITIES
)


def simulate_game(
    cards_data: List[Dict[str, Any]],
    turns: int = 4,
    config: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Simulate a single game.
    
    Args:
        cards_data: List of card dictionaries
        turns: Number of turns to simulate
        config: Simulation configuration
        
    Returns:
        Dictionary with simulation results
    """
    deck = Deck(cards_data)
    state = GameState(deck)
    
    # Perform mulligan
    key_cards = (config or {}).get("key_cards", [])
    mulligan_strategy = (config or {}).get("mulligan_strategy", {})
    kept_hand, mulligan_count = perform_mulligan(deck, key_cards, mulligan_strategy)
    
    # Set the kept hand as the opening hand
    state.turn = 0
    state.hand = kept_hand
    
    # Track opening hand for analysis
    opening_hand_list = sorted(list(kept_hand.elements()))
    opening_hand_size = len(opening_hand_list)
    
    # Mark cards in opening hand as seen on turn 0
    for card in state.hand.keys():
        state.cards_seen.add(card)
        state.cards_seen_by_turn[card] = 0
    
    state.cards_drawn_total = 7  # Started with 7 cards
    
    # Simulate each turn
    for turn in range(1, turns + 1):
        state.turn = turn
        
        # Play land for turn
        state.play_land()
        
        # Cast spells from hand
        for card in list(state.hand.keys()):
            if card in CARD_ACTIONS and state.can_cast(card):
                CARD_ACTIONS[card](state)
        
        # Activate abilities (Survival, Wild Mongrel, flashback, etc.)
        for card in list(state.battlefield.keys()):
            if card in ACTIVATED_ABILITIES:
                ACTIVATED_ABILITIES[card](state)
        
        # Check for flashback spells in graveyard
        for card in list(state.graveyard.keys()):
            if card in ACTIVATED_ABILITIES:
                ACTIVATED_ABILITIES[card](state)
        
        # Draw for turn
        state.draw_card(1)
    
    # Evaluate ideal setups
    setup_results = evaluate_ideal_setups(state, config or {})
    
    # Check key cards
    key_cards = (config or {}).get("key_cards", [])
    key_card_turn_limit = (config or {}).get("key_card_turn_limit", 4)
    key_seen = {
        k: (k in state.cards_seen_by_turn and 
            state.cards_seen_by_turn[k] <= key_card_turn_limit)
        for k in key_cards
    }
    
    return {
        "cards_seen": list(state.cards_seen),
        "cards_seen_by_turn": dict(state.cards_seen_by_turn),
        "key_seen": key_seen,
        "setup_results": setup_results,
        "spells_cast": dict(state.spells_cast),
        "lands_in_play": state.lands_in_play,
        "cards_drawn_total": state.cards_drawn_total,
        "mana_colors": list(state.mana_colors),
        "mulligan_count": mulligan_count,
        "graveyard": dict(state.graveyard),
        "battlefield": dict(state.battlefield),
        "madness_casts": dict(state.madness_casts),
        "flashback_casts": dict(state.flashback_casts),
        "cards_tutored": dict(state.cards_tutored),
        "opening_hand": opening_hand_list,
        "opening_hand_size": opening_hand_size
    }


def run_simulations(
    cards_data: List[Dict[str, Any]],
    runs: int = 1000,
    turns: int = 4,
    config: Optional[Dict] = None,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Run multiple simulations and aggregate results.
    
    Args:
        cards_data: List of card dictionaries
        runs: Number of simulations to run
        turns: Number of turns per simulation
        config: Simulation configuration
        progress_callback: Optional callback function(current, total, message)
        
    Returns:
        Dictionary with aggregated results
    """
    seen_counter = Counter()
    cast_counter = Counter()
    total_lands = 0
    total_cards_seen = 0
    key_card_counts = Counter()
    setup_success = Counter()
    mulligan_counts = Counter()
    total_mulligans = 0
    
    graveyard_counter = Counter()
    battlefield_counter = Counter()
    madness_counter = Counter()
    flashback_counter = Counter()
    tutored_counter = Counter()
    total_creatures_on_board = 0
    total_graveyard_size = 0
    
    all_results = []
    
    for i in range(runs):
        # Progress callback
        if progress_callback and i % max(1, runs // 100) == 0:
            progress_callback(i, runs, f"Simulating game {i+1}/{runs}")
        
        result = simulate_game(cards_data, turns, config=config)
        all_results.append(result)
        
        # Aggregate basic stats
        for c in result["cards_seen"]:
            seen_counter[c] += 1
        for c, n in result["spells_cast"].items():
            cast_counter[c] += n
        for k, seen in result["key_seen"].items():
            if seen:
                key_card_counts[k] += 1
        for setup_name, success in result["setup_results"].items():
            if success:
                setup_success[setup_name] += 1
        
        total_lands += result["lands_in_play"]
        total_cards_seen += len(result["cards_seen"])
        
        # Track mulligan stats
        mull_count = result["mulligan_count"]
        mulligan_counts[mull_count] += 1
        total_mulligans += mull_count
        
        # Track graveyard stats
        for card, count in result["graveyard"].items():
            graveyard_counter[card] += count
        for card, count in result["battlefield"].items():
            battlefield_counter[card] += count
        for card, count in result["madness_casts"].items():
            madness_counter[card] += count
        for card, count in result["flashback_casts"].items():
            flashback_counter[card] += count
        for card, count in result["cards_tutored"].items():
            tutored_counter[card] += count
        
        total_graveyard_size += sum(result["graveyard"].values())
        total_creatures_on_board += sum(result["battlefield"].values())
    
    # Final progress update
    if progress_callback:
        progress_callback(runs, runs, "Simulation complete")
    
    # Build result structure
    card_stats = []
    for card in seen_counter:
        card_stats.append({
            "card": card,
            "seen_percentage": round(seen_counter[card] / runs * 100, 2),
            "cast_percentage": round(cast_counter.get(card, 0) / runs * 100, 2)
        })
    
    key_card_stats = []
    for card in key_card_counts:
        key_card_stats.append({
            "card": card,
            "seen_percentage": round(key_card_counts[card] / runs * 100, 2)
        })
    
    # Build setup stats - include ALL configured setups, even if 0% success
    setup_stats = []
    configured_setups = (config or {}).get("ideal_setups", [])
    for setup in configured_setups:
        setup_name = setup["name"]
        success_count = setup_success.get(setup_name, 0)
        setup_stats.append({
            "setup_name": setup_name,
            "success_percentage": round(success_count / runs * 100, 2)
        })
    
    mulligan_stats = []
    for mull_count in sorted(mulligan_counts.keys()):
        mulligan_stats.append({
            "mulligan_count": mull_count,
            "games": mulligan_counts[mull_count],
            "percentage": round(mulligan_counts[mull_count] / runs * 100, 2)
        })
    
    graveyard_stats = []
    for card in graveyard_counter:
        graveyard_stats.append({
            "card": card,
            "avg_in_graveyard": round(graveyard_counter[card] / runs, 2),
            "percentage": round(graveyard_counter[card] / runs * 100, 2)
        })
    graveyard_stats.sort(key=lambda x: x["avg_in_graveyard"], reverse=True)
    
    # Battlefield stats
    battlefield_stats = []
    for card in battlefield_counter:
        battlefield_stats.append({
            "card": card,
            "avg_on_battlefield": round(battlefield_counter[card] / runs, 2),
            "percentage": round(battlefield_counter[card] / runs * 100, 2)
        })
    battlefield_stats.sort(key=lambda x: x["avg_on_battlefield"], reverse=True)
    
    # Madness casts
    madness_stats = []
    for card in madness_counter:
        madness_stats.append({
            "card": card,
            "madness_casts": madness_counter[card],
            "percentage": round(madness_counter[card] / runs * 100, 2)
        })
    madness_stats.sort(key=lambda x: x["madness_casts"], reverse=True)
    
    # Flashback casts
    flashback_stats = []
    for card in flashback_counter:
        flashback_stats.append({
            "card": card,
            "flashback_casts": flashback_counter[card],
            "percentage": round(flashback_counter[card] / runs * 100, 2)
        })
    flashback_stats.sort(key=lambda x: x["flashback_casts"], reverse=True)
    
    # Tutored cards
    tutored_stats = []
    for card in tutored_counter:
        tutored_stats.append({
            "card": card,
            "times_tutored": tutored_counter[card],
            "percentage": round(tutored_counter[card] / runs * 100, 2)
        })
    tutored_stats.sort(key=lambda x: x["times_tutored"], reverse=True)
    
    summary = {
        "average_lands_in_play": round(total_lands / runs, 2),
        "average_cards_seen": round(total_cards_seen / runs, 2),
        "average_mulligans": round(total_mulligans / runs, 2),
        "games_with_0_mulligans_percentage": round(
            mulligan_counts.get(0, 0) / runs * 100, 2
        ),
        "average_graveyard_size": round(total_graveyard_size / runs, 2),
        "average_creatures_on_board": round(total_creatures_on_board / runs, 2),
        "total_madness_casts": sum(madness_counter.values()),
        "total_flashback_casts": sum(flashback_counter.values()),
        "simulations_run": runs,
        "turns_simulated": turns
    }
    
    return {
        "summary": summary,
        "card_stats": card_stats,
        "key_card_stats": key_card_stats,
        "setup_stats": setup_stats,
        "mulligan_stats": mulligan_stats,
        "graveyard_stats": graveyard_stats,
        "battlefield_stats": battlefield_stats,
        "madness_stats": madness_stats,
        "flashback_stats": flashback_stats,
        "tutored_stats": tutored_stats,
        "all_results": all_results  # Include for detailed analysis
    }

