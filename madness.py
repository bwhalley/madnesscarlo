import pandas as pd
import random
import json
import argparse
import os
from collections import Counter
from tqdm import tqdm


# ==========================================================
# Phase 1: Condition Parsing
# ==========================================================

def parse_condition_string(cond_str):
    conditions = []
    if not isinstance(cond_str, str) or not cond_str.strip():
        return conditions
    for part in cond_str.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key, value = key.strip().lower(), value.strip()
        if key == "requires":
            if ">=" in value:
                left, right = value.split(">=")
                conditions.append({"type": "requires", "target": left.strip(), "op": ">=", "value": int(right.strip())})
            elif "=" in value:
                left, right = value.split("=")
                conditions.append({"type": "requires", "target": left.strip(), "op": "=", "value": right.strip()})
            else:
                conditions.append({"type": "requires", "target": value.strip(), "op": "exists"})
        elif key == "effect":
            conditions.append({"type": "effect", "value": value})
        elif key == "timing":
            conditions.append({"type": "timing", "value": value})
        elif key == "category":
            conditions.append({"type": "category", "value": value})
    return conditions

# ==========================================================
# Ideal Setup Evaluation
# ==========================================================
def evaluate_ideal_setups(state, config):
    setups = config.get("ideal_setups", [])
    setup_results = {}

    for setup in setups:
        name = setup["name"]
        turn_limit = setup.get("turn_limit", 4)
        
        # Check if all required cards were seen by the turn_limit
        required_cards = setup.get("requires_cards", [])
        cards_ok = all(
            card in state.cards_seen_by_turn and state.cards_seen_by_turn[card] <= turn_limit
            for card in required_cards
        )
        
        # Check if all required colors were available by the turn_limit
        required_colors = setup.get("requires_colors", [])
        colors_ok = True
        if required_colors:
            # Find if any turn <= turn_limit had all required colors
            colors_ok = any(
                all(color in colors for color in required_colors)
                for turn, colors in state.mana_colors_by_turn.items()
                if turn <= turn_limit
            )
        
        # Check if required cards are in graveyard
        required_in_graveyard = setup.get("requires_in_graveyard", [])
        graveyard_ok = all(
            card in state.graveyard and state.graveyard[card] > 0
            for card in required_in_graveyard
        )
        
        # Check if required cards are in play (battlefield)
        required_in_play = setup.get("requires_in_play", [])
        in_play_ok = all(
            card in state.battlefield and state.battlefield[card] > 0
            for card in required_in_play
        )
        
        # Check if any creature is in hand (for Survival engine scenarios)
        requires_any_creature_in_hand = setup.get("requires_any_creature_in_hand", False)
        creature_in_hand_ok = True
        if requires_any_creature_in_hand:
            # Check if any card in hand is a creature
            creature_in_hand_ok = any(
                "creature" in state.deck.card_info.get(card, {}).get("type", "").lower()
                for card in state.hand.keys()
            )
        
        # Check minimum lands requirement (for setups that need mana)
        min_lands = setup.get("requires_min_lands", 0)
        lands_ok = state.lands_in_play >= min_lands

        # Check all requirements
        setup_results[name] = (cards_ok and colors_ok and graveyard_ok and 
                               in_play_ok and creature_in_hand_ok and lands_ok)

    return setup_results


# ==========================================================
# Phase 2: Deck Class
# ==========================================================

class Deck:
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)
        self.cards = []
        for _, row in df.iterrows():
            self.cards.extend([row['Card Name']] * int(row['Quantity']))
        self.card_info = {
            row['Card Name']: {
                "type": row.get("Type", ""),
                "mana_cost": row.get("Mana Cost", ""),
                "conditions": parse_condition_string(row.get("Conditions", ""))
            }
            for _, row in df.iterrows()
        }

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        drawn = []
        for _ in range(n):
            if self.cards:
                drawn.append(self.cards.pop(0))
        return drawn


# ==========================================================
# Phase 3: Game State & Card Logic
# ==========================================================

