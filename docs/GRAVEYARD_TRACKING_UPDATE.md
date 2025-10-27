# Graveyard Tracking Update

## ✅ New Feature: `requires_in_graveyard`

Added support for tracking when specific cards are in the graveyard by a certain turn, perfect for evaluating:
- **Wonder in Graveyard** → Flying enabled for creatures
- **Roar Flashback Available** → Can cast Roar from graveyard

## Configuration

### New Field: `requires_in_graveyard`

Add this to any ideal setup in `simulation_config.json`:

```json
{
  "name": "Wonder in Graveyard",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_colors": [],
  "turn_limit": 4
}
```

### How It Works

The setup evaluates **three conditions**:

1. **`requires_cards`** - Card was seen (drawn/tutored) by turn X
2. **`requires_in_graveyard`** - Card is in graveyard at end of simulation
3. **`requires_colors`** - Mana colors available by turn X

All three must be true for the setup to succeed.

## Example Results (1000 games)

### Ideal Setups Sheet
```
Setup                      Success %
Survival Engine            31.5%
Naturalize Access          44.9%
Wonder in Graveyard        20.6%
Counter Protection         49.9%
Roar Flashback Available   12.1%
```

### Interpretation

**Wonder in Graveyard: 20.6%**
- Wonder was seen AND in graveyard by turn 4
- Grants flying to all your creatures
- ~1 in 5 games you have the flying bonus active

**Roar Flashback Available: 12.1%**
- Roar in graveyard AND Green mana available by turn 4
- Can cast 6/6 Wurm token for 3G from graveyard
- ~1 in 8 games this combo is ready

### Cross-Reference with Raw Graveyard Stats
```
Card                 In Graveyard %
Wonder               21.8%
Roar of the Wurm     (need to see in graveyard stats)
```

Note: Raw graveyard % is slightly higher because it doesn't require seeing the card early or having mana.

### Flashback Usage
```
Card                 Flashback Cast %
Roar of the Wurm     6.3%
```

Flashback usage (6.3%) is about **half** of availability (12.1%), indicating we cast it when possible but not always.

## Use Cases

### 1. Flying Enabler (Wonder)
```json
{
  "name": "Wonder in Graveyard",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_colors": [],
  "turn_limit": 4
}
```
Tracks: Can I get Wonder into the graveyard early for flying?

### 2. Flashback Ready (Roar of the Wurm)
```json
{
  "name": "Roar Flashback Available",
  "requires_cards": ["Roar of the Wurm"],
  "requires_in_graveyard": ["Roar of the Wurm"],
  "requires_colors": ["G"],
  "turn_limit": 4
}
```
Tracks: Is Roar in graveyard with mana to cast it?

### 3. Recursive Threats (Squee)
```json
{
  "name": "Squee Recursion Available",
  "requires_cards": ["Squee, Goblin Nabob"],
  "requires_in_graveyard": ["Squee, Goblin Nabob"],
  "requires_colors": [],
  "turn_limit": 2
}
```
Tracks: Do I have Squee in graveyard early for infinite discard fodder?

### 4. Multiple Cards in Graveyard
```json
{
  "name": "Full Graveyard Engine",
  "requires_cards": ["Wonder", "Roar of the Wurm", "Squee, Goblin Nabob"],
  "requires_in_graveyard": ["Wonder", "Roar of the Wurm"],
  "requires_colors": ["G"],
  "turn_limit": 4
}
```
Tracks: Complex setups requiring specific graveyard composition.

## Technical Details

### Implementation
- Added `requires_in_graveyard` field to setup evaluation in `evaluate_ideal_setups()`
- Checks `state.graveyard` Counter for card presence
- All three conditions (cards, colors, graveyard) must be met for success

### Location
- File: `madness.py` lines 42-78
- Function: `evaluate_ideal_setups(state, config)`

### Logic
```python
graveyard_ok = all(
    card in state.graveyard and state.graveyard[card] > 0
    for card in required_in_graveyard
)
```

## Benefits

✅ **Answer Key Questions:**
- "How often is Wonder active?" → 20.6%
- "Can I flashback Roar reliably?" → 12.1%
- "Do I mill enough cards?" → Check graveyard size

✅ **Optimize Deck:**
- Too low Wonder rate? Add more discard outlets
- Too low Roar rate? Add more self-mill
- High graveyard rate? Good for threshold/flashback strategies

✅ **Compare Strategies:**
- Test different discard outlet counts
- Evaluate mulligan impact on graveyard setups
- Measure speed of graveyard filling

## Future Enhancements

Potential additions:
- Track HOW cards entered graveyard (discarded vs milled vs cast)
- Turn-by-turn graveyard snapshots
- Graveyard threshold tracking (7+ cards)
- Flashback timing analysis (which turn was it cast)

