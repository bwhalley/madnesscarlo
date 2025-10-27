# Opening Hands Analysis Feature

## Overview

The Opening Hands Analysis feature tracks and analyzes opening hand patterns across simulations to identify which starting configurations lead to successful ideal setup achievement. This helps players understand which types of opening hands are most likely to result in achieving their desired game states.

## How It Works

### 1. Pattern Extraction

Each opening hand (after mulligans) is analyzed and converted into a pattern string that captures:

- **Land Count**: Number of lands in the opening hand (e.g., "3L")
- **Creature Count**: Number of creatures in the opening hand (e.g., "2C")
- **Key Cards**: Any key cards (as defined in simulation config) present (e.g., "+Survival")

**Example Patterns:**
- `3L 2C` - 3 lands, 2 creatures, no key cards
- `2L 1C +Survival` - 2 lands, 1 creature, has Survival of the Fittest
- `3L 2C +Survival+Squee` - 3 lands, 2 creatures, has both Survival and Squee

### 2. Pattern Aggregation

The simulation groups all games by their opening hand pattern and tracks:

- **Games**: How many games started with this pattern
- **Median Mulligans**: The median number of mulligans taken to achieve this pattern
- **Setup Success Rates**: For each ideal setup, what percentage of games with this pattern achieved that setup
- **Average Success %**: Overall average success rate across all ideal setups for this pattern

### 3. Pattern Ranking

Patterns are ranked by total setup successes (sum of all setup successes for that pattern), showing the most successful opening hand patterns first.

## Implementation Details

### Backend Changes

#### `backend/app/simulation/runner.py`

Added three key functions:

1. **`extract_hand_pattern(opening_hand, deck, config)`**
   - Converts an opening hand into a pattern string
   - Uses card database to identify lands and creatures
   - Abbreviates key card names for readability

2. **`analyze_opening_hands(all_results, deck, config)`**
   - Groups all simulation results by opening hand pattern
   - Calculates success rates for each ideal setup per pattern
   - Computes median mulligans for each pattern
   - Returns sorted list of pattern statistics

3. **Modified `run_simulations()`**
   - Now calls `analyze_opening_hands()` after all simulations complete
   - Returns `opening_hands_stats` in the results dictionary

#### `backend/app/services/google_sheets_oauth.py`

Added Opening Hands sheet support:

1. **Added "Opening Hands" sheet** to spreadsheet creation
2. **`_populate_opening_hands()`** method
   - Creates dynamic columns for each ideal setup
   - Formats data with pattern, games, median mulligans, and success rates
   - Shows patterns ranked by overall success
3. **Updated `_format_spreadsheet()`** to apply formatting to Opening Hands tab

### Data Structure

The `opening_hands_stats` field in simulation results contains:

```python
[
    {
        "pattern": "3L 2C +Survival",
        "games": 47,
        "median_mulligans": 1.0,
        "setup_success_rates": {
            "Survival + Creature": 89.4,
            "Wonder in Graveyard": 34.0,
            "Squee + Survival": 23.4
        },
        "avg_success_percentage": 48.9
    },
    # ... more patterns
]
```

## Google Sheets Export

The Opening Hands sheet in the exported Google Sheets includes:

- **Pattern**: The opening hand pattern (e.g., "3L 2C +Survival")
- **Games**: Number of games with this pattern
- **Median Mulligans**: Typical mulligans needed to get this pattern
- **Avg Success %**: Overall success rate across all setups
- **Individual Setup Columns**: Success rate for each configured ideal setup

The sheet is formatted with:
- Bold headers with gray background
- Frozen header row for easy scrolling
- Patterns sorted by total successes (best patterns first)

## Key Card Abbreviations

For readability, long card names are abbreviated in patterns:

- "Survival of the Fittest" → "Survival"
- "Squee, Goblin Nabob" → "Squee"
- "Roar of the Wurm" → "Roar"

Other cards use their full names.

## Use Cases

This feature helps answer questions like:

1. **"What's the best type of opening hand for this deck?"**
   - Look at the top patterns in the Opening Hands sheet

2. **"Should I mulligan a 2-land hand with Survival?"**
   - Check the success rate of the "2L XC +Survival" pattern

3. **"Is it worth mulliganing to find a key card?"**
   - Compare success rates of patterns with vs. without key cards
   - Check median mulligan counts for successful patterns

4. **"Do I need creatures in my opening hand?"**
   - Compare patterns with different creature counts

5. **"What's the ideal balance of lands and spells?"**
   - Identify which land counts correlate with highest success rates

## Example Analysis

Given these opening hand patterns:

| Pattern | Games | Median Mulligans | Avg Success % | Survival + Creature % | Wonder in Graveyard % |
|---------|-------|------------------|---------------|----------------------|----------------------|
| 3L 2C +Survival | 47 | 1.0 | 48.9% | 89.4% | 34.0% |
| 2L 2C +Survival | 35 | 0.0 | 42.1% | 82.9% | 28.6% |
| 3L 2C | 125 | 0.0 | 28.5% | 45.6% | 22.4% |
| 4L 1C | 78 | 0.0 | 18.9% | 30.8% | 15.4% |

**Insights:**
- Opening hands with Survival have significantly higher success rates (48.9% vs 28.5%)
- 3 lands is ideal (3L patterns outperform both 2L and 4L)
- Having 2 creatures is better than 1 creature
- Mulliganing once to find Survival is often correct (median 1.0 mulligan for best pattern)

## Technical Notes

- Pattern analysis requires the full simulation results (`all_results`) to be kept in memory
- Card type detection uses the integrated `AtomicCards.json` database
- Median (not mean) mulligans is used because it's more representative of typical gameplay
- Patterns are sorted by total setup successes, not average success rate, to prioritize patterns that occur frequently

## Future Enhancements

Possible future improvements:

- Pattern filtering (e.g., "show only patterns with >10 games")
- Visual heatmaps in the UI showing success rates by land/creature count
- Comparison mode (compare opening hand patterns between deck variants)
- Custom pattern definitions (e.g., "has removal spell", "has card draw")
- Interactive pattern exploration in the web UI

