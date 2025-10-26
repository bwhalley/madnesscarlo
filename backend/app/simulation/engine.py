"""
Simulation Engine

Core Monte Carlo simulation logic adapted from madness.py.
This module handles the simulation of Magic: The Gathering games.
"""

import random
from collections import Counter
from typing import Dict, List, Set, Optional, Any

from app.simulation.card_database import get_card_database


# ==========================================================
# Phase 1: Condition Parsing
# ==========================================================

def parse_condition_string(cond_str: Optional[str]) -> List[Dict]:
    """Parse condition string from card data."""
    conditions = []
    if not cond_str or not isinstance(cond_str, str) or not cond_str.strip():
        return conditions
    
    for part in cond_str.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key, value = key.strip().lower(), value.strip()
        
        if key == "requires":
            if ">=" in value:
                left, right = value.split(">=")
                conditions.append({
                    "type": "requires",
                    "target": left.strip(),
                    "op": ">=",
                    "value": int(right.strip())
                })
            elif "=" in value:
                left, right = value.split("=")
                conditions.append({
                    "type": "requires",
                    "target": left.strip(),
                    "op": "=",
                    "value": right.strip()
                })
            else:
                conditions.append({
                    "type": "requires",
                    "target": value.strip(),
                    "op": "exists"
                })
        elif key == "effect":
            conditions.append({"type": "effect", "value": value})
        elif key == "timing":
            conditions.append({"type": "timing", "value": value})
        elif key == "category":
            conditions.append({"type": "category", "value": value})
    
    return conditions


# ==========================================================
# Deck Class
# ==========================================================

class Deck:
    """Represents a deck of cards for simulation."""
    
    def __init__(self, cards_data: List[Dict[str, Any]]):
        """
        Initialize deck from list of card dictionaries.
        
        Args:
            cards_data: List of dicts with 'name', 'quantity', 'type', 'mana_cost', 'conditions'
        """
        self.cards = []
        self.card_info = {}
        
        # Get card database instance
        card_db = get_card_database()
        
        for card_data in cards_data:
            card_name = card_data.get('name') or card_data.get('card_name')
            # Support both 'quantity' (schema) and 'count' (legacy/test data)
            quantity = card_data.get('quantity') or card_data.get('count', 1)
            
            # Add cards to deck
            self.cards.extend([card_name] * quantity)
            
            # Look up card data from authoritative source (AtomicCards.json)
            card_type = card_db.get_card_type(card_name)
            mana_cost = card_db.get_mana_cost(card_name) or card_data.get("mana_cost", "")
            colors = card_db.get_card_colors(card_name)
            
            # Store card info (using AtomicCards.json data + our custom conditions)
            self.card_info[card_name] = {
                "type": card_type,
                "mana_cost": mana_cost,
                "colors": colors,
                "conditions": parse_condition_string(card_data.get("conditions"))
            }
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def draw(self, n: int = 1) -> List[str]:
        """Draw n cards from the top of the deck."""
        drawn = []
        for _ in range(n):
            if self.cards:
                drawn.append(self.cards.pop(0))
        return drawn


# ==========================================================
# Game State
# ==========================================================

