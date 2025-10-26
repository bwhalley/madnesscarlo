"""
Export simulation results in formats optimized for LLM analysis.

This module creates structured markdown documents that help LLMs provide
better deck building advice by organizing data around goals, bottlenecks,
and decision points.
"""

import pandas as pd
import json
from datetime import datetime


def export_deck_analysis_for_llm(excel_file, config, output_file="DECK_ANALYSIS_FOR_LLM.md"):
    """
    Create a comprehensive markdown document for LLM analysis.
    
    Args:
        excel_file: Path to simulation_results.xlsx
        config: Configuration dict from simulation_config.json
        output_file: Output markdown file path
    """
    
    # Load all sheets
    ideal_setups = pd.read_excel(excel_file, sheet_name='Ideal Setups')
    opening_hands = pd.read_excel(excel_file, sheet_name='Opening Hands')
    card_stats = pd.read_excel(excel_file, sheet_name='Card Stats')
    key_cards = pd.read_excel(excel_file, sheet_name='Key Card Stats')
    mulligan_stats = pd.read_excel(excel_file, sheet_name='Mulligan Stats')
    summary = pd.read_excel(excel_file, sheet_name='Summary')
    
    with open(output_file, 'w') as f:
        f.write("# UG Madness Deck - Performance Analysis for LLM Review\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write("### Deck Goal\n")
        f.write("Establish **Survival of the Fittest engine** by turn 4:\n")
        f.write("- Cast Survival of the Fittest (enchantment)\n")
        f.write("- Have any creature in hand\n")
        f.write("- Have 2+ lands and green mana\n")
        f.write("- Repeatedly discard creatures to tutor for optimal threats\n\n")
        
        # Current Performance
        f.write("### Current Performance\n\n")
        survival_success = ideal_setups[ideal_setups['Setup'] == 'Survival Engine']['Success %'].values[0]
        f.write(f"**Primary Goal Achievement: {survival_success}% games**\n\n")
        
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Survival Engine Success | {survival_success}% |\n")
        
        for _, row in ideal_setups.iterrows():
            if row['Setup'] != 'Survival Engine':
                f.write(f"| {row['Setup']} | {row['Success %']}% |\n")
        
        avg_mulligans = summary['Average Mulligans'].values[0]
        games_no_mull = summary['Games with 0 Mulligans %'].values[0]
        f.write(f"| Average Mulligans | {avg_mulligans:.2f} |\n")
        f.write(f"| Games with 0 Mulligans | {games_no_mull:.1f}% |\n\n")
        
        # Key Card Access
        f.write("## Key Card Access Analysis\n\n")
        f.write("Success depends on seeing key cards by turn 4:\n\n")
        f.write("| Card | See Rate (Turn ≤4) | Assessment |\n")
        f.write("|------|-------------------|------------|\n")
        for _, row in key_cards.iterrows():
            card = row['Key Card']
            rate = row['Seen % (Turn ≤4)']
            assessment = "✅ Good" if rate >= 60 else "⚠️ Needs Improvement" if rate >= 40 else "❌ Poor"
            f.write(f"| {card} | {rate:.1f}% | {assessment} |\n")
        f.write("\n")
        
        # Opening Hand Patterns
        f.write("## Best Opening Hand Patterns\n\n")
        f.write("Patterns that lead to Survival Engine success:\n\n")
        
        # Filter to patterns with 5+ games and Survival Engine data
        sig_hands = opening_hands[opening_hands['Games'] >= 5].copy()
        if 'Survival Engine %' in sig_hands.columns:
            survival_hands = sig_hands.dropna(subset=['Survival Engine %'])
            survival_hands = survival_hands.sort_values('Survival Engine %', ascending=False).head(10)
            
            f.write("| Pattern | Games | Median Mulligans | Survival Engine % |\n")
            f.write("|---------|-------|------------------|-------------------|\n")
            for _, row in survival_hands.iterrows():
                pattern = row['Pattern']
                games = int(row['Games'])
                mulligans = row['Median Mulligans']
                success = row['Survival Engine %']
                f.write(f"| {pattern} | {games} | {mulligans:.1f} | {success:.1f}% |\n")
            f.write("\n")
        
        # Mulligan Analysis
        f.write("## Mulligan Decision Analysis\n\n")
        f.write("| Mulligan Count | Frequency |\n")
        f.write("|----------------|----------|\n")
        for _, row in mulligan_stats.iterrows():
            count = int(row['Mulligans'])
            freq = row['Percentage']
            f.write(f"| {count} | {freq:.2f}% |\n")
        f.write("\n")
        
        # Bottleneck Analysis
        f.write("## Bottleneck Identification\n\n")
        f.write("### What's Working Well ✅\n\n")
        
        # Identify successful patterns
        if 'Survival Engine %' in sig_hands.columns:
            high_success = sig_hands[sig_hands['Survival Engine %'] >= 80]
            if len(high_success) > 0:
                f.write(f"- **{len(high_success)} hand patterns** achieve 80%+ Survival Engine success\n")
                f.write("- Common elements in successful patterns:\n")
                
                # Analyze common elements
                has_survival = sum(high_success['Pattern'].str.contains('Survival', case=False))
                has_multiple_creatures = sum(high_success['Pattern'].str.contains('[34]C', regex=True))
                has_counter = sum(high_success['Pattern'].str.contains('Counterspell', case=False))
                
                f.write(f"  - {has_survival} patterns include Survival ({has_survival/len(high_success)*100:.0f}%)\n")
                f.write(f"  - {has_multiple_creatures} patterns have 3-4 creatures ({has_multiple_creatures/len(high_success)*100:.0f}%)\n")
                f.write(f"  - {has_counter} patterns include Counterspell ({has_counter/len(high_success)*100:.0f}%)\n\n")
        
        f.write("### What's Not Working ⚠️\n\n")
        
        # Identify failure points
        f.write(f"- **{100-survival_success:.1f}%** of games fail to achieve Survival Engine\n")
        f.write("- Potential reasons:\n")
        
        survival_seen = key_cards[key_cards['Key Card'] == 'Survival of the Fittest']['Seen % (Turn ≤4)'].values[0]
        if survival_seen < 70:
            f.write(f"  - Survival only seen in {survival_seen:.1f}% of games by turn 4\n")
        
        creature_patterns = sig_hands[sig_hands['Pattern'].str.contains('0C|1C', regex=True)]
        if len(creature_patterns) > 0:
            low_creature_games = creature_patterns['Games'].sum()
            f.write(f"  - {low_creature_games} games with 0-1 creatures in opening hand\n")
        
        high_mull_games = mulligan_stats[mulligan_stats['Mulligans'] >= 2]['Percentage'].sum()
        f.write(f"  - {high_mull_games:.1f}% of games require 2+ mulligans\n\n")
        
        # Card Performance
        f.write("## Individual Card Performance\n\n")
        f.write("Cards by visibility (how often seen by turn 4):\n\n")
        
        card_stats_sorted = card_stats.sort_values('Seen %', ascending=False).head(15)
        f.write("| Card | Seen % | Cast % | Notes |\n")
        f.write("|------|--------|--------|-------|\n")
        for _, row in card_stats_sorted.iterrows():
            card = row['Card']
            seen = row['Seen %']
            cast = row['Cast %']
            
            notes = ""
            if seen < 20 and 'Land' not in card:
                notes = "⚠️ Rarely seen"
            elif cast > seen * 0.8:
                notes = "✅ High usage"
            elif cast < seen * 0.3 and 'Land' not in card:
                notes = "❓ Often not cast"
            
            f.write(f"| {card} | {seen:.1f}% | {cast:.1f}% | {notes} |\n")
        f.write("\n")
        
        # Questions for LLM
        f.write("## Strategic Questions for Analysis\n\n")
        f.write("### Deck Composition\n\n")
        f.write("1. **Land Count**: Currently shows optimal at 3 lands in opening hand. ")
        f.write("Should we adjust land ratios?\n\n")
        
        f.write("2. **Creature Density**: Survival Engine requires any creature. ")
        f.write(f"Current patterns with 3-4 creatures show {creature_patterns['Avg Success %'].mean() if len(creature_patterns) > 0 else 0:.1f}% average success. ")
        f.write("Should we increase creature count?\n\n")
        
        f.write("3. **Key Card Redundancy**: Survival of the Fittest is seen in ")
        f.write(f"{survival_seen:.1f}% of games. Should we add tutors or card selection?\n\n")
        
        f.write("### Opening Hand Strategy\n\n")
        f.write("4. **Mulligan Aggressiveness**: ")
        f.write(f"{games_no_mull:.1f}% of games keep opening 7. ")
        f.write("Should mulligan strategy be more or less aggressive?\n\n")
        
        f.write("5. **Pattern Recognition**: Best patterns include Survival + multiple creatures. ")
        f.write("Does this suggest prioritizing creature-heavy hands?\n\n")
        
        f.write("### Card Choices\n\n")
        f.write("6. **Underperforming Cards**: Which cards show low cast rates relative to seen rates?\n\n")
        
        f.write("7. **Missing Roles**: Are there gaps in the deck's functionality that sideboard ")
        f.write("analysis reveals?\n\n")
        
        # Recommended Next Steps
        f.write("## Recommended Analysis Steps\n\n")
        f.write("1. **Test Variants**: Run simulations with:\n")
        f.write("   - +1 creature, -1 spell\n")
        f.write("   - +1 land, -1 spell\n")
        f.write("   - Alternative card selection (e.g., more cantrips)\n\n")
        
        f.write("2. **Deeper Pattern Analysis**: Identify why certain patterns succeed\n\n")
        
        f.write("3. **Sideboard Testing**: Test post-board configurations for key matchups\n\n")
        
        f.write("4. **Alternative Win Conditions**: Should deck have backup plans if Survival fails?\n\n")
        
        # Raw Data Reference
        f.write("## Raw Data Files\n\n")
        f.write("For detailed analysis, reference:\n")
        f.write("- `simulation_results.xlsx` - All simulation data\n")
        f.write("- `deck.csv` - Current deck list\n")
        f.write("- `simulation_config.json` - Configuration and ideal setups\n\n")
        
        f.write("---\n\n")
        f.write("*This analysis is optimized for LLM review. Provide this document along with ")
        f.write("specific questions about deck building strategy.*\n")
    
    print(f"✅ LLM analysis document exported to {output_file}")


def export_comparative_json(baseline_file, variant_file, output_file="comparison.json"):
    """
    Export comparison data in JSON format for programmatic LLM analysis.
    """
    baseline_setups = pd.read_excel(baseline_file, sheet_name='Ideal Setups')
    variant_setups = pd.read_excel(variant_file, sheet_name='Ideal Setups')
    
    comparison = {
        "comparison_type": "deck_variant",
        "baseline": {},
        "variant": {},
        "deltas": {}
    }
    
    for _, row in baseline_setups.iterrows():
        setup = row['Setup']
        comparison["baseline"][setup] = float(row['Success %'])
    
    for _, row in variant_setups.iterrows():
        setup = row['Setup']
        comparison["variant"][setup] = float(row['Success %'])
        
        if setup in comparison["baseline"]:
            delta = comparison["variant"][setup] - comparison["baseline"][setup]
            comparison["deltas"][setup] = {
                "absolute": delta,
                "relative_pct": (delta / comparison["baseline"][setup] * 100) if comparison["baseline"][setup] > 0 else 0
            }
    
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"✅ Comparison data exported to {output_file}")


