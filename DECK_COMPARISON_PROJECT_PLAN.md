# Project Plan: Deck Comparison Feature

## Executive Summary

**Goal**: Enable side-by-side comparison of two deck configurations to evaluate the impact of card changes on performance metrics.

**Value Proposition**: Answer questions like "Is +2 Brainstorm, -2 Naturalize actually better?" with concrete statistical evidence.

**Effort Estimate**: 3-4 hours implementation + testing

---

## 1. Requirements

### Functional Requirements

#### Must Have (MVP)
- [x] Compare two deck CSV files
- [x] Run simulations for both decks with identical parameters (runs, turns, config)
- [x] Generate side-by-side comparison of key metrics
- [x] Calculate deltas (absolute and percentage changes)
- [x] Export comparison to Excel and/or Markdown
- [x] CLI interface: `--compare baseline.csv variant.csv`

#### Should Have (Phase 2)
- [ ] Compare opening hand patterns between decks
- [ ] Identify which specific cards are different
- [ ] Statistical significance testing (p-values, confidence intervals)
- [ ] Visualize deltas (color coding for improvements/regressions)
- [ ] Support comparing more than 2 decks at once

#### Nice to Have (Future)
- [ ] Automatic optimization suggestions
- [ ] Historical comparison tracking (database of previous tests)
- [ ] Interactive web dashboard for comparison
- [ ] Integration with sideboard comparison

### Non-Functional Requirements
- Performance: Each deck simulation should run independently (parallelizable)
- Usability: Single command to compare, clear output format
- Maintainability: Reuse existing simulation engine, minimal code duplication
- Documentation: Clear examples and use cases

---

## 2. Technical Approach

### 2.1 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CLI Interface                          │
│  python madness.py --compare deck1.csv deck2.csv        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           Comparison Controller                         │
│  • Load both deck files                                 │
│  • Run simulations for each                             │
│  • Aggregate results                                    │
│  • Calculate deltas                                     │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Deck 1 Sim   │  │ Deck 2 Sim   │
│ (parallel)   │  │ (parallel)   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│              Delta Analyzer                             │
│  • Compare all metrics                                  │
│  • Calculate absolute/relative changes                  │
│  • Identify significant differences                     │
│  • Generate insights                                    │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Excel Output │  │  MD Output   │
└──────────────┘  └──────────────┘
```

### 2.2 Data Structures

```python
DeckComparison = {
    "baseline": {
        "deck_path": str,
        "deck_cards": {card: quantity},
        "results": SimulationResults
    },
    "variant": {
        "deck_path": str,
        "deck_cards": {card: quantity},
        "results": SimulationResults
    },
    "differences": {
        "cards_added": {card: quantity},
        "cards_removed": {card: quantity},
        "cards_changed": {card: (old_qty, new_qty)}
    },
    "deltas": {
        "ideal_setups": {
            setup_name: {
                "baseline": float,
                "variant": float,
                "delta": float,
                "delta_pct": float
            }
        },
        "key_cards": {...},
        "mulligans": {...},
        "opening_hands": {...}
    }
}
```

---

## 3. Implementation Plan

### Phase 1: Core Comparison Engine (MVP)

#### Step 1: Add CLI Arguments
**File**: `madness.py`

```python
parser.add_argument("--compare", nargs=2, metavar=("BASELINE", "VARIANT"),
                    help="Compare two deck configurations")
parser.add_argument("--compare-output", default="comparison_results.xlsx",
                    help="Output file for comparison results")