class GameState:
    """Tracks the state of a simulated game."""
    
    def __init__(self, deck: Deck):
        self.deck = deck
        self.deck.shuffle()
        self.hand = Counter()
        self.lands_in_play = 0
        self.turn = 1
        self.cards_seen: Set[str] = set()
        self.cards_seen_by_turn: Dict[str, int] = {}
        self.spells_cast = Counter()
        self.cards_drawn_total = 0
        self.mana_colors: Set[str] = set()
        self.mana_colors_by_turn: Dict[int, Set[str]] = {}
        self.graveyard = Counter()
        self.battlefield = Counter()
        self.madness_casts = Counter()
        self.flashback_casts = Counter()
        self.cards_tutored = Counter()
    
    def draw_card(self, n: int = 1):
        """Draw n cards from the deck."""
        drawn = self.deck.draw(n)
        for card in drawn:
            self.hand[card] += 1
            self.cards_seen.add(card)
            if card not in self.cards_seen_by_turn:
                self.cards_seen_by_turn[card] = self.turn
        self.cards_drawn_total += len(drawn)
    
    def play_land(self):
        """Play one land per turn if possible."""
        for card, count in list(self.hand.items()):
            info = self.deck.card_info.get(card, {})
            if "land" in info.get("type", "").lower() and count > 0:
                # Extract mana colors from conditions (if present)
                conds = info.get("conditions", [])
                for cond in conds:
                    if cond["type"] == "effect" and cond["value"].startswith("mana_"):
                        color = cond["value"].split("_")[1]
                        self.mana_colors.add(color.upper())
                
                # Infer mana from basic land names
                if "Island" in card:
                    self.mana_colors.add("U")
                elif "Forest" in card:
                    self.mana_colors.add("G")
                elif "Mountain" in card:
                    self.mana_colors.add("R")
                elif "Plains" in card:
                    self.mana_colors.add("W")
                elif "Swamp" in card:
                    self.mana_colors.add("B")
                else:
                    # For non-basic lands, use colorIdentity from card database
                    colors = info.get("colors", [])
                    for color in colors:
                        self.mana_colors.add(color)
                
                self.hand[card] -= 1
                self.lands_in_play += 1
                self.battlefield[card] += 1
                self.mana_colors_by_turn[self.turn] = self.mana_colors.copy()
                break
    
    def has_color(self, color: str) -> bool:
        """Check if mana color is available."""
        return color.upper() in self.mana_colors
    
    def can_cast(self, card_name: str) -> bool:
        """Check if a card can be cast based on conditions."""
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] != "requires":
                continue
            target = cond["target"]
            op = cond["op"]
            value = cond.get("value")
            
            if target == "lands" and op == ">=" and self.lands_in_play < value:
                return False
            if target == "color" and op == "=" and not self.has_color(value):
                return False
        return True
    
    def move_to_graveyard(self, card_name: str, from_hand: bool = True):
        """Move a card to graveyard."""
        if from_hand and self.hand[card_name] > 0:
            self.hand[card_name] -= 1
        elif not from_hand and self.battlefield[card_name] > 0:
            self.battlefield[card_name] -= 1
        self.graveyard[card_name] += 1
    
    def get_card_effect(self, card_name: str, effect_prefix: str) -> Optional[str]:
        """Get effect value for a card."""
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] == "effect" and cond["value"].startswith(effect_prefix):
                return cond["value"].replace(effect_prefix, "")
        return None
    
    def has_effect(self, card_name: str, effect_name: str) -> bool:
        """Check if a card has a specific effect."""
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] == "effect" and cond["value"].startswith(effect_name):
                return True
        return False


# ==========================================================
# Card-specific Actions
# ==========================================================

def is_creature(card_name: str, deck: Deck) -> bool:
    """Check if a card is a creature."""
    card_info = deck.card_info.get(card_name, {})
    return "creature" in card_info.get("type", "").lower()


def discard_random(state: GameState, count: int, enable_madness: bool = False):
    """Discard random cards from hand."""
    discarded = []
    all_cards = list(state.hand.elements())
    
    for _ in range(min(count, len(all_cards))):
        if not all_cards:
            break
        card = random.choice(all_cards)
        all_cards.remove(card)
        state.hand[card] -= 1
        
        # Check for madness
        if enable_madness and state.has_effect(card, "madness_"):
            madness_cost = state.get_card_effect(card, "madness_")
            can_cast_madness = True
            if madness_cost and madness_cost != "0":
                for char in madness_cost:
                    if char.isalpha() and not state.has_color(char):
                        can_cast_madness = False
                        break
            if can_cast_madness:
                state.graveyard[card] += 1
                state.madness_casts[card] += 1
                state.spells_cast[card] += 1
                discarded.append((card, "madness"))
                continue
        
        state.graveyard[card] += 1
        discarded.append((card, "discard"))
    
    return discarded


def play_careful_study(state: GameState):
    """Play Careful Study: Draw 2, discard 2."""
    if state.hand["Careful Study"] > 0 and state.can_cast("Careful Study"):
        state.hand["Careful Study"] -= 1
        state.graveyard["Careful Study"] += 1
        state.spells_cast["Careful Study"] += 1
        state.draw_card(2)
        discard_random(state, 2, enable_madness=True)


def play_frantic_search(state: GameState):
    """Play Frantic Search: Draw 2, discard 2."""
    if state.hand["Frantic Search"] > 0 and state.can_cast("Frantic Search"):
        state.hand["Frantic Search"] -= 1
        state.graveyard["Frantic Search"] += 1
        state.spells_cast["Frantic Search"] += 1
        state.draw_card(2)
        discard_random(state, 2, enable_madness=True)


def play_survival(state: GameState):
    """Play Survival of the Fittest."""
    if state.hand["Survival of the Fittest"] > 0 and state.can_cast("Survival of the Fittest"):
        state.hand["Survival of the Fittest"] -= 1
        state.battlefield["Survival of the Fittest"] += 1
        state.spells_cast["Survival of the Fittest"] += 1


