# Sideboarding Feature Documentation

## Overview

The sideboarding feature allows you to test post-sideboard deck configurations for different matchups. This is essential for understanding how your deck performs after boarding for specific opponents or strategies.

## Quick Start

```bash
# Test your deck against combo decks
python madness.py --runs 1000 --sideboard vs_combo

# Test against aggressive strategies
python madness.py --runs 1000 --sideboard vs_aggro --output vs_aggro_results.xlsx

# Test against enchantment-heavy decks
python madness.py --runs 1000 --sideboard vs_enchantments
```

## Configuration

### 1. Create Your Sideboard (sideboard.csv)

Format is identical to your main deck CSV:

```csv
Card Name,Quantity,Type,Mana Cost,Conditions
Blue Elemental Blast,4,Instant,U,effect:hate_red
Cave-In,2,Sorcery,R,effect:wipe
Chill,2,Instant,U,effect:hate_red
```

### 2. Define Sideboard Plans (simulation_config.json)

Add a `sideboard_plans` section to your config:

```json
{
  "sideboard_plans": {
    "vs_combo": {
      "name": "Vs Combo",
      "board_in": {
        "Counterspell": 2,
        "Blue Elemental Blast": 2
      },
      "board_out": {
        "Naturalize": 2,
        "Waterfront Bouncer": 2
      }
    },
    "vs_aggro": {
      "name": "Vs Aggro",
      "board_in": {
        "Cave-In": 2,
        "Chill": 2
      },
      "board_out": {
        "Counterspell": 2,
        "Squee, Goblin Nabob": 2
      }
    }
  }
}
```

### Sideboard Plan Structure

Each plan has:
- **Key** (e.g., `vs_combo`): Used in CLI flag `--sideboard vs_combo`
- **name**: Human-readable name (displayed during simulation)
- **board_in**: Cards to add from sideboard (card name → quantity)
- **board_out**: Cards to remove from main deck (card name → quantity)

## How It Works

1. **Board Out**: Removes specified cards from main deck
   - If you have 3 copies and board out 2, you'll have 1 remaining
   - If you board out all copies, card is completely removed

2. **Board In**: Adds cards from sideboard
   - If card already exists in deck, increases quantity
   - If card doesn't exist in deck, adds it as new card
   - Card must exist in `sideboard.csv`

3. **Temporary Deck**: Creates modified deck for simulation
   - Automatically cleaned up after simulation
   - Original deck.csv is never modified

## CLI Usage

### Basic Sideboarding

```bash
python madness.py --sideboard vs_combo
```

### With Custom Output

```bash
python madness.py --sideboard vs_aggro --output vs_aggro_results.xlsx
```

### With Custom Sideboard File

```bash
python madness.py --sideboard vs_combo --sideboard-file my_sideboard.csv
```

### Full Options

```bash
python madness.py \
  --deck deck.csv \
  --sideboard vs_combo \
  --sideboard-file sideboard.csv \
  --runs 1000 \
  --turns 4 \
  --output vs_combo_results.xlsx \
  --config simulation_config.json
```

## Example Workflow

### 1. Run Pre-Board Simulation

```bash
python madness.py --runs 1000 --output game1_results.xlsx
```

### 2. Run Post-Board Simulations

```bash
# Against combo
python madness.py --runs 1000 --sideboard vs_combo --output game2_vs_combo.xlsx

# Against aggro
python madness.py --runs 1000 --sideboard vs_aggro --output game2_vs_aggro.xlsx
```

### 3. Compare Results

Open all three Excel files and compare:
- Key card access rates
- Ideal setup success rates
- Opening hand patterns
- Deck consistency metrics

## Example Sideboard Plans

### Vs Combo (Add Disruption)

```json
"vs_combo": {
  "name": "Vs Combo",
  "board_in": {
    "Counterspell": 2,
    "Blue Elemental Blast": 2,
    "Tormod's Crypt": 1
  },
  "board_out": {
    "Naturalize": 2,
    "Waterfront Bouncer": 2,
    "Wonder": 1
  }
}
```

**Strategy**: Add more countermagic and graveyard hate, cut creature-based interaction.

### Vs Aggro (Add Removal)

```json
"vs_aggro": {
  "name": "Vs Aggro",
  "board_in": {
    "Cave-In": 2,
    "Chill": 2,
    "Pyrokinesis": 1
  },
  "board_out": {
    "Counterspell": 3,
    "Squee, Goblin Nabob": 2
  }
}
```

**Strategy**: Add board wipes and creature removal, cut slow cards.

### Vs Control (Add Threats)

```json
"vs_control": {
  "name": "Vs Control",
  "board_in": {
    "Wild Mongrel": 2,
    "Arrogant Wurm": 2
  },
  "board_out": {
    "Naturalize": 2,
    "Careful Study": 2
  }
}
```

**Strategy**: Add resilient threats, cut reactive spells.

### Vs Enchantments (Add Hate)

```json
"vs_enchantments": {
  "name": "Vs Enchantments",
  "board_in": {
    "Reverent Silence": 2,
    "Naturalize": 2
  },
  "board_out": {
    "Wonder": 1,
    "Wild Mongrel": 3
  }
}
```

**Strategy**: Max out on enchantment removal.

## Verification

After running a sideboarded simulation, verify it worked:

### Check Card Stats

```python
import pandas as pd

df = pd.read_excel('vs_combo_results.xlsx', sheet_name='Card Stats')

# Cards that should be in
print(df[df['Card'] == 'Blue Elemental Blast'])

# Cards that should be reduced/removed
print(df[df['Card'] == 'Waterfront Bouncer'])
```

