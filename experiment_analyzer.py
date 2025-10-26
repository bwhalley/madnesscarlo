"""
Experiment Analyzer Module

Analyzes and ranks experiment results based on optimization goals.
"""

import pandas as pd
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

from experiment_config import ExperimentConfig
from experiment_runner import ExperimentResults
from variant_generator import Variant


@dataclass
class VariantRanking:
    """Ranking information for a variant."""
    rank: int
    variant: Variant
    score: float
    baseline_score: float
    delta: float
    delta_pct: float
    recommendation: str
    secondary_scores: Dict[str, float] = field(default_factory=dict)
    
    def __str__(self):
        sign = "+" if self.delta > 0 else ""
        return f"#{self.rank} {self.variant.name}: {self.score:.3f} ({sign}{self.delta:.3f}, {sign}{self.delta_pct:.1f}%)"


@dataclass
class AnalyzedExperiment:
    """Complete analyzed experiment with rankings and insights."""
    experiment_results: ExperimentResults
    rankings: List[VariantRanking]
    insights: List[str]
    statistics: Dict[str, Any]


def analyze_experiment(experiment_results: ExperimentResults) -> AnalyzedExperiment:
    """
    Analyze experiment results and generate rankings.
    
    Args:
        experiment_results: Raw experiment results
        
    Returns:
        AnalyzedExperiment with rankings and insights
    """
    config = experiment_results.config
    
    # Extract scores for all variants
    baseline_score = extract_goal_score(
        experiment_results.baseline_results,
        config.optimization_goal
    )
    
    rankings = []
    for variant_result in experiment_results.variant_results:
        if not variant_result.get('success', True):
            continue
        
        variant = variant_result['variant']
        results = variant_result['results']
        
        # Get primary score
        score = extract_goal_score(results, config.optimization_goal)
        delta = score - baseline_score
        delta_pct = (delta / baseline_score * 100) if baseline_score != 0 else 0
        
        # Get secondary scores
        secondary_scores = {}
        for goal in config.secondary_goals:
            secondary_scores[goal] = extract_goal_score(results, goal)
        
        # Generate recommendation
        recommendation = generate_recommendation(delta, delta_pct, config.optimization_goal)
        
        rankings.append(VariantRanking(
            rank=0,  # Will be assigned after sorting
            variant=variant,
            score=score,
            baseline_score=baseline_score,
            delta=delta,
            delta_pct=delta_pct,
            recommendation=recommendation,
            secondary_scores=secondary_scores
        ))
    
    # Sort rankings
    rankings = sort_rankings(rankings, config.optimization_goal)
    
    # Assign rank numbers
    for i, ranking in enumerate(rankings):
        ranking.rank = i + 1
    
    # Generate insights
    insights = generate_insights(config, rankings, baseline_score)
    
    # Calculate statistics
    statistics = calculate_statistics(rankings, config)
    
    return AnalyzedExperiment(
        experiment_results=experiment_results,
        rankings=rankings,
        insights=insights,
        statistics=statistics
    )


def extract_goal_score(results: Tuple, optimization_goal: str) -> float:
    """
    Extract the metric value for the optimization goal.
    
    Args:
        results: Simulation results tuple (11 elements)
        optimization_goal: Goal to extract
        
    Returns:
        Score value
    """
    # Unpack results tuple
    card_stats_df = results[0]
    key_card_stats_df = results[1]
    ideal_setups_df = results[2]
    mana_df = results[3]
    mulligan_df = results[4]
    graveyard_df = results[5]
    battlefield_df = results[6]
    madness_df = results[7]
    flashback_df = results[8]
    tutored_df = results[9]
    opening_hands_df = results[10] if len(results) > 10 else pd.DataFrame()
    summary = results[11] if len(results) > 11 else results[10] if len(results) > 10 else {}
    
    if optimization_goal == "maximize_survival_engine":
        # Extract Survival Engine success rate
        setup_row = ideal_setups_df[ideal_setups_df['Setup'] == 'Survival Engine']
        if not setup_row.empty:
            return float(setup_row['Success %'].values[0])
        return 0.0
    
    elif optimization_goal == "maximize_roar_flashback":
        # Extract Roar Flashback success rate
        setup_row = ideal_setups_df[ideal_setups_df['Setup'] == 'Roar Flashback']
        if not setup_row.empty:
            return float(setup_row['Success %'].values[0])
        return 0.0
    
    elif optimization_goal == "maximize_wonder_flying":
        # Extract Wonder Flying success rate
        setup_row = ideal_setups_df[ideal_setups_df['Setup'] == 'Wonder Flying']
        if not setup_row.empty:
            return float(setup_row['Success %'].values[0])
        return 0.0
    
    elif optimization_goal == "minimize_mulligans":
        # Extract average mulligans
        if isinstance(summary, dict) and 'Average Mulligans' in summary:
            return float(summary['Average Mulligans'])
        return 0.0
    
    elif optimization_goal == "maximize_color_access":
        # Calculate average color access across key cards
        if not key_card_stats_df.empty:
            return float(key_card_stats_df['Seen % (Turn ≤4)'].mean())
        return 0.0
    
    elif optimization_goal == "maximize_key_card_access":
        # Calculate average access to all key cards
        if not key_card_stats_df.empty:
            return float(key_card_stats_df['Seen % (Turn ≤4)'].mean())
        return 0.0
    
    # Default
    return 0.0