class GameState:
    def __init__(self, deck: Deck):
        self.deck = deck
        self.deck.shuffle()
        self.hand = Counter()
        self.lands_in_play = 0
        self.turn = 1
        self.cards_seen = set()
        self.cards_seen_by_turn = {}  # Maps card_name -> turn_first_seen
        self.spells_cast = Counter()
        self.cards_drawn_total = 0
        self.mana_colors = set()
        self.mana_colors_by_turn = {}  # Maps turn -> set of colors available
        self.graveyard = Counter()  # Cards in graveyard
        self.battlefield = Counter()  # Creatures/permanents in play
        self.madness_casts = Counter()  # Track madness casts
        self.flashback_casts = Counter()  # Track flashback casts
        self.cards_tutored = Counter()  # Track tutored cards

    def draw_card(self, n=1):
        drawn = self.deck.draw(n)
        for card in drawn:
            self.hand[card] += 1
            self.cards_seen.add(card)
            # Track which turn this card was first seen
            if card not in self.cards_seen_by_turn:
                self.cards_seen_by_turn[card] = self.turn
        self.cards_drawn_total += len(drawn)

    def play_land(self):
        """Play one land per turn if possible."""
        for card, count in list(self.hand.items()):
            info = self.deck.card_info.get(card, {})
            if "land" in info.get("type", "").lower() and count > 0:
                conds = info.get("conditions", [])
                for cond in conds:
                    if cond["type"] == "effect" and cond["value"].startswith("mana_"):
                        color = cond["value"].split("_")[1]
                        self.mana_colors.add(color.upper())
                self.hand[card] -= 1
                self.lands_in_play += 1
                self.battlefield[card] += 1  # Track specific land in play
                # Track which colors are available at each turn
                self.mana_colors_by_turn[self.turn] = self.mana_colors.copy()
                break

    def has_color(self, color):
        return color.upper() in self.mana_colors

    def can_cast(self, card_name: str):
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] != "requires":
                continue
            target, op, value = cond["target"], cond["op"], cond.get("value")
            if target == "lands" and op == ">=" and self.lands_in_play < value:
                return False
            if target == "color" and op == "=" and not self.has_color(value):
                return False
        return True
    
    def move_to_graveyard(self, card_name: str, from_hand=True):
        """Move a card to graveyard from hand or battlefield."""
        if from_hand and self.hand[card_name] > 0:
            self.hand[card_name] -= 1
        elif not from_hand and self.battlefield[card_name] > 0:
            self.battlefield[card_name] -= 1
        self.graveyard[card_name] += 1
    
    def get_card_effect(self, card_name: str, effect_prefix: str):
        """Get effect value for a card (e.g., 'madness_' -> '2G')."""
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] == "effect" and cond["value"].startswith(effect_prefix):
                return cond["value"].replace(effect_prefix, "")
        return None
    
    def has_effect(self, card_name: str, effect_name: str):
        """Check if a card has a specific effect."""
        card_data = self.deck.card_info.get(card_name, {})
        conds = card_data.get("conditions", [])
        for cond in conds:
            if cond["type"] == "effect" and cond["value"].startswith(effect_name):
                return True
        return False
    
    def play_creature(self, card_name: str):
        """Play a creature from hand to battlefield."""
        # DISABLED: Focus on hand development, not creature casting
        # Keep creatures in hand to track what's available
        if self.hand[card_name] > 0:
            # self.hand[card_name] -= 1  # DISABLED: Keep in hand
            # self.battlefield[card_name] += 1  # DISABLED: Don't put on battlefield
            self.spells_cast[card_name] += 1  # Still track for statistics
    
    def cast_with_madness(self, card_name: str):
        """Cast a card using madness (from discard)."""
        # DISABLED: Creatures don't go to battlefield, focusing on hand development
        # Card goes directly to graveyard regardless of type
        card_data = self.deck.card_info.get(card_name, {})
        # if "creature" in card_data.get("type", "").lower():
        #     self.battlefield[card_name] += 1  # DISABLED
        # else:
        #     self.graveyard[card_name] += 1
        self.graveyard[card_name] += 1  # All madness cards go to graveyard
        self.madness_casts[card_name] += 1
        self.spells_cast[card_name] += 1
    
    def cast_with_flashback(self, card_name: str):
        """Cast a card using flashback from graveyard (exile after)."""
        if self.graveyard[card_name] > 0:
            self.graveyard[card_name] -= 1
            # Card is exiled after flashback (not tracked for now)
            self.flashback_casts[card_name] += 1
            self.spells_cast[card_name] += 1
            # DISABLED: Don't create creature tokens, focus on hand development
            # if "roar" in card_name.lower():
            #     self.battlefield["Wurm Token"] += 1


# ---------------- Card Action Definitions ---------------- #

