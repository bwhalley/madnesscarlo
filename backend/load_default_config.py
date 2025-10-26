"""
Load Default Simulation Configuration

This script loads the default simulation configuration from simulation_config.json
into the database as a public, default configuration.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.database import SessionLocal
from app.models.user import User
from app.models.simulation_config import SimulationConfig
from app.utils.security import hash_password


def load_default_config(force_update=False):
    """Load default configuration from simulation_config.json
    
    Args:
        force_update: If True, update existing config without prompting
    """
    
    # Read the config file (in the same directory as this script)
    config_path = Path(__file__).parent / "simulation_config.json"
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    print(f"✅ Loaded configuration from {config_path}")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Check if we have a system user, create if not
        system_user = db.query(User).filter(User.username == "system").first()
        
        if not system_user:
            print("Creating system user...")
            system_user = User(
                username="system",
                email="system@madnesscarlo.local",
                full_name="System User",
                password_hash=hash_password("system_password_not_used"),
                is_active=True,
                is_verified=True
            )
            db.add(system_user)
            db.commit()
            db.refresh(system_user)
            print(f"✅ Created system user with ID: {system_user.id}")
        else:
            print(f"✅ Using existing system user with ID: {system_user.id}")
        
        # Check if default config already exists
        existing_config = db.query(SimulationConfig).filter(
            SimulationConfig.is_default == True
        ).first()
        
        if existing_config:
            print(f"⚠️  Default configuration already exists: {existing_config.name}")
            
            if not force_update:
                response = input("Do you want to update it? (y/n): ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return False
            else:
                print("🔄 Force updating configuration...")
            
            # Update existing config
            existing_config.name = "Default Madness Configuration"
            existing_config.description = "Default configuration for Madness deck simulations with key cards, ideal setups, and mulligan strategy"
            existing_config.default_runs = config_data.get("runs", 1000)
            existing_config.default_turns = config_data.get("turns", 4)
            existing_config.key_card_turn_limit = 4
            existing_config.key_cards = config_data.get("key_cards", [])
            existing_config.mulligan_strategy = config_data.get("mulligan_strategy", {})
            existing_config.ideal_setups = config_data.get("ideal_setups", [])
            existing_config.sideboard_plans = config_data.get("sideboard_plans", {})
            existing_config.is_default = True
            existing_config.is_public = True
            
            db.commit()
            db.refresh(existing_config)
            print(f"✅ Updated default configuration: {existing_config.name} (ID: {existing_config.id})")
        else:
            # Create new default config
            new_config = SimulationConfig(
                user_id=system_user.id,
                name="Default Madness Configuration",
                description="Default configuration for Madness deck simulations with key cards, ideal setups, and mulligan strategy",
                default_runs=config_data.get("runs", 1000),
                default_turns=config_data.get("turns", 4),
                key_card_turn_limit=4,
                key_cards=config_data.get("key_cards", []),
                mulligan_strategy=config_data.get("mulligan_strategy", {}),
                ideal_setups=config_data.get("ideal_setups", []),
                sideboard_plans=config_data.get("sideboard_plans", {}),
                is_default=True,
                is_public=True
            )
            
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            
            print(f"✅ Created default configuration: {new_config.name} (ID: {new_config.id})")
        
        # Display summary
        print("\n" + "="*60)
        print("📊 Configuration Summary")
        print("="*60)
        print(f"Name: Default Madness Configuration")
        print(f"Default Runs: {config_data.get('runs', 1000)}")
        print(f"Default Turns: {config_data.get('turns', 4)}")
        print(f"Key Cards: {len(config_data.get('key_cards', []))} cards")
        print(f"Ideal Setups: {len(config_data.get('ideal_setups', []))} setups")
        print(f"Sideboard Plans: {len(config_data.get('sideboard_plans', {}))} plans")
        print(f"Is Default: Yes")
        print(f"Is Public: Yes")
        print("="*60)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load default simulation configuration")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force update without prompting"
    )
    args = parser.parse_args()
    
    print("🚀 Loading Default Simulation Configuration...")
    print()
    
    success = load_default_config(force_update=args.force)
    
    if success:
        print("\n✅ Default configuration loaded successfully!")
        print("\n💡 You can now use this configuration in the web app.")
    else:
        print("\n❌ Failed to load default configuration.")
        sys.exit(1)

