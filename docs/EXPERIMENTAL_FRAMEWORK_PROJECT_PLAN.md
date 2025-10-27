# Project Plan: Experimental Deck Optimization Framework

## Executive Summary

**Goal**: Create an automated experimentation framework that tests multiple deck variations simultaneously to find the optimal configuration for achieving ideal setups.

**Value Proposition**: Instead of manually testing each variant, define experiment parameters once and let the engine automatically find the best deck configuration.

**Effort Estimate**: 4-6 hours for MVP, 10-15 hours for full feature

---

## 1. Requirements

### Functional Requirements

#### Must Have (MVP)
- [x] Define experiment parameters in configuration
- [x] Specify "slots" (flexible card positions) and alternatives
- [x] Generate all valid deck variations
- [x] Run simulations for each variant in parallel
- [x] Rank variants by ideal setup success rates
- [x] Export comparison of top N variants
- [x] CLI interface: `--experiment <name>`

#### Should Have (Phase 2)
- [ ] Multi-objective optimization (balance multiple goals)
- [ ] Constraint validation (e.g., max 4 copies per card)
- [ ] Incremental experiments (start from best, explore nearby)
- [ ] Statistical confidence intervals
- [ ] Pareto frontier analysis (trade-off visualization)
- [ ] Experiment history tracking

#### Nice to Have (Future)
- [ ] Genetic algorithm for large search spaces
- [ ] Machine learning to predict promising variants
- [ ] Interactive web UI for experiment design
- [ ] Cloud-based parallel execution
- [ ] Meta-experiments (optimize experiment parameters)

### Non-Functional Requirements
- Performance: Handle 50+ variants efficiently
- Usability: Simple configuration format
- Scalability: Parallelizable across cores/machines
- Reproducibility: Deterministic results with seed
- Documentation: Clear examples for common experiments

---

## 2. Use Cases & Examples

### Use Case 1: Land Count Optimization
**Goal**: Find optimal land count to minimize mulligans

```json
{
  "experiment_name": "land_count_optimization",
  "base_deck": "deck.csv",
  "runs_per_variant": 1000,
  "optimization_goal": "minimize_mulligans",
  "experiments": [
    {
      "type": "replace_quantity",
      "card": "Forest",
      "test_quantities": [6, 7, 8, 9],
      "compensate_with": "Island"
    }
  ]
}
```

**Output**: "8 Forest optimal: 0.38 avg mulligans (vs 0.45 baseline)"

### Use Case 2: Card Draw Engine Testing
**Goal**: Test different card draw spells

```json
{
  "experiment_name": "card_draw_comparison",
  "base_deck": "deck.csv",
  "optimization_goal": "maximize_survival_engine",
  "experiments": [
    {
      "type": "slot_testing",
      "slots": [
        {"card": "Careful Study", "quantity": 2}
      ],
      "alternatives": [
        {"card": "Deep Analysis", "quantity": 2},
        {"card": "Brainstorm", "quantity": 2},
        {"card": "Frantic Search", "quantity": 3},
        {"card": "Keep both", "quantity": 0}
      ]
    }
  ]
}
```

**Output**: "Best: Brainstorm (2) - 52.3% Survival Engine (+4.4%)"

### Use Case 3: Color Base Optimization
**Goal**: Reduce color mismatch issues

```json
{
  "experiment_name": "mana_base_tuning",
  "optimization_goal": "maximize_color_access",
  "experiments": [
    {
      "type": "land_ratio",
      "total_lands": 20,
      "forest_range": [5, 9],
      "island_range": [7, 11],
      "dual_lands": {"Yavimaya Coast": 4}
    }
  ]
}
```

### Use Case 4: Creature Density
**Goal**: Find optimal creature count for Survival Engine

```json
{
  "experiment_name": "creature_density",
  "optimization_goal": "maximize_survival_engine",
  "experiments": [
    {
      "type": "slot_testing",
      "slots": [
        {"card": "Wild Mongrel", "quantity": 1}
      ],
      "alternatives": [
        {"card": "Basking Rootwalla", "quantity": 1},
        {"card": "Wonder", "quantity": 1},
        {"card": "Waterfront Bouncer", "quantity": 1},
        {"card": "Remove slot", "quantity": 0}
      ]
    }
  ]
}
```

