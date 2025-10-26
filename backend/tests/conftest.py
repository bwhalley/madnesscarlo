"""
Pytest configuration and shared fixtures for backend tests.
"""

import pytest
from collections import Counter


@pytest.fixture
def sample_deck_cards():
    """Sample deck with UG Madness cards for testing."""
    return [
        {"card_name": "Island", "count": 9},
        {"card_name": "Forest", "count": 7},
        {"card_name": "Yavimaya Coast", "count": 4},
        {"card_name": "Careful Study", "count": 4},
        {"card_name": "Frantic Search", "count": 4},
        {"card_name": "Survival of the Fittest", "count": 4},
        {"card_name": "Wild Mongrel", "count": 4},
        {"card_name": "Basking Rootwalla", "count": 4},
        {"card_name": "Arrogant Wurm", "count": 4},
        {"card_name": "Wonder", "count": 3},
        {"card_name": "Roar of the Wurm", "count": 2},
        {"card_name": "Squee, Goblin Nabob", "count": 2},
        {"card_name": "Counterspell", "count": 4},
        {"card_name": "Naturalize", "count": 3},
        {"card_name": "Waterfront Bouncer", "count": 2},
    ]


@pytest.fixture
def sample_config():
    """Sample simulation configuration."""
    return {
        "key_cards": [
            "Survival of the Fittest",
            "Squee, Goblin Nabob",
            "Wonder",
            "Roar of the Wurm"
        ],
        "key_card_turn_limit": 4,
        "mulligan_strategy": {
            "enabled": True,
            "min_lands": 2,
            "max_lands": 5,
            "must_have_key_card": False
        },
        "ideal_setups": [
            {
                "name": "Survival Engine",
                "turn_limit": 4,
                "requires_cards": ["Survival of the Fittest"],
                "requires_colors": ["G"],
                "requires_in_play": ["Survival of the Fittest"],
                "requires_min_lands": 2,
                "requires_any_creature_in_hand": True
            },
            {
                "name": "Counter Protection",
                "turn_limit": 2,
                "requires_cards": ["Counterspell"],
                "requires_colors": ["U"]
            },
            {
                "name": "Naturalize Access",
                "turn_limit": 2,
                "requires_cards": ["Naturalize"],
                "requires_colors": ["G"]
            },
            {
                "name": "Wonder in Graveyard",
                "turn_limit": 4,
                "requires_cards": ["Wonder"],
                "requires_colors": [],
                "requires_in_play": ["Island"],
                "requires_in_graveyard": ["Wonder"]
            },
            {
                "name": "Roar Flashback Available",
                "turn_limit": 4,
                "requires_cards": ["Roar of the Wurm"],
                "requires_colors": ["G"],
                "requires_in_graveyard": ["Roar of the Wurm"]
            }
        ]
    }


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    from app.simulation.engine import Deck, GameState
    
    cards_data = [
        {"card_name": "Island", "count": 10},
        {"card_name": "Forest", "count": 10},
        {"card_name": "Counterspell", "count": 4},
    ]
    
    deck = Deck(cards_data)
    state = GameState(deck)
    
    # Set up a typical mid-game state
    state.turn = 3
    state.lands_in_play = 3
    state.mana_colors = {"U", "G"}
    state.hand = Counter({"Counterspell": 1, "Forest": 1})
    state.battlefield = Counter({"Island": 2, "Forest": 1})
    state.graveyard = Counter()
    state.cards_seen = {"Island", "Forest", "Counterspell"}
    state.cards_seen_by_turn = {
        "Island": 0,
        "Forest": 1,
        "Counterspell": 2
    }
    state.mana_colors_by_turn = {
        1: {"U"},
        2: {"U", "G"},
        3: {"U", "G"}
    }
    
    return state

