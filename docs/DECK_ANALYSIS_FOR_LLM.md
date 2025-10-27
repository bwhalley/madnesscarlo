# UG Madness Deck - Performance Analysis for LLM Review

*Generated: 2025-10-25 22:06:27*

## Executive Summary

### Deck Goal
Establish **Survival of the Fittest engine** by turn 4:
- Cast Survival of the Fittest (enchantment)
- Have any creature in hand
- Have 2+ lands and green mana
- Repeatedly discard creatures to tutor for optimal threats

### Current Performance

**Primary Goal Achievement: 45.52% games**

| Metric | Value |
|--------|-------|
| Survival Engine Success | 45.52% |
| Counter Protection | 34.34% |
| Roar Flashback Available | 2.64% |
| Naturalize Access | 28.34% |
| Wonder in Graveyard | 8.08% |
| Average Mulligans | 0.43 |
| Games with 0 Mulligans | 69.9% |

## Key Card Access Analysis

Success depends on seeing key cards by turn 4:

| Card | See Rate (Turn ≤4) | Assessment |
|------|-------------------|------------|
| Survival of the Fittest | 60.4% | ✅ Good |
| Counterspell | 52.7% | ⚠️ Needs Improvement |
| Naturalize | 52.6% | ⚠️ Needs Improvement |

## Best Opening Hand Patterns

Patterns that lead to Survival Engine success:

| Pattern | Games | Median Mulligans | Survival Engine % |
|---------|-------|------------------|-------------------|
| 2L 2C +Naturalize+Naturalize+Survival | 5 | 0.0 | 100.0% |
| 2L 1C +Naturalize+Survival+Survival | 13 | 0.0 | 100.0% |
| 3L 2C +Survival+Survival | 18 | 0.0 | 100.0% |
| 2L 2C +Naturalize+Survival+Survival | 11 | 0.0 | 100.0% |
| 2L 2C +Counterspell+Naturalize+Survival | 10 | 0.0 | 100.0% |
| 3L 1C +Survival+Survival | 32 | 0.0 | 96.9% |
| 2L 3C +Counterspell+Survival | 27 | 0.0 | 96.3% |
| 3L 3C +Survival | 79 | 0.0 | 96.2% |
| 4L 2C +Survival | 62 | 0.0 | 95.2% |
| 3L 0C +Survival | 17 | 3.0 | 94.1% |

## Mulligan Decision Analysis

| Mulligan Count | Frequency |
|----------------|----------|
| 0 | 69.88% |
| 1 | 21.06% |
| 2 | 6.22% |
| 3 | 1.84% |
| 4 | 0.72% |
| 5 | 0.22% |
| 6 | 0.02% |
| 7 | 0.04% |

## Bottleneck Identification

### What's Working Well ✅

- **36 hand patterns** achieve 80%+ Survival Engine success
- Common elements in successful patterns:
  - 36 patterns include Survival (100%)
  - 6 patterns have 3-4 creatures (17%)
  - 13 patterns include Counterspell (36%)

### What's Not Working ⚠️

- **54.5%** of games fail to achieve Survival Engine
- Potential reasons:
  - Survival only seen in 60.4% of games by turn 4
  - 1515 games with 0-1 creatures in opening hand
  - 9.1% of games require 2+ mulligans

## Individual Card Performance

Cards by visibility (how often seen by turn 4):

| Card | Seen % | Cast % | Notes |
|------|--------|--------|-------|
| Island | 92.6% | 0.0% | ❓ Often not cast |
| Forest | 85.3% | 0.0% | ❓ Often not cast |
| Basking Rootwalla | 72.4% | 205.5% | ✅ High usage |
| Wild Mongrel | 71.6% | 127.9% | ✅ High usage |
| Arrogant Wurm | 71.1% | 162.5% | ✅ High usage |
| Squee, Goblin Nabob | 71.1% | 0.0% | ❓ Often not cast |
| Yavimaya Coast | 67.3% | 0.0% | ❓ Often not cast |
| Survival of the Fittest | 60.4% | 62.5% | ✅ High usage |
| Careful Study | 56.3% | 63.6% | ✅ High usage |
| Counterspell | 52.7% | 0.0% | ❓ Often not cast |
| Naturalize | 52.6% | 0.0% | ❓ Often not cast |
| Frantic Search | 46.1% | 35.5% |  |
| Waterfront Bouncer | 45.7% | 70.8% | ✅ High usage |
| Roar of the Wurm | 34.2% | 4.0% | ❓ Often not cast |
| Gilded Drake | 27.5% | 0.0% | ❓ Often not cast |

## Strategic Questions for Analysis

### Deck Composition

1. **Land Count**: Currently shows optimal at 3 lands in opening hand. Should we adjust land ratios?

2. **Creature Density**: Survival Engine requires any creature. Current patterns with 3-4 creatures show 39.3% average success. Should we increase creature count?

3. **Key Card Redundancy**: Survival of the Fittest is seen in 60.4% of games. Should we add tutors or card selection?

### Opening Hand Strategy

4. **Mulligan Aggressiveness**: 69.9% of games keep opening 7. Should mulligan strategy be more or less aggressive?

5. **Pattern Recognition**: Best patterns include Survival + multiple creatures. Does this suggest prioritizing creature-heavy hands?

### Card Choices

6. **Underperforming Cards**: Which cards show low cast rates relative to seen rates?

7. **Missing Roles**: Are there gaps in the deck's functionality that sideboard analysis reveals?

## Recommended Analysis Steps

1. **Test Variants**: Run simulations with:
   - +1 creature, -1 spell
   - +1 land, -1 spell
   - Alternative card selection (e.g., more cantrips)

2. **Deeper Pattern Analysis**: Identify why certain patterns succeed

3. **Sideboard Testing**: Test post-board configurations for key matchups

4. **Alternative Win Conditions**: Should deck have backup plans if Survival fails?

## Raw Data Files

For detailed analysis, reference:
- `simulation_results.xlsx` - All simulation data
- `deck.csv` - Current deck list
- `simulation_config.json` - Configuration and ideal setups

---

*This analysis is optimized for LLM review. Provide this document along with specific questions about deck building strategy.*
