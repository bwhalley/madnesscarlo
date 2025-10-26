"""
Experiment Configuration Module

Handles loading, validation, and management of deck optimization experiments.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CardSpec:
    """Specification for a card in the deck."""
    card: str
    quantity: int
    
    def __str__(self):
        return f"{self.quantity}x {self.card}"


@dataclass
class Slot:
    """A flexible slot in the deck with alternatives."""
    name: str
    baseline: CardSpec
    alternatives: List[CardSpec]


@dataclass
class ExperimentDefinition:
    """Definition of a single experiment type."""
    type: str  # replace_quantity, slot_testing, land_ratio, combinatorial
    config: Dict[str, Any]
    
    def __post_init__(self):
        """Validate experiment definition on initialization."""
        valid_types = ['replace_quantity', 'slot_testing', 'land_ratio', 'combinatorial']
        if self.type not in valid_types:
            raise ValueError(f"Invalid experiment type: {self.type}. Must be one of {valid_types}")


@dataclass
class ExperimentConfig:
    """Configuration for a deck optimization experiment."""
    
    name: str
    base_deck: str
    runs_per_variant: int = 1000
    optimization_goal: str = "maximize_survival_engine"
    secondary_goals: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    experiments: List[ExperimentDefinition] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self):
        """Validate experiment configuration."""
        errors = []
        
        # Check base deck exists
        if not os.path.exists(self.base_deck):
            errors.append(f"Base deck file not found: {self.base_deck}")
        
        # Validate runs_per_variant
        if self.runs_per_variant < 100:
            errors.append(f"runs_per_variant too low: {self.runs_per_variant}. Minimum is 100 for statistical validity.")
        
        if self.runs_per_variant > 10000:
            print(f"⚠️  Warning: runs_per_variant is high ({self.runs_per_variant}). This may take a long time.")
        
        # Validate optimization goal
        valid_goals = [
            'maximize_survival_engine',
            'maximize_roar_flashback', 
            'maximize_wonder_flying',
            'minimize_mulligans',
            'maximize_color_access',
            'maximize_key_card_access'
        ]
        
        if self.optimization_goal not in valid_goals:
            errors.append(f"Invalid optimization_goal: {self.optimization_goal}. Valid goals: {valid_goals}")
        
        # Validate secondary goals
        for goal in self.secondary_goals:
            if goal not in valid_goals:
                errors.append(f"Invalid secondary goal: {goal}")
        
        # Check for experiments
        if not self.experiments:
            errors.append("No experiments defined in configuration")
        
        # Validate constraints
        if 'max_copies' in self.constraints:
            if not 1 <= self.constraints['max_copies'] <= 4:
                errors.append("max_copies constraint must be between 1 and 4")
        
        if 'deck_size' in self.constraints:
            if self.constraints['deck_size'] != 60:
                print(f"⚠️  Warning: Non-standard deck size: {self.constraints['deck_size']}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        print(f"✓ Configuration validated: {self.name}")


def load_experiment_config(config_path: str) -> ExperimentConfig:
    """
    Load experiment configuration from JSON file.
    
    Args:
        config_path: Path to experiment config JSON
        
    Returns:
        ExperimentConfig object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Experiment config not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    # Parse experiments
    experiments = []
    for exp_dict in config_dict.get('experiments', []):
        exp_type = exp_dict.pop('type')
        experiments.append(ExperimentDefinition(type=exp_type, config=exp_dict))
    
    # Create config
    config = ExperimentConfig(
        name=config_dict['experiment_name'],
        base_deck=config_dict.get('base_deck', 'deck.csv'),
        runs_per_variant=config_dict.get('runs_per_variant', 1000),
        optimization_goal=config_dict.get('optimization_goal', 'maximize_survival_engine'),
        secondary_goals=config_dict.get('secondary_goals', []),
        constraints=config_dict.get('constraints', {}),
        experiments=experiments
    )
    
    return config


def parse_card_spec(spec_dict: Dict[str, Any]) -> CardSpec:
    """Parse a CardSpec from dictionary."""
    return CardSpec(
        card=spec_dict['card'],
        quantity=spec_dict['quantity']
    )


def parse_slot(slot_dict: Dict[str, Any]) -> Slot:
    """Parse a Slot from dictionary."""
    return Slot(
        name=slot_dict['name'],
        baseline=parse_card_spec(slot_dict['baseline']),
        alternatives=[parse_card_spec(alt) for alt in slot_dict['alternatives']]
    )


def get_default_constraints() -> Dict[str, Any]:
    """Get default deck constraints."""
    return {
        'max_copies': 4,
        'deck_size': 60,
        'min_lands': 15,
        'max_lands': 30
    }


