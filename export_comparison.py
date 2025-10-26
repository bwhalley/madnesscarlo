"""
Export deck comparison results to various formats (Excel, Markdown).

This module handles exporting comparison data in formats optimized for
analysis and sharing.
"""

import pandas as pd
from datetime import datetime


def export_comparison_to_excel(comparison, output_file):
    """
    Export comparison results to Excel with multiple sheets.
    
    Args:
        comparison: DeckComparison object
        output_file: Output Excel file path
    """
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_df = create_summary_sheet(comparison)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Deck Changes
        deck_changes_df = create_deck_changes_sheet(comparison)
        deck_changes_df.to_excel(writer, sheet_name='Deck Changes', index=False)
        
        # Sheet 3: Setup Comparison
        setup_df = create_setup_comparison_sheet(comparison)
        setup_df.to_excel(writer, sheet_name='Setup Comparison', index=False)
        
        # Sheet 4: Key Card Comparison
        key_card_df = create_key_card_comparison_sheet(comparison)
        key_card_df.to_excel(writer, sheet_name='Key Card Comparison', index=False)
        
        # Sheet 5: Opening Hand Patterns
        pattern_df = create_pattern_comparison_sheet(comparison)
        pattern_df.to_excel(writer, sheet_name='Opening Hand Patterns', index=False)
        
        # Sheet 6: Insights
        insights_df = create_insights_sheet(comparison)
        insights_df.to_excel(writer, sheet_name='Insights', index=False)
    
    print(f"\n✅ Comparison results exported to: {output_file}")


def create_summary_sheet(comparison):
    """Create high-level summary comparison table."""
    rows = []
    
    # Metadata
    rows.append({
        'Metric': 'Baseline Deck',
        'Value': comparison.baseline_path,
        'Notes': ''
    })
    
    rows.append({
        'Metric': 'Variant Deck',
        'Value': comparison.variant_path,
        'Notes': ''
    })
    
    rows.append({
        'Metric': 'Total Card Changes',
        'Value': comparison.deck_diffs['total_changes'],
        'Notes': f"{len(comparison.deck_diffs['cards_added'])} added, {len(comparison.deck_diffs['cards_removed'])} removed"
    })
    
    rows.append({'Metric': '', 'Value': '', 'Notes': ''})  # Blank row
    
    # Key metrics
    rows.append({
        'Metric': 'PERFORMANCE METRICS',
        'Value': '',
        'Notes': ''
    })
    
    # Mulligans
    mull = comparison.deltas['mulligans']
    rows.append({
        'Metric': 'Average Mulligans',
        'Value': f"{mull['baseline']:.2f} → {mull['variant']:.2f}",
        'Notes': f"Delta: {mull['delta']:+.2f}"
    })
    
    # Games with 0 mulligans
    no_mull = comparison.deltas['summary']['games_no_mulligan']
    rows.append({
        'Metric': 'Games with 0 Mulligans',
        'Value': f"{no_mull['baseline']:.1f}% → {no_mull['variant']:.1f}%",
        'Notes': f"Delta: {no_mull['delta']:+.1f}%"
    })
    
    rows.append({'Metric': '', 'Value': '', 'Notes': ''})  # Blank row
    
    # Top ideal setup changes
    rows.append({
        'Metric': 'TOP SETUP CHANGES',
        'Value': '',
        'Notes': ''
    })
    
    # Sort setups by absolute delta
    sorted_setups = sorted(
        comparison.deltas['ideal_setups'].items(),
        key=lambda x: abs(x[1]['delta']),
        reverse=True
    )
    
    for setup_name, delta_data in sorted_setups[:5]:
        rows.append({
            'Metric': setup_name,
            'Value': f"{delta_data['baseline']:.1f}% → {delta_data['variant']:.1f}%",
            'Notes': f"Delta: {delta_data['delta']:+.1f}%"
        })
    
    return pd.DataFrame(rows)


