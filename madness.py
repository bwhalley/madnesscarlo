import pandas as pd
import random
import json
import argparse
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

        # Check both cards and color requirements
        setup_results[name] = cards_ok and colors_ok

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


# ---------------- Card Action Definitions ---------------- #

def discard_random(state: GameState, n=2):
    all_cards = list(state.hand.elements())
    for _ in range(min(n, len(all_cards))):
        discard = random.choice(all_cards)
        state.hand[discard] -= 1
        all_cards.remove(discard)

def play_careful_study(state: GameState):
    if state.hand["Careful Study"] > 0 and state.can_cast("Careful Study"):
        state.hand["Careful Study"] -= 1
        state.spells_cast["Careful Study"] += 1
        state.draw_card(2)
        discard_random(state, 2)

def play_frantic_search(state: GameState):
    if state.hand["Frantic Search"] > 0 and state.can_cast("Frantic Search"):
        state.hand["Frantic Search"] -= 1
        state.spells_cast["Frantic Search"] += 1
        state.draw_card(2)
        discard_random(state, 2)

card_actions = {
    "Careful Study": play_careful_study,
    "Frantic Search": play_frantic_search
}


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

def should_mulligan(hand, deck):
    """
    Determine if a hand should be mulliganed based on:
    - 0 or 1 lands
    - 5 or more lands
    - No creatures
    """
    land_count = count_lands_in_hand(hand, deck)
    has_creature = has_creature_in_hand(hand, deck)
    
    if land_count <= 1:
        return True
    if land_count >= 5:
        return True
    if not has_creature:
        return True
    
    return False

def choose_card_to_remove(hand, deck, key_cards):
    """
    Choose which card to remove after keeping a mulligan hand.
    Preference:
    - If 4 lands in hand, remove a random land
    - Otherwise, remove a non-key-card that's not a land
    - Fallback: remove any card
    """
    land_count = count_lands_in_hand(hand, deck)
    all_cards = list(hand.elements())
    
    # If exactly 4 lands, prefer to remove a land
    if land_count == 4:
        lands = [card for card in all_cards if "land" in deck.card_info.get(card, {}).get("type", "").lower()]
        if lands:
            return random.choice(lands)
    
    # Otherwise, prefer to remove non-key, non-land cards
    non_key_non_land = [
        card for card in all_cards
        if card not in key_cards and "land" not in deck.card_info.get(card, {}).get("type", "").lower()
    ]
    if non_key_non_land:
        return random.choice(non_key_non_land)
    
    # Fallback: remove any card
    return random.choice(all_cards) if all_cards else None

def perform_mulligan(deck, key_cards):
    """
    Perform mulligan logic according to London mulligan rules.
    Returns: (hand, mulligan_count)
    """
    mulligan_count = 0
    max_mulligans = 7  # Safety limit
    
    # Draw initial hand
    hand = Counter()
    for card in deck.draw(7):
        hand[card] += 1
    
    # Keep mulliganing until we get a keepable hand
    while should_mulligan(hand, deck) and mulligan_count < max_mulligans:
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
        card_to_remove = choose_card_to_remove(hand, deck, key_cards)
        if card_to_remove:
            hand[card_to_remove] -= 1
            if hand[card_to_remove] == 0:
                del hand[card_to_remove]
            # Put it on bottom of library
            deck.cards.append(card_to_remove)
    
    return hand, mulligan_count


# ==========================================================
# Phase 5: Simulation Engine
# ==========================================================

def simulate_game(deck_csv_path, turns=4, config=None):
    deck = Deck(deck_csv_path)
    state = GameState(deck)
    
    # Perform mulligan logic
    key_cards = (config or {}).get("key_cards", [])
    kept_hand, mulligan_count = perform_mulligan(deck, key_cards)
    
    # Set the kept hand as the opening hand
    state.turn = 0
    state.hand = kept_hand
    
    # Mark cards in opening hand as seen on turn 0
    for card in state.hand.keys():
        state.cards_seen.add(card)
        state.cards_seen_by_turn[card] = 0
    
    state.cards_drawn_total = 7  # Started with 7 cards

    for turn in range(1, turns + 1):
        state.turn = turn
        state.play_land()
        for card in list(state.hand.keys()):
            if card in card_actions and state.can_cast(card):
                card_actions[card](state)
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
        "mulligan_count": mulligan_count
    }


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

    for _ in tqdm(range(runs), desc="Simulating games"):
        result = simulate_game(deck_csv_path, turns, config=config)

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

    # Summary overview
    summary = {
        "Average Lands in Play": total_lands / runs,
        "Average Cards Seen": total_cards_seen / runs,
        "Average Mulligans": total_mulligans / runs,
        "Games with 0 Mulligans %": mulligan_counts.get(0, 0) / runs * 100,
        "Simulations Run": runs,
        "Turns Simulated": turns
    }

    return seen_df, key_df, setup_df, mulligan_df, summary


# ==========================================================
# Phase 6: Export
# ==========================================================

def export_results(seen_df, key_df, setup_df, mulligan_df, summary, output_file="simulation_results.xlsx"):
    with pd.ExcelWriter(output_file) as writer:
        seen_df.to_excel(writer, index=False, sheet_name="Card Stats")
        key_df.to_excel(writer, index=False, sheet_name="Key Card Stats")
        setup_df.to_excel(writer, index=False, sheet_name="Ideal Setups")
        mulligan_df.to_excel(writer, index=False, sheet_name="Mulligan Stats")
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

    args = parser.parse_args()
    config = load_config(args.config)

    # CLI flags override config file
    deck_path = args.deck or config.get("deck", "deck.csv")
    runs = args.runs or config.get("runs", 1000)
    turns = args.turns or config.get("turns", 4)
    output = args.output or config.get("output", "simulation_results.xlsx")

    seen_df, key_df, setup_df, mulligan_df, summary = run_simulations(deck_path, runs=runs, turns=turns, config=config)
    export_results(seen_df, key_df, setup_df, mulligan_df, summary, output)
    print("\n📊 Simulation Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()