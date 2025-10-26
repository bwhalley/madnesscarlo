"""
Utility functions for deck comparison analysis.

This module provides functions for:
- Calculating deck differences (cards added/removed)
- Computing deltas (absolute and percentage changes)
- Generating insights from comparison data
"""

import pandas as pd
from collections import Counter


def load_deck_cards(csv_path):
    """
    Load deck CSV and return dictionary of card quantities.
    
    Args:
        csv_path: Path to deck CSV file
        
    Returns:
        Dict mapping card name to quantity
    """
    df = pd.read_csv(csv_path)
    return dict(zip(df['Card Name'], df['Quantity']))


def calculate_deck_differences(baseline_cards, variant_cards):
    """
    Calculate differences between two deck configurations.
    
    Args:
        baseline_cards: Dict of {card_name: quantity} for baseline
        variant_cards: Dict of {card_name: quantity} for variant
        
    Returns:
        Dict with keys:
        - cards_added: Cards in variant but not baseline
        - cards_removed: Cards in baseline but not variant
        - cards_changed: Cards with different quantities
        - total_changes: Total number of card swaps
    """
    all_cards = set(baseline_cards.keys()) | set(variant_cards.keys())
    
    added = {}
    removed = {}
    changed = {}
    
    for card in all_cards:
        baseline_qty = baseline_cards.get(card, 0)
        variant_qty = variant_cards.get(card, 0)
        
        if baseline_qty == 0 and variant_qty > 0:
            added[card] = variant_qty
        elif variant_qty == 0 and baseline_qty > 0:
            removed[card] = baseline_qty
        elif baseline_qty != variant_qty:
            changed[card] = {
                'baseline': baseline_qty,
                'variant': variant_qty,
                'delta': variant_qty - baseline_qty
            }
    
    # Calculate total changes
    total_changes = sum(added.values()) + sum(removed.values())
    
    return {
        'cards_added': added,
        'cards_removed': removed,
        'cards_changed': changed,
        'total_changes': total_changes
    }


def calculate_metric_delta(baseline_value, variant_value, precision=2):
    """
    Calculate absolute and percentage delta for a metric.
    
    Args:
        baseline_value: Baseline metric value
        variant_value: Variant metric value
        precision: Number of decimal places for rounding
        
    Returns:
        Dict with baseline, variant, delta, and delta_pct
    """
    delta = variant_value - baseline_value
    
    # Calculate percentage change (handle division by zero)
    if baseline_value != 0:
        delta_pct = (delta / baseline_value) * 100
    else:
        delta_pct = None if variant_value == 0 else float('inf')
    
    return {
        'baseline': round(baseline_value, precision),
        'variant': round(variant_value, precision),
        'delta': round(delta, precision),
        'delta_pct': round(delta_pct, precision) if delta_pct is not None else None
    }


def calculate_all_deltas(baseline_results, variant_results):
    """
    Calculate deltas for all metrics between two simulation results.
    
    Args:
        baseline_results: Results dict from run_simulations (baseline)
        variant_results: Results dict from run_simulations (variant)
        
    Returns:
        Dict with deltas for all metrics
    """
    deltas = {
        'ideal_setups': {},
        'key_cards': {},
        'mulligans': {},
        'summary': {}
    }
    
    # Ideal setup deltas
    baseline_setups = baseline_results['ideal_setups_df']
    variant_setups = variant_results['ideal_setups_df']
    
    for _, b_row in baseline_setups.iterrows():
        setup_name = b_row['Setup']
        v_row = variant_setups[variant_setups['Setup'] == setup_name]
        
        if not v_row.empty:
            deltas['ideal_setups'][setup_name] = calculate_metric_delta(
                b_row['Success %'],
                v_row.iloc[0]['Success %']
            )
    
    # Key card access deltas
    baseline_key = baseline_results['key_card_stats_df']
    variant_key = variant_results['key_card_stats_df']
    
    for _, b_row in baseline_key.iterrows():
        card_name = b_row['Key Card']
        v_row = variant_key[variant_key['Key Card'] == card_name]
        
        if not v_row.empty:
            deltas['key_cards'][card_name] = calculate_metric_delta(
                b_row['Seen % (Turn ≤4)'],
                v_row.iloc[0]['Seen % (Turn ≤4)']
            )
    
    # Mulligan deltas
    baseline_summary = baseline_results['summary']
    variant_summary = variant_results['summary']
    
    deltas['mulligans'] = calculate_metric_delta(
        baseline_summary['Average Mulligans'],
        variant_summary['Average Mulligans']
    )
    
    # Summary metrics
    deltas['summary']['games_no_mulligan'] = calculate_metric_delta(
        baseline_summary['Games with 0 Mulligans %'],
        variant_summary['Games with 0 Mulligans %']
    )
    
    return deltas


