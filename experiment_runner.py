"""
Experiment Runner Module

Runs deck optimization experiments with parallel simulation execution.
"""

import multiprocessing as mp
import time
from typing import Dict, Any, List, Callable, Optional
from functools import partial
from dataclasses import dataclass

from experiment_config import ExperimentConfig, estimate_runtime
from variant_generator import VariantGenerator, Variant
from madness import run_simulations


@dataclass
class ExperimentResults:
    """Results from running an experiment."""
    experiment_name: str
    baseline_results: Dict[str, Any]
    variant_results: List[Dict[str, Any]]
    variants: List[Variant]
    execution_time: float
    config: ExperimentConfig


def run_experiment(
    config: ExperimentConfig,
    sim_config: Dict[str, Any],
    num_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[str], None]] = None
) -> ExperimentResults:
    """
    Run complete experiment with all variants.
    
    Args:
        config: Experiment configuration
        sim_config: Simulation configuration (from simulation_config.json)
        num_workers: Number of parallel workers (default: CPU count - 1)
        progress_callback: Optional callback for progress updates
        
    Returns:
        ExperimentResults with all variant data
    """
    start_time = time.time()
    
    def log(msg: str):
        """Log message to console and callback."""
        print(msg)
        if progress_callback:
            progress_callback(msg)
    
    # Determine worker count
    if num_workers is None:
        num_workers = max(1, mp.cpu_count() - 1)
    
    log(f"\n{'='*80}")
    log(f"EXPERIMENT: {config.name}".center(80))
    log(f"{'='*80}\n")
    
    # Generate variants
    log("Step 1: Generating variants...")
    generator = VariantGenerator(config.base_deck)
    variants = generator.generate_variants(config)
    
    if not variants:
        log("⚠️  No variants generated. Check experiment configuration.")
        return None
    
    # Estimate runtime
    estimate = estimate_runtime(config, len(variants), num_workers)
    log(f"\nExperiment Configuration:")
    log(f"  Base Deck: {config.base_deck}")
    log(f"  Optimization Goal: {config.optimization_goal}")
    log(f"  Runs per Variant: {config.runs_per_variant}")
    log(f"  Total Variants: {estimate['total_variants']}")
    log(f"  Total Simulations: {estimate['total_simulations']:,}")
    log(f"  Parallel Workers: {num_workers}")
    log(f"  Estimated Runtime: {estimate['formatted']}")
    log("")
    
    # Run baseline simulation
    log("Step 2: Running baseline simulation...")
    baseline_start = time.time()
    baseline_results = run_simulations(
        config.base_deck,
        config.runs_per_variant,
        4,  # turns
        sim_config
    )
    baseline_time = time.time() - baseline_start
    log(f"  ✓ Baseline complete in {baseline_time:.1f}s")
    
    # Run variant simulations in parallel
    log(f"\nStep 3: Running {len(variants)} variant simulations...")
    variant_results = run_variants_parallel(
        variants=variants,
        runs=config.runs_per_variant,
        sim_config=sim_config,
        num_workers=num_workers,
        progress_callback=log
    )
    
    execution_time = time.time() - start_time
    log(f"\n{'='*80}")
    log(f"  ✓ Experiment complete in {execution_time:.1f}s")
    log(f"{'='*80}\n")
    
    return ExperimentResults(
        experiment_name=config.name,
        baseline_results=baseline_results,
        variant_results=variant_results,
        variants=variants,
        execution_time=execution_time,
        config=config
    )


def run_variants_parallel(
    variants: List[Variant],
    runs: int,
    sim_config: Dict[str, Any],
    num_workers: int,
    progress_callback: Optional[Callable[[str], None]] = None
) -> List[Dict[str, Any]]:
    """
    Run simulations for multiple variants in parallel.
    
    Args:
        variants: List of variants to simulate
        runs: Number of simulation runs per variant
        sim_config: Simulation configuration
        num_workers: Number of parallel workers
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of simulation results (one per variant)
    """
    if num_workers == 1:
        # Single-threaded execution (useful for debugging)
        return run_variants_sequential(variants, runs, sim_config, progress_callback)
    
    # Prepare worker function
    sim_func = partial(
        run_variant_simulation,
        runs=runs,
        turns=4,
        config=sim_config
    )
    
    # Run in parallel with progress tracking
    variant_results = []
    completed = 0
    
    with mp.Pool(num_workers) as pool:
        # Use imap_unordered for progress tracking
        for result in pool.imap_unordered(sim_func, variants):
            variant_results.append(result)
            completed += 1
            
            if progress_callback:
                progress = (completed / len(variants)) * 100
                progress_callback(f"  Progress: {completed}/{len(variants)} ({progress:.1f}%)")
    
    # Re-order results to match variant order
    variant_results_ordered = []
    for variant in variants:
        for result in variant_results:
            if result['variant'].id == variant.id:
                variant_results_ordered.append(result)
                break
    
    return variant_results_ordered