def discard_random(state: GameState, n=2, enable_madness=True):
    """Discard n random cards, optionally casting madness cards."""
    all_cards = list(state.hand.elements())
    for _ in range(min(n, len(all_cards))):
        discard = random.choice(all_cards)
        state.hand[discard] -= 1
        all_cards.remove(discard)
        
        # Check if this card has madness and can be cast
        if enable_madness and state.has_effect(discard, "madness_"):
            madness_cost = state.get_card_effect(discard, "madness_")
            # For simplicity, assume we can always pay madness cost if we have the colors
            # Parse madness cost (e.g., "2G" means need G mana)
            can_cast_madness = True
            if madness_cost and madness_cost != "0":
                # Check if we have required colors
                for char in madness_cost:
                    if char.isalpha() and not state.has_color(char):
                        can_cast_madness = False
                        break
            
            if can_cast_madness:
                state.cast_with_madness(discard)
            else:
                state.move_to_graveyard(discard, from_hand=False)
        else:
            # Regular discard to graveyard
            state.graveyard[discard] += 1

def play_careful_study(state: GameState):
    """Draw 2, discard 2 (with madness triggers)."""
    if state.hand["Careful Study"] > 0 and state.can_cast("Careful Study"):
        state.hand["Careful Study"] -= 1
        state.graveyard["Careful Study"] += 1  # Spell goes to graveyard
        state.spells_cast["Careful Study"] += 1
        state.draw_card(2)
        discard_random(state, 2, enable_madness=True)

def play_frantic_search(state: GameState):
    """Draw 2, discard 2, untap 3 lands (with madness triggers)."""
    if state.hand["Frantic Search"] > 0 and state.can_cast("Frantic Search"):
        state.hand["Frantic Search"] -= 1
        state.graveyard["Frantic Search"] += 1  # Spell goes to graveyard
        state.spells_cast["Frantic Search"] += 1
        state.draw_card(2)
        discard_random(state, 2, enable_madness=True)
        # Note: Untap 3 lands effect is implicit (mana efficiency tracked elsewhere)

def play_survival(state: GameState):
    """Discard creature, tutor another creature (with madness triggers)."""
    if state.hand["Survival of the Fittest"] > 0 and state.can_cast("Survival of the Fittest"):
        # Play as enchantment (stays on battlefield)
        state.hand["Survival of the Fittest"] -= 1
        state.battlefield["Survival of the Fittest"] += 1
        state.spells_cast["Survival of the Fittest"] += 1

def activate_survival(state: GameState):
    """Activate Survival: discard creature, tutor another creature."""
    if state.battlefield["Survival of the Fittest"] > 0:
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
                    state.cast_with_madness(discard)
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
    if state.hand["Wild Mongrel"] > 0 and state.can_cast("Wild Mongrel"):
        state.play_creature("Wild Mongrel")

def activate_wild_mongrel(state: GameState):
    """Discard to pump Wild Mongrel (with madness triggers)."""
    if state.battlefield["Wild Mongrel"] > 0 and len(list(state.hand.elements())) > 0:
        discard_random(state, 1, enable_madness=True)

def play_waterfront_bouncer(state: GameState):
    """Play Waterfront Bouncer as creature."""
    if state.hand["Waterfront Bouncer"] > 0 and state.can_cast("Waterfront Bouncer"):
        state.play_creature("Waterfront Bouncer")

def activate_waterfront_bouncer(state: GameState):
    """Discard to bounce a creature (with madness triggers)."""
    if state.battlefield["Waterfront Bouncer"] > 0 and len(list(state.hand.elements())) > 0:
        discard_random(state, 1, enable_madness=True)

def play_roar_flashback(state: GameState):
    """Cast Roar of the Wurm from graveyard via flashback."""
    if state.graveyard["Roar of the Wurm"] > 0 and state.can_cast("Roar of the Wurm"):
        flashback_cost = state.get_card_effect("Roar of the Wurm", "flashback_")
        # Check if we can pay flashback cost (need G mana for 3G)
        if flashback_cost and "G" in flashback_cost and state.has_color("G"):
            state.cast_with_flashback("Roar of the Wurm")

def play_basking_rootwalla(state: GameState):
    """Play Basking Rootwalla from hand."""
    if state.hand["Basking Rootwalla"] > 0 and state.can_cast("Basking Rootwalla"):
        state.play_creature("Basking Rootwalla")

def play_arrogant_wurm(state: GameState):
    """Play Arrogant Wurm from hand."""
    if state.hand["Arrogant Wurm"] > 0 and state.can_cast("Arrogant Wurm"):
        state.play_creature("Arrogant Wurm")

def play_wonder(state: GameState):
    """Play Wonder from hand."""
    if state.hand["Wonder"] > 0 and state.can_cast("Wonder"):
        state.play_creature("Wonder")