def compare_opening_hand_patterns(baseline_results, variant_results, top_n=10):
    """
    Compare opening hand patterns between two decks.
    
    Args:
        baseline_results: Results dict with opening_hands_df
        variant_results: Results dict with opening_hands_df
        top_n: Number of top patterns to compare
        
    Returns:
        Dict with pattern comparison data
    """
    baseline_hands = baseline_results['opening_hands_df']
    variant_hands = variant_results['opening_hands_df']
    
    # Get top patterns from each (by games played)
    baseline_top = baseline_hands.nlargest(top_n, 'Games')
    variant_top = variant_hands.nlargest(top_n, 'Games')
    
    # Find common patterns
    baseline_patterns = set(baseline_top['Pattern'].values)
    variant_patterns = set(variant_top['Pattern'].values)
    
    common = baseline_patterns & variant_patterns
    baseline_only = baseline_patterns - common
    variant_only = variant_patterns - common
    
    # Compare common patterns
    common_comparison = {}
    for pattern in common:
        b_data = baseline_hands[baseline_hands['Pattern'] == pattern].iloc[0]
        v_data = variant_hands[variant_hands['Pattern'] == pattern].iloc[0]
        
        # Get setup columns (anything ending with %)
        setup_cols = [col for col in baseline_hands.columns if col.endswith(' %') and col != 'Avg Success %']
        
        common_comparison[pattern] = {
            'baseline_games': int(b_data['Games']),
            'variant_games': int(v_data['Games']),
            'baseline_mulligans': float(b_data['Median Mulligans']),
            'variant_mulligans': float(v_data['Median Mulligans']),
            'baseline_avg_success': float(b_data.get('Avg Success %', 0)),
            'variant_avg_success': float(v_data.get('Avg Success %', 0)),
            'setup_deltas': {}
        }
        
        # Calculate deltas for each setup
        for setup_col in setup_cols:
            if setup_col in b_data.index and setup_col in v_data.index:
                if pd.notna(b_data[setup_col]) and pd.notna(v_data[setup_col]):
                    common_comparison[pattern]['setup_deltas'][setup_col] = {
                        'baseline': float(b_data[setup_col]),
                        'variant': float(v_data[setup_col]),
                        'delta': float(v_data[setup_col] - b_data[setup_col])
                    }
    
    return {
        'common_patterns': common_comparison,
        'baseline_only': list(baseline_only),
        'variant_only': list(variant_only),
        'baseline_top_patterns': baseline_top[['Pattern', 'Games', 'Median Mulligans', 'Avg Success %']].to_dict('records'),
        'variant_top_patterns': variant_top[['Pattern', 'Games', 'Median Mulligans', 'Avg Success %']].to_dict('records')
    }


