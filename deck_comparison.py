"""
Deck comparison engine for analyzing differences between two deck configurations.

This module provides the main comparison functionality that:
- Runs simulations for both decks
- Calculates all deltas
- Generates insights
- Returns comprehensive comparison results
"""

import sys
from comparison_utils import (
    load_deck_cards,
    calculate_deck_differences,
    calculate_all_deltas,
    compare_opening_hand_patterns,
    generate_insights,
    rank_changes_by_impact
)


class DeckComparison:
    """Container for deck comparison results."""
    
    def __init__(self, baseline_path, variant_path, baseline_results,
                 variant_results, deck_diffs, deltas, pattern_comparison, insights):
        self.baseline_path = baseline_path
        self.variant_path = variant_path
        self.baseline_results = baseline_results
        self.variant_results = variant_results
        self.deck_diffs = deck_diffs
        self.deltas = deltas
        self.pattern_comparison = pattern_comparison
        self.insights = insights
        
    def __repr__(self):
        return f"DeckComparison(baseline={self.baseline_path}, variant={self.variant_path})"


def compare_decks(baseline_path, variant_path, runs, turns, config, progress_callback=None):
    """
    Compare two deck configurations by running simulations and analyzing differences.
    
    Args:
        baseline_path: Path to baseline deck CSV
        variant_path: Path to variant deck CSV
        runs: Number of simulation runs per deck
        turns: Number of turns to simulate
        config: Simulation configuration dict
        progress_callback: Optional function to call with progress updates
        
    Returns:
        DeckComparison object with all comparison data
    """
    # Import here to avoid circular dependency
    from madness import run_simulations
    
    # Step 1: Load both decks and calculate differences
    if progress_callback:
        progress_callback("Loading decks and calculating differences...")
    
    baseline_cards = load_deck_cards(baseline_path)
    variant_cards = load_deck_cards(variant_path)
    deck_diffs = calculate_deck_differences(baseline_cards, variant_cards)
    
    # Step 2: Run simulations for baseline
    if progress_callback:
        progress_callback(f"Running {runs} simulations for baseline deck...")
    
    baseline_tuple = run_simulations(baseline_path, runs, turns, config)
    baseline_results = {
        'card_stats_df': baseline_tuple[0],
        'key_card_stats_df': baseline_tuple[1],
        'ideal_setups_df': baseline_tuple[2],
        'mulligan_stats_df': baseline_tuple[3],
        'graveyard_df': baseline_tuple[4],
        'battlefield_df': baseline_tuple[5],
        'madness_df': baseline_tuple[6],
        'flashback_df': baseline_tuple[7],
        'tutored_df': baseline_tuple[8],
        'opening_hands_df': baseline_tuple[9],
        'summary': baseline_tuple[10]
    }
    
    # Step 3: Run simulations for variant
    if progress_callback:
        progress_callback(f"Running {runs} simulations for variant deck...")
    
    variant_tuple = run_simulations(variant_path, runs, turns, config)
    variant_results = {
        'card_stats_df': variant_tuple[0],
        'key_card_stats_df': variant_tuple[1],
        'ideal_setups_df': variant_tuple[2],
        'mulligan_stats_df': variant_tuple[3],
        'graveyard_df': variant_tuple[4],
        'battlefield_df': variant_tuple[5],
        'madness_df': variant_tuple[6],
        'flashback_df': variant_tuple[7],
        'tutored_df': variant_tuple[8],
        'opening_hands_df': variant_tuple[9],
        'summary': variant_tuple[10]
    }
    
    # Step 4: Calculate all deltas
    if progress_callback:
        progress_callback("Calculating deltas...")
    
    deltas = calculate_all_deltas(baseline_results, variant_results)
    
    # Step 5: Compare opening hand patterns
    if progress_callback:
        progress_callback("Comparing opening hand patterns...")
    
    pattern_comparison = compare_opening_hand_patterns(
        baseline_results, variant_results, top_n=15
    )
    
    # Step 6: Generate insights
    if progress_callback:
        progress_callback("Generating insights...")
    
    insights = generate_insights(deck_diffs, deltas, pattern_comparison)
    
    # Create and return comparison object
    comparison = DeckComparison(
        baseline_path=baseline_path,
        variant_path=variant_path,
        baseline_results=baseline_results,
        variant_results=variant_results,
        deck_diffs=deck_diffs,
        deltas=deltas,
        pattern_comparison=pattern_comparison,
        insights=insights
    )
    
    if progress_callback:
        progress_callback("Comparison complete!")
    
    return comparison


