"""
Card Database Service

Loads and queries card data from AtomicCards.json (MTGJSON format).
Provides authoritative card information for simulations.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from functools import lru_cache


class CardDatabase:
    """
    Singleton card database that loads card data from AtomicCards.json.
    
    This provides authoritative data about card types, mana costs, colors, etc.
    """
    
    _instance = None
    _data: Dict = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance
    
    def _load_data(self):
        """Load card data from AtomicCards.json."""
        # Look for AtomicCards.json in the backend directory (where it's copied for Docker)
        backend_root = Path(__file__).parent.parent.parent
        card_file = backend_root / "AtomicCards.json"
        
        # Fallback to project root if not in backend
        if not card_file.exists():
            project_root = backend_root.parent
            card_file = project_root / "AtomicCards.json"
        
        if not card_file.exists():
            print(f"Warning: AtomicCards.json not found at {card_file}")
            self._data = {}
            return
        
        print(f"Loading card database from {card_file}...")
        try:
            with open(card_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self._data = json_data.get('data', {})
            print(f"✅ Loaded {len(self._data)} cards from AtomicCards.json")
        except Exception as e:
            print(f"Error loading AtomicCards.json: {e}")
            self._data = {}
    
    def get_card(self, card_name: str) -> Optional[Dict]:
        """
        Get card data by name.
        
        Args:
            card_name: The name of the card
            
        Returns:
            Dictionary with card data, or None if not found
        """
        if not self._data:
            return None
        
        # Try exact match first
        if card_name in self._data:
            # Return the first version of the card (usually the most recent)
            versions = self._data[card_name]
            if versions and len(versions) > 0:
                return versions[0]
        
        # Try case-insensitive match
        card_name_lower = card_name.lower()
        for key, versions in self._data.items():
            if key.lower() == card_name_lower and versions:
                return versions[0]
        
        return None
    
    def get_card_type(self, card_name: str) -> str:
        """
        Get the card type (e.g., "Creature", "Land", "Instant").
        
        Args:
            card_name: The name of the card
            
        Returns:
            Primary card type, or "Unknown" if not found
        """
        card_data = self.get_card(card_name)
        if not card_data:
            return "Unknown"
        
        # Get the full type line (e.g., "Legendary Creature — Human Wizard")
        type_line = card_data.get('type', '')
        
        # Extract the main type from types array
        types = card_data.get('types', [])
        if types:
            return types[0]  # First type is the primary type
        
        # Fallback to parsing type line
        if type_line:
            # Type line format: "Supertypes Type — Subtypes"
            # Examples: "Creature", "Legendary Artifact", "Land"
            parts = type_line.split('—')[0].strip().split()
            
            # Common types
            main_types = ['Creature', 'Land', 'Instant', 'Sorcery', 'Enchantment', 
                         'Artifact', 'Planeswalker', 'Battle', 'Kindred']
            
            for part in parts:
                if part in main_types:
                    return part
            
            # If no recognized type, return the last word before —
            if parts:
                return parts[-1]
        
        return "Unknown"
    
    def get_card_colors(self, card_name: str) -> List[str]:
        """
        Get the card's colors.
        
        Args:
            card_name: The name of the card
            
        Returns:
            List of color codes (W, U, B, R, G)
        """
        card_data = self.get_card(card_name)
        if not card_data:
            return []
        return card_data.get('colors', [])
    
    def get_mana_cost(self, card_name: str) -> str:
        """
        Get the card's mana cost.
        
        Args:
            card_name: The name of the card
            
        Returns:
            Mana cost string (e.g., "{2}{U}{B}") or empty string
        """
        card_data = self.get_card(card_name)
        if not card_data:
            return ""
        return card_data.get('manaCost', '')
    
    def get_cmc(self, card_name: str) -> float:
        """
        Get the card's converted mana cost (mana value).
        
        Args:
            card_name: The name of the card
            
        Returns:
            Converted mana cost as a float
        """
        card_data = self.get_card(card_name)
        if not card_data:
            return 0.0
        return card_data.get('manaValue', 0.0)
    
    def is_land(self, card_name: str) -> bool:
        """Check if a card is a land."""
        return self.get_card_type(card_name) == "Land"
    
    def is_creature(self, card_name: str) -> bool:
        """Check if a card is a creature."""
        return self.get_card_type(card_name) == "Creature"
    
    def get_subtypes(self, card_name: str) -> List[str]:
        """Get card subtypes (e.g., ["Human", "Wizard"])."""
        card_data = self.get_card(card_name)
        if not card_data:
            return []
        return card_data.get('subtypes', [])
    
    def get_supertypes(self, card_name: str) -> List[str]:
        """Get card supertypes (e.g., ["Legendary"])."""
        card_data = self.get_card(card_name)
        if not card_data:
            return []
        return card_data.get('supertypes', [])


# Singleton instance
_card_db = None


def get_card_database() -> CardDatabase:
    """Get the singleton CardDatabase instance."""
    global _card_db
    if _card_db is None:
        _card_db = CardDatabase()
    return _card_db

