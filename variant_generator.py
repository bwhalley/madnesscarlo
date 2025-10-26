"""
Variant Generator Module

Generates deck variants based on experiment configurations.
"""

import os
import hashlib
import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from itertools import product
from experiment_config import ExperimentConfig, ExperimentDefinition, CardSpec, Slot


@dataclass
class Change:
    """Represents a change to the deck."""
    type: str  # "add", "remove", "modify"
    card: str
    baseline_qty: int
    variant_qty: int
    
    @property
    def delta(self) -> int:
        return self.variant_qty - self.baseline_qty
    
    def __str__(self):
        if self.type == "add":
            return f"+{self.variant_qty} {self.card}"
        elif self.type == "remove":
            return f"-{self.baseline_qty} {self.card}"
        else:  # modify
            sign = "+" if self.delta > 0 else ""
            return f"{sign}{self.delta} {self.card} (from {self.baseline_qty})"


@dataclass
class Variant:
    """Represents a deck variant."""
    id: str
    name: str
    deck_path: str
    changes: List[Change]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def summary(self) -> str:
        """Get a summary of changes."""
        return ", ".join(str(c) for c in self.changes)


class VariantGenerator:
    """Generates deck variants from experiment configurations."""
    
    def __init__(self, base_deck_path: str, output_dir: str = "temp_variants"):
        """
        Initialize variant generator.
        
        Args:
            base_deck_path: Path to base deck CSV
            output_dir: Directory to save variant CSVs
        """
        self.base_deck_path = base_deck_path
        self.base_deck = pd.read_csv(base_deck_path)
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Validate base deck
        self._validate_deck(self.base_deck)
    
    def _validate_deck(self, deck: pd.DataFrame):
        """Validate deck DataFrame has required columns."""
        required_cols = ['Card Name', 'Quantity']
        missing = [col for col in required_cols if col not in deck.columns]
        if missing:
            raise ValueError(f"Deck missing required columns: {missing}")
        
        # Check deck size
        total = deck['Quantity'].sum()
        if total != 60:
            print(f"⚠️  Warning: Deck has {total} cards (expected 60)")
    
    def generate_variants(self, experiment_config: ExperimentConfig) -> List[Variant]:
        """
        Generate all variants from experiment configuration.
        
        Args:
            experiment_config: Experiment configuration
            
        Returns:
            List of Variant objects
        """
        variants = []
        
        for exp in experiment_config.experiments:
            if exp.type == "replace_quantity":
                variants.extend(self._generate_quantity_variants(exp))
            elif exp.type == "slot_testing":
                variants.extend(self._generate_slot_variants(exp))
            elif exp.type == "land_ratio":
                variants.extend(self._generate_land_variants(exp))
            elif exp.type == "combinatorial":
                variants.extend(self._generate_combinatorial_variants(exp))
        
        print(f"✓ Generated {len(variants)} variants")
        return variants
    
    def _generate_quantity_variants(self, exp: ExperimentDefinition) -> List[Variant]:
        """Generate variants with different quantities of a card."""
        variants = []
        card = exp.config['card']
        test_quantities = exp.config['test_quantities']
        compensate = exp.config.get('compensate_with')
        
        # Get baseline quantity
        baseline_row = self.base_deck[self.base_deck['Card Name'] == card]
        if baseline_row.empty:
            raise ValueError(f"Card not found in base deck: {card}")
        baseline_qty = int(baseline_row['Quantity'].values[0])
        
        for qty in test_quantities:
            if qty == baseline_qty:
                continue  # Skip baseline
            
            variant_deck = self.base_deck.copy()
            changes = []
            
            # Update card quantity
            variant_deck.loc[variant_deck['Card Name'] == card, 'Quantity'] = qty
            changes.append(Change("modify", card, baseline_qty, qty))
            
            # Compensate to maintain deck size
            if compensate:
                delta = qty - baseline_qty
                comp_row = variant_deck[variant_deck['Card Name'] == compensate]
                if comp_row.empty:
                    raise ValueError(f"Compensation card not found: {compensate}")
                
                current_comp = int(comp_row['Quantity'].values[0])
                new_comp = current_comp - delta
                
                if new_comp < 0:
                    raise ValueError(f"Cannot compensate: {compensate} would go negative")
                
                variant_deck.loc[variant_deck['Card Name'] == compensate, 'Quantity'] = new_comp
                changes.append(Change("modify", compensate, current_comp, new_comp))
            
            # Create variant
            variant_name = f"{card.replace(' ', '_').replace(',', '')}_{qty}"
            variant = self._save_variant(variant_deck, variant_name, changes, exp)
            variants.append(variant)
        
        return variants
    
    def _generate_slot_variants(self, exp: ExperimentDefinition) -> List[Variant]:
        """Generate variants by swapping cards in/out of slots."""
        variants = []
        slots = exp.config['slots']
        alternatives = exp.config['alternatives']
        
        for alt in alternatives:
            variant_deck = self.base_deck.copy()
            changes = []
            
            # Remove cards from slots
            for slot in slots:
                slot_card = slot['card']
                slot_qty = slot['quantity']
                
                current_row = variant_deck[variant_deck['Card Name'] == slot_card]
                if not current_row.empty:
                    current_qty = int(current_row['Quantity'].values[0])
                    new_qty = max(0, current_qty - slot_qty)
                    variant_deck.loc[variant_deck['Card Name'] == slot_card, 'Quantity'] = new_qty
                    changes.append(Change("modify" if new_qty > 0 else "remove", slot_card, current_qty, new_qty))
            
            # Add alternative
            alt_card = alt['card']
            alt_qty = alt.get('quantity', 0)
            
            if alt_qty > 0 and alt_card != "Keep both" and alt_card != "Remove slot":
                alt_row = variant_deck[variant_deck['Card Name'] == alt_card]
                if alt_row.empty:
                    # Add new card
                    # Get template row for card data
                    template = variant_deck.iloc[0].copy()
                    template['Card Name'] = alt_card
                    template['Quantity'] = alt_qty
                    variant_deck = pd.concat([variant_deck, pd.DataFrame([template])], ignore_index=True)
                    changes.append(Change("add", alt_card, 0, alt_qty))
                else:
                    # Increase existing card
                    current_qty = int(alt_row['Quantity'].values[0])
                    new_qty = current_qty + alt_qty
                    variant_deck.loc[variant_deck['Card Name'] == alt_card, 'Quantity'] = new_qty
                    changes.append(Change("modify", alt_card, current_qty, new_qty))
            
            # Create variant
            variant_name = f"slot_{alt_card.replace(' ', '_').replace(',', '')}"
            variant = self._save_variant(variant_deck, variant_name, changes, exp)
            variants.append(variant)
        
        return variants
    
    def _generate_land_variants(self, exp: ExperimentDefinition) -> List[Variant]:
        """Generate variants with different land ratios."""
        variants = []
        total_lands = exp.config['total_lands']
        forest_range = exp.config.get('forest_range', [5, 10])
        island_range = exp.config.get('island_range', [5, 10])
        dual_lands = exp.config.get('dual_lands', {})
        
        # Generate combinations
        for forest_count in range(forest_range[0], forest_range[1] + 1):
            for island_count in range(island_range[0], island_range[1] + 1):
                dual_count = sum(dual_lands.values())
                
                if forest_count + island_count + dual_count != total_lands:
                    continue
                
                variant_deck = self.base_deck.copy()
                changes = []
                
                # Update Forest
                self._update_land_quantity(variant_deck, "Forest", forest_count, changes)
                
                # Update Island
                self._update_land_quantity(variant_deck, "Island", island_count, changes)
                
                # Update dual lands
                for dual_name, dual_qty in dual_lands.items():
                    self._update_land_quantity(variant_deck, dual_name, dual_qty, changes)
                
                variant_name = f"lands_F{forest_count}_I{island_count}"
                variant = self._save_variant(variant_deck, variant_name, changes, exp)
                variants.append(variant)
        
        return variants
    
    def _update_land_quantity(self, deck: pd.DataFrame, land_name: str, new_qty: int, changes: List[Change]):
        """Helper to update land quantity and track change."""
        land_row = deck[deck['Card Name'] == land_name]
        if not land_row.empty:
            old_qty = int(land_row['Quantity'].values[0])
            deck.loc[deck['Card Name'] == land_name, 'Quantity'] = new_qty
            if old_qty != new_qty:
                changes.append(Change("modify", land_name, old_qty, new_qty))
    
    def _generate_combinatorial_variants(self, exp: ExperimentDefinition) -> List[Variant]:
        """Generate all combinations of slot alternatives."""
        slots = exp.config['slots']
        max_combinations = exp.config.get('max_combinations', 50)
        
        # Build alternatives for each slot
        slot_alternatives = []
        for slot in slots:
            baseline = CardSpec(slot['baseline']['card'], slot['baseline']['quantity'])
            alternatives = [baseline]
            for alt in slot['alternatives']:
                alternatives.append(CardSpec(alt['card'], alt['quantity']))
            slot_alternatives.append((slot['name'], alternatives))
        
        # Generate all combinations
        slot_names = [s[0] for s in slot_alternatives]
        alt_lists = [s[1] for s in slot_alternatives]
        combinations = list(product(*alt_lists))
        
        # Limit to max_combinations
        if len(combinations) > max_combinations:
            print(f"⚠️  Limiting to {max_combinations} of {len(combinations)} possible combinations")
            # Take first max_combinations (could use sampling here)
            combinations = combinations[:max_combinations]
        
        variants = []
        for combo in combinations:
            variant_deck = self.base_deck.copy()
            changes = []
            is_baseline = True
            
            for slot_data, card_spec in zip(slot_alternatives, combo):
                slot_name = slot_data[0]
                baseline_spec = slot_data[1][0]  # First is baseline
                
                # Check if this is different from baseline
                if card_spec.card != baseline_spec.card or card_spec.quantity != baseline_spec.quantity:
                    is_baseline = False
                
                # Remove baseline
                if baseline_spec.quantity > 0:
                    self._adjust_card_quantity(variant_deck, baseline_spec.card, -baseline_spec.quantity, changes)
                
                # Add selected alternative
                if card_spec.quantity > 0:
                    self._adjust_card_quantity(variant_deck, card_spec.card, card_spec.quantity, changes)
            
            # Skip if this is the baseline configuration
            if is_baseline:
                continue
            
            # Create variant name
            variant_name = "_".join([
                f"{name}-{spec.card[:5].replace(' ', '')}{spec.quantity}"
                for name, spec in zip(slot_names, combo)
            ])
            
            variant = self._save_variant(variant_deck, variant_name, changes, exp)
            variants.append(variant)
        
        return variants
    
    def _adjust_card_quantity(self, deck: pd.DataFrame, card: str, delta: int, changes: List[Change]):
        """Adjust card quantity by delta."""
        card_row = deck[deck['Card Name'] == card]
        
        if card_row.empty:
            if delta > 0:
                # Add new card
                template = deck.iloc[0].copy()
                template['Card Name'] = card
                template['Quantity'] = delta
                # This doesn't actually modify the deck in place - need to handle this differently
                changes.append(Change("add", card, 0, delta))
        else:
            old_qty = int(card_row['Quantity'].values[0])
            new_qty = old_qty + delta
            
            if new_qty < 0:
                raise ValueError(f"Cannot adjust {card} by {delta}: would go negative")
            
            deck.loc[deck['Card Name'] == card, 'Quantity'] = new_qty
            
            if old_qty != new_qty:
                change_type = "remove" if new_qty == 0 else "modify"
                changes.append(Change(change_type, card, old_qty, new_qty))
    
    def _save_variant(self, deck: pd.DataFrame, name: str, changes: List[Change], exp: ExperimentDefinition) -> Variant:
        """Save variant to CSV and create Variant object."""
        # Remove cards with 0 quantity
        deck = deck[deck['Quantity'] > 0].copy()
        
        # Validate deck size
        total = deck['Quantity'].sum()
        if total != 60:
            print(f"⚠️  Warning: Variant {name} has {total} cards")
        
        # Save to CSV
        variant_path = os.path.join(self.output_dir, f"{name}.csv")
        deck.to_csv(variant_path, index=False)
        
        # Generate unique ID
        variant_id = self._generate_id(name, changes)
        
        return Variant(
            id=variant_id,
            name=name,
            deck_path=variant_path,
            changes=changes,
            metadata={'experiment_type': exp.type}
        )
    
    def _generate_id(self, name: str, changes: List[Change]) -> str:
        """Generate unique ID for variant."""
        # Create hash of name and changes
        content = name + "".join(str(c) for c in changes)
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def cleanup(self):
        """Clean up temporary variant files."""
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
            print(f"✓ Cleaned up {self.output_dir}")