def print_comparison_summary(comparison):
    """
    Print a formatted summary of the comparison to console.
    
    Args:
        comparison: DeckComparison object
    """
    print("\n" + "="*80)
    print("DECK COMPARISON SUMMARY".center(80))
    print("="*80)
    
    # Deck info
    print(f"\nBaseline: {comparison.baseline_path}")
    print(f"Variant:  {comparison.variant_path}")
    
    # Card changes
    print("\n" + "-"*80)
    print("CARD CHANGES")
    print("-"*80)
    
    diffs = comparison.deck_diffs
    
    if diffs['cards_added']:
        print("\n✅ Added:")
        for card, qty in sorted(diffs['cards_added'].items()):
            print(f"   +{qty} {card}")
    
    if diffs['cards_removed']:
        print("\n❌ Removed:")
        for card, qty in sorted(diffs['cards_removed'].items()):
            print(f"   -{qty} {card}")
    
    if diffs['cards_changed']:
        print("\n🔄 Changed:")
        for card, change in sorted(diffs['cards_changed'].items()):
            delta = change['delta']
            print(f"   {card}: {change['baseline']} → {change['variant']} ({delta:+d})")
    
    if diffs['total_changes'] == 0:
        print("\n⚠️  No card changes detected (identical decks)")
    
    # Ideal setup comparison
    print("\n" + "-"*80)
    print("IDEAL SETUP COMPARISON")
    print("-"*80)
    print(f"\n{'Setup':<30} {'Baseline':>10} {'Variant':>10} {'Delta':>12}")
    print("-"*70)
    
    for setup_name, delta_data in sorted(comparison.deltas['ideal_setups'].items()):
        baseline = delta_data['baseline']
        variant = delta_data['variant']
        delta = delta_data['delta']
        
        # Add emoji indicator
        if delta > 1:
            indicator = "✅"
        elif delta < -1:
            indicator = "⚠️"
        else:
            indicator = "⚖️"
        
        print(f"{setup_name:<30} {baseline:>9.1f}% {variant:>9.1f}% {delta:>+10.1f}% {indicator}")
    
    # Mulligan comparison
    print("\n" + "-"*80)
    print("MULLIGAN COMPARISON")
    print("-"*80)
    
    mull_data = comparison.deltas['mulligans']
    print(f"\nAverage Mulligans: {mull_data['baseline']:.2f} → {mull_data['variant']:.2f} ({mull_data['delta']:+.2f})")
    
    no_mull_data = comparison.deltas['summary']['games_no_mulligan']
    print(f"Games with 0 Mulligans: {no_mull_data['baseline']:.1f}% → {no_mull_data['variant']:.1f}% ({no_mull_data['delta']:+.1f}%)")
    
    # Opening hand patterns
    print("\n" + "-"*80)
    print("OPENING HAND PATTERN CHANGES")
    print("-"*80)
    
    pc = comparison.pattern_comparison
    
    if pc['common_patterns']:
        print(f"\n✅ {len(pc['common_patterns'])} patterns present in both decks")
        
        # Show top 5 common patterns by improvement
        common_sorted = sorted(
            pc['common_patterns'].items(),
            key=lambda x: x[1]['variant_avg_success'] - x[1]['baseline_avg_success'],
            reverse=True
        )[:5]
        
        if common_sorted:
            print("\nTop Improved Patterns:")
            for pattern, data in common_sorted:
                delta = data['variant_avg_success'] - data['baseline_avg_success']
                if delta > 0:
                    print(f"   {pattern}")
                    print(f"      Success: {data['baseline_avg_success']:.1f}% → {data['variant_avg_success']:.1f}% ({delta:+.1f}%)")
    
    if pc['variant_only']:
        print(f"\n🆕 {len(pc['variant_only'])} new patterns in variant")
        for pattern in list(pc['variant_only'])[:3]:
            print(f"   {pattern}")
    
    if pc['baseline_only']:
        print(f"\n❌ {len(pc['baseline_only'])} patterns lost in variant")
        for pattern in list(pc['baseline_only'])[:3]:
            print(f"   {pattern}")
    
    # Key insights
    print("\n" + "-"*80)
    print("KEY INSIGHTS")
    print("-"*80)
    
    insights = comparison.insights
    
    if insights['improvements']:
        print("\n✅ Improvements:")
        for improvement in insights['improvements']:
            print(f"   • {improvement}")
    
    if insights['declines']:
        print("\n⚠️  Declines:")
        for decline in insights['declines']:
            print(f"   • {decline}")
    
    if insights['neutral']:
        print("\n⚖️  Neutral Changes:")
        for neutral in insights['neutral']:
            print(f"   • {neutral}")
    
    if insights['key_takeaways']:
        print("\n📊 Key Takeaways:")
        for takeaway in insights['key_takeaways']:
            print(f"   • {takeaway}")
    
    print("\n" + "="*80 + "\n")


def print_comparison_progress(message):
    """Simple progress callback that prints to console."""
    print(f"[Comparison] {message}")