### Use Case 5: Multi-Slot Optimization
**Goal**: Test combinations of changes

```json
{
  "experiment_name": "multi_slot_test",
  "optimization_goal": "maximize_survival_engine",
  "experiments": [
    {
      "type": "combinatorial",
      "max_combinations": 20,
      "slots": [
        {
          "name": "slot1",
          "baseline": {"card": "Naturalize", "quantity": 2},
          "alternatives": [
            {"card": "Naturalize", "quantity": 1},
            {"card": "Naturalize", "quantity": 3}
          ]
        },
        {
          "name": "slot2",
          "baseline": {"card": "Counterspell", "quantity": 3},
          "alternatives": [
            {"card": "Counterspell", "quantity": 2},
            {"card": "Counterspell", "quantity": 4}
          ]
        }
      ]
    }
  ]
}
```

---

## 3. Technical Architecture

### 3.1 System Design

```
┌─────────────────────────────────────────────────────────┐
│                  CLI Interface                          │
│  python madness.py --experiment land_count_optimization │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           Experiment Controller                         │
│  • Load experiment config                               │
│  • Validate parameters                                  │
│  • Generate all variants                                │
│  • Orchestrate simulations                              │
│  • Rank results                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           Variant Generator                             │
│  • Create deck variations from config                   │
│  • Apply constraints (4x limit, 60 cards)               │
│  • Save variant CSVs                                    │
│  • Track variant metadata                               │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Variant 1    │  │ Variant N    │
│ Simulation   │  │ Simulation   │
│ (parallel)   │  │ (parallel)   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│              Results Analyzer                           │
│  • Collect all simulation results                       │
│  • Rank by optimization goal                            │
│  • Calculate statistical significance                   │
│  • Generate insights                                    │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Excel Output │  │  MD Report   │
└──────────────┘  └──────────────┘
```

### 3.2 Data Structures

```python
ExperimentConfig = {
    "experiment_name": str,
    "base_deck": str,  # Path to baseline deck
    "runs_per_variant": int,
    "optimization_goal": str,  # Primary metric to optimize
    "secondary_goals": [str],  # Additional metrics to track
    "constraints": {
        "max_copies": int,
        "deck_size": int,
        "budget": float  # Optional price constraint
    },
    "experiments": [ExperimentDefinition]
}

ExperimentDefinition = {
    "type": str,  # replace_quantity, slot_testing, land_ratio, combinatorial
    "card": str,  # For replace_quantity
    "test_quantities": [int],  # For replace_quantity
    "compensate_with": str,  # Card to add/remove to maintain deck size
    "slots": [Slot],  # For slot_testing/combinatorial
    "alternatives": [CardSpec]
}

Slot = {
    "name": str,
    "baseline": CardSpec,
    "alternatives": [CardSpec]
}

CardSpec = {
    "card": str,
    "quantity": int
}

Variant = {
    "id": str,
    "name": str,
    "deck_path": str,
    "changes": [Change],
    "metadata": dict
}

Change = {
    "type": str,  # "add", "remove", "modify"
    "card": str,
    "baseline_qty": int,
    "variant_qty": int,
    "delta": int
}

ExperimentResults = {
    "experiment_name": str,
    "baseline_results": SimulationResults,
    "variants": [VariantResults],
    "ranking": [VariantRanking],
    "insights": [str]
}

VariantResults = {
    "variant": Variant,
    "results": SimulationResults,
    "scores": {
        "primary_goal": float,
        "secondary_goals": {goal: float}
    },
    "deltas_from_baseline": {metric: float}
}

VariantRanking = {
    "rank": int,
    "variant_id": str,
    "variant_name": str,
    "primary_score": float,
    "delta_from_baseline": float,
    "confidence": float,  # Statistical confidence
    "recommendation": str  # "Strong", "Moderate", "Weak", "Not Recommended"
}
```

---

## 4. Implementation Plan

### Phase 1: Core Framework (MVP)

#### Step 1: Experiment Configuration
**New File**: `experiment_config.py`