def estimate_runtime(config: ExperimentConfig, num_variants: int, num_workers: int = 4) -> Dict[str, Any]:
    """
    Estimate experiment runtime.
    
    Args:
        config: Experiment configuration
        num_variants: Number of variants to test
        num_workers: Number of parallel workers
        
    Returns:
        Dictionary with time estimates
    """
    # Rough estimate: 0.002 seconds per simulation
    simulations_per_variant = config.runs_per_variant
    total_simulations = num_variants * simulations_per_variant
    
    # Account for parallelization
    estimated_seconds = (total_simulations * 0.002) / num_workers
    
    # Add overhead for variant generation and analysis
    overhead_seconds = num_variants * 0.5
    total_seconds = estimated_seconds + overhead_seconds
    
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    
    return {
        'total_variants': num_variants,
        'runs_per_variant': simulations_per_variant,
        'total_simulations': total_simulations,
        'estimated_minutes': minutes,
        'estimated_seconds': seconds,
        'formatted': f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    }


def create_example_experiment(experiment_type: str, output_path: str):
    """
    Create an example experiment configuration file.
    
    Args:
        experiment_type: Type of example (land_count, card_draw, multi_slot)
        output_path: Where to save the example
    """
    examples = {
        'land_count': {
            "experiment_name": "land_count_optimization",
            "base_deck": "deck.csv",
            "runs_per_variant": 1000,
            "optimization_goal": "minimize_mulligans",
            "secondary_goals": ["maximize_survival_engine"],
            "experiments": [
                {
                    "type": "replace_quantity",
                    "card": "Forest",
                    "test_quantities": [5, 6, 7, 8, 9, 10],
                    "compensate_with": "Island"
                }
            ]
        },
        'card_draw': {
            "experiment_name": "card_draw_optimization",
            "base_deck": "deck.csv",
            "runs_per_variant": 1000,
            "optimization_goal": "maximize_survival_engine",
            "experiments": [
                {
                    "type": "slot_testing",
                    "slots": [
                        {"card": "Careful Study", "quantity": 2}
                    ],
                    "alternatives": [
                        {"card": "Deep Analysis", "quantity": 2},
                        {"card": "Brainstorm", "quantity": 2},
                        {"card": "Frantic Search", "quantity": 1}
                    ]
                }
            ]
        },
        'multi_slot': {
            "experiment_name": "multi_slot_optimization",
            "base_deck": "deck.csv",
            "runs_per_variant": 1000,
            "optimization_goal": "maximize_survival_engine",
            "secondary_goals": ["minimize_mulligans"],
            "experiments": [
                {
                    "type": "combinatorial",
                    "max_combinations": 20,
                    "slots": [
                        {
                            "name": "draw_slot",
                            "baseline": {"card": "Careful Study", "quantity": 2},
                            "alternatives": [
                                {"card": "Careful Study", "quantity": 3},
                                {"card": "Careful Study", "quantity": 1}
                            ]
                        },
                        {
                            "name": "creature_slot",
                            "baseline": {"card": "Wild Mongrel", "quantity": 4},
                            "alternatives": [
                                {"card": "Wild Mongrel", "quantity": 3},
                                {"card": "Wild Mongrel", "quantity": 5}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    if experiment_type not in examples:
        raise ValueError(f"Unknown example type: {experiment_type}. Choose from: {list(examples.keys())}")
    
    with open(output_path, 'w') as f:
        json.dump(examples[experiment_type], f, indent=2)
    
    print(f"✓ Created example experiment: {output_path}")


if __name__ == "__main__":
    # Test configuration loading
    print("Testing experiment configuration...")
    
    # Create a test config
    test_config = {
        "experiment_name": "test_experiment",
        "base_deck": "deck.csv",
        "runs_per_variant": 500,
        "optimization_goal": "maximize_survival_engine",
        "experiments": [
            {
                "type": "replace_quantity",
                "card": "Forest",
                "test_quantities": [7, 8, 9]
            }
        ]
    }
    
    # Save and load
    os.makedirs("experiments", exist_ok=True)
    with open("experiments/test.json", "w") as f:
        json.dump(test_config, f, indent=2)
    
    config = load_experiment_config("experiments/test.json")
    print(f"✓ Loaded config: {config.name}")
    print(f"  Base deck: {config.base_deck}")
    print(f"  Optimization goal: {config.optimization_goal}")
    print(f"  Experiments: {len(config.experiments)}")
    
    # Test runtime estimation
    estimate = estimate_runtime(config, num_variants=3, num_workers=4)
    print(f"  Estimated runtime: {estimate['formatted']}")

