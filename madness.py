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
def evaluate_ideal_setups(state, first_four_seen, config):
    setups = config.get("ideal_setups", [])
    setup_results = {}

    for setup in setups:
        name = setup["name"]
        cards_ok = all(c in first_four_seen for c in setup.get("requires_cards", []))
        colors_ok = all(color in state.mana_colors for color in setup.get("requires_colors", []))
        turn_limit = setup.get("turn_limit", 4)

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
        self.spells_cast = Counter()
        self.cards_drawn_total = 0
        self.mana_colors = set()

    def draw_card(self, n=1):
        drawn = self.deck.draw(n)
        for card in drawn:
            self.hand[card] += 1
            self.cards_seen.add(card)
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
# Phase 4: Simulation Engine
# ==========================================================

def simulate_game(deck_csv_path, turns=4, config=None):
    deck = Deck(deck_csv_path)
    state = GameState(deck)
    state.draw_card(7)
    first_four_seen = set(state.cards_seen)

    for turn in range(1, turns + 1):
        state.turn = turn
        state.play_land()
        for card in list(state.hand.keys()):
            if card in card_actions and state.can_cast(card):
                card_actions[card](state)
        state.draw_card(1)
        if turn <= 4:
            first_four_seen.update(state.cards_seen)

    key_cards = (config or {}).get("key_cards", [])
    key_seen = {k: (k in first_four_seen) for k in key_cards}
    setup_results = evaluate_ideal_setups(state, first_four_seen, config or {})

    return {
        "cards_seen": list(state.cards_seen),
        "key_seen": key_seen,
        "setup_results": setup_results,
        "spells_cast": dict(state.spells_cast),
        "lands_in_play": state.lands_in_play,
        "cards_drawn_total": state.cards_drawn_total,
        "mana_colors": list(state.mana_colors)
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

    # Summary overview
    summary = {
        "Average Lands in Play": total_lands / runs,
        "Average Cards Seen": total_cards_seen / runs,
        "Simulations Run": runs,
        "Turns Simulated": turns
    }

    return seen_df, key_df, setup_df, summary


# ==========================================================
# Phase 6: Export
# ==========================================================

def export_results(seen_df, key_df, setup_df, summary, output_file="simulation_results.xlsx"):
    with pd.ExcelWriter(output_file) as writer:
        seen_df.to_excel(writer, index=False, sheet_name="Card Stats")
        key_df.to_excel(writer, index=False, sheet_name="Key Card Stats")
        setup_df.to_excel(writer, index=False, sheet_name="Ideal Setups")
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

    seen_df, key_df, setup_df, summary = run_simulations(deck_path, runs=runs, turns=turns, config=config)
    export_results(seen_df, key_df, setup_df, summary, output)
    print("\n📊 Simulation Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()