```python
class ExperimentConfig:
    """Configuration for deck optimization experiment."""
    
    def __init__(self, config_dict):
        self.name = config_dict["experiment_name"]
        self.base_deck = config_dict["base_deck"]
        self.runs_per_variant = config_dict.get("runs_per_variant", 1000)
        self.optimization_goal = config_dict["optimization_goal"]
        self.experiments = config_dict["experiments"]
        self.constraints = config_dict.get("constraints", {})
    
    def validate(self):
        """Validate experiment configuration."""
        # Check base deck exists
        # Validate experiment types
        # Check for conflicts
        pass

def load_experiment_config(config_path):
    """Load experiment from JSON file."""
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    config = ExperimentConfig(config_dict)
    config.validate()
    return config
```

#### Step 2: Variant Generation
**New File**: `variant_generator.py`

```python
def generate_variants(base_deck_path, experiment_config):
    """
    Generate all deck variants from experiment config.
    
    Returns:
        List of Variant objects
    """
    base_deck = pd.read_csv(base_deck_path)
    variants = []
    
    for exp in experiment_config.experiments:
        if exp["type"] == "replace_quantity":
            variants.extend(generate_quantity_variants(base_deck, exp))
        elif exp["type"] == "slot_testing":
            variants.extend(generate_slot_variants(base_deck, exp))
        elif exp["type"] == "land_ratio":
            variants.extend(generate_land_variants(base_deck, exp))
        elif exp["type"] == "combinatorial":
            variants.extend(generate_combinatorial_variants(base_deck, exp))
    
    return variants

def generate_quantity_variants(base_deck, exp):
    """Generate variants with different quantities of a card."""
    variants = []
    card = exp["card"]
    compensate = exp.get("compensate_with")
    
    for qty in exp["test_quantities"]:
        variant_deck = base_deck.copy()
        
        # Update card quantity
        variant_deck.loc[variant_deck['Card Name'] == card, 'Quantity'] = qty
        
        # Compensate to maintain deck size
        if compensate:
            baseline_qty = base_deck[base_deck['Card Name'] == card]['Quantity'].values[0]
            delta = qty - baseline_qty
            current_comp = variant_deck[variant_deck['Card Name'] == compensate]['Quantity'].values[0]
            variant_deck.loc[variant_deck['Card Name'] == compensate, 'Quantity'] = current_comp - delta
        
        variant = create_variant(variant_deck, f"{card}_{qty}", exp)
        variants.append(variant)
    
    return variants

def generate_slot_variants(base_deck, exp):
    """Generate variants by swapping cards in/out of slots."""
    variants = []
    slots = exp["slots"]
    alternatives = exp["alternatives"]
    
    for alt in alternatives:
        variant_deck = base_deck.copy()
        
        # Remove cards from slots
        for slot in slots:
            variant_deck = remove_or_reduce_card(variant_deck, slot["card"], slot["quantity"])
        
        # Add alternative
        if alt.get("quantity", 0) > 0:
            variant_deck = add_or_increase_card(variant_deck, alt["card"], alt["quantity"])
        
        variant = create_variant(variant_deck, f"slot_{alt['card']}", exp)
        variants.append(variant)
    
    return variants

def generate_combinatorial_variants(base_deck, exp):
    """Generate all combinations of slot alternatives."""
    from itertools import product
    
    slots = exp["slots"]
    max_combinations = exp.get("max_combinations", 50)
    
    # Get all alternatives for each slot
    slot_alternatives = []
    for slot in slots:
        alternatives = [slot["baseline"]] + slot["alternatives"]
        slot_alternatives.append(alternatives)
    
    # Generate all combinations
    combinations = list(product(*slot_alternatives))
    
    # Limit to max_combinations
    if len(combinations) > max_combinations:
        # Sample or use heuristic to select best combinations
        combinations = sample_combinations(combinations, max_combinations)
    
    variants = []
    for combo in combinations:
        variant_deck = apply_combination(base_deck, slots, combo)
        variant_name = "_".join([f"{s['name']}-{c['card'][:3]}" for s, c in zip(slots, combo)])
        variant = create_variant(variant_deck, variant_name, exp)
        variants.append(variant)
    
    return variants

def create_variant(variant_deck, name, experiment):
    """Create Variant object from deck DataFrame."""
    # Save to temp CSV
    variant_path = f"temp_variants/{name}.csv"
    variant_deck.to_csv(variant_path, index=False)
    
    # Calculate changes
    changes = calculate_changes(base_deck, variant_deck)
    
    return Variant(
        id=generate_variant_id(),
        name=name,
        deck_path=variant_path,
        changes=changes,
        metadata={"experiment_type": experiment["type"]}
    )
```