def generate_insights(deck_diffs, deltas, pattern_comparison):
    """
    Generate human-readable insights from comparison data.
    
    Args:
        deck_diffs: Deck differences dict
        deltas: All deltas dict
        pattern_comparison: Opening hand pattern comparison
        
    Returns:
        Dict with categorized insights
    """
    insights = {
        'improvements': [],
        'declines': [],
        'neutral': [],
        'key_takeaways': []
    }
    
    # Analyze ideal setup changes
    for setup_name, delta_data in deltas['ideal_setups'].items():
        delta = delta_data['delta']
        if abs(delta) >= 1.0:  # Significant change threshold
            insight = f"{setup_name}: {delta:+.1f}% ({delta_data['baseline']:.1f}% → {delta_data['variant']:.1f}%)"
            if delta > 0:
                insights['improvements'].append(insight)
            else:
                insights['declines'].append(insight)
    
    # Mulligan analysis
    mull_delta = deltas['mulligans']['delta']
    if abs(mull_delta) >= 0.05:
        insight = f"Average mulligans changed by {mull_delta:+.2f}"
        if mull_delta < 0:
            insights['improvements'].append(insight + " (fewer mulligans)")
        else:
            insights['declines'].append(insight + " (more mulligans)")
    
    # Pattern analysis
    if pattern_comparison['common_patterns']:
        patterns_improved = 0
        patterns_declined = 0
        
        for pattern, data in pattern_comparison['common_patterns'].items():
            avg_delta = data['variant_avg_success'] - data['baseline_avg_success']
            if avg_delta > 5:
                patterns_improved += 1
            elif avg_delta < -5:
                patterns_declined += 1
        
        if patterns_improved > 0:
            insights['improvements'].append(f"{patterns_improved} common patterns improved")
        if patterns_declined > 0:
            insights['declines'].append(f"{patterns_declined} common patterns declined")
    
    # New patterns
    if pattern_comparison['variant_only']:
        insights['neutral'].append(f"{len(pattern_comparison['variant_only'])} new opening hand patterns emerged")
    
    if pattern_comparison['baseline_only']:
        insights['neutral'].append(f"{len(pattern_comparison['baseline_only'])} opening hand patterns disappeared")
    
    # Key takeaways
    total_improvements = len(insights['improvements'])
    total_declines = len(insights['declines'])
    
    if total_improvements > total_declines:
        insights['key_takeaways'].append("Net positive: More metrics improved than declined")
    elif total_declines > total_improvements:
        insights['key_takeaways'].append("Net negative: More metrics declined than improved")
    else:
        insights['key_takeaways'].append("Mixed results: Similar number of improvements and declines")
    
    # Card change summary
    if deck_diffs['total_changes'] > 0:
        insights['key_takeaways'].append(
            f"Total of {deck_diffs['total_changes']} card changes tested"
        )
    
    return insights


def format_delta_display(delta_value, show_sign=True, precision=1):
    """
    Format a delta value for display with appropriate styling.
    
    Args:
        delta_value: Numeric delta value
        show_sign: Whether to show + sign for positive values
        precision: Decimal places
        
    Returns:
        Formatted string with emoji indicator
    """
    formatted = f"{delta_value:+.{precision}f}" if show_sign else f"{delta_value:.{precision}f}"
    
    if delta_value > 0:
        return f"{formatted} ✅"
    elif delta_value < 0:
        return f"{formatted} ⚠️"
    else:
        return f"{formatted} ⚖️"


def rank_changes_by_impact(deltas):
    """
    Rank all changes by their impact magnitude.
    
    Args:
        deltas: All deltas dict
        
    Returns:
        List of (metric_name, delta_value) tuples, sorted by impact
    """
    changes = []
    
    # Ideal setup changes
    for setup_name, delta_data in deltas['ideal_setups'].items():
        changes.append((f"Setup: {setup_name}", abs(delta_data['delta'])))
    
    # Key card changes
    for card_name, delta_data in deltas['key_cards'].items():
        changes.append((f"Card Access: {card_name}", abs(delta_data['delta'])))
    
    # Sort by absolute magnitude
    changes.sort(key=lambda x: x[1], reverse=True)
    
    return changes