def run_variants_sequential(
    variants: List[Variant],
    runs: int,
    sim_config: Dict[str, Any],
    progress_callback: Optional[Callable[[str], None]] = None
) -> List[Dict[str, Any]]:
    """
    Run simulations for variants sequentially (single-threaded).
    
    Useful for debugging or when parallelization causes issues.
    """
    results = []
    
    for i, variant in enumerate(variants):
        if progress_callback:
            progress_callback(f"  Running variant {i+1}/{len(variants)}: {variant.name}")
        
        result = run_variant_simulation(variant, runs, 4, sim_config)
        results.append(result)
    
    return results


def run_variant_simulation(
    variant: Variant,
    runs: int,
    turns: int,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run simulation for a single variant.
    
    This function is designed to be pickled for multiprocessing.
    
    Args:
        variant: Variant to simulate
        runs: Number of simulation runs
        turns: Number of turns to simulate
        config: Simulation configuration
        
    Returns:
        Dictionary with variant and simulation results
    """
    try:
        # Run simulation
        results = run_simulations(variant.deck_path, runs, turns, config)
        
        return {
            'variant': variant,
            'results': results,
            'success': True,
            'error': None
        }
    
    except Exception as e:
        # Handle errors gracefully
        return {
            'variant': variant,
            'results': None,
            'success': False,
            'error': str(e)
        }


def print_experiment_progress(message: str):
    """Default progress callback that prints to console."""
    print(message)


def verify_experiment_results(experiment_results: ExperimentResults) -> bool:
    """
    Verify experiment results are valid.
    
    Args:
        experiment_results: Results to verify
        
    Returns:
        True if valid, False otherwise
    """
    errors = []
    
    # Check baseline results
    if not experiment_results.baseline_results:
        errors.append("Missing baseline results")
    
    # Check variant results
    if not experiment_results.variant_results:
        errors.append("No variant results")
    
    if len(experiment_results.variant_results) != len(experiment_results.variants):
        errors.append(f"Variant count mismatch: {len(experiment_results.variant_results)} results vs {len(experiment_results.variants)} variants")
    
    # Check for failed simulations
    failed = [r for r in experiment_results.variant_results if not r.get('success', True)]
    if failed:
        errors.append(f"{len(failed)} variant simulations failed")
        for f in failed[:3]:  # Show first 3 failures
            errors.append(f"  - {f['variant'].name}: {f.get('error', 'Unknown error')}")
    
    if errors:
        print("⚠️  Experiment verification failed:")
        for error in errors:
            print(f"  {error}")
        return False
    
    return True


def calculate_experiment_statistics(experiment_results: ExperimentResults) -> Dict[str, Any]:
    """
    Calculate summary statistics for the experiment.
    
    Args:
        experiment_results: Experiment results
        
    Returns:
        Dictionary with statistics
    """
    successful_variants = [r for r in experiment_results.variant_results if r.get('success', True)]
    failed_variants = [r for r in experiment_results.variant_results if not r.get('success', True)]
    
    return {
        'total_variants': len(experiment_results.variants),
        'successful_simulations': len(successful_variants),
        'failed_simulations': len(failed_variants),
        'total_simulations': len(experiment_results.variants) * experiment_results.config.runs_per_variant,
        'execution_time': experiment_results.execution_time,
        'average_time_per_variant': experiment_results.execution_time / len(experiment_results.variants) if experiment_results.variants else 0
    }


if __name__ == "__main__":
    # Test experiment runner
    print("Testing experiment runner...")
    
    from experiment_config import load_experiment_config
    import json
    
    # Load configs
    experiment_config = load_experiment_config("experiments/test.json")
    
    with open("simulation_config.json", 'r') as f:
        sim_config = json.load(f)
    
    # Run experiment
    results = run_experiment(
        config=experiment_config,
        sim_config=sim_config,
        num_workers=2,
        progress_callback=print_experiment_progress
    )
    
    # Verify results
    if results:
        is_valid = verify_experiment_results(results)
        print(f"\nResults valid: {is_valid}")
        
        # Print statistics
        stats = calculate_experiment_statistics(results)
        print(f"\nExperiment Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