```

#### Step 2: Create Comparison Controller
**New File**: `deck_comparison.py`

```python
def compare_decks(baseline_path, variant_path, runs, turns, config):
    """
    Run simulations for both decks and generate comparison.
    
    Returns:
        ComparisonResults object
    """
    # 1. Load both decks
    baseline_deck = load_deck_cards(baseline_path)
    variant_deck = load_deck_cards(variant_path)
    
    # 2. Identify differences
    diffs = calculate_deck_differences(baseline_deck, variant_deck)
    
    # 3. Run simulations (potentially in parallel)
    baseline_results = run_simulations(baseline_path, runs, turns, config)
    variant_results = run_simulations(variant_path, runs, turns, config)
    
    # 4. Calculate deltas
    deltas = calculate_deltas(baseline_results, variant_results)
    
    # 5. Generate insights
    insights = analyze_comparison(diffs, deltas)
    
    return ComparisonResults(baseline_results, variant_results, 
                             diffs, deltas, insights)
```

#### Step 3: Calculate Deltas
**Function**: `calculate_deltas()`

```python
def calculate_deltas(baseline, variant):
    """Calculate differences across all metrics."""
    deltas = {}
    
    # Ideal setup deltas
    for setup in baseline.ideal_setups:
        b_rate = baseline.ideal_setups[setup]
        v_rate = variant.ideal_setups[setup]
        deltas[setup] = {
            "baseline": b_rate,
            "variant": v_rate,
            "delta": v_rate - b_rate,
            "delta_pct": ((v_rate - b_rate) / b_rate * 100) if b_rate > 0 else None
        }
    
    # Key card access deltas
    # Mulligan deltas
    # Opening hand pattern deltas
    
    return deltas
```

#### Step 4: Export Comparison Results
**Function**: `export_comparison()`

```python
def export_comparison(comparison, output_file):
    """Export comparison to Excel with multiple sheets."""
    with pd.ExcelWriter(output_file) as writer:
        # Summary comparison
        summary_df = create_summary_comparison(comparison)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        # Ideal setup comparison
        setup_df = create_setup_comparison(comparison)
        setup_df.to_excel(writer, sheet_name="Setup Comparison", index=False)
        
        # Deck difference
        diff_df = create_deck_diff(comparison)
        diff_df.to_excel(writer, sheet_name="Deck Changes", index=False)
        
        # Opening hand comparison (best patterns from each)
        # ...
```

---

### Phase 2: Enhanced Comparison Features

#### Step 5: Opening Hand Pattern Comparison

```python
def compare_opening_hand_patterns(baseline_results, variant_results):
    """
    Compare opening hand patterns between decks.
    
    Focus on:
    - Patterns unique to each deck
    - Patterns present in both (which deck performs better)
    - How card changes affect pattern success rates
    """
    # Get top 10 patterns from each
    baseline_patterns = get_top_patterns(baseline_results, n=10)
    variant_patterns = get_top_patterns(variant_results, n=10)
    
    # Identify common patterns
    common = set(baseline_patterns.keys()) & set(variant_patterns.keys())
    baseline_only = set(baseline_patterns.keys()) - common
    variant_only = set(variant_patterns.keys()) - common
    
    return {
        "common_patterns": {
            pattern: {
                "baseline_success": baseline_patterns[pattern],
                "variant_success": variant_patterns[pattern],
                "delta": variant_patterns[pattern] - baseline_patterns[pattern]
            }
            for pattern in common
        },
        "baseline_only": baseline_only,
        "variant_only": variant_only
    }
```

#### Step 6: Statistical Significance Testing

```python
def calculate_statistical_significance(baseline_results, variant_results, 
                                      metric_name):
    """
    Determine if observed difference is statistically significant.
    
    Uses:
    - Z-test for proportions (success rates)
    - Confidence intervals
    - P-values
    """
    from scipy.stats import proportions_ztest
    
    # Example for ideal setup success
    baseline_successes = baseline_results.successes
    baseline_total = baseline_results.total
    variant_successes = variant_results.successes
    variant_total = variant_results.total
    
    stat, p_value = proportions_ztest(
        [baseline_successes, variant_successes],
        [baseline_total, variant_total]
    )
    
    return {
        "p_value": p_value,
        "significant": p_value < 0.05,
        "confidence_95": calculate_confidence_interval(variant_results)
    }