#### Step 3: Parallel Simulation Runner
**New File**: `experiment_runner.py`

```python
import multiprocessing as mp
from functools import partial

def run_experiment(config, sim_config, num_workers=None):
    """
    Run all variants of an experiment.
    
    Args:
        config: ExperimentConfig
        sim_config: Simulation config dict
        num_workers: Number of parallel workers (default: CPU count)
    
    Returns:
        ExperimentResults
    """
    if num_workers is None:
        num_workers = mp.cpu_count()
    
    # Generate variants
    variants = generate_variants(config.base_deck, config)
    
    print(f"Generated {len(variants)} variants")
    print(f"Running {config.runs_per_variant} simulations per variant")
    print(f"Total simulations: {len(variants) * config.runs_per_variant}")
    print(f"Using {num_workers} parallel workers\n")
    
    # Run baseline
    baseline_results = run_simulations(config.base_deck, config.runs_per_variant, 4, sim_config)
    
    # Run variants in parallel
    with mp.Pool(num_workers) as pool:
        sim_func = partial(
            run_variant_simulation,
            runs=config.runs_per_variant,
            turns=4,
            config=sim_config
        )
        
        variant_results = pool.map(sim_func, variants)
    
    # Analyze results
    experiment_results = analyze_experiment_results(
        config,
        baseline_results,
        variants,
        variant_results
    )
    
    return experiment_results

def run_variant_simulation(variant, runs, turns, config):
    """Run simulation for a single variant."""
    from madness import run_simulations
    
    results = run_simulations(variant.deck_path, runs, turns, config)
    
    return {
        'variant': variant,
        'results': results
    }
```

#### Step 4: Results Analysis & Ranking
**New File**: `experiment_analyzer.py`

```python
def analyze_experiment_results(config, baseline_results, variants, variant_results):
    """Analyze and rank experiment results."""
    
    # Extract optimization goal scores
    rankings = []
    for variant, results in zip(variants, variant_results):
        score = extract_goal_score(results['results'], config.optimization_goal)
        baseline_score = extract_goal_score(baseline_results, config.optimization_goal)
        
        rankings.append({
            'variant': variant,
            'results': results['results'],
            'score': score,
            'delta': score - baseline_score,
            'delta_pct': ((score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
        })
    
    # Sort by score
    if config.optimization_goal.startswith("minimize"):
        rankings.sort(key=lambda x: x['score'])
    else:
        rankings.sort(key=lambda x: x['score'], reverse=True)
    
    # Add ranking position
    for i, r in enumerate(rankings):
        r['rank'] = i + 1
        r['recommendation'] = generate_recommendation(r['delta'], r['delta_pct'])
    
    return ExperimentResults(
        experiment_name=config.name,
        baseline_results=baseline_results,
        variants=variant_results,
        rankings=rankings,
        insights=generate_insights(config, rankings)
    )

def extract_goal_score(results, optimization_goal):
    """Extract the metric value for the optimization goal."""
    if optimization_goal == "maximize_survival_engine":
        # Extract Survival Engine success rate from ideal_setups_df
        setup_df = results[2]  # ideal_setups_df
        return setup_df[setup_df['Setup'] == 'Survival Engine']['Success %'].values[0]
    
    elif optimization_goal == "minimize_mulligans":
        # Extract average mulligans from summary
        return results[10]['Average Mulligans']  # summary dict
    
    elif optimization_goal == "maximize_color_access":
        # Calculate average color access across key cards
        key_df = results[1]  # key_card_stats_df
        return key_df['Seen % (Turn ≤4)'].mean()
    
    # Add more goals as needed
    return 0.0

def generate_recommendation(delta, delta_pct):
    """Generate recommendation based on improvement magnitude."""
    if delta_pct > 10:
        return "Strong"
    elif delta_pct > 5:
        return "Moderate"
    elif delta_pct > 2:
        return "Weak"
    elif delta_pct < -5:
        return "Not Recommended"
    else:
        return "Neutral"

def generate_insights(config, rankings):
    """Generate insights from experiment results."""
    insights = []
    
    # Top performer
    top = rankings[0]
    insights.append(f"Best variant: {top['variant'].name} (+{top['delta']:.2f}, +{top['delta_pct']:.1f}%)")
    
    # Count improvements
    improvements = sum(1 for r in rankings if r['delta'] > 0)
    insights.append(f"{improvements}/{len(rankings)} variants improved over baseline")
    
    # Identify patterns
    # ... analyze what types of changes worked best
    
    return insights
```