def activate_survival(state: GameState):
    """Activate Survival: discard creature, tutor another creature."""
    if state.battlefield.get("Survival of the Fittest", 0) > 0:
        # Find a creature in hand to discard
        creatures_in_hand = [
            card for card in state.hand.elements()
            if is_creature(card, state.deck)
        ]
        if creatures_in_hand:
            discard = random.choice(creatures_in_hand)
            state.hand[discard] -= 1
            
            # Check for madness
            if state.has_effect(discard, "madness_"):
                madness_cost = state.get_card_effect(discard, "madness_")
                can_cast_madness = True
                if madness_cost and madness_cost != "0":
                    for char in madness_cost:
                        if char.isalpha() and not state.has_color(char):
                            can_cast_madness = False
                            break
                if can_cast_madness:
                    state.battlefield[discard] += 1
                    state.madness_casts[discard] += 1
                else:
                    state.graveyard[discard] += 1
            else:
                state.graveyard[discard] += 1
            
            # Tutor for a creature from library
            creatures_in_deck = [
                card for card in state.deck.cards
                if is_creature(card, state.deck)
            ]
            if creatures_in_deck:
                tutored = random.choice(creatures_in_deck)
                state.deck.cards.remove(tutored)
                state.hand[tutored] += 1
                state.cards_seen.add(tutored)
                if tutored not in state.cards_seen_by_turn:
                    state.cards_seen_by_turn[tutored] = state.turn
                state.cards_tutored[tutored] += 1


def play_wild_mongrel(state: GameState):
    """Play Wild Mongrel as creature."""
    if state.hand.get("Wild Mongrel", 0) > 0 and state.can_cast("Wild Mongrel"):
        state.hand["Wild Mongrel"] -= 1
        state.battlefield["Wild Mongrel"] += 1
        state.spells_cast["Wild Mongrel"] += 1


def activate_wild_mongrel(state: GameState):
    """Activate Wild Mongrel: discard a card."""
    if state.battlefield.get("Wild Mongrel", 0) > 0 and len(list(state.hand.elements())) > 0:
        discard_random(state, 1, enable_madness=True)


def play_waterfront_bouncer(state: GameState):
    """Play Waterfront Bouncer as creature."""
    if state.hand.get("Waterfront Bouncer", 0) > 0 and state.can_cast("Waterfront Bouncer"):
        state.hand["Waterfront Bouncer"] -= 1
        state.battlefield["Waterfront Bouncer"] += 1
        state.spells_cast["Waterfront Bouncer"] += 1


def activate_waterfront_bouncer(state: GameState):
    """Activate Waterfront Bouncer: discard a card."""
    if state.battlefield.get("Waterfront Bouncer", 0) > 0 and len(list(state.hand.elements())) > 0:
        discard_random(state, 1, enable_madness=True)


def play_basking_rootwalla(state: GameState):
    """Play Basking Rootwalla as creature."""
    if state.hand.get("Basking Rootwalla", 0) > 0 and state.can_cast("Basking Rootwalla"):
        state.hand["Basking Rootwalla"] -= 1
        state.battlefield["Basking Rootwalla"] += 1
        state.spells_cast["Basking Rootwalla"] += 1


def play_arrogant_wurm(state: GameState):
    """Play Arrogant Wurm as creature."""
    if state.hand.get("Arrogant Wurm", 0) > 0 and state.can_cast("Arrogant Wurm"):
        state.hand["Arrogant Wurm"] -= 1
        state.battlefield["Arrogant Wurm"] += 1
        state.spells_cast["Arrogant Wurm"] += 1


def play_wonder(state: GameState):
    """Play Wonder as creature."""
    if state.hand.get("Wonder", 0) > 0 and state.can_cast("Wonder"):
        state.hand["Wonder"] -= 1
        state.battlefield["Wonder"] += 1
        state.spells_cast["Wonder"] += 1


def play_roar_flashback(state: GameState):
    """Cast Roar of the Wurm from graveyard via flashback."""
    if state.graveyard.get("Roar of the Wurm", 0) > 0:
        # Check if we have 3G mana (simplified - just check for G)
        if state.has_color("G"):
            state.graveyard["Roar of the Wurm"] -= 1
            # Create a 6/6 token (tracked as battlefield entry)
            state.battlefield["Wurm Token"] = state.battlefield.get("Wurm Token", 0) + 1
            state.flashback_casts["Roar of the Wurm"] += 1


# Card actions registry
CARD_ACTIONS = {
    "Careful Study": play_careful_study,
    "Frantic Search": play_frantic_search,
    "Survival of the Fittest": play_survival,
    "Wild Mongrel": play_wild_mongrel,
    "Waterfront Bouncer": play_waterfront_bouncer,
    "Basking Rootwalla": play_basking_rootwalla,
    "Arrogant Wurm": play_arrogant_wurm,
    "Wonder": play_wonder,
}


