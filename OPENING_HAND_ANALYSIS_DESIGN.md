# Opening Hand Analysis Feature Design

## Goal
Identify which opening hand compositions are most likely to achieve ideal setups by turn 4.

## Use Cases
1. **Mulligan Decisions**: "Should I keep a hand with Survival but no Squee?"
2. **Deck Optimization**: "Do I need more turn 1 plays?"
3. **Setup Requirements**: "What cards do I need in opening hand for Wonder setup?"
4. **Pattern Recognition**: "Hands with 2 creatures + 3 lands have 45% success rate"

## Data to Track

### Per Simulation
```python
{
    "opening_hand": ["Forest", "Island", "Survival of the Fittest", ...],
    "opening_hand_size": 7,  # After mulligans
    "mulligan_count": 0,
    "setup_results": {
        "Survival Engine": True,
        "Wonder in Graveyard": False,
        ...
    }
}
```

### Aggregated Patterns
```python
{
    "pattern": "Contains: Survival + Squee, Lands: 3",
    "occurrences": 47,
    "setup_success": {
        "Survival Engine": {"attempts": 47, "successes": 38, "rate": 80.9},
        "Counter Protection": {"attempts": 47, "successes": 22, "rate": 46.8}
    }
}
```

## Implementation Steps

### Step 1: Track Opening Hands

**File**: `madness.py` - `simulate_game()`

```python
def simulate_game(deck_csv_path, turns=4, config=None):
    # ... existing mulligan logic ...
    kept_hand, mulligan_count = perform_mulligan(deck, key_cards, mulligan_strategy)
    
    # NEW: Track opening hand
    opening_hand_list = sorted(list(kept_hand.elements()))
    opening_hand_size = len(opening_hand_list)
    
    # ... rest of simulation ...
    
    return {
        # ... existing fields ...
        "opening_hand": opening_hand_list,
        "opening_hand_size": opening_hand_size,
    }
```

### Step 2: Analyze Hand Patterns

**New Function**: `analyze_opening_hands()`

```python
def analyze_opening_hands(simulation_results, config):
    """
    Analyze which opening hand patterns lead to setup success.
    
    Returns:
        DataFrame with patterns and success rates
    """
    patterns = defaultdict(lambda: {
        "count": 0,
        "setup_success": defaultdict(int)
    })
    
    for result in simulation_results:
        # Extract pattern
        pattern = extract_hand_pattern(result["opening_hand"], config)
        patterns[pattern]["count"] += 1
        
        # Track setup successes
        for setup_name, succeeded in result["setup_results"].items():
            if succeeded:
                patterns[pattern]["setup_success"][setup_name] += 1
    
    # Convert to DataFrame
    rows = []
    for pattern, data in patterns.items():
        for setup_name, successes in data["setup_success"].items():
            rows.append({
                "Pattern": pattern,
                "Occurrences": data["count"],
                "Setup": setup_name,
                "Successes": successes,
                "Success Rate %": (successes / data["count"]) * 100
            })
    
    return pd.DataFrame(rows)
```

### Step 3: Pattern Extraction

**New Function**: `extract_hand_pattern()`

```python
def extract_hand_pattern(opening_hand, config):
    """
    Convert opening hand to a pattern string.
    
    Patterns include:
    - Key cards present
    - Land count
    - Creature count
    - Color access potential
    """
    key_cards = config.get("key_cards", [])
    
    # Count components
    lands = [c for c in opening_hand if "Land" in deck.card_info.get(c, {}).get("type", "")]
    creatures = [c for c in opening_hand if "Creature" in deck.card_info.get(c, {}).get("type", "")]
    key_present = [c for c in opening_hand if c in key_cards]
    
    # Build pattern string
    parts = []
    parts.append(f"L{len(lands)}")  # L3 = 3 lands
    parts.append(f"C{len(creatures)}")  # C2 = 2 creatures
    
    if key_present:
        parts.append(f"K:{','.join(sorted(key_present))}")
    
    return " | ".join(parts)
```

### Step 4: Enhanced Patterns

**Advanced Pattern Matching**:

```python
def extract_detailed_pattern(opening_hand, config, deck):
    """
    More detailed pattern with:
    - Specific key card combinations
    - Discard outlets
    - Turn 1 plays available
    """
    pattern_features = []
    
    # Land count
    land_count = count_lands_in_hand(Counter(opening_hand), deck)
    pattern_features.append(f"{land_count}L")
    
    # Key cards
    key_cards = config.get("key_cards", [])
    for key in key_cards:
        if key in opening_hand:
            pattern_features.append(f"+{key}")
    
    # Discard outlets
    outlets = ["Wild Mongrel", "Waterfront Bouncer", "Careful Study"]
    has_outlet = any(o in opening_hand for o in outlets)
    if has_outlet:
        pattern_features.append("Outlet")
    
    # Madness cards
    madness_cards = [c for c in opening_hand 
                     if "madness_" in str(deck.card_info.get(c, {}).get("conditions", ""))]
    if madness_cards:
        pattern_features.append(f"{len(madness_cards)}Madness")
    
    # Turn 1 play available
    one_drops = [c for c in opening_hand 
                 if "G" in deck.card_info.get(c, {}).get("mana_cost", "") 
                 and "2" not in deck.card_info.get(c, {}).get("mana_cost", "")]
    if one_drops and land_count >= 1:
        pattern_features.append("T1Play")
    
    return " ".join(pattern_features)
```

## Output Formats