def create_deck_changes_sheet(comparison):
    """Create detailed deck changes table."""
    rows = []
    
    diffs = comparison.deck_diffs
    
    # Added cards
    for card, qty in sorted(diffs['cards_added'].items()):
        rows.append({
            'Change Type': 'Added',
            'Card Name': card,
            'Baseline Qty': 0,
            'Variant Qty': qty,
            'Delta': qty
        })
    
    # Removed cards
    for card, qty in sorted(diffs['cards_removed'].items()):
        rows.append({
            'Change Type': 'Removed',
            'Card Name': card,
            'Baseline Qty': qty,
            'Variant Qty': 0,
            'Delta': -qty
        })
    
    # Changed cards
    for card, change in sorted(diffs['cards_changed'].items()):
        rows.append({
            'Change Type': 'Modified',
            'Card Name': card,
            'Baseline Qty': change['baseline'],
            'Variant Qty': change['variant'],
            'Delta': change['delta']
        })
    
    if not rows:
        rows.append({
            'Change Type': 'None',
            'Card Name': 'No changes detected',
            'Baseline Qty': 0,
            'Variant Qty': 0,
            'Delta': 0
        })
    
    return pd.DataFrame(rows)


def create_setup_comparison_sheet(comparison):
    """Create ideal setup comparison table."""
    rows = []
    
    for setup_name, delta_data in sorted(comparison.deltas['ideal_setups'].items()):
        # Determine assessment
        delta = delta_data['delta']
        if delta > 5:
            assessment = 'Major Improvement'
        elif delta > 1:
            assessment = 'Improved'
        elif delta < -5:
            assessment = 'Major Decline'
        elif delta < -1:
            assessment = 'Declined'
        else:
            assessment = 'No Change'
        
        rows.append({
            'Setup': setup_name,
            'Baseline %': delta_data['baseline'],
            'Variant %': delta_data['variant'],
            'Delta': delta_data['delta'],
            'Delta %': delta_data['delta_pct'] if delta_data['delta_pct'] is not None else 'N/A',
            'Assessment': assessment
        })
    
    return pd.DataFrame(rows)


def create_key_card_comparison_sheet(comparison):
    """Create key card access comparison table."""
    rows = []
    
    for card_name, delta_data in sorted(comparison.deltas['key_cards'].items()):
        delta = delta_data['delta']
        
        # Determine assessment
        if delta > 5:
            assessment = 'Much More Visible'
        elif delta > 2:
            assessment = 'More Visible'
        elif delta < -5:
            assessment = 'Much Less Visible'
        elif delta < -2:
            assessment = 'Less Visible'
        else:
            assessment = 'Similar Visibility'
        
        rows.append({
            'Card': card_name,
            'Baseline Seen %': delta_data['baseline'],
            'Variant Seen %': delta_data['variant'],
            'Delta': delta_data['delta'],
            'Assessment': assessment
        })
    
    return pd.DataFrame(rows)


def create_pattern_comparison_sheet(comparison):
    """Create opening hand pattern comparison table."""
    rows = []
    
    pc = comparison.pattern_comparison
    
    # Common patterns
    for pattern, data in sorted(pc['common_patterns'].items(), 
                                 key=lambda x: x[1]['variant_avg_success'] - x[1]['baseline_avg_success'],
                                 reverse=True):
        rows.append({
            'Pattern': pattern,
            'Status': 'Common',
            'Baseline Games': data['baseline_games'],
            'Variant Games': data['variant_games'],
            'Baseline Success %': data['baseline_avg_success'],
            'Variant Success %': data['variant_avg_success'],
            'Success Delta': data['variant_avg_success'] - data['baseline_avg_success'],
            'Baseline Mulligans': data['baseline_mulligans'],
            'Variant Mulligans': data['variant_mulligans']
        })
    
    # Baseline-only patterns
    for pattern_data in pc['baseline_top_patterns']:
        if pattern_data['Pattern'] in pc['baseline_only']:
            rows.append({
                'Pattern': pattern_data['Pattern'],
                'Status': 'Baseline Only',
                'Baseline Games': pattern_data['Games'],
                'Variant Games': 0,
                'Baseline Success %': pattern_data.get('Avg Success %', 0),
                'Variant Success %': None,
                'Success Delta': None,
                'Baseline Mulligans': pattern_data['Median Mulligans'],
                'Variant Mulligans': None
            })
    
    # Variant-only patterns
    for pattern_data in pc['variant_top_patterns']:
        if pattern_data['Pattern'] in pc['variant_only']:
            rows.append({
                'Pattern': pattern_data['Pattern'],
                'Status': 'Variant Only',
                'Baseline Games': 0,
                'Variant Games': pattern_data['Games'],
                'Baseline Success %': None,
                'Variant Success %': pattern_data.get('Avg Success %', 0),
                'Success Delta': None,
                'Baseline Mulligans': None,
                'Variant Mulligans': pattern_data['Median Mulligans']
            })
    
    return pd.DataFrame(rows)