#### Step 5: Export Results
**New File**: `export_experiment.py`

```python
def export_experiment_results(experiment_results, output_file):
    """Export experiment results to Excel."""
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_df = create_experiment_summary(experiment_results)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Rankings
        rankings_df = create_rankings_table(experiment_results)
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 3: Variant Details
        details_df = create_variant_details(experiment_results)
        details_df.to_excel(writer, sheet_name='Variant Details', index=False)
        
        # Sheet 4: Top 5 Comparison
        top5_df = create_top_variants_comparison(experiment_results, n=5)
        top5_df.to_excel(writer, sheet_name='Top 5 Comparison', index=False)
        
        # Sheet 5: Statistical Analysis
        stats_df = create_statistical_analysis(experiment_results)
        stats_df.to_excel(writer, sheet_name='Statistical Analysis', index=False)

def create_rankings_table(experiment_results):
    """Create rankings table for export."""
    rows = []
    
    for ranking in experiment_results.rankings:
        variant = ranking['variant']
        
        # Get card changes summary
        changes_summary = format_changes(variant.changes)
        
        rows.append({
            'Rank': ranking['rank'],
            'Variant Name': variant.name,
            'Score': ranking['score'],
            'Baseline Score': ranking['score'] - ranking['delta'],
            'Delta': ranking['delta'],
            'Delta %': ranking['delta_pct'],
            'Recommendation': ranking['recommendation'],
            'Changes': changes_summary
        })
    
    return pd.DataFrame(rows)
```

---

## 5. CLI Interface Design

### Basic Experiment
```bash
python madness.py --experiment land_count_optimization
```

### With Custom Config
```bash
python madness.py --experiment-config experiments/my_experiment.json \
  --runs-per-variant 2000 \
  --output experiment_results.xlsx
```

### Parallel Workers
```bash
python madness.py --experiment land_count_optimization \
  --workers 8 \
  --runs-per-variant 1000
```

### Resume Interrupted Experiment
```bash
python madness.py --experiment land_count_optimization --resume
```

---

## 6. Configuration Examples

### Example 1: Simple Land Count Test

**File**: `experiments/land_count.json`

```json
{
  "experiment_name": "land_count_optimization",
  "base_deck": "deck.csv",
  "runs_per_variant": 1000,
  "optimization_goal": "minimize_mulligans",
  "secondary_goals": ["maximize_survival_engine"],
  "experiments": [
    {
      "type": "replace_quantity",
      "card": "Forest",
      "test_quantities": [5, 6, 7, 8, 9, 10],
      "compensate_with": "Island"
    }
  ]
}
```

### Example 2: Card Draw Spell Comparison

**File**: `experiments/card_draw.json`

```json
{
  "experiment_name": "card_draw_optimization",
  "base_deck": "deck.csv",
  "runs_per_variant": 2000,
  "optimization_goal": "maximize_survival_engine",
  "experiments": [
    {
      "type": "slot_testing",
      "slots": [
        {"card": "Careful Study", "quantity": 2}
      ],
      "alternatives": [
        {"card": "Baseline", "quantity": 0},
        {"card": "Deep Analysis", "quantity": 2},
        {"card": "Brainstorm", "quantity": 2},
        {"card": "Frantic Search", "quantity": 1},
        {"card": "Ideas Unbound", "quantity": 2}
      ]
    }
  ]
}
```

### Example 3: Multi-Dimensional Optimization

**File**: `experiments/multi_slot.json`

```json
{
  "experiment_name": "multi_slot_optimization",
  "base_deck": "deck.csv",
  "runs_per_variant": 1500,
  "optimization_goal": "maximize_survival_engine",
  "secondary_goals": ["minimize_mulligans", "maximize_counter_protection"],
  "experiments": [
    {
      "type": "combinatorial",
      "max_combinations": 25,
      "slots": [
        {
          "name": "removal_slot",
          "baseline": {"card": "Naturalize", "quantity": 3},
          "alternatives": [
            {"card": "Naturalize", "quantity": 2},
            {"card": "Naturalize", "quantity": 4},
            {"card": "Krosan Grip", "quantity": 3}
          ]
        },
        {
          "name": "creature_slot",
          "baseline": {"card": "Wild Mongrel", "quantity": 4},
          "alternatives": [
            {"card": "Wild Mongrel", "quantity": 3},
            {"card": "Merfolk Looter", "quantity": 4}
          ]
        }
      ]
    }
  ]
}
```