def create_llm_prompt_template(output_file="LLM_PROMPT_TEMPLATE.md"):
    """
    Create a template prompt for asking LLMs about deck building.
    """
    with open(output_file, 'w') as f:
        f.write("# LLM Prompt Template for Deck Building Analysis\n\n")
        f.write("## Prompt Structure\n\n")
        f.write("```\n")
        f.write("I'm analyzing a Magic: The Gathering UG Madness deck for Premodern format.\n\n")
        f.write("GOAL: Establish Survival of the Fittest engine by turn 4\n\n")
        f.write("CURRENT PERFORMANCE:\n")
        f.write("[Paste relevant sections from DECK_ANALYSIS_FOR_LLM.md]\n\n")
        f.write("SPECIFIC QUESTION:\n")
        f.write("[Your specific question here]\n\n")
        f.write("Please provide:\n")
        f.write("1. Analysis of current bottlenecks\n")
        f.write("2. Specific card recommendations (adds/cuts)\n")
        f.write("3. Reasoning for each recommendation\n")
        f.write("4. Expected impact on win rate\n")
        f.write("5. Potential downsides or trade-offs\n")
        f.write("```\n\n")
        
        f.write("## Example Prompts\n\n")
        f.write("### Prompt 1: General Optimization\n")
        f.write("```\n")
        f.write("My Survival Engine achieves 43.8% success rate. Patterns with Survival + ")
        f.write("multiple creatures show 90%+ success. However, I only see Survival in 63% ")
        f.write("of games by turn 4.\n\n")
        f.write("Should I:\n")
        f.write("A) Add more creatures to improve pattern success when I do see Survival\n")
        f.write("B) Add tutors/card selection to see Survival more consistently\n")
        f.write("C) Adjust land count to improve mulligan decisions\n\n")
        f.write("Current deck: [paste deck.csv]\n")
        f.write("```\n\n")
        
        f.write("### Prompt 2: Specific Card Evaluation\n")
        f.write("```\n")
        f.write("Naturalize shows 58% seen rate but only 26.9% success rate for its ideal setup.\n")
        f.write("Meanwhile, Counterspell shows 45% seen but 33.1% success rate.\n\n")
        f.write("Should I cut Naturalize for more Counterspells? What are the trade-offs?\n")
        f.write("```\n\n")
        
        f.write("### Prompt 3: Comparative Analysis\n")
        f.write("```\n")
        f.write("I tested two variants:\n")
        f.write("[Paste comparison.json contents]\n\n")
        f.write("Which variant is better and why? Are there other variants worth testing?\n")
        f.write("```\n\n")
    
    print(f"✅ LLM prompt template created: {output_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python export_llm_analysis.py <simulation_results.xlsx> [config.json]")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "simulation_config.json"
    
    # Load config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Export LLM analysis
    export_deck_analysis_for_llm(excel_file, config)
    
    # Create prompt template
    create_llm_prompt_template()
    
    print("\n📊 Ready for LLM analysis!")
    print("1. Review DECK_ANALYSIS_FOR_LLM.md")
    print("2. Use LLM_PROMPT_TEMPLATE.md for guidance")
    print("3. Paste relevant sections into your LLM conversation")

