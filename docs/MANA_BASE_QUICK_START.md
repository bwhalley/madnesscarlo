# Quick Start: Mana Base Optimization

## Your Question
> Find the correct makeup of lands with 21 land slots shared between Island, Forest, Cephalid Coliseum, and Yavimaya Coast to minimize mulligans and ensure we can cast Survival of the Fittest and Counterspell reliably.

## Quick Answer: Run These Commands

### Step 1: Ensure Your Baseline is Set
Make sure `deck.csv` has your current mana base. Example baseline:
- 9 Island
- 7 Forest  
- 4 Yavimaya Coast
- 1 Cephalid Coliseum
- (= 21 lands total)

### Step 2: Test Island/Forest Ratio
```bash
python madness.py --experiment experiments/mana_base_simple.json --runs 1500
```
**What it does:** Tests Island counts from 7-12, with Forest compensating to keep 21 lands total.

**Output:** `experiment_mana_base_simple_results.xlsx`

**What to check:**
- Sheet "Rankings" - See which Island count minimizes mulligans
- Sheet "Summary" - Compare average mulligans across variants
- Sheet "Insights" - Auto-generated recommendations

### Step 3: Test Dual Land Count
```bash
python madness.py --experiment experiments/mana_base_duals.json --runs 1500
```
**What it does:** Tests Yavimaya Coast counts from 2-7, with Islands compensating.

**What to check:**
- More duals = more flexibility, but life loss from pain lands
- Fewer duals = safer, but less flexible

### Step 4: Create and Test Specific Configurations

Based on Steps 2-3 results, create manual variants for fine-tuning:

```bash
# Create variant file
cp deck.csv deck_optimized.csv
# Edit deck_optimized.csv with your optimized land counts

# Compare
python madness.py --compare deck.csv deck_optimized.csv --runs 2000
```

---

## Example: Complete Workflow

```bash
# 1. Test Island/Forest balance (5 minutes)
python madness.py --experiment experiments/mana_base_simple.json --runs 1500

# 2. Review results
open experiment_mana_base_simple_results.xlsx
# Let's say 9 Islands wins

# 3. Test dual land count (5 minutes)  
python madness.py --experiment experiments/mana_base_duals.json --runs 1500

# 4. Review results
open experiment_mana_base_duals_results.xlsx
# Let's say 5 Yavimaya Coast wins

# 5. Create optimized deck with 9I, 7F, 5Y, 0C (21 total)
cp deck.csv deck_optimized.csv
# Edit deck_optimized.csv:
#   - Island: 9
#   - Forest: 7
#   - Yavimaya Coast: 5
#   - Cephalid Coliseum: 0

# 6. Validate the change (10 minutes)
python madness.py --compare deck.csv deck_optimized.csv --runs 2000

# 7. Review comparison
open comparison_results.xlsx
# Check:
#   - Did mulligans decrease? ✅
#   - Did Survival Engine % improve/stay same? ✅
#   - Is color access better? ✅

# 8. Apply if better
mv deck_optimized.csv deck.csv
```

---

## What You'll Learn

After running these experiments, you'll know:

✅ **Optimal Island count** (usually 8-10)
- Too many: Reduces green access, hurts Survival
- Too few: Can't reliably cast UU for Counterspell

✅ **Optimal Forest count** (usually 6-9)
- Balance with Islands to total ~15-17 basic lands

✅ **Optimal Yavimaya Coast count** (usually 4-6)
- More = flexibility, but life loss adds up
- Fewer = safer, but less color fixing

✅ **Cephalid Coliseum value** (usually 0-1)
- Great late game, awkward early
- Test with/without to see impact

✅ **Expected mulligan rate**
- Good manabase: 30-40% mulligan rate
- Great manabase: 25-35% mulligan rate
- Excellent manabase: 20-30% mulligan rate

✅ **Survival Engine reliability**
- Should be able to achieve >45% success by turn 4
- Manabase is key to this

---

## Interpreting Results

### In the Excel Output:

**"Rankings" Sheet:**
```
Rank  Variant      Score   Delta    Δ%      Recommendation
1     Island_9     0.32    -0.08   -20.0%   ✅ Strong
2     Island_10    0.35    -0.05   -12.5%   ✅ Strong
3     Island_8     0.37    -0.03    -7.5%   ⚖️  Moderate
```
→ **9 Islands is best!** (20% fewer mulligans)

**"Summary" Sheet:**
```
Metric                Value
Baseline Score        0.40
Best Score            0.32
Average Improvement   -0.05 (-12.5%)
```
→ **Average variant improved by 12.5%**

**"Insights" Sheet:**
```
🏆 Best variant: Island_9
   Score: 0.32 (baseline: 0.40)
   Change: -0.08 (-20.0%)
   Changes: +1 Island (from 8), -1 Forest (from 8)
```
→ **Clear recommendation with reasoning**

---

## Common Findings

Based on typical UG Madness decks:

### Island Count
- **7 Islands:** Often too few, Counterspell unreliable, higher mulligans
- **8-9 Islands:** Sweet spot for most builds
- **10+ Islands:** Survival becomes less reliable, Forest scarcity issues

### Forest Count  
- **5-6 Forests:** Minimum for reliable Survival
- **7-8 Forests:** Comfortable range
- **9+ Forests:** Possibly too many unless your deck is very green

### Yavimaya Coast
- **2-3:** Probably too few for flexible mana
- **4-5:** Sweet spot for most builds
- **6-7:** Maximum flexibility, but significant life loss

### Cephalid Coliseum
- **0 copies:** Safest, no awkward early draws
- **1 copy:** Good if you want late-game card draw
- **2+ copies:** Usually too many, hurts early mana

---

## Pro Tips

1. **Run simple tests first** - Don't jump to complex variants
2. **1500 runs is enough** for initial testing
3. **2000+ runs for finals** when comparing close options
4. **Check secondary goals** - Don't just minimize mulligans
5. **Consider your meta** - More control? Need more blue. More aggressive? Need more green.

---

## Troubleshooting

**Q: The experiment says "runs_per_variant too low"**  
A: The minimum is 100. Use at least 500 for testing, 1500+ for real results.

**Q: Results are inconsistent between runs**  
A: Run more simulations (2000+) for statistical confidence.

**Q: How do I know if a change is significant?**  
A: Look at the Delta % column. Changes >5% are meaningful, >10% are strong.

**Q: Can I test more than one thing at once?**  
A: Use the `combinatorial` type, but limit `max_combinations` to avoid explosion.

---

## Ready to Start?

```bash
# Make sure you're in the right directory
cd /path/to/madnesscarlo

# Run the first experiment
python madness.py --experiment experiments/mana_base_simple.json --runs 1500
```

Results will be in `experiment_mana_base_simple_results.xlsx`

Good luck finding your optimal mana base! 🎯