---

## 7. Output Format

### Terminal Output
```
$ python madness.py --experiment land_count_optimization --workers 4

╔══════════════════════════════════════════════════════════╗
║         EXPERIMENT: Land Count Optimization              ║
╚══════════════════════════════════════════════════════════╝

Configuration:
  Base Deck: deck.csv
  Optimization Goal: Minimize Mulligans
  Runs per Variant: 1000
  Total Variants: 6

Generating variants...
  ✓ 6 variants generated

Running simulations...
  [=====>                    ] 25% (250/1000) Variant 2/6
  
Baseline Results:
  Average Mulligans: 0.45
  Survival Engine: 47.2%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPERIMENT RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rank  Variant         Score  Delta    Δ%     Recommendation
────────────────────────────────────────────────────────────
  1   Forest_8        0.38   -0.07   -15.6%  ✅ Strong
  2   Forest_7        0.39   -0.06   -13.3%  ✅ Strong
  3   Forest_9        0.42   -0.03    -6.7%  ⚖️  Moderate
  4   Forest_6        0.44   -0.01    -2.2%  ⚠️  Weak
  5   Forest_10       0.47   +0.02    +4.4%  ❌ Not Recommended
  6   Forest_5        0.53   +0.08   +17.8%  ❌ Not Recommended

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Best variant: Forest_8 (-0.07, -15.6%)
✅ 4/6 variants improved over baseline
⚠️  Secondary goal (Survival Engine) declined 1.2% in best variant

RECOMMENDATION: Switch to Forest_8 configuration
  • Reduces mulligans by 15.6%
  • Trade-off: Slight decline in Survival Engine success
  • Net impact: Positive (more consistent opening hands)

Results exported to: experiment_land_count_results.xlsx
```

---

## 8. Advanced Features (Phase 2+)

### Multi-Objective Optimization

```python
def pareto_frontier_analysis(variants, goals):
    """
    Find Pareto-optimal variants (no variant strictly dominates).
    
    Useful when optimizing multiple conflicting goals.
    """
    pareto_front = []
    
    for v1 in variants:
        dominated = False
        for v2 in variants:
            if v1 == v2:
                continue
            
            # Check if v2 dominates v1
            if all(v2.scores[g] >= v1.scores[g] for g in goals) and \
               any(v2.scores[g] > v1.scores[g] for g in goals):
                dominated = True
                break
        
        if not dominated:
            pareto_front.append(v1)
    
    return pareto_front
```

### Incremental Optimization

```python
def incremental_experiment(base_variant, search_radius):
    """
    Start from best known variant, explore nearby configurations.
    
    Useful for fine-tuning after initial broad search.
    """
    # Generate variants within search_radius of base_variant
    # Run experiment
    # If improvement found, use as new base and repeat
    pass
```

### Genetic Algorithm

```python
def genetic_optimization(config, generations=10, population_size=20):
    """
    Use genetic algorithm for large search spaces.
    
    Evolution steps:
    1. Initialize random population
    2. Evaluate fitness (simulation)
    3. Select best performers
    4. Crossover (combine deck features)
    5. Mutate (random changes)
    6. Repeat
    """
    pass
```

---

## 9. Performance Considerations

### Parallel Execution
- Use multiprocessing for CPU-bound simulations
- Distribute variants across worker processes
- Consider cloud execution for 100+ variants

### Caching
- Cache simulation results by deck hash
- Reuse results if identical variant tested before
- Persist cache to disk for resumable experiments

### Smart Sampling
- For large combinatorial spaces, sample intelligently
- Use Latin Hypercube Sampling for coverage
- Prioritize variants likely to succeed based on heuristics

---

## 10. Validation & Testing

