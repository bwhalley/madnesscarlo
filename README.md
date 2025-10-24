# MTG Madness Carlo Simulator

A Monte Carlo simulation tool for analyzing Magic: The Gathering deck performance, with a focus on "Madness" and card draw chains.

## Overview

This simulator runs thousands of games to analyze:
- Opening hand consistency
- Key card access rates
- Ideal setup/combo success rates
- Card draw and spell-casting patterns
- Mana color availability

Perfect for testing MTG deck builds, especially combo-oriented strategies that rely on seeing specific cards early.

## Features

- 🎴 **CSV-based deck input** - Easy deck configuration
- 🎲 **Monte Carlo simulation** - Run thousands of games in seconds
- 📊 **Excel output** - Detailed statistics and success rates
- ⚙️ **JSON configuration** - Define key cards and ideal setups
- 🎯 **Condition system** - Model mana requirements, color requirements, and card effects
- 🃏 **Auto-mulligan logic** - Intelligent London mulligan with configurable criteria
- ⏱️ **Flexible turn tracking** - Evaluate setups at specific turn limits
- 📈 **Progress tracking** - Real-time simulation progress with tqdm
- 🎰 **Opening hand analysis** - Identify which opening 7s lead to winning setups
- 🧠 **Pattern recognition** - Correlate hand composition with success rates
- 🪦 **Graveyard tracking** - Monitor cards entering graveyard from discards
- 🎪 **Battlefield tracking** - Track creatures and permanents in play
- ⚡ **Madness & Flashback** - Full support for alternative casting costs
- 🔄 **Recursion mechanics** - Handle returns from graveyard (Squee, etc.)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd madnesschains
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run a simulation with default settings (1000 games, 4 turns):

```bash
python madness.py
```

### Custom Parameters

```bash
python madness.py --deck deck.csv --runs 5000 --turns 6 --output results.xlsx
```

### Configuration File

Edit `simulation_config.json` to define:
- **Key cards** - Track specific cards you want to see early
- **Ideal setups** - Define combos that require specific cards and colors
- **Default parameters** - Set default runs, turns, and output file

Example configuration:
```json
{
  "runs": 1000,
  "turns": 4,
  "key_card_turn_limit": 4,
  "key_cards": ["Survival of the Fittest", "Squee, Goblin Nabob"],
  "ideal_setups": [
    {
      "name": "Survival Engine",
      "requires_cards": ["Survival of the Fittest", "Squee, Goblin Nabob"],
      "requires_colors": ["G"],
      "turn_limit": 4
    },
    {
      "name": "Counter Protection",
      "requires_cards": ["Counterspell"],
      "requires_colors": ["U"],
      "turn_limit": 2
    }
  ]
}
```

### Turn-Based Evaluation

The simulator tracks exactly when each card is seen and when mana colors become available:
- **Flexible simulation length**: Run any number of turns (4, 6, 8, etc.)
- **Per-setup turn limits**: Each ideal setup is evaluated at its specific `turn_limit`
- **Example**: "Counter Protection" requires Counterspell + U mana by turn 2, even if the simulation runs 6+ turns
- **Key card tracking**: Configure `key_card_turn_limit` to control when key cards should be evaluated (default: 4)

### Opening Hand Analysis

The simulator automatically analyzes which opening hand patterns correlate with setup success:

**Pattern Format**: `{lands}L {creatures}C [+KeyCard1+KeyCard2...]`

Examples:
- `3L 2C` - 3 lands, 2 creatures, no key cards
- `2L 1C +Survival` - 2 lands, 1 creature, has Survival of the Fittest
- `3L 2C +Squee+Survival` - 3 lands, 2 creatures, has both key cards

**How to Use**:
1. Run simulation as normal (automatically included)
2. Open the **"Opening Hands"** sheet in Excel
3. Sort by **"Avg Success %"** to see best patterns
4. Filter by **"Games >= 5"** for statistical significance
5. Use insights for mulligan decisions!

**Example Insights**:
- "Hands with Survival + Squee have 100% Survival Engine success"
- "3 lands optimal - 2 lands more variance, 4 lands flooding"
- "Counterspell provides 100% Counter Protection in any hand"

See `OPENING_HANDS_FEATURE_SUMMARY.md` for detailed analysis.

## Deck Format

Create a CSV file with the following columns:

| Card Name | Quantity | Type | Mana Cost | Conditions |
|-----------|----------|------|-----------|------------|
| Forest | 7 | Land | | effect:mana_G;category:land |
| Careful Study | 3 | Sorcery | U | requires:lands>=1;color=U;effect:draw2_discard2 |
| Wild Mongrel | 4 | Creature | 1G | |

### Condition Syntax

- `requires:lands>=3` - Requires 3 or more lands in play
- `requires:color=U` - Requires blue mana available
- `effect:mana_G` - Produces green mana
- `effect:draw2_discard2` - Card effect (for tracking)
- `category:land` - Card category

## Output

The simulator generates an Excel file with **11 comprehensive sheets**:

### Core Statistics
1. **Card Stats** - See % and Cast % for each card
2. **Key Card Stats** - Success rate for seeing key cards by turn 4
3. **Ideal Setups** - Success rate for assembling specific combos (evaluated at each setup's turn_limit)
4. **Mulligan Stats** - Distribution of mulligan counts across games

### Opening Hand Analysis 🎰
5. **Opening Hands** - Which opening hand patterns lead to setup success
   - Shows patterns like "3L 2C +Survival+Squee"
   - Success rate for each ideal setup per pattern
   - Average success across all setups
   - Identifies god hands vs mulligan hands

### Game State Tracking
6. **Graveyard Stats** - Cards in graveyard by turn 4 (from discards)
7. **Battlefield Stats** - Creatures and lands in play by turn 4
8. **Madness Casts** - Frequency of madness triggers by card
9. **Flashback Casts** - Frequency of flashback usage by card
10. **Tutored Cards** - What cards are searched for (e.g., Survival targets)

### Summary
11. **Summary** - Average lands, cards seen, mulligan rate, graveyard size, and simulation parameters

## Project Structure

```
madnesschains/
├── madness.py              # Main simulation engine
├── deck.csv                # Example deck list
├── simulation_config.json  # Configuration file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── v1_madness.py          # Earlier version (archived)
```

## How It Works

1. **Deck Parsing** - Loads deck from CSV with card conditions
2. **Mulligan Logic** - Auto-mulligan hands with 0-1 lands, 5+ lands, or no creatures
3. **Game State** - Tracks hand, lands, mana colors, and cards seen by turn
4. **Turn Simulation** - Plays lands, casts spells, draws cards for N turns
5. **Card Actions** - Resolves effects like "Careful Study" (draw 2, discard 2)
6. **Setup Evaluation** - Checks if ideal setups were achieved by their specific turn limits
7. **Aggregation** - Collects statistics across thousands of simulations
8. **Export** - Outputs results to Excel for analysis

## Mulligan Logic

The simulator uses London mulligan rules with **configurable auto-mulligan strategy**. All mulligan logic is defined in `simulation_config.json` for easy customization:

### Configuration

```json
"mulligan_strategy": {
  "enabled": true,
  "min_lands": 2,
  "max_lands": 4,
  "requires_creature": true,
  "max_mulligans": 7,
  "bottom_priority": {
    "prefer_land_at_count": 4,
    "protect_key_cards": true
  }
}
```

### Parameters

- **`enabled`** (bool): Enable/disable auto-mulligan logic entirely
- **`min_lands`** (int): Mulligan if lands < this value (default: 2)
- **`max_lands`** (int): Mulligan if lands > this value (default: 4)
- **`requires_creature`** (bool): Mulligan if no creatures in hand (default: true)
- **`max_mulligans`** (int): Safety limit for mulligan loops (default: 7)
- **`bottom_priority`**:
  - **`prefer_land_at_count`** (int): Bottom a land if hand has exactly this many lands (default: 4)
  - **`protect_key_cards`** (bool): Avoid bottoming key cards when possible (default: true)

### How It Works

1. Draw 7 cards
2. Check mulligan criteria (lands, creatures)
3. If criteria not met, shuffle back and draw 7 again
4. After keeping a hand, bottom N cards (where N = mulligan count)
5. Card selection for bottoming respects priority settings

### Example Results (Default Strategy: 2-4 lands, requires creature)

- ~69% of games keep the opening 7
- ~21% mulligan to 6
- ~7% mulligan to 5
- ~2% mulligan to 4 or fewer

### Custom Strategies

**No Mulligan** (always keep):
```json
"mulligan_strategy": {
  "enabled": false
}
```

**Aggressive** (exactly 3 lands):
```json
"mulligan_strategy": {
  "enabled": true,
  "min_lands": 3,
  "max_lands": 3,
  "requires_creature": true
}
```
Result: ~27% keep opening hand, avg 2.4 mulligans per game

**Lenient** (accept more variance):
```json
"mulligan_strategy": {
  "enabled": true,
  "min_lands": 1,
  "max_lands": 6,
  "requires_creature": false
}
```

## Example Deck

Included is a "Madness" themed deck featuring:
- Card draw/discard engines (Careful Study, Frantic Search)
- Madness creatures (Arrogant Wurm, Basking Rootwalla)
- Graveyard synergies (Roar of the Wurm, Wonder)
- Key combo pieces (Survival of the Fittest)

## Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--deck` | Path to deck CSV file | `deck.csv` |
| `--runs` | Number of simulations | `1000` |
| `--turns` | Turns to simulate per game | `4` |
| `--output` | Output Excel filename | `simulation_results.xlsx` |
| `--config` | Path to JSON config | `simulation_config.json` |

## Testing

This project includes a comprehensive test suite with 80% code coverage.

### Running Tests

```bash
# Quick test
./run_tests.sh

# With coverage report
./run_tests.sh coverage

# Fast tests only
./run_tests.sh quick
```

### Test Coverage

- **49 tests** covering all core functionality
- **80% code coverage** of `madness.py`
- Tests for: condition parsing, deck loading, game state, mulligan logic, simulation, and more

See `TESTING.md` and `TEST_SUMMARY.md` for detailed testing documentation.

## Contributing

Feel free to open issues or submit PRs for:
- New card action implementations
- Improved condition parsing
- Additional statistics tracking
- UI improvements

**Please run tests before submitting PRs:**
```bash
./run_tests.sh
```

## License

MIT License - Feel free to use and modify for your MTG deck testing needs!

## Author

Built for analyzing MTG "Madness" chains and combo consistency.

