# Guide: Preparing Simulation Data for LLM Analysis

## Overview

This guide explains how to structure your deck simulation data for optimal LLM analysis and deck building advice.

## Quick Start

```bash
# Run your simulation
python madness.py --runs 1000 --turns 4

# Generate LLM-optimized analysis
python export_llm_analysis.py simulation_results.xlsx simulation_config.json

# Review generated files
# 1. DECK_ANALYSIS_FOR_LLM.md - Complete structured analysis
# 2. LLM_PROMPT_TEMPLATE.md - Example prompts for your LLM
```

## What Makes Good LLM Input?

### ✅ DO: Goal-Oriented Framing
- **State your objective clearly**: "Achieve Survival Engine by turn 4"
- **Quantify current performance**: "45.5% success rate"
- **Identify specific bottlenecks**: "Only see Survival in 60% of games"

### ✅ DO: Provide Context
- **Deck archetype**: "UG Madness combo deck"
- **Format constraints**: "Premodern (no cards after Scourge)"
- **Meta considerations**: "Facing combo, aggro, and control"

### ✅ DO: Include Structured Data
- **Tables with clear headers**: Success rates, card visibility, patterns
- **Comparative metrics**: Before vs after, variant A vs variant B
- **Statistical significance**: Only show patterns with 5+ occurrences

### ❌ DON'T: Raw Data Dumps
- Don't paste entire Excel sheets
- Don't include every single pattern (filter to significant ones)
- Don't forget to explain what the numbers mean

### ❌ DON'T: Vague Questions
- Bad: "How do I improve my deck?"
- Good: "Should I add tutors to increase Survival visibility from 60% to 70%+?"

## File Guide

### 1. DECK_ANALYSIS_FOR_LLM.md

**Purpose**: Comprehensive structured analysis optimized for LLM consumption

**Contains**:
- Executive summary with goal and current performance
- Key card access rates with assessments (✅ Good / ⚠️ Needs Improvement)
- Best opening hand patterns
- Bottleneck identification
- Individual card performance
- Strategic questions for the LLM to address

**How to use**:
1. Review the entire document
2. Copy relevant sections based on your question
3. Paste into LLM conversation with your specific question

**Example usage**:
```
I'm optimizing a UG Madness deck. Here's my analysis:

[Paste "Current Performance" section]
[Paste "Bottleneck Identification" section]

My question: Should I add more card selection (Brainstorm/Ponder) 
to improve Survival visibility from 60% to 70%+?
```

### 2. LLM_PROMPT_TEMPLATE.md

**Purpose**: Pre-structured prompts you can customize

**Contains**:
- Template structure for asking questions
- Example prompts for common scenarios
- Guidelines on what to include

**How to use**:
1. Choose the example closest to your question
2. Fill in your specific data
3. Adjust the question to your needs

### 3. simulation_results.xlsx (Original Data)

**Purpose**: Reference for detailed queries

**When to include**:
- LLM asks for more detail on a specific card
- You need to do comparative analysis
- Deep dive into specific patterns

**How to share**: Copy specific sheets as markdown tables

## Recommended Workflow

### Phase 1: Initial Analysis

1. **Run baseline simulation**
```bash
python madness.py --runs 1000 --output baseline_results.xlsx
python export_llm_analysis.py baseline_results.xlsx simulation_config.json
```

2. **Ask broad questions**
```
Context: [Paste DECK_ANALYSIS_FOR_LLM.md sections]

Question: What are the top 3 bottlenecks preventing Survival Engine success?
Provide specific card recommendations for each.
```

3. **Get initial recommendations**
- LLM will identify key issues
- Suggest specific card changes
- Explain reasoning

### Phase 2: Test Variants

4. **Implement recommended changes** (e.g., +2 card selection, -2 Naturalize)

5. **Run comparison simulation**
```bash
# Modify deck.csv with changes
python madness.py --runs 1000 --output variant1_results.xlsx

# Generate comparison
python export_llm_analysis.py variant1_results.xlsx simulation_config.json
```

6. **Ask comparative questions**
```
Baseline: Survival Engine 45.5%
Variant (+2 Mystical Tutor, -2 Naturalize): Survival Engine 52.3%

Is this improvement worth the trade-off in artifact/enchantment removal?
What matchups suffer? What other variants should I test?
```

### Phase 3: Refinement

7. **Test sideboard plans**
```bash
python madness.py --runs 1000 --sideboard vs_combo --output vs_combo_results.xlsx
python madness.py --runs 1000 --sideboard vs_aggro --output vs_aggro_results.xlsx
```

8. **Matchup-specific questions**
```
Pre-board vs Combo: 45.5% Survival Engine
Post-board vs Combo: 62.3% Counter Protection, 43.1% Survival Engine

Did I sideboard correctly? Should I board out Survival against combo?
```

## Best Practices for LLM Conversations

### 1. Start Broad, Then Narrow
```
First message: "What are my biggest bottlenecks?"
Follow-up: "You suggested adding tutors. Which specific tutors work in Premodern?"
Follow-up: "Between Worldly Tutor and Mystical Tutor, which is better for this deck?"
```

### 2. Provide Decision Context
```
Bad: "Should I play Brainstorm?"
Good: "I need to see Survival more consistently (currently 60%). 
      Should I add Brainstorm (+card selection, -deck thinning) 
      or Mystical Tutor (+direct tutor, +costs a turn)?"
```