def sort_rankings(rankings: List[VariantRanking], optimization_goal: str) -> List[VariantRanking]:
    """
    Sort rankings based on optimization goal.
    
    Args:
        rankings: List of variant rankings
        optimization_goal: Goal to optimize
        
    Returns:
        Sorted list of rankings
    """
    if optimization_goal.startswith("minimize"):
        # Lower is better
        return sorted(rankings, key=lambda x: x.score)
    else:
        # Higher is better (maximize)
        return sorted(rankings, key=lambda x: x.score, reverse=True)


def generate_recommendation(delta: float, delta_pct: float, optimization_goal: str) -> str:
    """
    Generate recommendation based on improvement magnitude.
    
    Args:
        delta: Absolute change from baseline
        delta_pct: Percentage change from baseline
        optimization_goal: Goal being optimized
        
    Returns:
        Recommendation string
    """
    # Determine if higher or lower is better
    if optimization_goal.startswith("minimize"):
        # For minimization, negative delta is good
        delta_pct = -delta_pct
    
    # Categorize based on improvement
    if delta_pct > 10:
        return "✅ Strong"
    elif delta_pct > 5:
        return "⚖️  Moderate"
    elif delta_pct > 2:
        return "⚠️  Weak"
    elif delta_pct < -5:
        return "❌ Not Recommended"
    else:
        return "⚪ Neutral"


def generate_insights(config: ExperimentConfig, rankings: List[VariantRanking], baseline_score: float) -> List[str]:
    """
    Generate insights from experiment results.
    
    Args:
        config: Experiment configuration
        rankings: Sorted variant rankings
        baseline_score: Baseline score
        
    Returns:
        List of insight strings
    """
    insights = []
    
    if not rankings:
        insights.append("⚠️  No successful variants to analyze")
        return insights
    
    # Top performer
    top = rankings[0]
    insights.append(f"🏆 Best variant: {top.variant.name}")
    insights.append(f"   Score: {top.score:.3f} (baseline: {baseline_score:.3f})")
    
    sign = "+" if top.delta > 0 else ""
    insights.append(f"   Change: {sign}{top.delta:.3f} ({sign}{top.delta_pct:.1f}%)")
    insights.append(f"   Changes: {top.variant.summary()}")
    
    # Count improvements
    if config.optimization_goal.startswith("minimize"):
        improvements = [r for r in rankings if r.score < baseline_score]
    else:
        improvements = [r for r in rankings if r.score > baseline_score]
    
    insights.append(f"\n📊 {len(improvements)}/{len(rankings)} variants improved over baseline")
    
    # Secondary goal analysis
    if config.secondary_goals:
        insights.append(f"\n📈 Secondary Goals (for best variant):")
        for goal in config.secondary_goals:
            if goal in top.secondary_scores:
                score = top.secondary_scores[goal]
                insights.append(f"   {goal}: {score:.2f}")
    
    # Pattern analysis
    if len(rankings) >= 3:
        # Look for patterns in top 3
        top_3 = rankings[:3]
        
        # Analyze card changes
        card_frequency = {}
        for ranking in top_3:
            for change in ranking.variant.changes:
                if change.delta > 0:  # Cards that were added/increased
                    card_frequency[change.card] = card_frequency.get(change.card, 0) + 1
        
        if card_frequency:
            most_common = max(card_frequency.items(), key=lambda x: x[1])
            if most_common[1] >= 2:
                insights.append(f"\n💡 Pattern: Top variants frequently include more {most_common[0]}")
    
    # Warning for close results
    if len(rankings) >= 2:
        top_2_delta = abs(rankings[0].score - rankings[1].score)
        if top_2_delta < 0.01:
            insights.append(f"\n⚠️  Warning: Top 2 variants are very close ({top_2_delta:.4f} difference)")
            insights.append("   Consider running with more simulations for statistical confidence")
    
    return insights


