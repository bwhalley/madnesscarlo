# Experiment Configurations

This directory contains example experiment configurations for optimizing deck performance.

## Available Experiments

### 1. Land Count Optimization (`land_count_optimization.json`)

**Goal**: Find the optimal number of Forests to minimize mulligans

**Strategy**: Test 5-10 Forests, compensating with Islands

**Usage**:
```bash
python madness.py --experiment experiments/land_count_optimization.json
```

**What it tests**: Different Forest quantities to find the sweet spot that reduces mulligans while maintaining Survival Engine success rate.

---

### 2. Card Draw Comparison (`card_draw_comparison.json`)

**Goal**: Compare card draw spells to maximize Survival Engine success

**Strategy**: Test alternative card draw spells in place of Careful Study

**Usage**:
```bash
python madness.py --experiment experiments/card_draw_comparison.json
```

**What it tests**:
- Deep Analysis (2 copies)
- Brainstorm (2 copies)
- Frantic Search (1 copy)
- Careful Study variations (1-3 copies)

---

### 3. Creature Density (`creature_density.json`)

**Goal**: Find optimal creature counts for Survival of the Fittest engine

**Strategy**: Test different combinations of Wild Mongrel and Basking Rootwalla counts

**Usage**:
```bash
python madness.py --experiment experiments/creature_density.json --runs 1500
```

**What it tests**: Combinatorial experiment testing 3-5 copies of key creatures to find the best density.

---

## Creating Your Own Experiments

### Experiment Configuration Format

```json
{
  "experiment_name": "my_experiment",
  "base_deck": "deck.csv",
  "runs_per_variant": 1000,
  "optimization_goal": "maximize_survival_engine",
  "secondary_goals": ["minimize_mulligans"],
  "experiments": [...]
}
```

### Optimization Goals

Available optimization goals:
- `maximize_survival_engine` - Increase Survival Engine ideal setup success
- `maximize_roar_flashback` - Increase Roar of the Wurm flashback success
- `maximize_wonder_flying` - Increase Wonder flying success
- `minimize_mulligans` - Reduce average mulligan count
- `maximize_color_access` - Improve key card access
- `maximize_key_card_access` - Improve overall card visibility

### Experiment Types

#### 1. Replace Quantity
Test different quantities of a single card:

```json
{
  "type": "replace_quantity",
  "card": "Forest",
  "test_quantities": [6, 7, 8, 9],
  "compensate_with": "Island"
}
```

#### 2. Slot Testing
Swap cards in and out:

```json
{
  "type": "slot_testing",
  "slots": [
    {"card": "Careful Study", "quantity": 2}
  ],
  "alternatives": [
    {"card": "Deep Analysis", "quantity": 2},
    {"card": "Brainstorm", "quantity": 2}
  ]
}
```

#### 3. Combinatorial
Test multiple changes simultaneously:

```json
{
  "type": "combinatorial",
  "max_combinations": 20,
  "slots": [
    {
      "name": "slot1",
      "baseline": {"card": "Card A", "quantity": 4},
      "alternatives": [
        {"card": "Card A", "quantity": 3},
        {"card": "Card B", "quantity": 4}
      ]
    }
  ]
}
```

### CLI Options

```bash
# Basic usage
python madness.py --experiment experiments/my_experiment.json

# With more simulations
python madness.py --experiment experiments/my_experiment.json --runs 2000

# With custom output file
python madness.py --experiment experiments/my_experiment.json --experiment-output my_results.xlsx

# With more parallel workers
python madness.py --experiment experiments/my_experiment.json --workers 8
```

### Tips for Effective Experiments

1. **Start with fewer runs** (500-1000) for quick iteration
2. **Use combinatorial sparingly** - combinations explode quickly
3. **Set max_combinations** limit for large combinatorial spaces
4. **Focus on one goal** - use secondary_goals for context only
5. **Run final tests with 2000+ runs** for statistical confidence
6. **Compare top 3 variants** manually to understand patterns

### Output

Each experiment produces:
1. **Excel file** with 6 sheets:
   - Summary: Experiment overview
   - Rankings: All variants ranked
   - Variant Details: Card-by-card changes
   - Top 5 Comparison: Side-by-side comparison
   - Statistical Analysis: Stats and distributions
   - Insights: Auto-generated recommendations

2. **Markdown summary** with key findings and recommendations

### Example Workflow

```bash
# 1. Quick test to validate config
python madness.py --experiment experiments/land_count_optimization.json --runs 500

# 2. Review results
open experiment_land_count_optimization_results.xlsx

# 3. Run full test with best parameters
python madness.py --experiment experiments/land_count_optimization.json --runs 2000

# 4. Apply changes to deck
# Edit deck.csv based on recommendations

# 5. Validate with comparison
python madness.py --compare deck_old.csv deck.csv --runs 1000
```

## Need Help?

See the main [EXPERIMENTAL_FRAMEWORK_PROJECT_PLAN.md](../EXPERIMENTAL_FRAMEWORK_PROJECT_PLAN.md) for detailed documentation.

