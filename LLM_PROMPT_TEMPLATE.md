# LLM Prompt Template for Deck Building Analysis

## Prompt Structure

```
I'm analyzing a Magic: The Gathering UG Madness deck for Premodern format.

GOAL: Establish Survival of the Fittest engine by turn 4

CURRENT PERFORMANCE:
[Paste relevant sections from DECK_ANALYSIS_FOR_LLM.md]

SPECIFIC QUESTION:
[Your specific question here]

Please provide:
1. Analysis of current bottlenecks
2. Specific card recommendations (adds/cuts)
3. Reasoning for each recommendation
4. Expected impact on win rate
5. Potential downsides or trade-offs
```

## Example Prompts

### Prompt 1: General Optimization
```
My Survival Engine achieves 43.8% success rate. Patterns with Survival + multiple creatures show 90%+ success. However, I only see Survival in 63% of games by turn 4.

Should I:
A) Add more creatures to improve pattern success when I do see Survival
B) Add tutors/card selection to see Survival more consistently
C) Adjust land count to improve mulligan decisions

Current deck: [paste deck.csv]
```

### Prompt 2: Specific Card Evaluation
```
Naturalize shows 58% seen rate but only 26.9% success rate for its ideal setup.
Meanwhile, Counterspell shows 45% seen but 33.1% success rate.

Should I cut Naturalize for more Counterspells? What are the trade-offs?
```

### Prompt 3: Comparative Analysis
```
I tested two variants:
[Paste comparison.json contents]

Which variant is better and why? Are there other variants worth testing?
```

