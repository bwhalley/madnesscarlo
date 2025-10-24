# Quick Guide: `requires_in_graveyard` Feature

## What Changed

Added a new field to ideal setups: **`requires_in_graveyard`**

This lets you track when specific cards are **in your graveyard** by a certain turn.

## Why This Matters

For graveyard-dependent strategies like:
- **Wonder** → Need it in graveyard for flying
- **Roar of the Wurm** → Need it in graveyard for flashback
- **Squee** → Want it in graveyard early for recursion

## Configuration Example

### Before (Only tracked if you SAW the card)
```json
{
  "name": "Wonder Graveyard",
  "requires_cards": ["Wonder"],
  "requires_colors": ["U"],
  "turn_limit": 4
}
```
Result: 49% success (just seeing Wonder by turn 4)

### After (Tracks if it's IN GRAVEYARD)
```json
{
  "name": "Wonder in Graveyard",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_colors": [],
  "turn_limit": 4
}
```
Result: 20.6% success (saw it AND got it into graveyard by turn 4)

## Real Results (1000 games)

| Setup | Success % | Meaning |
|-------|-----------|---------|
| Wonder in Graveyard | 20.6% | Flying active ~1 in 5 games |
| Roar Flashback Available | 12.1% | Can cast 6/6 token ~1 in 8 games |
| Survival Engine | 31.5% | Both pieces online |

## How To Use

### 1. Edit `simulation_config.json`

Add or modify ideal setups with the `requires_in_graveyard` field:

```json
{
  "ideal_setups": [
    {
      "name": "Wonder in Graveyard",
      "requires_cards": ["Wonder"],
      "requires_in_graveyard": ["Wonder"],
      "requires_colors": [],
      "turn_limit": 4
    }
  ]
}
```

### 2. Run Simulation

```bash
python madness.py --runs 1000 --turns 4
```

### 3. Check Results

Look at the "Ideal Setups" sheet in `simulation_results.xlsx`

## Field Reference

| Field | Purpose | Example |
|-------|---------|---------|
| `requires_cards` | Card must be SEEN by turn X | `["Wonder"]` |
| `requires_in_graveyard` | Card must be IN GRAVEYARD | `["Wonder"]` |
| `requires_colors` | Mana colors available by turn X | `["U", "G"]` |
| `turn_limit` | Turn to evaluate by | `4` |

**All conditions must be true for setup success!**

## Common Patterns

### Pattern 1: Card in Graveyard Only
For cards that need to be in graveyard (Wonder):
```json
{
  "name": "Wonder in Graveyard",
  "requires_cards": ["Wonder"],
  "requires_in_graveyard": ["Wonder"],
  "requires_colors": [],
  "turn_limit": 4
}
```

### Pattern 2: Card in Graveyard + Mana
For flashback spells (Roar):
```json
{
  "name": "Roar Flashback Available",
  "requires_cards": ["Roar of the Wurm"],
  "requires_in_graveyard": ["Roar of the Wurm"],
  "requires_colors": ["G"],
  "turn_limit": 4
}
```

### Pattern 3: Multiple Cards in Graveyard
For complex setups:
```json
{
  "name": "Threshold Active",
  "requires_cards": ["Wonder", "Roar of the Wurm"],
  "requires_in_graveyard": ["Wonder", "Roar of the Wurm"],
  "requires_colors": ["G", "U"],
  "turn_limit": 4
}
```

### Pattern 4: Early Recursion
For recursive cards (Squee):
```json
{
  "name": "Squee Recursion Ready",
  "requires_cards": ["Squee, Goblin Nabob"],
  "requires_in_graveyard": ["Squee, Goblin Nabob"],
  "requires_colors": [],
  "turn_limit": 2
}
```

## Tips

✅ **Empty arrays are fine**: If you don't need a requirement, use `[]`
- `"requires_colors": []` if mana doesn't matter
- `"requires_in_graveyard": []` for normal setups

✅ **Use for optimization**: 
- Low success %? Add more discard outlets
- High graveyard %? Good for threshold strategies

✅ **Combine with other data**:
- Check "Graveyard Stats" sheet for raw percentages
- Check "Madness Casts" for discard efficiency
- Check "Flashback Casts" for usage vs availability

## Troubleshooting

**Q: My setup shows 0% success?**
- Check spelling of card names (must match deck.csv exactly)
- Verify the card has discard outlets to reach graveyard
- Try increasing turn_limit

**Q: Graveyard % higher than setup %?**
- Normal! Setup requires seeing the card early
- Some cards reach graveyard but weren't drawn yet

**Q: Setup % higher than flashback casts?**
- Normal! Setup tracks availability, not usage
- Simulator may not always cast available flashback spells

## Next Steps

Now that graveyard tracking is working, you can:
1. Optimize discard outlet density
2. Test mulligan strategy impact on graveyard setups
3. Evaluate speed of getting key cards into graveyard
4. Compare different deck configurations

Happy brewing! 🧪

