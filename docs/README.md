# MTG Madness Carlo Simulator

A Monte Carlo simulation tool for analyzing Magic: The Gathering deck performance, with a focus on "Madness" and card draw chains.

## 🚀 NEW: Full-Featured Web Application!

**Phase 2 Complete!** A production-ready web application with comprehensive features:
- 🌐 **Browser-based interface** - Run simulations from anywhere
- 👤 **Google OAuth** - Secure authentication with Google accounts
- 💾 **Cloud storage** - PostgreSQL database for decks and configs
- 📊 **Interactive dashboards** - Real-time visualization with Recharts
- 🔄 **Background processing** - Celery + Redis for long-running simulations
- 📱 **Modern UI** - Built with React, TypeScript, and TailwindCSS
- ⚡ **Live updates** - WebSocket integration for simulation progress
- 📈 **Google Sheets export** - One-click export to your Google Drive
- 🧪 **Comprehensive tests** - 40 tests covering all core functionality
- 🎯 **Ideal setups tracking** - Monitor multiple win conditions simultaneously
- 🃏 **Opening hands analysis** - Pattern recognition for optimal starting configurations

**Quick Start Web App:**
```bash
docker-compose up -d
# Visit http://localhost:5173
# Login with Google to access all features
```

📖 **Full Documentation:**
- [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Initial web app setup
- [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) - Simulation engine integration
- [OPENING_HANDS_FEATURE.md](OPENING_HANDS_FEATURE.md) - Opening hands analysis guide
- [TEST_SUITE_SUMMARY.md](TEST_SUITE_SUMMARY.md) - Test coverage details
- [backend/tests/README.md](backend/tests/README.md) - Testing guide

---

## Overview (CLI Tool)

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
- 🎴 **Sideboarding support** - Test post-board configurations for different matchups
- 🎯 **Matchup analysis** - Compare pre-board vs post-board performance
- ⚖️ **Deck comparison** - Side-by-side analysis of two deck configurations
- 📈 **Delta tracking** - Measure impact of card changes on all metrics
- 🔬 **Experimental framework** - Automatically test dozens of deck variants
- 🎯 **Auto-optimization** - Find best configuration for your goals
- ⚡ **Parallel testing** - Multi-threaded experiment execution

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

### Sideboarding (Post-Board Testing)

Test your deck after sideboarding for different matchups:

```bash
# Test against combo decks
python madness.py --runs 1000 --sideboard vs_combo

# Test against aggro decks  
python madness.py --runs 1000 --sideboard vs_aggro --output vs_aggro.xlsx

# List available sideboard plans (will show error with list)
python madness.py --sideboard invalid_plan
```

Define sideboard plans in `simulation_config.json`:
```json
{
  "sideboard_plans": {
    "vs_combo": {
      "name": "Vs Combo",
      "board_in": {"Counterspell": 2, "Blue Elemental Blast": 2},
      "board_out": {"Naturalize": 2, "Waterfront Bouncer": 2}
    }
  }
}
```

See `SIDEBOARDING_FEATURE.md` for complete documentation.

### Deck Comparison

Compare two deck configurations side-by-side to analyze the impact of card changes:

```bash
# Compare baseline deck vs variant with card swaps
python madness.py --compare deck.csv variant.csv --runs 1000

# Customize output file
python madness.py --compare deck.csv variant.csv --runs 2000 --compare-output my_comparison.xlsx
```

**What gets compared:**
- ✅ **Ideal setup success rates** - See how changes affect your primary goals
- 📊 **Opening hand patterns** - Identify which patterns improved or declined
- 🎲 **Mulligan statistics** - Track consistency improvements
- 🎯 **Key card access** - Monitor card visibility changes
- 📝 **Card-by-card changes** - Detailed breakdown of what changed

**Output files:**
- `comparison_results.xlsx` - Excel with 6 sheets of detailed comparison data
- `comparison_results_summary.md` - Markdown summary with key insights

**Example workflow:**
```bash
# 1. Test baseline
python madness.py --runs 1000 --output baseline.xlsx

# 2. Modify deck (e.g., -2 Naturalize, +2 Frantic Search)
cp deck.csv variant.csv
# Edit variant.csv with changes

# 3. Compare
python madness.py --compare deck.csv variant.csv --runs 1000

# 4. Review comparison_results_summary.md for insights
```

**Key comparison features:**
- **Opening Hand Development**: See how card swaps change the frequency and success of different opening hand patterns
- **Turn-by-Turn Impact**: Understand how changes affect hand development over turns 1-4
- **Ideal Setup Deltas**: Direct before/after comparison of your primary win condition success rates
- **Pattern Analysis**: Identify new patterns that emerge or disappear with changes
- **Statistical Insights**: Auto-generated analysis of improvements vs declines

See `DECK_COMPARISON_PROJECT_PLAN.md` for technical details.

### Experimental Deck Optimization

**Automatically find the best deck configuration** by testing multiple variants simultaneously:

```bash
# Basic experiment
python madness.py --experiment experiments/land_count_optimization.json

# With custom parameters
python madness.py --experiment experiments/card_draw_comparison.json --runs 2000 --workers 8

# Custom output file
python madness.py --experiment experiments/creature_density.json --experiment-output my_results.xlsx
```

**What it does:**
- 🔬 **Automated Testing** - Generate and test dozens of deck variants automatically
- 🎯 **Goal Optimization** - Optimize for specific metrics (mulligan rate, ideal setup success, etc.)
- ⚡ **Parallel Execution** - Test variants in parallel using all CPU cores
- 📊 **Smart Ranking** - Automatically rank variants by performance
- 💡 **Auto-Insights** - Generate recommendations based on results

**Experiment Types:**

1. **Land Count Optimization** - Find optimal land ratios
   ```json
   {
     "type": "replace_quantity",
     "card": "Forest",
     "test_quantities": [5, 6, 7, 8, 9, 10],
     "compensate_with": "Island"
   }
   ```

2. **Card Slot Testing** - Compare alternative cards
   ```json
   {
     "type": "slot_testing",
     "slots": [{"card": "Careful Study", "quantity": 2}],
     "alternatives": [
       {"card": "Deep Analysis", "quantity": 2},
       {"card": "Brainstorm", "quantity": 2}
     ]
   }
   ```

3. **Combinatorial Testing** - Test multiple changes together
   ```json
   {
     "type": "combinatorial",
     "max_combinations": 20,
     "slots": [
       {
         "name": "draw_slot",
         "baseline": {"card": "Careful Study", "quantity": 2},
         "alternatives": [...]
       }
     ]
   }
   ```

**Output:**
- `experiment_<name>_results.xlsx` - 6 sheets with detailed analysis
  - Summary: Experiment overview and statistics
  - Rankings: All variants ranked by optimization goal
  - Variant Details: Card-by-card breakdown
  - Top 5 Comparison: Side-by-side comparison
  - Statistical Analysis: Confidence intervals and distributions
  - Insights: Auto-generated recommendations
- `experiment_<name>_results_summary.md` - Quick reference with key findings

**Example Workflow:**
```bash
# 1. Create experiment config (or use examples)
cat experiments/land_count_optimization.json

# 2. Run experiment (quick test)
python madness.py --experiment experiments/land_count_optimization.json --runs 500

# 3. Review results
open experiment_land_count_optimization_results.xlsx

# 4. Run with more samples for confidence
python madness.py --experiment experiments/land_count_optimization.json --runs 2000

# 5. Apply best variant to your deck
# Check "Variant Details" sheet and update deck.csv

# 6. Validate improvement
python madness.py --compare deck_old.csv deck.csv --runs 1000
```

**Optimization Goals:**
- `maximize_survival_engine` - Increase Survival Engine setup success
- `maximize_roar_flashback` - Increase Roar of the Wurm flashback access
- `maximize_wonder_flying` - Increase Wonder flying team success
- `minimize_mulligans` - Reduce average mulligan count
- `maximize_color_access` - Improve mana color availability
- `maximize_key_card_access` - Improve key card draw rates

**Example Experiments:**
See `experiments/` directory for ready-to-use configurations:
- `land_count_optimization.json` - Find optimal Forest/Island split
- `card_draw_comparison.json` - Compare card draw engines
- `creature_density.json` - Optimize creature counts for Survival

Create custom experiments or modify examples for your specific needs. See `experiments/README.md` and `EXPERIMENTAL_FRAMEWORK_PROJECT_PLAN.md` for detailed documentation.

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
| `--sideboard` | Sideboard plan name (e.g., `vs_combo`) | None |
| `--sideboard-file` | Path to sideboard CSV | `sideboard.csv` |
| `--compare` | Compare two decks (e.g., `deck.csv variant.csv`) | None |
| `--compare-output` | Comparison output filename | `comparison_results.xlsx` |

## Testing

This project includes comprehensive test suites for both CLI and web application.

### CLI Tool Tests

```bash
# Quick test
./run_tests.sh

# With coverage report
./run_tests.sh coverage

# Fast tests only
./run_tests.sh quick

# Or run directly with pytest
pytest test_madness.py -v
pytest test_madness.py --cov=. --cov-report=html
```

**CLI Test Coverage:**
- **121 tests** covering all functionality
- **70% overall code coverage** (91% for critical modules)
- **100% of tests passing**

**Coverage by Feature:**
- ✅ Core simulation engine: 75%
- ✅ Comparison utilities: 91%
- ✅ Export modules: 91%
- ✅ Experimental framework: 60-68%
- ✅ All mechanics: Fully tested (madness, flashback, tutoring, returns)

See `TEST_COVERAGE_REPORT.md`, `TESTING.md`, and `TEST_SUMMARY.md` for detailed CLI testing documentation.

### Web Application Tests

```bash
# Run all web app tests
docker exec madness-backend pytest /app/tests/ -v

# Run with coverage
docker exec madness-backend pytest /app/tests/ --cov=app.simulation --cov-report=term-missing

# Run specific test suite
docker exec madness-backend pytest /app/tests/test_simulation_engine.py -v
docker exec madness-backend pytest /app/tests/test_simulation_runner.py -v
```

**Web App Test Coverage:**
- ✅ **40 core tests** covering all simulation functionality
- ✅ **29 engine tests** - Card actions, abilities, mana detection, ideal setups
- ✅ **11 runner tests** - Aggregation, statistics, progress tracking
- ✅ **100% of core tests passing** (11 export tests skipped, needs refactoring)
- ⚡ **Fast execution** - Full suite runs in ~1.5 seconds

**What's Tested:**
- ✅ All 8 card actions (Careful Study, Frantic Search, Survival, etc.)
- ✅ All 4 activated abilities (Survival, Wild Mongrel, Roar flashback, etc.)
- ✅ Mana color detection for all 5 basic land types
- ✅ All 6 ideal setup condition types
- ✅ Simulation aggregation and statistics generation
- ✅ Zero-success setups (not omitted from results)
- ✅ Card database integration (AtomicCards.json)
- ✅ Mulligan, graveyard, battlefield tracking
- ✅ Madness triggers and flashback mechanics

See [TEST_SUITE_SUMMARY.md](TEST_SUITE_SUMMARY.md) and [backend/tests/README.md](backend/tests/README.md) for detailed web app testing documentation.

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--deck` | Path to deck CSV file (default: `deck.csv`) |
| `--runs` | Number of simulation runs (default: 1000) |
| `--turns` | Number of turns to simulate (default: 4) |
| `--output` | Output Excel file path (default: `simulation_results.xlsx`) |
| `--config` | Simulation configuration JSON (default: `simulation_config.json`) |
| `--sideboard` | Sideboard plan name (e.g., `vs_combo`, `vs_aggro`) |
| `--sideboard-file` | Path to sideboard CSV (default: `sideboard.csv`) |
| `--compare` | Compare two decks (e.g., `--compare deck.csv variant.csv`) |
| `--compare-output` | Comparison results output file (default: `comparison_results.xlsx`) |
| `--experiment` | Run experiment from config file (e.g., `--experiment experiments/land_count.json`) |
| `--experiment-output` | Experiment results output file (default: `experiment_<name>_results.xlsx`) |
| `--workers` | Number of parallel workers for experiments (default: CPU count - 1) |

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