def create_insights_sheet(comparison):
    """Create insights summary table."""
    rows = []
    
    insights = comparison.insights
    
    # Improvements
    for improvement in insights['improvements']:
        rows.append({
            'Category': 'Improvement',
            'Insight': improvement
        })
    
    # Declines
    for decline in insights['declines']:
        rows.append({
            'Category': 'Decline',
            'Insight': decline
        })
    
    # Neutral
    for neutral in insights['neutral']:
        rows.append({
            'Category': 'Neutral',
            'Insight': neutral
        })
    
    # Key takeaways
    for takeaway in insights['key_takeaways']:
        rows.append({
            'Category': 'Key Takeaway',
            'Insight': takeaway
        })
    
    return pd.DataFrame(rows)


def export_comparison_to_markdown(comparison, output_file):
    """
    Export comparison summary to Markdown format.
    
    Args:
        comparison: DeckComparison object
        output_file: Output Markdown file path
    """
    with open(output_file, 'w') as f:
        f.write("# Deck Comparison Summary\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Deck info
        f.write("## Deck Information\n\n")
        f.write(f"- **Baseline**: `{comparison.baseline_path}`\n")
        f.write(f"- **Variant**: `{comparison.variant_path}`\n")
        f.write(f"- **Total Changes**: {comparison.deck_diffs['total_changes']} cards\n\n")
        
        # Card changes
        f.write("## Card Changes\n\n")
        
        diffs = comparison.deck_diffs
        
        if diffs['cards_added']:
            f.write("### Added\n")
            for card, qty in sorted(diffs['cards_added'].items()):
                f.write(f"- **+{qty}** {card}\n")
            f.write("\n")
        
        if diffs['cards_removed']:
            f.write("### Removed\n")
            for card, qty in sorted(diffs['cards_removed'].items()):
                f.write(f"- **-{qty}** {card}\n")
            f.write("\n")
        
        if diffs['cards_changed']:
            f.write("### Modified\n")
            for card, change in sorted(diffs['cards_changed'].items()):
                f.write(f"- **{card}**: {change['baseline']} → {change['variant']} ({change['delta']:+d})\n")
            f.write("\n")
        
        # Ideal setup comparison
        f.write("## Ideal Setup Performance\n\n")
        f.write("| Setup | Baseline | Variant | Delta | Assessment |\n")
        f.write("|-------|----------|---------|-------|------------|\n")
        
        for setup_name, delta_data in sorted(comparison.deltas['ideal_setups'].items()):
            delta = delta_data['delta']
            if delta > 1:
                assessment = "✅ Improved"
            elif delta < -1:
                assessment = "⚠️ Declined"
            else:
                assessment = "⚖️ No Change"
            
            f.write(f"| {setup_name} | {delta_data['baseline']:.1f}% | "
                   f"{delta_data['variant']:.1f}% | **{delta:+.1f}%** | {assessment} |\n")
        
        f.write("\n")
        
        # Opening hand insights
        f.write("## Opening Hand Analysis\n\n")
        
        pc = comparison.pattern_comparison
        
        if pc['common_patterns']:
            f.write(f"### Common Patterns ({len(pc['common_patterns'])} patterns)\n\n")
            
            # Top 5 improved patterns
            common_sorted = sorted(
                pc['common_patterns'].items(),
                key=lambda x: x[1]['variant_avg_success'] - x[1]['baseline_avg_success'],
                reverse=True
            )[:5]
            
            if any(data['variant_avg_success'] - data['baseline_avg_success'] > 0 
                   for _, data in common_sorted):
                f.write("**Top Improved Patterns:**\n\n")
                for pattern, data in common_sorted:
                    delta = data['variant_avg_success'] - data['baseline_avg_success']
                    if delta > 0:
                        f.write(f"- `{pattern}`\n")
                        f.write(f"  - Success: {data['baseline_avg_success']:.1f}% → "
                               f"{data['variant_avg_success']:.1f}% (**{delta:+.1f}%**)\n")
                        f.write(f"  - Mulligans: {data['baseline_mulligans']:.1f} → "
                               f"{data['variant_mulligans']:.1f}\n")
                f.write("\n")
        
        if pc['variant_only']:
            f.write(f"### New Patterns in Variant ({len(pc['variant_only'])} patterns)\n\n")
            for pattern in list(pc['variant_only'])[:5]:
                f.write(f"- `{pattern}`\n")
            f.write("\n")
        
        if pc['baseline_only']:
            f.write(f"### Patterns Lost in Variant ({len(pc['baseline_only'])} patterns)\n\n")
            for pattern in list(pc['baseline_only'])[:5]:
                f.write(f"- `{pattern}`\n")
            f.write("\n")
        
        # Mulligan comparison
        f.write("## Mulligan Statistics\n\n")
        mull = comparison.deltas['mulligans']
        no_mull = comparison.deltas['summary']['games_no_mulligan']
        
        f.write(f"- **Average Mulligans**: {mull['baseline']:.2f} → {mull['variant']:.2f} "
               f"(**{mull['delta']:+.2f}**)\n")
        f.write(f"- **Games with 0 Mulligans**: {no_mull['baseline']:.1f}% → {no_mull['variant']:.1f}% "
               f"(**{no_mull['delta']:+.1f}%**)\n\n")
        
        # Insights
        f.write("## Key Insights\n\n")
        
        insights = comparison.insights
        
        if insights['improvements']:
            f.write("### ✅ Improvements\n\n")
            for improvement in insights['improvements']:
                f.write(f"- {improvement}\n")
            f.write("\n")
        
        if insights['declines']:
            f.write("### ⚠️ Declines\n\n")
            for decline in insights['declines']:
                f.write(f"- {decline}\n")
            f.write("\n")
        
        if insights['key_takeaways']:
            f.write("### 📊 Key Takeaways\n\n")
            for takeaway in insights['key_takeaways']:
                f.write(f"- {takeaway}\n")
            f.write("\n")
        
        # Recommendation
        f.write("## Recommendation\n\n")
        
        total_improvements = len(insights['improvements'])
        total_declines = len(insights['declines'])
        
        if total_improvements > total_declines * 1.5:
            f.write("✅ **Strong Recommendation**: Variant shows significant improvement. "
                   "Consider adopting these changes.\n\n")
        elif total_improvements > total_declines:
            f.write("✅ **Positive**: Variant shows net improvement. "
                   "Review trade-offs to ensure they align with your strategy.\n\n")
        elif total_declines > total_improvements:
            f.write("⚠️ **Caution**: Variant shows net decline. "
                   "Review whether trade-offs are worth it for your specific goals.\n\n")
        else:
            f.write("⚖️ **Mixed Results**: Similar number of improvements and declines. "
                   "Decision depends on which metrics you prioritize.\n\n")
        
        f.write("---\n\n")
        f.write("*For detailed data, see the Excel export file.*\n")
    
    print(f"✅ Comparison summary exported to: {output_file}")

