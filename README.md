# MTG Madness Chains Simulator

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
- 📈 **Progress tracking** - Real-time simulation progress with tqdm

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
  "key_cards": ["Survival of the Fittest", "Squee"],
  "ideal_setups": [
    {
      "name": "Survival Engine",
      "requires_cards": ["Survival of the Fittest", "Squee"],
      "requires_colors": ["G"],
      "turn_limit": 4
    }
  ]
}
```

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

The simulator generates an Excel file with four sheets:

1. **Card Stats** - See % and Cast % for each card
2. **Key Card Stats** - Success rate for seeing key cards by turn 4
3. **Ideal Setups** - Success rate for assembling specific combos
4. **Summary** - Average lands, cards seen, and simulation parameters

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
2. **Game State** - Tracks hand, lands, mana colors, and cards seen
3. **Turn Simulation** - Plays lands, casts spells, draws cards for N turns
4. **Card Actions** - Resolves effects like "Careful Study" (draw 2, discard 2)
5. **Aggregation** - Collects statistics across thousands of simulations
6. **Export** - Outputs results to Excel for analysis

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

## Contributing

Feel free to open issues or submit PRs for:
- New card action implementations
- Improved condition parsing
- Additional statistics tracking
- UI improvements

## License

MIT License - Feel free to use and modify for your MTG deck testing needs!

## Author

Built for analyzing MTG "Madness" chains and combo consistency.

