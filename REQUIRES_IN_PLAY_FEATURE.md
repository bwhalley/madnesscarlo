# `requires_in_play` Feature Documentation

## Overview

Added support for checking if specific cards are **on the battlefield** (in play) as part of ideal setup evaluation.

## Use Case: Wonder + Island

Wonder grants flying to your creatures, but **only if you control an Island**. The `requires_in_play` field lets you track when this condition is actually met.

## Configuration

### New Field: `requires_in_play`

Add this to any ideal setup in `simulation_config.json`:

```json
{
  "name": "Wonder in Graveyard",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_in_play": ["Island"],
  "requires_colors": [],
  "turn_limit": 4
}
```

### Four-Part Evaluation

Setups now check **four conditions**:

1. ✅ `requires_cards` - Card was seen (drawn/tutored) by turn X
2. ✅ `requires_in_graveyard` - Card is in graveyard at end of simulation
3. ✅ `requires_in_play` - Card is on battlefield at end of simulation
4. ✅ `requires_colors` - Mana colors available by turn X

**All four must be true for setup success!**

## Results Comparison (1000 games)

### Before (Without Island Requirement)
```
Wonder in Graveyard: 20.6%
→ Wonder seen + in graveyard
```

### After (With Island Requirement)
```
Wonder in Graveyard: 16.4%
→ Wonder seen + in graveyard + Island in play
```

### Analysis
- **Island availability**: 145.5% (avg 1.45 Islands in play per game)
- **Success drop**: 20.6% → 16.4% (4.2% of games had Wonder in graveyard but no Island)
- **Insight**: ~80% of games with Wonder in graveyard also have Island in play

## What Gets Tracked in Battlefield

The `battlefield` Counter now tracks:
- **Lands** (Island, Forest, Yavimaya Coast, etc.)
- **Creatures** (Wild Mongrel, Arrogant Wurm, etc.)
- **Permanents** (Survival of the Fittest, etc.)
- **Tokens** (Wurm Token from flashback)

### Battlefield Stats Example
```
Card                  Avg on Battlefield    %
Island                1.455                 145.5%
Forest                1.078                 107.8%
Wild Mongrel          0.512                  51.2%
Arrogant Wurm         0.678                  67.8%
Basking Rootwalla     0.934                  93.4%
```

Note: Percentages > 100% indicate multiple copies in play on average.

## Common Use Cases

### 1. Land-Dependent Graveyard Effects (Wonder)
```json
{
  "name": "Wonder Flying Active",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_in_play": ["Island"],
  "requires_colors": [],
  "turn_limit": 4
}
```
Tracks: Is flying actually enabled? (Wonder + Island)

### 2. Discard Outlet Available
```json
{
  "name": "Wild Mongrel Outlet Ready",
  "requires_cards": ["Wild Mongrel", "Arrogant Wurm"],
  "requires_in_play": ["Wild Mongrel"],
  "requires_colors": ["G"],
  "turn_limit": 3
}
```
Tracks: Do I have discard outlet on board with madness card in hand?

### 3. Engine Pieces on Board
```json
{
  "name": "Survival Active with Squee",
  "requires_cards": ["Survival of the Fittest", "Squee, Goblin Nabob"],
  "requires_in_play": ["Survival of the Fittest"],
  "requires_colors": ["G"],
  "turn_limit": 4
}
```
Tracks: Is Survival enchantment actually on the battlefield?

### 4. Multiple Lands Required
```json
{
  "name": "UG Dual Land Base",
  "requires_cards": [],
  "requires_in_play": ["Island", "Forest"],
  "requires_colors": ["U", "G"],
  "turn_limit": 2
}
```
Tracks: Do I have both basic land types by turn 2?

### 5. Specific Land Requirements
```json
{
  "name": "Cephalid Coliseum Draw Ready",
  "requires_cards": ["Cephalid Coliseum"],
  "requires_in_play": ["Cephalid Coliseum"],
  "requires_colors": [],
  "turn_limit": 4
}
```
Tracks: Is Coliseum on battlefield for late-game draw?

## Technical Details

### Implementation

**File**: `madness.py`

**Changes Made**:

1. **`play_land()` method** (line 156):
```python
self.battlefield[card] += 1  # Track specific land in play
```

2. **`evaluate_ideal_setups()` function** (lines 75-80):
```python
required_in_play = setup.get("requires_in_play", [])
in_play_ok = all(
    card in state.battlefield and state.battlefield[card] > 0
    for card in required_in_play
)
```

3. **Combined check** (line 83):
```python
setup_results[name] = cards_ok and colors_ok and graveyard_ok and in_play_ok
```

### Logic Flow
1. Land is played from hand
2. Added to `battlefield` Counter
3. At end of simulation, `evaluate_ideal_setups` checks `battlefield`
4. Setup succeeds only if all required cards are present

## Side Effect: Battlefield Stats

Now that lands are tracked in battlefield, the **Battlefield Stats** sheet shows:
- Average lands in play per game
- Average creatures in play per game
- Land type distribution
- Permanent distribution

This provides valuable data about board development!

## Benefits

✅ **Accurate Graveyard Synergy Tracking**
- Wonder flying only counts when Island is present
- More realistic success rates

✅ **Board State Analysis**
- See which lands hit the battlefield most
- Track creature deployment patterns
- Identify bottlenecks

✅ **Complex Setup Evaluation**
- Combine multiple conditions
- Test realistic game scenarios
- Optimize deck composition

✅ **Land Base Optimization**
- Verify land type distribution
- Test color consistency
- Evaluate special lands (Coliseum, Coast)

## Examples from Real Data

### Wonder Analysis (1000 games)
```
Raw Stats:
- Wonder in graveyard: 21.8% of games
- Island in play: 145.5% (1.45 per game)

Setup Stats:
- Wonder + Island: 16.4%

Insight: ~75% of games with Wonder in graveyard also have Island
         (16.4 / 21.8 = 75.2%)
```

### Land Distribution
```
Island:  1.455 avg (9 in deck)
Forest:  1.078 avg (7 in deck)
Coast:   0.584 avg (4 in deck)
Coliseum: 0.146 avg (1 in deck)
```
Shows blue-heavy mana base with good Island availability.

## Troubleshooting

**Q: Setup shows 0% but cards are in graveyard?**
- Check if required lands/permanents are in `requires_in_play`
- Verify card names match exactly (case-sensitive)

**Q: Battlefield % over 100%?**
- Normal! Means multiple copies in play on average
- Example: 145.5% = 1.45 Islands per game

**Q: Land not showing up in battlefield stats?**
- Check deck.csv for correct Type field ("Land")
- Verify land is being drawn and played

## Future Enhancements

Potential additions:
- `requires_not_in_play` - Check for absence of cards
- Turn-based tracking (which turn card entered battlefield)
- Board state snapshots per turn
- Creature count thresholds
- Permanent type counting (# of artifacts, enchantments, etc.)

## Summary

The `requires_in_play` feature enables **realistic setup evaluation** by checking actual battlefield state, not just card availability. This is essential for:
- Graveyard synergies with land requirements (Wonder)
- Engine pieces that must be on board (Survival)
- Discard outlets availability (Wild Mongrel)
- Land type requirements

Your ideal setups now reflect **actual game conditions**! 🎯