card_actions = {
    "Careful Study": play_careful_study,
    "Frantic Search": play_frantic_search,
    "Survival of the Fittest": play_survival,
    "Wild Mongrel": play_wild_mongrel,
    "Waterfront Bouncer": play_waterfront_bouncer,
    "Basking Rootwalla": play_basking_rootwalla,
    "Arrogant Wurm": play_arrogant_wurm,
    "Wonder": play_wonder,
}

# Activated abilities (run after main card actions)
activated_abilities = {
    "Survival of the Fittest": activate_survival,
    "Wild Mongrel": activate_wild_mongrel,
    "Waterfront Bouncer": activate_waterfront_bouncer,
    "Roar of the Wurm": play_roar_flashback,
}


# ==========================================================
# Helper: Returns Mechanic
# ==========================================================

def process_returns(state: GameState):
    """Process cards with 'returns' effect (e.g., Squee) at start of turn."""
    cards_to_return = []
    for card in state.graveyard.keys():
        if state.has_effect(card, "returns") and state.graveyard[card] > 0:
            cards_to_return.append(card)
    
    for card in cards_to_return:
        state.graveyard[card] -= 1
        state.hand[card] += 1


# ==========================================================
# Phase 4: Mulligan Logic
# ==========================================================

def is_creature(card_name, deck):
    """Check if a card is a creature."""
    card_info = deck.card_info.get(card_name, {})
    return "creature" in card_info.get("type", "").lower()

def count_lands_in_hand(hand, deck):
    """Count the number of lands in hand."""
    count = 0
    for card, quantity in hand.items():
        card_info = deck.card_info.get(card, {})
        if "land" in card_info.get("type", "").lower():
            count += quantity
    return count

def has_creature_in_hand(hand, deck):
    """Check if hand contains any creatures."""
    for card in hand.keys():
        if is_creature(card, deck):
            return True
    return False

def should_mulligan(hand, deck, strategy):
    """
    Determine if a hand should be mulliganed based on strategy config.
    
    Default strategy:
    - min_lands: 2 (mulligan if < 2 lands)
    - max_lands: 4 (mulligan if > 4 lands)
    - requires_creature: true (mulligan if no creatures)
    """
    if not strategy or not strategy.get("enabled", True):
        return False  # Never mulligan if disabled
    
    land_count = count_lands_in_hand(hand, deck)
    has_creature = has_creature_in_hand(hand, deck)
    
    min_lands = strategy.get("min_lands", 2)
    max_lands = strategy.get("max_lands", 4)
    requires_creature = strategy.get("requires_creature", True)
    
    if land_count < min_lands:
        return True
    if land_count > max_lands:
        return True
    if requires_creature and not has_creature:
        return True
    
    return False

def choose_card_to_remove(hand, deck, key_cards, strategy):
    """
    Choose which card to remove after keeping a mulligan hand.
    Uses strategy from config to determine priority.
    
    Default preference:
    - If land_count == prefer_land_at_count, remove a random land
    - Otherwise, remove a non-key-card that's not a land (if protect_key_cards is True)
    - Fallback: remove any card
    """
    land_count = count_lands_in_hand(hand, deck)
    all_cards = list(hand.elements())
    
    # Get bottom priority settings from strategy
    bottom_priority = strategy.get("bottom_priority", {}) if strategy else {}
    prefer_land_at_count = bottom_priority.get("prefer_land_at_count", 4)
    protect_key_cards = bottom_priority.get("protect_key_cards", True)
    
    # If land count matches preference, remove a land
    if land_count == prefer_land_at_count:
        lands = [card for card in all_cards if "land" in deck.card_info.get(card, {}).get("type", "").lower()]
        if lands:
            return random.choice(lands)
    
    # Otherwise, prefer to remove non-key, non-land cards (if protection is enabled)
    if protect_key_cards:
        non_key_non_land = [
            card for card in all_cards
            if card not in key_cards and "land" not in deck.card_info.get(card, {}).get("type", "").lower()
        ]
        if non_key_non_land:
            return random.choice(non_key_non_land)
    
    # Fallback: remove any card
    return random.choice(all_cards) if all_cards else None

def perform_mulligan(deck, key_cards, strategy):
    """
    Perform mulligan logic according to London mulligan rules.
    Uses strategy from config to determine mulligan criteria.
    Returns: (hand, mulligan_count)
    """
    # If mulligan is disabled, just draw 7 and keep
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
        card_to_remove = choose_card_to_remove(hand, deck, key_cards, strategy)
        if card_to_remove:
            hand[card_to_remove] -= 1
            if hand[card_to_remove] == 0:
                del hand[card_to_remove]
            # Put it on bottom of library
            deck.cards.append(card_to_remove)
    
    return hand, mulligan_count