```

---

## 4. Output Formats

### 4.1 Excel Output

**File**: `comparison_results.xlsx`

#### Sheet 1: Summary
| Metric | Baseline | Variant | Delta | Delta % | Significant? |
|--------|----------|---------|-------|---------|--------------|
| Survival Engine | 45.5% | 52.3% | +6.8% | +14.9% | ✓ Yes |
| Counter Protection | 34.3% | 28.1% | -6.2% | -18.1% | ✓ Yes |
| Avg Mulligans | 0.43 | 0.39 | -0.04 | -9.3% | No |

#### Sheet 2: Setup Comparison
| Setup | Baseline % | Variant % | Delta | Assessment |
|-------|-----------|-----------|-------|------------|
| Survival Engine | 45.5 | 52.3 | +6.8 | ✅ Improved |
| Counter Protection | 34.3 | 28.1 | -6.2 | ⚠️ Declined |

#### Sheet 3: Deck Changes
| Change Type | Card | Baseline Qty | Variant Qty | Delta |
|-------------|------|--------------|-------------|-------|
| Removed | Naturalize | 3 | 1 | -2 |
| Added | Brainstorm | 0 | 2 | +2 |

#### Sheet 4: Opening Hand Pattern Comparison
| Pattern | Baseline Success | Variant Success | Delta | Frequency Change |
|---------|-----------------|-----------------|-------|------------------|
| 3L 2C +Survival | 96% | 98% | +2% | Same |
| 3L 2C +Counterspell | 100% | N/A | N/A | Pattern lost |

### 4.2 Markdown Output

**File**: `comparison_summary.md`

```markdown
# Deck Comparison Summary

**Baseline**: deck.csv
**Variant**: variant.csv
**Simulations**: 1000 games each

## Card Changes

### Added (+2 cards)
- Brainstorm x2

### Removed (-2 cards)
- Naturalize x2

## Performance Comparison

### Ideal Setup Success

| Setup | Baseline | Variant | Delta | Assessment |
|-------|----------|---------|-------|------------|
| Survival Engine | 45.5% | 52.3% | **+6.8%** ✅ | Improved |
| Counter Protection | 34.3% | 28.1% | **-6.2%** ⚠️ | Declined |

### Key Insights

✅ **Improvements**
- Survival Engine +6.8% (trade-off: added card selection)
- Average Mulligans reduced by 0.04

⚠️ **Trade-offs**
- Counter Protection declined 6.2% (lost 2 Counterspell equivalents)

### Recommendation

Variant shows **net positive** improvement:
- Primary goal (Survival Engine) improved significantly
- Counter Protection decline may be acceptable depending on meta
```

---

## 5. CLI Interface Design

### Basic Comparison
```bash
python madness.py --compare deck.csv variant.csv --runs 1000
```

### With Custom Output
```bash
python madness.py --compare deck.csv variant.csv \
  --runs 1000 \
  --compare-output my_comparison.xlsx
```

### With Sideboard Plans
```bash
# Compare post-sideboard configurations
python madness.py --compare deck.csv variant.csv \
  --sideboard vs_combo \
  --runs 1000 \
  --compare-output vs_combo_comparison.xlsx
```

### Batch Comparison
```bash
# Compare multiple variants (future)
python madness.py --compare-batch baseline.csv variant1.csv variant2.csv variant3.csv
```

---

## 6. Use Cases & Examples

### Use Case 1: Testing Card Swap
**Scenario**: Is +2 Mystical Tutor, -2 Naturalize better?

```bash
# Create variant deck
cp deck.csv variant.csv
# Edit variant.csv: -2 Naturalize, +2 Mystical Tutor

# Compare
python madness.py --compare deck.csv variant.csv --runs 1000

