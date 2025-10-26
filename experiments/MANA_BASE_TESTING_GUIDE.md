# Mana Base Optimization Guide

## Goal
Find the optimal 21-land configuration split between:
- **Island** (produces U)
- **Forest** (produces G)
- **Yavimaya Coast** (produces U or G, 4 copies max)
- **Cephalid Coliseum** (colorless utility land)

**Casting Requirements:**
- Survival of the Fittest: 1G (needs 1 green source)
- Counterspell: UU (needs 2 blue sources early)

**Optimization Goals:**
- Minimize mulligans
- Ensure reliable G for Survival
- Ensure reliable UU for Counterspell

---

## Recommended Testing Approach

### Phase 1: Test Island/Forest Ratio (Simple)

**Config:** `mana_base_simple.json`

This tests the core Island/Forest split while keeping Yavimaya Coast (4) and Cephalid Coliseum (1) constant.

```bash
python madness.py --experiment experiments/mana_base_simple.json --runs 1500
```

**What it tests:**
- 7 Islands / 13 Forests (+ 4 Coast + 1 Coliseum = 25 total - wait, this won't work)

**Important:** Make sure your baseline `deck.csv` has:
- 9 Islands
- 7 Forests
- 4 Yavimaya Coast
- 1 Cephalid Coliseum
- (Total: 21 lands)

This will test: 7I, 8I, 9I, 10I, 11I, 12I (with Forest compensating to keep 21 total).

---

### Phase 2: Manual Variant Testing

For testing dual land counts, you'll need to manually create variant deck files:

#### Create Test Variants:

**Variant 1: Blue-Heavy (for reliable UU)**
```bash
cp deck.csv deck_blue_heavy.csv
# Edit to: 11 Island, 6 Forest, 0 Coliseum, 4 Coast
```

**Variant 2: Green-Heavy (for reliable G)**
```bash
cp deck.csv deck_green_heavy.csv
# Edit to: 8 Island, 9 Forest, 0 Coliseum, 4 Coast
```

**Variant 3: Max Duals**
```bash
cp deck.csv deck_max_duals.csv
# Edit to: 7 Island, 6 Forest, 1 Coliseum, 7 Coast
```

**Variant 4: No Coliseum**
```bash
cp deck.csv deck_no_coliseum.csv
# Edit to: 9 Island, 8 Forest, 0 Coliseum, 4 Coast
```

#### Compare Variants:

```bash
# Compare baseline vs blue-heavy
python madness.py --compare deck.csv deck_blue_heavy.csv --runs 1500

# Compare baseline vs green-heavy
python madness.py --compare deck.csv deck_green_heavy.csv --runs 1500

# Compare baseline vs max duals
python madness.py --compare deck.csv deck_max_duals.csv --runs 1500

# Compare baseline vs no coliseum
python madness.py --compare deck.csv deck_no_coliseum.csv --runs 1500
```

---

## Recommended Starting Points

Based on typical UG Madness builds, here are suggested configurations to test:

### Configuration A: Blue-Focused (Reliable Counterspell)
```
11 Island
6 Forest
4 Yavimaya Coast
0 Cephalid Coliseum
= 21 lands, 15 blue sources, 10 green sources
```
**Pros:** Very reliable UU for Counterspell
**Cons:** Less green sources for Survival

### Configuration B: Balanced
```
9 Island
7 Forest
4 Yavimaya Coast
1 Cephalid Coliseum
= 21 lands, 13 blue sources, 11 green sources
```
**Pros:** Good balance, utility land
**Cons:** Coliseum is colorless early

### Configuration C: Green-Focused (Reliable Survival)
```
8 Island
9 Forest
4 Yavimaya Coast
0 Cephalid Coliseum
= 21 lands, 12 blue sources, 13 green sources
```
**Pros:** Very reliable G for Survival
**Cons:** Slightly less reliable UU

### Configuration D: Maximum Flexibility
```
7 Island
6 Forest
7 Yavimaya Coast
1 Cephalid Coliseum
= 21 lands, 14 blue sources, 13 green sources
```
**Pros:** Maximum dual lands for flexibility
**Cons:** Life loss from Coast, fewer basics

---

## Quick Workflow

### Step 1: Run Simple Experiment
```bash
# Ensure your deck.csv has the baseline config (9I, 7F, 4Y, 1C)
python madness.py --experiment experiments/mana_base_simple.json --runs 1500

# Review results
open experiment_mana_base_simple_results.xlsx
```

### Step 2: Create Top 2-3 Variant Files
Based on the results, create manual variant files for the top configurations.

### Step 3: Deep Dive Comparison
```bash
python madness.py --compare deck.csv deck_variant1.csv --runs 2000
```

### Step 4: Iterate
- Check mulligan rates
- Check Survival Engine success %
- Check color access stats
- Apply the best configuration

---

## What to Look For in Results

### In Excel Output:

**Sheet: Summary**
- `Average Mulligans` - Lower is better
- `Survival Engine Success %` - Higher is better

**Sheet: Key Card Stats**
- `Survival of the Fittest` - "Seen % (Turn ≤4)" should be high
- Check if you're seeing it but can't cast it (indicates color problems)

**Sheet: Opening Hands**
- Look for patterns with high mulligan rates
- Identify hands with too many/few lands of each color

**Sheet: Comparison (when using --compare)**
- Direct before/after delta on mulligan rate
- Impact on ideal setup success rates

---

## Expected Results

Typical findings:
- **Too many Islands (12+):** Increases mulligans, reduces Survival reliability
- **Too few Islands (7-):** Makes Counterspell unreliable, increases mulligans
- **Optimal range:** Usually 8-10 Islands with current meta
- **Yavimaya Coast sweet spot:** 4-6 copies balances flexibility vs life loss
- **Cephalid Coliseum:** 0-1 copies (great late, awkward early)

---

## Advanced: Testing Dual Land Counts

To test different Yavimaya Coast counts, create a separate experiment:

**File: `mana_base_duals.json`**
```json
{
  "experiment_name": "mana_base_duals",
  "base_deck": "deck.csv",
  "runs_per_variant": 1500,
  "optimization_goal": "minimize_mulligans",
  "secondary_goals": ["maximize_survival_engine"],
  "experiments": [
    {
      "type": "replace_quantity",
      "card": "Yavimaya Coast",
      "test_quantities": [2, 3, 4, 5, 6, 7],
      "compensate_with": "Island"
    }
  ]
}
```

```bash
python madness.py --experiment experiments/mana_base_duals.json --runs 1500
```

---

## Tips

1. **Start with 1500 runs** - Good balance of speed and accuracy
2. **Run finals with 2000+ runs** - For statistical confidence on close results
3. **Test one dimension at a time** - Island/Forest first, then duals
4. **Check secondary goals** - Don't just minimize mulligans, ensure your combos work
5. **Consider the meta** - More Counterspells needed? Shift blue. More aggressive? Shift green.

---

## Questions to Answer

After testing, you should be able to answer:

- ✅ What's the optimal Island/Forest split?
- ✅ How many Yavimaya Coast should I run?
- ✅ Is Cephalid Coliseum worth it?
- ✅ What's my expected mulligan rate with the optimal config?
- ✅ How reliably can I cast Survival by turn 2-3?
- ✅ How reliably can I cast Counterspell by turn 2?

---

## Need Help?

See the main experiment documentation:
- `EXPERIMENTAL_FRAMEWORK_PROJECT_PLAN.md` - Technical details
- `experiments/README.md` - General experiment guide
- `README.md` - CLI options and usage