# ==========================================================
# Sideboard Support
# ==========================================================

def apply_sideboard_plan(deck_csv_path, sideboard_csv_path, plan_config):
    """
    Apply a sideboard plan to create a modified deck.
    
    Args:
        deck_csv_path: Path to main deck CSV
        sideboard_csv_path: Path to sideboard CSV
        plan_config: Dict with 'board_in' and 'board_out' specifications
    
    Returns:
        Modified deck as pandas DataFrame
    """
    # Load main deck and sideboard
    deck_df = pd.read_csv(deck_csv_path)
    sideboard_df = pd.read_csv(sideboard_csv_path)
    
    # Create working copy
    modified_deck = deck_df.copy()
    
    # Board out (remove cards from main deck)
    board_out = plan_config.get('board_out', {})
    for card_name, quantity in board_out.items():
        # Find card in deck
        card_idx = modified_deck[modified_deck['Card Name'] == card_name].index
        if len(card_idx) > 0:
            idx = card_idx[0]
            current_qty = modified_deck.loc[idx, 'Quantity']
            new_qty = max(0, current_qty - quantity)
            if new_qty == 0:
                # Remove card entirely
                modified_deck = modified_deck.drop(idx)
            else:
                # Reduce quantity
                modified_deck.loc[idx, 'Quantity'] = new_qty
    
    # Board in (add cards from sideboard)
    board_in = plan_config.get('board_in', {})
    for card_name, quantity in board_in.items():
        # Find card in sideboard
        sb_card = sideboard_df[sideboard_df['Card Name'] == card_name]
        if len(sb_card) > 0:
            sb_row = sb_card.iloc[0]
            # Check if card already exists in modified deck
            existing = modified_deck[modified_deck['Card Name'] == card_name]
            if len(existing) > 0:
                # Increase quantity
                idx = existing.index[0]
                modified_deck.loc[idx, 'Quantity'] += quantity
            else:
                # Add new card to deck
                new_row = sb_row.copy()
                new_row['Quantity'] = quantity
                modified_deck = pd.concat([modified_deck, pd.DataFrame([new_row])], ignore_index=True)
    
    return modified_deck


def create_sideboarded_deck(deck_csv_path, sideboard_csv_path, plan_config, temp_path='temp_sideboarded_deck.csv'):
    """
    Create a temporary CSV file with sideboarded deck.
    
    Returns:
        Path to temporary CSV file
    """
    modified_deck = apply_sideboard_plan(deck_csv_path, sideboard_csv_path, plan_config)
    modified_deck.to_csv(temp_path, index=False)
    return temp_path


# ==========================================================
# Phase 5: Simulation Engine
# ==========================================================