### Unit Tests
```python
def test_variant_generation():
    """Test generating variants from config."""
    config = {...}
    variants = generate_variants("deck.csv", config)
    assert len(variants) == expected_count

def test_constraint_validation():
    """Test deck constraints are enforced."""
    variant = generate_variant_with_5_copies()
    assert not validate_constraints(variant)

def test_combinatorial_limits():
    """Test max_combinations respected."""
    config = {"max_combinations": 10}
    variants = generate_combinatorial_variants(config)
    assert len(variants) <= 10
```

### Integration Tests
```python
def test_full_experiment_workflow():
    """Test complete experiment from config to export."""
    results = run_experiment("experiments/test.json")
    assert len(results.rankings) > 0
    assert results.rankings[0]['rank'] == 1
```

---

## 11. Documentation Needs

### User Guide
- `EXPERIMENTAL_FRAMEWORK_GUIDE.md` - Complete usage guide
- `EXPERIMENT_COOKBOOK.md` - Common experiment recipes
- README section on experimentation

### API Documentation
- Docstrings for all public functions
- Configuration schema reference
- Example experiments library

---

## 12. Risks & Mitigation

### Risk 1: Combinatorial Explosion
**Problem**: Multi-slot experiments can generate thousands of variants

**Mitigation**:
- Enforce `max_combinations` limit
- Use sampling strategies
- Provide warnings when combinations > threshold
- Suggest incremental approach

### Risk 2: Long Execution Time
**Problem**: 100 variants × 1000 runs = 100,000 simulations

**Mitigation**:
- Default to fewer runs_per_variant (500)
- Show estimated completion time upfront
- Allow resuming interrupted experiments
- Support distributed execution

### Risk 3: Misleading Results
**Problem**: Statistical noise could favor suboptimal variants

**Mitigation**:
- Require minimum sample size per variant
- Calculate confidence intervals
- Flag results with low confidence
- Recommend validation testing

### Risk 4: Configuration Errors
**Problem**: Invalid experiment configs could crash

**Mitigation**:
- Comprehensive validation on load
- Clear error messages
- Dry-run mode to preview variants
- Example configs included

---

## 13. Success Metrics

### MVP Success Criteria
- ✅ Generate 20+ variants from config
- ✅ Run experiment in < 5 minutes (20 variants, 500 runs)
- ✅ Correctly rank variants by optimization goal
- ✅ Export results to Excel with rankings
- ✅ All tests pass

### User Success Criteria
- ✅ Find optimal land count in single command
- ✅ Test 5+ card alternatives efficiently
- ✅ Understand which changes helped/hurt
- ✅ Make data-driven deck decisions
- ✅ Iterate on findings with new experiments

---

## 14. Timeline Estimate

### Phase 1 (MVP): 4-6 hours
- Hour 1-2: Configuration and variant generation
- Hour 2-3: Experiment runner with parallelization
- Hour 3-4: Results analysis and ranking
- Hour 4-5: Export functionality
- Hour 5-6: CLI integration, testing, docs

### Phase 2 (Advanced): 4-6 hours
- Multi-objective optimization
- Statistical analysis
- Pareto frontier
- Incremental experiments
- Comprehensive testing

### Phase 3 (Polish): 2-3 hours
- Genetic algorithms
- Cloud execution support
- Web UI mockup
- Advanced visualizations

**Total MVP to Production**: 10-15 hours

---

## 15. Next Steps After Approval

1. Create feature branch
2. Implement variant generation
3. Build experiment runner
4. Add ranking/analysis
5. Create export functionality
6. Integrate with CLI
7. Write tests
8. Create example experiments
9. Document usage
10. Merge to main

---

## 16. Example Workflow

```bash
# 1. Create experiment config
cat > experiments/optimize_lands.json << EOF
{
  "experiment_name": "land_optimization",
  "base_deck": "deck.csv",
  "runs_per_variant": 1000,
  "optimization_goal": "maximize_survival_engine",
  "experiments": [...]
}
EOF

# 2. Run experiment
python madness.py --experiment optimize_lands --workers 4

# 3. Review results
open experiment_land_optimization_results.xlsx

# 4. Apply best variant
cp temp_variants/Forest_8.csv deck.csv

# 5. Run follow-up experiment
python madness.py --experiment fine_tune_creatures
```

---

**Status**: Draft Plan - Awaiting Approval  
**Last Updated**: 2025-10-25  
**Version**: 1.0  
**Estimated Effort**: 10-15 hours (MVP + Polish)