# Review comparison_results.xlsx
```

**Expected Output**:
- Survival visibility increase
- Naturalize Access setup decrease
- Net impact analysis

### Use Case 2: Land Count Optimization
**Scenario**: Is 20 lands better than 19?

```bash
# Test variants
python madness.py --compare deck_19lands.csv deck_20lands.csv --runs 2000
```

**Metrics to watch**:
- Mulligan rate changes
- Average lands in play by turn 4
- Setup success rates
- Opening hand patterns

### Use Case 3: Creature Density Testing
**Scenario**: More creatures vs more spells

```bash
# Compare high-creature vs high-spell versions
python madness.py --compare creature_heavy.csv spell_heavy.csv --runs 1000
```

**Analysis focus**:
- Survival Engine success (needs creatures in hand)
- Opening hand pattern distribution
- Mulligan frequency

### Use Case 4: Post-Sideboard Comparison
**Scenario**: Is my sideboard plan optimal?

```bash
# Pre-board comparison
python madness.py --compare current_sb.csv new_sb.csv --runs 1000

# Post-board comparison vs combo
python madness.py --compare current_sb.csv new_sb.csv \
  --sideboard vs_combo --runs 1000
```

---

## 7. Implementation Details

### 7.1 File Structure

```
madnesscarlo/
├── madness.py                      # Main CLI (updated)
├── deck_comparison.py              # NEW: Comparison engine
├── comparison_utils.py             # NEW: Delta calculation utilities
├── export_comparison.py            # NEW: Export functionality
├── DECK_COMPARISON_PROJECT_PLAN.md # This document
└── tests/
    └── test_deck_comparison.py     # NEW: Tests
```

### 7.2 Key Functions

#### `deck_comparison.py`
- `compare_decks(baseline, variant, runs, turns, config)` - Main entry point
- `load_deck_cards(csv_path)` - Load deck into dict
- `calculate_deck_differences(deck1, deck2)` - Identify changes
- `run_parallel_simulations(decks, params)` - Run multiple sims

#### `comparison_utils.py`
- `calculate_metric_delta(baseline_val, variant_val)` - Standard delta calc
- `calculate_significance(baseline_results, variant_results)` - Stats
- `generate_insights(deltas)` - Auto-generate observations
- `rank_changes(deltas)` - Order by impact

#### `export_comparison.py`
- `export_to_excel(comparison, output_file)` - Excel export
- `export_to_markdown(comparison, output_file)` - MD export
- `create_summary_table(comparison)` - Generate summary
- `create_deck_diff_table(comparison)` - Show card changes

### 7.3 Integration Points

#### Modify `madness.py` main():
```python
def main():
    args = parse_args()
    
    # NEW: Handle comparison mode
    if args.compare:
        baseline_path, variant_path = args.compare
        comparison = compare_decks(
            baseline_path, 
            variant_path,
            runs=args.runs,
            turns=args.turns,
            config=load_config(args.config)
        )
        export_comparison(comparison, args.compare_output)
        print_comparison_summary(comparison)
        return
    
    # Existing single-deck simulation
    # ...
```

---

## 8. Testing Strategy

### Unit Tests
```python
def test_calculate_deck_differences():
    """Test card diff calculation."""
    baseline = {"Forest": 7, "Island": 9, "Survival": 4}
    variant = {"Forest": 8, "Island": 9, "Survival": 3}
    
    diffs = calculate_deck_differences(baseline, variant)
    
    assert diffs["cards_added"] == {"Forest": 1}
    assert diffs["cards_removed"] == {"Survival": 1}

def test_calculate_delta():
    """Test delta calculation."""
    delta = calculate_metric_delta(45.5, 52.3)
    
    assert delta["delta"] == 6.8
    assert delta["delta_pct"] == pytest.approx(14.9, rel=0.1)

def test_compare_decks_same_deck():
    """Comparing identical decks should show zero deltas."""
    comparison = compare_decks("deck.csv", "deck.csv", runs=10, turns=4, config={})
    
    for setup, delta in comparison.deltas["ideal_setups"].items():
        assert abs(delta["delta"]) < 5  # Allow for random variance