### Expected Results

Given this plan:
```json
"board_in": {"Counterspell": 2},
"board_out": {"Naturalize": 2}
```

If original deck had:
- 3x Counterspell
- 3x Naturalize

Sideboarded deck should have:
- 5x Counterspell (3 + 2 = 5)
- 1x Naturalize (3 - 2 = 1)

## Error Handling

### Invalid Sideboard Plan

```bash
$ python madness.py --sideboard invalid_plan
❌ Error: Sideboard plan 'invalid_plan' not found in config.
Available plans: vs_combo, vs_aggro, vs_enchantments
```

### Missing Sideboard File

If `sideboard.csv` doesn't exist:
```
FileNotFoundError: sideboard.csv not found
```

### Card Not in Sideboard

If you try to board in a card not in `sideboard.csv`, it will be silently skipped. Add the card to your sideboard file.

## Use Cases

### 1. Matchup Analysis

Compare pre-board vs post-board win rates:

```bash
python madness.py --runs 1000 --output preboard.xlsx
python madness.py --runs 1000 --sideboard vs_combo --output postboard_combo.xlsx
```

**Analysis**: If "Survival Engine" success goes from 40% → 60%, sideboarding improves the matchup.

### 2. Sideboard Card Evaluation

Test if a sideboard card actually helps:

```bash
# With Cave-In in sideboard
python madness.py --sideboard vs_aggro --output with_cavein.xlsx

# Without Cave-In (remove from plan)
python madness.py --sideboard vs_aggro_no_cavein --output without_cavein.xlsx
```

**Analysis**: Compare creature counts, graveyard sizes, setup success rates.

### 3. Optimal Sideboard Numbers

Test different quantities:

```json
"vs_combo_light": {
  "board_in": {"Counterspell": 1, "Blue Elemental Blast": 1},
  "board_out": {"Naturalize": 2}
},
"vs_combo_heavy": {
  "board_in": {"Counterspell": 2, "Blue Elemental Blast": 3},
  "board_out": {"Naturalize": 2, "Wonder": 2, "Wild Mongrel": 1}
}
```

**Analysis**: Which configuration achieves better counter protection without hurting consistency?

### 4. Multiple Matchups

Run comprehensive post-board testing:

```bash
for plan in vs_combo vs_aggro vs_control vs_enchantments; do
  python madness.py --runs 1000 --sideboard $plan --output ${plan}_results.xlsx
done
```

**Analysis**: Compare how each configuration affects your ideal setups.

## Technical Details

### Implementation

1. **`apply_sideboard_plan()`**: Modifies deck DataFrame
   - Reduces quantities for board_out cards
   - Increases/adds quantities for board_in cards
   - Returns modified DataFrame

2. **`create_sideboarded_deck()`**: Saves temporary CSV
   - Writes modified deck to `temp_sideboarded_deck.csv`
   - Used by simulation engine
   - Cleaned up automatically in `finally` block

3. **Simulation**: Uses temporary deck
   - All existing features work normally
   - Opening hand analysis
   - Graveyard tracking
   - Setup evaluation

### Files

- **Input**: 
  - `deck.csv` - Main deck
  - `sideboard.csv` - Sideboard cards
  - `simulation_config.json` - Sideboard plans

- **Temporary**:
  - `temp_sideboarded_deck.csv` - Created and deleted automatically

- **Output**:
  - `simulation_results.xlsx` (or custom name)
  - Contains results for sideboarded configuration

## Tips & Best Practices

### 1. Match Real Play Patterns

Design sideboard plans that match actual sideboarding decisions:
- Board out cards that are bad in the matchup
- Board in cards that address opponent's strategy
- Keep total cards at 60

### 2. Test Incrementally

Start with small changes:
```json
// Start here
"board_in": {"Counterspell": 1},
"board_out": {"Wonder": 1}

// Then increase if needed
"board_in": {"Counterspell": 2, "Blue Elemental Blast": 2},
"board_out": {"Wonder": 2, "Naturalize": 2}
```

### 3. Document Your Plans

Use descriptive names and comments:
```json
"vs_combo": {
  "name": "Vs Storm/Combo - Heavy Disruption",
  "board_in": {
    "Counterspell": 2,    // Additional counters
    "Blue Elemental Blast": 2,  // Efficient answers
    "Tormod's Crypt": 1   // Graveyard hate
  },
  ...
}
```

### 4. Compare Opening Hands

The "Opening Hands" sheet is particularly valuable for sideboarded configurations:
- Shows if you're more likely to have disruption
- Reveals if sideboarding hurt your combo pieces
- Identifies new winning patterns

### 5. Track Multiple Metrics

Don't just look at one setup success rate. Consider:
- Overall consistency (mulligan rate)
- Multiple setup success rates
- Key card access
- Opening hand patterns

## Future Enhancements

Potential additions:
- Pre-configured matchup setups
- Automatic comparison reports (pre-board vs post-board)
- Sideboard coverage analysis (which cards hit which matchups)
- Optimal sideboard composition recommendations

## Summary

✅ **Simple CLI**: Just add `--sideboard plan_name`
✅ **Flexible Plans**: Define any number of matchup configurations
✅ **Complete Analysis**: All existing features work with sideboarded decks
✅ **Safe**: Never modifies original deck files
✅ **Verifiable**: Easy to confirm cards were properly swapped

Sideboarding is now fully integrated into the simulation workflow!