def simulate_game(deck_csv_path, turns=4, config=None):
    deck = Deck(deck_csv_path)
    state = GameState(deck)
    
    # Perform mulligan logic with strategy from config
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

    for turn in range(1, turns + 1):
        state.turn = turn
        
        # Process returns at start of turn (e.g., Squee)
        process_returns(state)
        
        # Play land for turn
        state.play_land()
        
        # Cast spells from hand
        for card in list(state.hand.keys()):
            if card in card_actions and state.can_cast(card):
                card_actions[card](state)
        
        # Activate abilities (Survival, Wild Mongrel, flashback, etc.)
        for card in list(state.battlefield.keys()):
            if card in activated_abilities:
                activated_abilities[card](state)
        
        # Check for flashback spells in graveyard
        for card in list(state.graveyard.keys()):
            if card in activated_abilities:
                activated_abilities[card](state)
        
        # Draw for turn
        state.draw_card(1)

    # Evaluate ideal setups using turn-based tracking
    setup_results = evaluate_ideal_setups(state, config or {})
    
    # For key cards, check if they were seen by turn 4 (configurable default)
    key_cards = (config or {}).get("key_cards", [])
    key_card_turn_limit = (config or {}).get("key_card_turn_limit", 4)
    key_seen = {
        k: (k in state.cards_seen_by_turn and state.cards_seen_by_turn[k] <= key_card_turn_limit)
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


# ==========================================================
# Opening Hand Analysis
# ==========================================================

def extract_hand_pattern(opening_hand, deck, config):
    """
    Extract a pattern string from an opening hand.
    Pattern includes: land count, key cards present, creature count.
    """
    key_cards = (config or {}).get("key_cards", [])
    
    # Count lands
    land_count = sum(1 for card in opening_hand 
                     if "land" in deck.card_info.get(card, {}).get("type", "").lower())
    
    # Count creatures
    creature_count = sum(1 for card in opening_hand 
                         if "creature" in deck.card_info.get(card, {}).get("type", "").lower())
    
    # Identify key cards present
    key_present = sorted([card for card in opening_hand if card in key_cards])
    
    # Build pattern string
    pattern_parts = [f"{land_count}L", f"{creature_count}C"]
    
    if key_present:
        # Abbreviate long names for readability
        abbreviated = []
        for card in key_present:
            if card == "Survival of the Fittest":
                abbreviated.append("Survival")
            elif card == "Squee, Goblin Nabob":
                abbreviated.append("Squee")
            else:
                abbreviated.append(card)
        pattern_parts.append("+" + "+".join(abbreviated))
    
    return " ".join(pattern_parts)


def analyze_opening_hands(all_results, deck, config):
    """
    Analyze which opening hand patterns lead to ideal setup success.
    
    Returns DataFrame with patterns and their success rates.
    """
    from collections import defaultdict
    import statistics
    
    # Group results by pattern
    pattern_data = defaultdict(lambda: {
        "count": 0,
        "setup_success": Counter(),
        "total_setups_succeeded": 0,
        "mulligan_counts": []
    })
    
    for result in all_results:
        pattern = extract_hand_pattern(result["opening_hand"], deck, config)
        pattern_data[pattern]["count"] += 1
        pattern_data[pattern]["mulligan_counts"].append(result["mulligan_count"])
        
        # Track which setups succeeded
        setups_succeeded_this_game = 0
        for setup_name, succeeded in result["setup_results"].items():
            if succeeded:
                pattern_data[pattern]["setup_success"][setup_name] += 1
                setups_succeeded_this_game += 1
        
        pattern_data[pattern]["total_setups_succeeded"] += setups_succeeded_this_game
    
    # Build DataFrame
    rows = []
    for pattern, data in sorted(pattern_data.items(), 
                                 key=lambda x: x[1]["total_setups_succeeded"], 
                                 reverse=True):
        row = {
            "Pattern": pattern,
            "Games": data["count"],
        }
        
        # Calculate median mulligans for this pattern
        median_mulligans = statistics.median(data["mulligan_counts"])
        row["Median Mulligans"] = median_mulligans
        
        # Add success rates for each setup
        for setup_name, successes in sorted(data["setup_success"].items()):
            rate = (successes / data["count"]) * 100
            row[f"{setup_name} %"] = round(rate, 1)
        
        # Overall success metric (average across all setups)
        if data["setup_success"]:
            total_possible = data["count"] * len(data["setup_success"])
            total_successes = sum(data["setup_success"].values())
            row["Avg Success %"] = round((total_successes / total_possible) * 100, 1)
        else:
            row["Avg Success %"] = 0.0
        
        rows.append(row)
    
    return pd.DataFrame(rows)


# ==========================================================
# Phase 5: Aggregation
# ==========================================================

def run_simulations(deck_csv_path, runs=1000, turns=4, config=None):
    seen_counter = Counter()
    cast_counter = Counter()
    total_lands = 0
    total_cards_seen = 0
    key_card_counts = Counter()
    setup_success = Counter()
    mulligan_counts = Counter()
    total_mulligans = 0
    
    # New graveyard tracking
    graveyard_counter = Counter()
    battlefield_counter = Counter()
    madness_counter = Counter()
    flashback_counter = Counter()
    tutored_counter = Counter()
    total_creatures_on_board = 0
    total_graveyard_size = 0
    
    # Store all results for opening hand analysis
    all_results = []

    for _ in tqdm(range(runs), desc="Simulating games"):
        result = simulate_game(deck_csv_path, turns, config=config)
        all_results.append(result)  # Store for later analysis

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

    # -----------------------------
    # Build output DataFrames
    # -----------------------------

    # Card-level stats
    seen_df = pd.DataFrame({
        "Card": list(seen_counter.keys()),
        "Seen %": [seen_counter[c] / runs * 100 for c in seen_counter],
        "Cast %": [cast_counter[c] / runs * 100 for c in seen_counter]
    }).fillna(0)

    # Key cards (defined globally in KEY_CARDS)
    key_df = pd.DataFrame({
        "Key Card": list(key_card_counts.keys()),
        "Seen % (Turn ≤4)": [key_card_counts[k] / runs * 100 for k in key_card_counts]
    }).fillna(0)

    # Ideal setups from config
    setup_df = pd.DataFrame({
        "Setup": list(setup_success.keys()),
        "Success %": [setup_success[s] / runs * 100 for s in setup_success]
    }).fillna(0)

    # Mulligan distribution
    mulligan_df = pd.DataFrame({
        "Mulligans": list(mulligan_counts.keys()),
        "Games": [mulligan_counts[m] for m in mulligan_counts],
        "Percentage": [mulligan_counts[m] / runs * 100 for m in mulligan_counts]
    }).sort_values("Mulligans").fillna(0)
    
    # Graveyard stats
    graveyard_df = pd.DataFrame({
        "Card": list(graveyard_counter.keys()),
        "Avg in Graveyard": [graveyard_counter[c] / runs for c in graveyard_counter],
        "In Graveyard %": [graveyard_counter[c] / runs * 100 for c in graveyard_counter]
    }).fillna(0).sort_values("Avg in Graveyard", ascending=False)
    
    # Battlefield stats (creatures/permanents)
    battlefield_df = pd.DataFrame({
        "Card": list(battlefield_counter.keys()),
        "Avg on Battlefield": [battlefield_counter[c] / runs for c in battlefield_counter],
        "On Battlefield %": [battlefield_counter[c] / runs * 100 for c in battlefield_counter]
    }).fillna(0).sort_values("Avg on Battlefield", ascending=False)
    
    # Madness stats
    madness_df = pd.DataFrame({
        "Card": list(madness_counter.keys()),
        "Madness Casts": [madness_counter[c] for c in madness_counter],
        "Madness Cast %": [madness_counter[c] / runs * 100 for c in madness_counter]
    }).fillna(0).sort_values("Madness Casts", ascending=False)
    
    # Flashback stats
    flashback_df = pd.DataFrame({
        "Card": list(flashback_counter.keys()),
        "Flashback Casts": [flashback_counter[c] for c in flashback_counter],
        "Flashback Cast %": [flashback_counter[c] / runs * 100 for c in flashback_counter]
    }).fillna(0).sort_values("Flashback Casts", ascending=False)
    
    # Tutor stats
    tutored_df = pd.DataFrame({
        "Card": list(tutored_counter.keys()),
        "Times Tutored": [tutored_counter[c] for c in tutored_counter],
        "Tutored %": [tutored_counter[c] / runs * 100 for c in tutored_counter]
    }).fillna(0).sort_values("Times Tutored", ascending=False)

    # Summary overview
    summary = {
        "Average Lands in Play": total_lands / runs,
        "Average Cards Seen": total_cards_seen / runs,
        "Average Mulligans": total_mulligans / runs,
        "Games with 0 Mulligans %": mulligan_counts.get(0, 0) / runs * 100,
        "Average Graveyard Size": total_graveyard_size / runs,
        "Average Creatures on Board": total_creatures_on_board / runs,
        "Total Madness Casts": sum(madness_counter.values()),
        "Total Flashback Casts": sum(flashback_counter.values()),
        "Simulations Run": runs,
        "Turns Simulated": turns
    }
    
    # Opening hand analysis
    deck = Deck(deck_csv_path)
    opening_hands_df = analyze_opening_hands(all_results, deck, config)

    return seen_df, key_df, setup_df, mulligan_df, graveyard_df, battlefield_df, madness_df, flashback_df, tutored_df, opening_hands_df, summary


# ==========================================================
# Phase 6: Export
# ==========================================================

def export_results(seen_df, key_df, setup_df, mulligan_df, graveyard_df, battlefield_df, 
                   madness_df, flashback_df, tutored_df, opening_hands_df, summary, output_file="simulation_results.xlsx"):
    with pd.ExcelWriter(output_file) as writer:
        seen_df.to_excel(writer, index=False, sheet_name="Card Stats")
        key_df.to_excel(writer, index=False, sheet_name="Key Card Stats")
        setup_df.to_excel(writer, index=False, sheet_name="Ideal Setups")
        mulligan_df.to_excel(writer, index=False, sheet_name="Mulligan Stats")
        opening_hands_df.to_excel(writer, index=False, sheet_name="Opening Hands")
        graveyard_df.to_excel(writer, index=False, sheet_name="Graveyard Stats")
        battlefield_df.to_excel(writer, index=False, sheet_name="Battlefield Stats")
        madness_df.to_excel(writer, index=False, sheet_name="Madness Casts")
        flashback_df.to_excel(writer, index=False, sheet_name="Flashback Casts")
        tutored_df.to_excel(writer, index=False, sheet_name="Tutored Cards")
        pd.DataFrame([summary]).to_excel(writer, index=False, sheet_name="Summary")
    print(f"✅ Results exported to {output_file}")


# ==========================================================
# Phase 7: CLI & Config
# ==========================================================

def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No config file found at {config_path}. Using defaults.")
        return {}

def main():
    parser = argparse.ArgumentParser(description="MTG Deck Simulation Tool")
    parser.add_argument("--deck", type=str, default="deck.csv", help="Path to deck CSV")
    parser.add_argument("--runs", type=int, default=1000, help="Number of simulation runs")
    parser.add_argument("--turns", type=int, default=4, help="Turns to simulate")
    parser.add_argument("--output", type=str, default="simulation_results.xlsx", help="Output Excel file")
    parser.add_argument("--config", type=str, default="simulation_config.json", help="Optional config JSON")
    parser.add_argument("--sideboard", type=str, default=None, help="Sideboard plan name (e.g., 'vs_combo', 'vs_aggro')")
    parser.add_argument("--sideboard-file", type=str, default="sideboard.csv", help="Path to sideboard CSV")
    parser.add_argument("--compare", nargs=2, metavar=("BASELINE", "VARIANT"), 
                        help="Compare two deck configurations (e.g., --compare deck.csv variant.csv)")
    parser.add_argument("--compare-output", type=str, default="comparison_results.xlsx",
                        help="Output file for comparison results")

    args = parser.parse_args()
    config = load_config(args.config)
    
    # Handle comparison mode
    if args.compare:
        from deck_comparison import compare_decks, print_comparison_summary, print_comparison_progress
        from export_comparison import export_comparison_to_excel, export_comparison_to_markdown
        
        baseline_path, variant_path = args.compare
        
        print("\n" + "="*80)
        print("DECK COMPARISON MODE".center(80))
        print("="*80 + "\n")
        
        # Run comparison
        comparison = compare_decks(
            baseline_path=baseline_path,
            variant_path=variant_path,
            runs=args.runs,
            turns=args.turns,
            config=config,
            progress_callback=print_comparison_progress
        )
        
        # Print summary to console
        print_comparison_summary(comparison)
        
        # Export results
        excel_output = args.compare_output
        md_output = excel_output.replace('.xlsx', '_summary.md')
        
        export_comparison_to_excel(comparison, excel_output)
        export_comparison_to_markdown(comparison, md_output)
        
        return

    # CLI flags override config file
    deck_path = args.deck or config.get("deck", "deck.csv")
    runs = args.runs or config.get("runs", 1000)
    turns = args.turns or config.get("turns", 4)
    output = args.output or config.get("output", "simulation_results.xlsx")
    
    # Handle sideboarding if requested
    temp_deck_file = None
    if args.sideboard:
        sideboard_plans = config.get("sideboard_plans", {})
        if args.sideboard not in sideboard_plans:
            print(f"❌ Error: Sideboard plan '{args.sideboard}' not found in config.")
            print(f"Available plans: {', '.join(sideboard_plans.keys())}")
            return
        
        plan = sideboard_plans[args.sideboard]
        print(f"\n🎴 Applying sideboard plan: {plan.get('name', args.sideboard)}")
        print(f"  Boarding in: {plan.get('board_in', {})}")
        print(f"  Boarding out: {plan.get('board_out', {})}")
        
        # Create sideboarded deck
        temp_deck_file = create_sideboarded_deck(deck_path, args.sideboard_file, plan)
        deck_path = temp_deck_file
        print(f"  ✅ Sideboarded deck created\n")

    try:
        results = run_simulations(deck_path, runs=runs, turns=turns, config=config)
        seen_df, key_df, setup_df, mulligan_df, graveyard_df, battlefield_df, madness_df, flashback_df, tutored_df, opening_hands_df, summary = results
        export_results(seen_df, key_df, setup_df, mulligan_df, graveyard_df, battlefield_df, 
                       madness_df, flashback_df, tutored_df, opening_hands_df, summary, output)
        print("\n📊 Simulation Summary:")
        for k, v in summary.items():
            print(f"  {k}: {v}")
    finally:
        # Clean up temporary sideboarded deck file
        if temp_deck_file and os.path.exists(temp_deck_file):
            os.remove(temp_deck_file)

if __name__ == "__main__":
    main()