def calculate_statistics(rankings: List[VariantRanking], config: ExperimentConfig) -> Dict[str, Any]:
    """
    Calculate summary statistics for the experiment.
    
    Args:
        rankings: List of variant rankings
        config: Experiment configuration
        
    Returns:
        Dictionary of statistics
    """
    if not rankings:
        return {}
    
    scores = [r.score for r in rankings]
    deltas = [r.delta for r in rankings]
    delta_pcts = [r.delta_pct for r in rankings]
    
    # Count recommendations
    recommendations = {}
    for ranking in rankings:
        rec = ranking.recommendation
        recommendations[rec] = recommendations.get(rec, 0) + 1
    
    return {
        'total_variants': len(rankings),
        'best_score': rankings[0].score,
        'worst_score': rankings[-1].score,
        'baseline_score': rankings[0].baseline_score,
        'average_score': sum(scores) / len(scores),
        'median_score': sorted(scores)[len(scores) // 2],
        'score_range': max(scores) - min(scores),
        'average_delta': sum(deltas) / len(deltas),
        'average_delta_pct': sum(delta_pcts) / len(delta_pcts),
        'max_improvement': max(deltas) if config.optimization_goal.startswith("maximize") else min(deltas),
        'max_improvement_pct': max(delta_pcts) if config.optimization_goal.startswith("maximize") else min(delta_pcts),
        'recommendations': recommendations
    }


def print_analysis_summary(analyzed: AnalyzedExperiment):
    """
    Print a formatted summary of the analysis.
    
    Args:
        analyzed: Analyzed experiment
    """
    print(f"\n{'='*80}")
    print("EXPERIMENT RESULTS".center(80))
    print(f"{'='*80}\n")
    
    # Print top 10 rankings
    print("Rankings:")
    print(f"{'─'*80}")
    print(f"{'Rank':<6} {'Variant':<30} {'Score':<10} {'Delta':<12} {'Δ%':<10} {'Recommendation':<20}")
    print(f"{'─'*80}")
    
    for ranking in analyzed.rankings[:10]:
        sign = "+" if ranking.delta > 0 else ""
        print(f"{ranking.rank:<6} {ranking.variant.name[:29]:<30} "
              f"{ranking.score:<10.3f} {sign}{ranking.delta:<11.3f} "
              f"{sign}{ranking.delta_pct:<9.1f} {ranking.recommendation:<20}")
    
    if len(analyzed.rankings) > 10:
        print(f"... and {len(analyzed.rankings) - 10} more variants")
    
    print(f"{'─'*80}\n")
    
    # Print insights
    print("KEY INSIGHTS:")
    print(f"{'─'*80}")
    for insight in analyzed.insights:
        print(insight)
    print(f"{'─'*80}\n")
    
    # Print statistics
    print("STATISTICS:")
    print(f"{'─'*80}")
    stats = analyzed.statistics
    print(f"Total Variants: {stats.get('total_variants', 0)}")
    print(f"Best Score: {stats.get('best_score', 0):.3f}")
    print(f"Baseline Score: {stats.get('baseline_score', 0):.3f}")
    print(f"Average Score: {stats.get('average_score', 0):.3f}")
    print(f"Average Improvement: {stats.get('average_delta', 0):.3f} ({stats.get('average_delta_pct', 0):.1f}%)")
    print(f"\nRecommendations:")
    for rec, count in stats.get('recommendations', {}).items():
        print(f"  {rec}: {count} variants")
    print(f"{'─'*80}\n")


if __name__ == "__main__":
    # Test analyzer
    print("Testing experiment analyzer...")
    
    from experiment_config import load_experiment_config
    from experiment_runner import run_experiment
    import json
    
    # Load configs
    experiment_config = load_experiment_config("experiments/test.json")
    
    with open("simulation_config.json", 'r') as f:
        sim_config = json.load(f)
    
    # Run experiment
    print("Running experiment...")
    experiment_results = run_experiment(experiment_config, sim_config, num_workers=2)
    
    # Analyze results
    if experiment_results:
        print("\nAnalyzing results...")
        analyzed = analyze_experiment(experiment_results)
        
        # Print summary
        print_analysis_summary(analyzed)