### 3. Share Trade-off Concerns
```
"Adding 4 Brainstorms would increase Survival visibility but:
- Reduces creature density (Survival needs creatures in hand)
- Requires fetchlands to work optimally (I only have 4)
- Takes up turn 1 tempo

How do I weigh these trade-offs?"
```

### 4. Ask for Alternative Perspectives
```
"You recommended path A (add tutors). 
What about path B (add more creatures to reduce Survival dependency)?
What are the pros/cons of each approach?"
```

### 5. Request Specific Metrics
```
"If I add 2 Mystical Tutors, what Survival visibility % should I expect?
What's the expected impact on Survival Engine success rate?
At what visibility % does this become worth the deck slots?"
```

## Example Full Conversation

### Message 1: Setup
```
I'm optimizing a UG Madness deck for Premodern. Goal: Achieve Survival 
of the Fittest engine (Survival on battlefield + any creature in hand + 
2 lands + G mana) by turn 4.

Current Performance (1000 games):
- Survival Engine: 45.5% success
- Survival seen by turn 4: 60.4%
- Patterns with Survival + 3 creatures: 96% success
- Patterns with Survival + 0-1 creatures: 65% success

Bottlenecks:
- Don't see Survival 40% of games
- Sometimes lack creatures when I do have Survival

What's my best path to 60%+ Survival Engine success?
```

### Message 2: Follow-up
```
You suggested adding Brainstorm and Worldly Tutor. 

Current deck space (relevant cards):
- 3 Naturalize (52.6% visibility, 28.3% setup success)
- 3 Counterspell (52.7% visibility, 34.3% setup success)
- 4 Careful Study (already have)

Which 4 slots should I cut? Explain the trade-offs for each option.
```

### Message 3: Validation
```
I tested your recommendation (-2 Naturalize, -1 Counterspell, +3 Brainstorm):

New results (1000 games):
- Survival Engine: 52.3% success (+6.8%)
- Survival visibility: 67.2% (+6.8%)
- Counter Protection: 28.1% (-6.2%)

Is this trade-off worth it? Or should I find slots elsewhere?
```

## Advanced: Comparative Analysis

For A/B testing multiple variants:

```python
# Run multiple variants
variants = ['baseline', 'more_tutors', 'more_creatures', 'more_lands']

for variant in variants:
    # Modify deck
    # Run simulation
    # Export analysis
    pass

# Compare
python export_llm_analysis.py --compare baseline.xlsx variant1.xlsx variant2.xlsx
```

Then ask:
```
I tested 3 variants (baseline, +tutors, +creatures). 
Here's the comparison: [paste comparison table]

Which variant has the best risk/reward profile?
Are there hybrid approaches worth testing?
```

## Tips for Specific Scenarios

### Scenario: Mulligan Strategy
```
Include: 
- Mulligan distribution table
- Best hand patterns with median mulligans
- Games requiring 2+ mulligans

Ask: "Should I mulligan more/less aggressively?"
```

### Scenario: Sideboard Optimization
```
Include:
- Pre-board vs post-board comparison
- Matchup-specific success rates
- Cards boarded in/out

Ask: "Is my sideboard plan optimal for this matchup?"
```

### Scenario: Card Cut Decisions
```
Include:
- Card visibility vs usage rate
- Setup success rates
- Pattern analysis

Ask: "Card X shows 50% visibility but only 15% usage. Cut it?"
```

### Scenario: Alternative Win Conditions
```
Include:
- Success rates for all ideal setups
- Games where primary plan fails
- Current card distribution

Ask: "Should I add a backup plan for when Survival fails?"
```

## Common LLM Questions to Prepare For

LLMs will often ask:

1. **"What matchups are you targeting?"**
   - Have matchup priorities ready
   - Mention meta considerations

2. **"What's your budget for changes?"**
   - Card availability constraints
   - Testing time available

3. **"What other variants have you tried?"**
   - Keep notes on previous tests
   - Explain why they didn't work

4. **"What's your risk tolerance?"**
   - Prefer consistency or explosiveness?
   - Okay with silver bullets vs broad answers?

## Output Files Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `DECK_ANALYSIS_FOR_LLM.md` | Structured analysis | Every LLM conversation |
| `LLM_PROMPT_TEMPLATE.md` | Example prompts | First time / reference |
| `simulation_results.xlsx` | Raw data | Deep dives / specific queries |
| `comparison.json` | Variant comparison | A/B testing |
| `deck.csv` | Current decklist | Always include for context |
| `simulation_config.json` | Goals & strategy | Reference if LLM asks |

## Key Takeaways

✅ **Frame around goals**: "Achieve X% success" not "make deck better"
✅ **Quantify everything**: Use percentages and concrete numbers
✅ **Show patterns**: What works vs what doesn't
✅ **Ask specific questions**: Request actionable recommendations
✅ **Iterate with data**: Test recommendations, show results
✅ **Include trade-offs**: Help LLM understand constraints

❌ **Avoid raw dumps**: Don't paste entire spreadsheets
❌ **Avoid vague asks**: "Improve my deck" is not actionable
❌ **Avoid single data points**: Need statistical significance
❌ **Avoid missing context**: Always explain the goal

## Next Steps

1. **Run initial simulation** with current deck
2. **Generate LLM analysis** using export script
3. **Start conversation** using prompt template
4. **Implement recommendations** and test
5. **Compare results** and iterate

Happy brewing! 🎴

