"""
Export Experiment Module

Exports experiment results to Excel and Markdown formats.
"""

import pandas as pd
from typing import Dict, Any
from datetime import datetime

from experiment_analyzer import AnalyzedExperiment, VariantRanking


def export_experiment_results(analyzed: AnalyzedExperiment, output_file: str):
    """
    Export experiment results to Excel.
    
    Args:
        analyzed: Analyzed experiment
        output_file: Path to output Excel file
    """
    print(f"\nExporting results to {output_file}...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_df = create_summary_sheet(analyzed)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Rankings
        rankings_df = create_rankings_sheet(analyzed)
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 3: Variant Details
        details_df = create_variant_details_sheet(analyzed)
        details_df.to_excel(writer, sheet_name='Variant Details', index=False)
        
        # Sheet 4: Top 5 Comparison
        if len(analyzed.rankings) >= 5:
            top5_df = create_top_variants_comparison(analyzed, n=5)
            top5_df.to_excel(writer, sheet_name='Top 5 Comparison', index=False)
        
        # Sheet 5: Statistical Analysis
        stats_df = create_statistical_analysis(analyzed)
        stats_df.to_excel(writer, sheet_name='Statistical Analysis', index=False)
        
        # Sheet 6: Insights
        insights_df = create_insights_sheet(analyzed)
        insights_df.to_excel(writer, sheet_name='Insights', index=False)
    
    print(f"✓ Exported to {output_file}")


def create_summary_sheet(analyzed: AnalyzedExperiment) -> pd.DataFrame:
    """Create summary sheet with experiment overview."""
    config = analyzed.experiment_results.config
    stats = analyzed.statistics
    
    rows = [
        {'Metric': 'Experiment Name', 'Value': config.name},
        {'Metric': 'Base Deck', 'Value': config.base_deck},
        {'Metric': 'Optimization Goal', 'Value': config.optimization_goal},
        {'Metric': 'Runs per Variant', 'Value': config.runs_per_variant},
        {'Metric': 'Total Variants', 'Value': stats.get('total_variants', 0)},
        {'Metric': 'Execution Time (s)', 'Value': f"{analyzed.experiment_results.execution_time:.1f}"},
        {'Metric': '', 'Value': ''},
        {'Metric': 'Baseline Score', 'Value': f"{stats.get('baseline_score', 0):.3f}"},
        {'Metric': 'Best Score', 'Value': f"{stats.get('best_score', 0):.3f}"},
        {'Metric': 'Average Score', 'Value': f"{stats.get('average_score', 0):.3f}"},
        {'Metric': 'Score Range', 'Value': f"{stats.get('score_range', 0):.3f}"},
        {'Metric': '', 'Value': ''},
        {'Metric': 'Average Improvement', 'Value': f"{stats.get('average_delta', 0):.3f}"},
        {'Metric': 'Average Improvement %', 'Value': f"{stats.get('average_delta_pct', 0):.1f}%"},
        {'Metric': 'Max Improvement', 'Value': f"{stats.get('max_improvement', 0):.3f}"},
        {'Metric': 'Max Improvement %', 'Value': f"{stats.get('max_improvement_pct', 0):.1f}%"},
    ]
    
    return pd.DataFrame(rows)


def create_rankings_sheet(analyzed: AnalyzedExperiment) -> pd.DataFrame:
    """Create rankings table."""
    rows = []
    
    for ranking in analyzed.rankings:
        # Format changes
        changes_summary = ranking.variant.summary()
        
        sign = "+" if ranking.delta > 0 else ""
        
        row = {
            'Rank': ranking.rank,
            'Variant Name': ranking.variant.name,
            'Score': f"{ranking.score:.3f}",
            'Baseline Score': f"{ranking.baseline_score:.3f}",
            'Delta': f"{sign}{ranking.delta:.3f}",
            'Delta %': f"{sign}{ranking.delta_pct:.1f}%",
            'Recommendation': ranking.recommendation,
            'Changes': changes_summary
        }
        
        # Add secondary goals
        for goal, score in ranking.secondary_scores.items():
            row[f'Secondary: {goal}'] = f"{score:.3f}"
        
        rows.append(row)
    
    return pd.DataFrame(rows)


def create_variant_details_sheet(analyzed: AnalyzedExperiment) -> pd.DataFrame:
    """Create detailed variant information."""
    rows = []
    
    for ranking in analyzed.rankings:
        variant = ranking.variant
        
        # Get each change as a separate row
        for change in variant.changes:
            rows.append({
                'Rank': ranking.rank,
                'Variant Name': variant.name,
                'Change Type': change.type,
                'Card': change.card,
                'Baseline Qty': change.baseline_qty,
                'Variant Qty': change.variant_qty,
                'Delta': change.delta,
                'Score': f"{ranking.score:.3f}",
                'Recommendation': ranking.recommendation
            })
    
    return pd.DataFrame(rows)


def create_top_variants_comparison(analyzed: AnalyzedExperiment, n: int = 5) -> pd.DataFrame:
    """Create side-by-side comparison of top N variants."""
    top_n = analyzed.rankings[:n]
    
    # Collect all unique cards that changed
    all_cards = set()
    for ranking in top_n:
        for change in ranking.variant.changes:
            all_cards.add(change.card)
    
    # Build comparison table
    rows = []
    
    # Add baseline row
    baseline_row = {'Card': 'BASELINE'}
    exp_results = analyzed.experiment_results
    baseline_deck = pd.read_csv(exp_results.config.base_deck)
    
    for ranking in top_n:
        baseline_row[f"#{ranking.rank} {ranking.variant.name}"] = "Baseline"
    
    rows.append(baseline_row)
    
    # Add card rows
    for card in sorted(all_cards):
        row = {'Card': card}
        
        # Get baseline quantity
        baseline_row_data = baseline_deck[baseline_deck['Card Name'] == card]
        baseline_qty = int(baseline_row_data['Quantity'].values[0]) if not baseline_row_data.empty else 0
        
        for ranking in top_n:
            # Find this card's quantity in variant
            variant_qty = baseline_qty
            for change in ranking.variant.changes:
                if change.card == card:
                    variant_qty = change.variant_qty
                    break
            
            delta = variant_qty - baseline_qty
            if delta > 0:
                row[f"#{ranking.rank} {ranking.variant.name}"] = f"{variant_qty} (+{delta})"
            elif delta < 0:
                row[f"#{ranking.rank} {ranking.variant.name}"] = f"{variant_qty} ({delta})"
            else:
                row[f"#{ranking.rank} {ranking.variant.name}"] = f"{variant_qty}"
        
        rows.append(row)
    
    # Add score row
    score_row = {'Card': '--- SCORE ---'}
    for ranking in top_n:
        score_row[f"#{ranking.rank} {ranking.variant.name}"] = f"{ranking.score:.3f}"
    rows.append(score_row)
    
    return pd.DataFrame(rows)


def create_statistical_analysis(analyzed: AnalyzedExperiment) -> pd.DataFrame:
    """Create statistical analysis table."""
    stats = analyzed.statistics
    
    rows = []
    
    # Overall statistics
    rows.append({'Category': 'Overall', 'Metric': 'Total Variants', 'Value': stats.get('total_variants', 0)})
    rows.append({'Category': 'Overall', 'Metric': 'Baseline Score', 'Value': f"{stats.get('baseline_score', 0):.3f}"})
    rows.append({'Category': 'Overall', 'Metric': 'Best Score', 'Value': f"{stats.get('best_score', 0):.3f}"})
    rows.append({'Category': 'Overall', 'Metric': 'Worst Score', 'Value': f"{stats.get('worst_score', 0):.3f}"})
    rows.append({'Category': 'Overall', 'Metric': 'Average Score', 'Value': f"{stats.get('average_score', 0):.3f}"})
    rows.append({'Category': 'Overall', 'Metric': 'Median Score', 'Value': f"{stats.get('median_score', 0):.3f}"})
    rows.append({'Category': 'Overall', 'Metric': 'Score Range', 'Value': f"{stats.get('score_range', 0):.3f}"})
    
    # Improvement statistics
    rows.append({'Category': 'Improvement', 'Metric': 'Average Delta', 'Value': f"{stats.get('average_delta', 0):.3f}"})
    rows.append({'Category': 'Improvement', 'Metric': 'Average Delta %', 'Value': f"{stats.get('average_delta_pct', 0):.1f}%"})
    rows.append({'Category': 'Improvement', 'Metric': 'Max Improvement', 'Value': f"{stats.get('max_improvement', 0):.3f}"})
    rows.append({'Category': 'Improvement', 'Metric': 'Max Improvement %', 'Value': f"{stats.get('max_improvement_pct', 0):.1f}%"})
    
    # Recommendation distribution
    for rec, count in stats.get('recommendations', {}).items():
        pct = (count / stats.get('total_variants', 1)) * 100
        rows.append({'Category': 'Recommendations', 'Metric': rec, 'Value': f"{count} ({pct:.1f}%)"})
    
    return pd.DataFrame(rows)


def create_insights_sheet(analyzed: AnalyzedExperiment) -> pd.DataFrame:
    """Create insights table."""
    rows = []
    
    for i, insight in enumerate(analyzed.insights, 1):
        rows.append({'#': i, 'Insight': insight})
    
    return pd.DataFrame(rows)


def export_experiment_markdown(analyzed: AnalyzedExperiment, output_file: str):
    """
    Export experiment results to Markdown summary.
    
    Args:
        analyzed: Analyzed experiment
        output_file: Path to output markdown file
    """
    config = analyzed.experiment_results.config
    stats = analyzed.statistics
    
    md_content = f"""# Experiment Results: {config.name}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Configuration

- **Base Deck**: {config.base_deck}
- **Optimization Goal**: {config.optimization_goal}
- **Runs per Variant**: {config.runs_per_variant:,}
- **Total Variants**: {stats.get('total_variants', 0)}
- **Execution Time**: {analyzed.experiment_results.execution_time:.1f}s

## Summary

- **Baseline Score**: {stats.get('baseline_score', 0):.3f}
- **Best Score**: {stats.get('best_score', 0):.3f} (Rank #1)
- **Average Score**: {stats.get('average_score', 0):.3f}
- **Average Improvement**: {stats.get('average_delta', 0):.3f} ({stats.get('average_delta_pct', 0):.1f}%)

## Top 5 Variants

| Rank | Variant | Score | Delta | Δ% | Recommendation |
|------|---------|-------|-------|-----|----------------|
"""
    
    # Add top 5 rankings
    for ranking in analyzed.rankings[:5]:
        sign = "+" if ranking.delta > 0 else ""
        md_content += f"| {ranking.rank} | {ranking.variant.name} | {ranking.score:.3f} | {sign}{ranking.delta:.3f} | {sign}{ranking.delta_pct:.1f}% | {ranking.recommendation} |\n"
    
    md_content += "\n## Key Insights\n\n"
    
    for insight in analyzed.insights:
        md_content += f"- {insight}\n"
    
    md_content += "\n## Best Variant Details\n\n"
    
    if analyzed.rankings:
        best = analyzed.rankings[0]
        md_content += f"**Variant**: {best.variant.name}\n\n"
        md_content += f"**Score**: {best.score:.3f} (baseline: {best.baseline_score:.3f})\n\n"
        md_content += f"**Changes**:\n"
        for change in best.variant.changes:
            md_content += f"- {change}\n"
        
        if best.secondary_scores:
            md_content += "\n**Secondary Goals**:\n"
            for goal, score in best.secondary_scores.items():
                md_content += f"- {goal}: {score:.3f}\n"
    
    md_content += "\n## Recommendation Distribution\n\n"
    
    for rec, count in stats.get('recommendations', {}).items():
        pct = (count / stats.get('total_variants', 1)) * 100
        md_content += f"- **{rec}**: {count} variants ({pct:.1f}%)\n"
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(md_content)
    
    print(f"✓ Exported markdown summary to {output_file}")


if __name__ == "__main__":
    # Test export
    print("Testing experiment export...")
    
    from experiment_config import load_experiment_config
    from experiment_runner import run_experiment
    from experiment_analyzer import analyze_experiment
    import json
    
    # Load configs
    experiment_config = load_experiment_config("experiments/test.json")
    
    with open("simulation_config.json", 'r') as f:
        sim_config = json.load(f)
    
    # Run experiment
    print("Running experiment...")
    experiment_results = run_experiment(experiment_config, sim_config, num_workers=2)
    
    if experiment_results:
        # Analyze
        print("Analyzing results...")
        analyzed = analyze_experiment(experiment_results)
        
        # Export
        export_experiment_results(analyzed, "test_experiment_results.xlsx")
        export_experiment_markdown(analyzed, "test_experiment_results.md")