### Excel Sheet: "Best Opening Hands"

| Pattern | Games | Survival Engine % | Counter Protection % | Wonder in Graveyard % | Overall Success % |
|---------|-------|-------------------|---------------------|---------------------|-------------------|
| 3L +Survival +Squee | 42 | 85.7 | 52.4 | 23.8 | 53.3 |
| 3L Outlet 1Madness | 87 | 28.7 | 45.9 | 31.0 | 35.2 |
| 2L +Survival | 35 | 42.9 | 20.0 | 11.4 | 24.8 |

### Excel Sheet: "Key Card Correlation"

| Key Card | In Opening Hand % | Setup Success When Present | Setup Success When Absent |
|----------|-------------------|---------------------------|---------------------------|
| Survival of the Fittest | 35.2 | Survival Engine: 72.3% | Survival Engine: 18.1% |
| Squee, Goblin Nabob | 34.8 | Survival Engine: 65.8% | Survival Engine: 21.2% |
| Careful Study | 32.1 | Wonder GY: 28.4% | Wonder GY: 15.7% |

### Excel Sheet: "Opening Hand Stats"

| Metric | Value |
|--------|-------|
| Avg Hand Size | 6.6 cards (after mulligans) |
| Most Common Land Count | 3 lands (42.3% of hands) |
| % with Discard Outlet | 38.7% |
| % with Key Card | 45.2% |
| % with Multiple Key Cards | 12.8% |

## API Updates

### New Function: `run_simulations_with_hand_analysis()`

```python
def run_simulations_with_hand_analysis(deck_csv_path, runs=1000, turns=4, config=None):
    """
    Run simulations and analyze opening hand patterns.
    
    Returns:
        Tuple of (standard_results, opening_hand_analysis)
    """
    # Store all simulation results
    all_results = []
    
    for _ in tqdm(range(runs), desc="Simulating games"):
        result = simulate_game(deck_csv_path, turns, config=config)
        all_results.append(result)
    
    # Standard aggregation
    standard_stats = aggregate_standard_stats(all_results)
    
    # NEW: Opening hand analysis
    hand_patterns_df = analyze_opening_hands(all_results, config)
    key_card_correlation_df = analyze_key_card_correlation(all_results, config)
    hand_stats_df = compute_hand_statistics(all_results, config)
    
    return {
        "standard": standard_stats,
        "hand_patterns": hand_patterns_df,
        "key_card_correlation": key_card_correlation_df,
        "hand_statistics": hand_stats_df
    }
```

## Usage Example

```python
# Run with hand analysis
results = run_simulations_with_hand_analysis(
    "deck.csv", 
    runs=1000, 
    turns=4, 
    config=config
)

# Export all results
with pd.ExcelWriter("simulation_results.xlsx") as writer:
    # Standard sheets
    results["standard"]["seen_df"].to_excel(writer, sheet_name="Card Stats")
    # ... other standard sheets ...
    
    # NEW: Opening hand analysis sheets
    results["hand_patterns"].to_excel(writer, sheet_name="Best Opening Hands")
    results["key_card_correlation"].to_excel(writer, sheet_name="Key Card Correlation")
    results["hand_statistics"].to_excel(writer, sheet_name="Opening Hand Stats")
```

## Configuration

Add to `simulation_config.json`:

```json
{
  "opening_hand_analysis": {
    "enabled": true,
    "pattern_type": "detailed",  // "simple" or "detailed"
    "min_pattern_occurrences": 5,  // Only show patterns seen 5+ times
    "focus_cards": [  // Cards to specifically track
      "Survival of the Fittest",
      "Squee, Goblin Nabob",
      "Careful Study"
    ]
  }
}
```

## Benefits

✅ **Mulligan Guidance**
- "Hands with Survival + 3 lands have 72% setup success"
- "Should almost always keep Survival + Squee"

✅ **Deck Tuning**
- "Need more discard outlets - only 38% of hands have one"
- "Turn 1 plays matter - hands with T1 play have 15% higher success"

✅ **Setup Optimization**
- "Wonder setup needs Careful Study in opener (45% vs 16%)"
- "Survival Engine works even without Squee in opener (42% success)"

✅ **Pattern Recognition**
- "3 lands is optimal - 2 lands has 25% success, 4 lands has 28% success"
- "Multiple key cards doesn't help much - focus on 1 key + enablers"

## Future Enhancements

1. **Machine Learning**: Train model to predict setup success from opening hand
2. **Interactive Tool**: Web interface to input hand and see success probability
3. **Mulligan Advisor**: "Given this 7, should you mulligan?" with reasoning
4. **Turn-by-Turn Tracking**: "Hands that drew key card on turn 2 had 65% success"
5. **Opponent Interaction**: Model opponent disruption and adjust success rates

## Implementation Priority

**Phase 1** (Easy):
- Track opening hands in simulation results
- Simple pattern extraction (land count + key cards)
- Basic correlation statistics

**Phase 2** (Medium):
- Detailed pattern extraction (outlets, madness, T1 plays)
- Multiple Excel sheets with different views
- Configuration options

**Phase 3** (Advanced):
- Statistical significance testing
- Confidence intervals on success rates
- Pattern discovery (automatic identification of good patterns)

## Summary

This feature would answer:
- "What makes a good opening hand?"
- "Should I mulligan this hand?"
- "What cards do I need to see early?"
- "Which patterns lead to my ideal setups?"

The implementation is straightforward and builds on existing infrastructure!

