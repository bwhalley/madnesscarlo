import pandas as pd
import random
from collections import Counter

# ==========================================================
# Phase 1: Deck Parsing
# ==========================================================

class Deck:
    """
    Represents a Magic: The Gathering deck loaded from a CSV file.
    Each card entry includes quantity, type, mana cost, and any conditions.
    """

    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)
        self.cards = []
        for _, row in df.iterrows():
            self.cards.extend([row['Card Name']] * int(row['Quantity']))
        self.card_info = {
            row['Card Name']: {
                "type": row.get("Type", ""),
                "mana_cost": row.get("Mana Cost", ""),
                "condition": row.get("Conditions", "")
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
# Phase 2: Game State Modeling
# ==========================================================

class GameState:
    """
    Tracks the evolving state of a simulated game.
    """
    def __init__(self, deck: Deck):
        self.deck = deck
        self.deck.shuffle()
        self.hand = Counter()
        self.lands_in_play = 0
        self.turn = 1
        self.cards_seen = set()
        self.spells_cast = Counter()
        self.cards_drawn_total = 0

    def draw_card(self, n=1):
        drawn = self.deck.draw(n)
        for card in drawn:
            self.hand[card] += 1
            self.cards_seen.add(card)
        self.cards_drawn_total += len(drawn)

    def play_land(self):
        """Play one land per turn if possible."""
        for card, count in list(self.hand.items()):
            if "land" in self.deck.card_info.get(card, {}).get("type", "").lower() and count > 0:
                self.hand[card] -= 1
                self.lands_in_play += 1
                break

    def can_cast(self, card_name: str):
        """Determine if a card can be cast based on simple conditions."""
        card_data = self.deck.card_info.get(card_name, {})
        cond = card_data.get("condition", "").lower()
        if "3 lands" in cond and self.lands_in_play < 3:
            return False
        if "1 island" in cond and self.lands_in_play < 1:
            return False
        return True

# ==========================================================
# Phase 3: Card Logic Layer
# ==========================================================

def play_careful_study(state: GameState):
    if state.hand["Careful Study"] > 0 and state.lands_in_play >= 1:
        state.hand["Careful Study"] -= 1
        state.spells_cast["Careful Study"] += 1
        drawn = state.deck.draw(2)
        for c in drawn:
            state.hand[c] += 1
            state.cards_seen.add(c)
        # discard 2 random cards
        discard_random(state, 2)

def play_frantic_search(state: GameState):
    if state.hand["Frantic Search"] > 0 and state.lands_in_play >= 3:
        state.hand["Frantic Search"] -= 1
        state.spells_cast["Frantic Search"] += 1
        drawn = state.deck.draw(2)
        for c in drawn:
            state.hand[c] += 1
            state.cards_seen.add(c)
        discard_random(state, 2)

def discard_random(state: GameState, n=2):
    """Discard n random cards from hand if possible."""
    all_cards = list(state.hand.elements())
    for _ in range(min(n, len(all_cards))):
        discard = random.choice(all_cards)
        state.hand[discard] -= 1
        all_cards.remove(discard)

# Registry of card-specific effects
card_actions = {
    "Careful Study": play_careful_study,
    "Frantic Search": play_frantic_search
}

# ==========================================================
# Example test harness
# ==========================================================

if __name__ == "__main__":
    deck = Deck("deck.csv")
    state = GameState(deck)

    # Draw opening hand
    state.draw_card(7)

    # Play through 4 turns
    for turn in range(1, 5):
        state.turn = turn
        state.play_land()
        # Try casting any playable spells
        for card in list(state.hand.keys()):
            if card in card_actions and state.can_cast(card):
                card_actions[card](state)
        # Draw for turn
        state.draw_card(1)

    print(f"Lands in play: {state.lands_in_play}")
    print(f"Spells cast: {state.spells_cast}")
    print(f"Cards seen: {len(state.cards_seen)}")
    print(f"Cards drawn total: {state.cards_drawn_total}")