def calculate_deck_differences(baseline_deck: pd.DataFrame, variant_deck: pd.DataFrame) -> List[Change]:
    """Calculate differences between two decks."""
    changes = []
    
    # Get all unique card names
    all_cards = set(baseline_deck['Card Name'].values) | set(variant_deck['Card Name'].values)
    
    for card in all_cards:
        baseline_row = baseline_deck[baseline_deck['Card Name'] == card]
        variant_row = variant_deck[variant_deck['Card Name'] == card]
        
        baseline_qty = int(baseline_row['Quantity'].values[0]) if not baseline_row.empty else 0
        variant_qty = int(variant_row['Quantity'].values[0]) if not variant_row.empty else 0
        
        if baseline_qty != variant_qty:
            if baseline_qty == 0:
                change_type = "add"
            elif variant_qty == 0:
                change_type = "remove"
            else:
                change_type = "modify"
            
            changes.append(Change(change_type, card, baseline_qty, variant_qty))
    
    return changes


if __name__ == "__main__":
    # Test variant generation
    print("Testing variant generation...")
    
    from experiment_config import load_experiment_config
    
    # Load test config
    config = load_experiment_config("experiments/test.json")
    
    # Generate variants
    generator = VariantGenerator("deck.csv")
    variants = generator.generate_variants(config)
    
    print(f"\nGenerated variants:")
    for v in variants:
        print(f"  {v.name}: {v.summary()}")
    
    # Cleanup
    generator.cleanup()