```

### Integration Tests
```python
def test_full_comparison_workflow():
    """Test complete comparison from CLI to output."""
    result = subprocess.run([
        "python", "madness.py",
        "--compare", "test_deck1.csv", "test_deck2.csv",
        "--runs", "100",
        "--compare-output", "test_comparison.xlsx"
    ])
    
    assert result.returncode == 0
    assert os.path.exists("test_comparison.xlsx")
    
    # Verify Excel contents
    df = pd.read_excel("test_comparison.xlsx", sheet_name="Summary")
    assert "Delta" in df.columns
    assert len(df) > 0
```

### Performance Tests
```python
def test_comparison_performance():
    """Ensure comparison doesn't take too long."""
    start = time.time()
    
    compare_decks("deck1.csv", "deck2.csv", runs=1000, turns=4, config={})
    
    elapsed = time.time() - start
    assert elapsed < 5.0  # Should complete in under 5 seconds
```

---

## 9. Documentation Needs

### 9.1 README Updates
- Add "Deck Comparison" section
- Include usage examples
- Show sample output

### 9.2 New Documentation Files
- `COMPARISON_GUIDE.md` - Complete guide on using comparisons
- `COMPARISON_EXAMPLES.md` - Real-world examples with interpretations

### 9.3 Docstrings
- All new functions need comprehensive docstrings
- Include parameter descriptions
- Provide usage examples

---

## 10. Potential Challenges & Solutions

### Challenge 1: Statistical Noise
**Problem**: Small sample sizes or random variance can show "differences" that aren't real.

**Solution**: 
- Default to larger sample sizes for comparisons (2000+ games)
- Add confidence intervals
- Flag "not significant" differences
- Recommend re-running if results are borderline

### Challenge 2: Too Much Data
**Problem**: Comparing everything creates overwhelming output.

**Solution**:
- Focus on "most important" metrics first (ideal setups)
- Provide summary view with option to drill down
- Only show patterns that changed significantly
- Use visual indicators (✅ ⚠️ ❌) for quick scanning

### Challenge 3: Complex Changes
**Problem**: Comparing decks with 10+ card changes is hard to interpret.

**Solution**:
- Recommend testing smaller changes
- Group changes by category (lands, creatures, spells)
- Provide "primary driver" analysis (which change mattered most)
- Allow iterative comparison (A→B→C tracking)

### Challenge 4: Performance
**Problem**: Running 2 simulations takes 2x the time.

**Solution**:
- Parallelize simulations using multiprocessing
- Cache results for repeated comparisons
- Provide progress indicators for both simulations
- Allow resuming interrupted comparisons

---

## 11. Future Enhancements

### Phase 3: Advanced Features
- **Multi-deck comparison**: Compare 3+ decks simultaneously
- **Optimization mode**: Auto-test card counts (3 vs 4 copies)
- **Historical tracking**: Database of previous comparisons
- **Regression detection**: Alert if new changes hurt previous gains
- **Matchup comparison**: Compare post-sideboard for multiple matchups

### Phase 4: Visualization
- **Charts**: Bar charts of delta magnitudes
- **Heatmaps**: Show which patterns improved/declined
- **Trend lines**: Track metrics across multiple comparisons
- **Interactive dashboard**: Web UI for exploring comparisons

### Phase 5: AI Integration
- **Auto-suggestions**: "Based on comparison, consider testing..."
- **Pattern recognition**: "This change pattern typically improves X"
- **Meta-optimization**: "Given current meta, variant is better"

---

## 12. Success Metrics

### How We'll Know It's Working

**MVP Success Criteria**:
- ✅ Can compare two decks with single CLI command
- ✅ Output shows clear deltas for all key metrics
- ✅ Execution time < 2x single simulation time
- ✅ Zero crashes on valid input
- ✅ All tests pass

**User Success Criteria**:
- ✅ Can make informed keep/cut decisions based on data
- ✅ Understand trade-offs of card changes
- ✅ Validate hypotheses ("Does adding tutors help?")
- ✅ Iterate quickly on deck optimization

**Quality Criteria**:
- ✅ Statistical rigor (confidence intervals, significance testing)
- ✅ Clear, actionable output
- ✅ Handles edge cases gracefully
- ✅ Well-documented with examples

---

## 13. Timeline Estimate

### Phase 1 (MVP): 3-4 hours
- Hour 1: CLI interface + deck loading (30 min) + diff calculation (30 min)
- Hour 2: Run parallel simulations + delta calculation
- Hour 3: Excel export + basic markdown export
- Hour 4: Testing + bug fixes + documentation

### Phase 2 (Enhanced): 2-3 hours
- Opening hand pattern comparison
- Statistical significance testing
- Enhanced insights generation
- Comprehensive testing

### Phase 3 (Advanced): 4-6 hours
- Multi-deck comparison
- Optimization modes
- Historical tracking
- Advanced visualizations

**Total MVP to Production**: 9-13 hours

---

## 14. Decision Points

### Before Implementation, Decide:

1. **Output Priority**: Excel, Markdown, or both?
   - Recommendation: Both (Excel for data, MD for quick review)

2. **Parallelization**: Use multiprocessing or sequential?
   - Recommendation: Parallel (significant time savings)

3. **Statistical Testing**: Include from MVP or defer to Phase 2?
   - Recommendation: Defer (can add later without breaking changes)

4. **Comparison Depth**: Just summary or deep pattern analysis?
   - Recommendation: Summary for MVP, deep analysis in Phase 2

5. **CLI Design**: Separate command or flag on main command?
   - Recommendation: Flag on main command (simpler UX)

---

## 15. Approval Checklist

Before proceeding with implementation:

- [ ] Review requirements - are they complete?
- [ ] Validate technical approach - any concerns?
- [ ] Confirm output format meets needs
- [ ] Check CLI interface is intuitive
- [ ] Verify use cases cover your scenarios
- [ ] Assess timeline estimate is reasonable
- [ ] Approve file structure and integration points
- [ ] Confirm testing strategy is sufficient

---

## 16. Next Steps

Once approved:

1. **Create feature branch**: `git checkout -b feature/deck-comparison`
2. **Implement Phase 1 (MVP)**: Follow implementation plan
3. **Test thoroughly**: Run all test scenarios
4. **Update documentation**: README, usage guides
5. **Create example comparisons**: Real deck variants for reference
6. **Merge to main**: After review and approval

---

## Appendix A: Example Output

### Terminal Output
```
$ python madness.py --compare deck.csv variant.csv --runs 1000

Comparing decks...
  Baseline: deck.csv (60 cards)
  Variant: variant.csv (60 cards)
  
Card Changes:
  +2 Brainstorm
  -2 Naturalize

Running simulations...
  Baseline: 100%|████████████| 1000/1000 [00:00<00:00, 1200/s]
  Variant:  100%|████████████| 1000/1000 [00:00<00:00, 1180/s]

Calculating deltas...

╔══════════════════════════════════════════════════════╗
║         DECK COMPARISON RESULTS                      ║
╚══════════════════════════════════════════════════════╝

IDEAL SETUP COMPARISON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup                  Baseline  Variant   Delta    
──────────────────────────────────────────────────────
Survival Engine        45.5%     52.3%     +6.8% ✅
Counter Protection     34.3%     28.1%     -6.2% ⚠️
Naturalize Access      26.9%     18.2%     -8.7% ⚠️

KEY INSIGHTS:
✅ Primary goal (Survival Engine) improved 6.8%
⚠️  Defensive setups declined (expected with -2 interaction)

Results exported to: comparison_results.xlsx
```

---

**Status**: Draft Plan - Awaiting Approval  
**Last Updated**: 2025-10-25  
**Author**: Project Planning  
**Version**: 1.0