# Activated abilities (run after casting spells)
ACTIVATED_ABILITIES = {
    "Survival of the Fittest": activate_survival,
    "Wild Mongrel": activate_wild_mongrel,
    "Waterfront Bouncer": activate_waterfront_bouncer,
    "Roar of the Wurm": play_roar_flashback,
}


# ==========================================================
# Mulligan Logic
# ==========================================================

def count_lands_in_hand(hand: Counter, deck: Deck) -> int:
    """Count the number of lands in hand."""
    return sum(
        count for card, count in hand.items()
        if "land" in (deck.card_info.get(card, {}).get("type") or "").lower()
    )


def should_mulligan(hand: Counter, deck: Deck, strategy: Dict) -> bool:
    """Determine if we should mulligan based on strategy."""
    if not strategy or not strategy.get("enabled", True):
        return False
    
    land_count = count_lands_in_hand(hand, deck)
    min_lands = strategy.get("min_lands", 2)
    max_lands = strategy.get("max_lands", 5)
    
    # Check land count criteria
    if land_count < min_lands or land_count > max_lands:
        return True
    
    # Check if we need a creature
    requires_creature = strategy.get("requires_creature", False)
    if requires_creature:
        has_creature = any(
            is_creature(card, deck) for card in hand.keys()
        )
        if not has_creature:
            return True
    
    return False


def perform_mulligan(deck: Deck, key_cards: List[str], strategy: Dict) -> tuple:
    """
    Perform mulligan logic according to London mulligan rules.
    Returns: (hand, mulligan_count)
    """
    if not strategy or not strategy.get("enabled", True):
        hand = Counter()
        for card in deck.draw(7):
            hand[card] += 1
        return hand, 0
    
    mulligan_count = 0
    max_mulligans = strategy.get("max_mulligans", 7)
    
    # Draw initial hand
    hand = Counter()
    for card in deck.draw(7):
        hand[card] += 1
    
    # Keep mulliganing until we get a keepable hand
    while should_mulligan(hand, deck, strategy) and mulligan_count < max_mulligans:
        mulligan_count += 1
        
        # Put cards back and reshuffle
        for card, count in hand.items():
            deck.cards.extend([card] * count)
        deck.shuffle()
        
        # Draw 7 again
        hand = Counter()
        for card in deck.draw(7):
            hand[card] += 1
    
    # After keeping, remove one card per mulligan taken
    for _ in range(mulligan_count):
        all_cards = list(hand.elements())
        if all_cards:
            card_to_remove = random.choice(all_cards)
            hand[card_to_remove] -= 1
            if hand[card_to_remove] == 0:
                del hand[card_to_remove]
            deck.cards.append(card_to_remove)
    
    return hand, mulligan_count


# ==========================================================
# Ideal Setup Evaluation
# ==========================================================

def evaluate_ideal_setups(state: GameState, config: Dict) -> Dict[str, bool]:
    """Evaluate if ideal setups were achieved."""
    setups = config.get("ideal_setups", [])
    setup_results = {}
    
    for setup in setups:
        name = setup["name"]
        turn_limit = setup.get("turn_limit", 4)
        
        # Check if all required cards were seen by the turn_limit
        required_cards = setup.get("requires_cards", [])
        cards_ok = all(
            card in state.cards_seen_by_turn and
            state.cards_seen_by_turn[card] <= turn_limit
            for card in required_cards
        )
        
        # Check if all required colors were available
        required_colors = setup.get("requires_colors", [])
        colors_ok = True
        if required_colors:
            colors_ok = any(
                all(color in colors for color in required_colors)
                for turn, colors in state.mana_colors_by_turn.items()
                if turn <= turn_limit
            )
        
        # Check minimum lands requirement
        min_lands = setup.get("requires_min_lands", 0)
        lands_ok = state.lands_in_play >= min_lands
        
        # Check if required cards are in play
        requires_in_play = setup.get("requires_in_play", [])
        in_play_ok = all(
            card in state.battlefield
            for card in requires_in_play
        )
        
        # Check if required cards are in graveyard
        requires_in_graveyard = setup.get("requires_in_graveyard", [])
        in_graveyard_ok = all(
            card in state.graveyard
            for card in requires_in_graveyard
        )
        
        # Check if any creature in hand is required
        requires_any_creature = setup.get("requires_any_creature_in_hand", False)
        creature_in_hand_ok = True
        if requires_any_creature:
            # Check if any card in hand is a creature
            creature_in_hand_ok = any(
                state.deck.card_info.get(card, {}).get("type", "").startswith("Creature")
                for card in state.hand.keys()
            )
        
        setup_results[name] = (
            cards_ok and 
            colors_ok and 
            lands_ok and 
            in_play_ok and 
            in_graveyard_ok and 
            creature_in_hand_ok
        )
    
    return setup_results


# Continue with more simulation logic in the next file...

