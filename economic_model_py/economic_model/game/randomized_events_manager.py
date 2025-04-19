"""
Randomized events management for the China Growth Game.

This module contains the RandomizedEventsManager class, which extends
the EventsManager to support randomized economic events.
"""

import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from economic_model_py.economic_model.game.events_manager import EventsManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Event categories
EVENT_CATEGORIES = {
    "economic_boom": {
        "name": "Economic Boom",
        "description": "A period of rapid economic growth",
        "probability": 0.15,  # 15% chance per round
        "effects": {
            "gdp_growth_delta": (0.02, 0.05),  # Range of possible values
            "tfp_increase": (0.01, 0.03)
        }
    },
    "economic_recession": {
        "name": "Economic Recession",
        "description": "A period of economic decline",
        "probability": 0.1,  # 10% chance per round
        "effects": {
            "gdp_growth_delta": (-0.05, -0.02),  # Range of possible values
            "exports_multiplier": (0.8, 0.9)
        }
    },
    "natural_disaster": {
        "name": "Natural Disaster",
        "description": "A major natural disaster affecting the economy",
        "probability": 0.05,  # 5% chance per round
        "effects": {
            "gdp_growth_delta": (-0.08, -0.03),  # Range of possible values
            "capital_damage": (0.02, 0.05)  # Percentage of capital destroyed
        },
        "regional_impact": {
            "coastal": 1.5,  # 50% more impact in coastal regions
            "inland": 0.8,   # 20% less impact in inland regions
            "western": 1.2   # 20% more impact in western regions
        }
    },
    "technological_breakthrough": {
        "name": "Technological Breakthrough",
        "description": "A major technological innovation",
        "probability": 0.08,  # 8% chance per round
        "effects": {
            "tfp_increase": (0.02, 0.06),  # Range of possible values
        },
        "r_and_d_modifier": 0.5  # Increases probability by 50% for teams with high R&D
    },
    "trade_agreement": {
        "name": "Trade Agreement",
        "description": "A new international trade agreement",
        "probability": 0.12,  # 12% chance per round
        "effects": {
            "exports_multiplier": (1.1, 1.25),  # Range of possible values
            "fdi_ratio_multiplier": (1.05, 1.15)
        }
    },
    "political_instability": {
        "name": "Political Instability",
        "description": "A period of political uncertainty",
        "probability": 0.07,  # 7% chance per round
        "effects": {
            "gdp_growth_delta": (-0.04, -0.01),  # Range of possible values
            "fdi_ratio_multiplier": (0.7, 0.9)
        }
    }
}

class RandomizedEventsManager(EventsManager):
    """
    Extends the EventsManager to support randomized economic events.
    """
    
    def __init__(self, seed: Optional[int] = None, randomization_enabled: bool = True):
        """
        Initialize the randomized events manager.
        
        Args:
            seed: Optional random seed for reproducibility.
            randomization_enabled: Whether to enable randomized events.
        """
        super().__init__()
        self.randomization_enabled = randomization_enabled
        self.random_events = []  # List of randomly generated events
        self.random_generator = random.Random(seed)  # Use a separate random generator with a fixed seed
        self.event_history = []  # Track all events that have occurred
        
    def get_current_events(self, current_year: int) -> List[Dict[str, Any]]:
        """
        Get events that should be triggered in the current year.
        Includes both fixed events and random events.
        
        Args:
            current_year: The current game year.
            
        Returns:
            List of events for the current year.
        """
        # Get fixed events from parent class
        fixed_events = super().get_current_events(current_year)
        
        # If randomization is disabled, return only fixed events
        if not self.randomization_enabled:
            return fixed_events
            
        # Generate random events for this year
        random_events = self._generate_random_events(current_year)
        
        # Combine fixed and random events
        all_events = fixed_events + random_events
        
        # Add events to history
        for event in all_events:
            self.event_history.append({
                "year": current_year,
                "event": event
            })
            
        return all_events
        
    def _generate_random_events(self, current_year: int) -> List[Dict[str, Any]]:
        """
        Generate random events for the current year.
        
        Args:
            current_year: The current game year.
            
        Returns:
            List of randomly generated events.
        """
        random_events = []
        
        # Check each event category for occurrence
        for category, config in EVENT_CATEGORIES.items():
            # Skip if this category has already occurred this year
            if any(e.get("category") == category and e.get("year") == current_year for e in self.random_events):
                continue
                
            # Check if event occurs based on probability
            if self.random_generator.random() < config["probability"]:
                # Generate event with random effects within the specified ranges
                event = self._create_random_event(category, config, current_year)
                random_events.append(event)
                self.random_events.append(event)
                
        return random_events
        
    def _create_random_event(self, category: str, config: Dict[str, Any], year: int) -> Dict[str, Any]:
        """
        Create a random event based on the category configuration.
        
        Args:
            category: The event category.
            config: The category configuration.
            year: The current year.
            
        Returns:
            A randomly generated event.
        """
        # Generate random effects within the specified ranges
        effects = {}
        for effect_name, effect_range in config["effects"].items():
            min_val, max_val = effect_range
            effects[effect_name] = self.random_generator.uniform(min_val, max_val)
            
        # Create the event
        event = {
            "year": year,
            "name": config["name"],
            "description": config["description"],
            "category": category,
            "effects": effects,
            "triggered": True  # Mark as triggered immediately
        }
        
        # Add regional impact if applicable
        if "regional_impact" in config:
            event["regional_impact"] = config["regional_impact"]
            
        # Add R&D modifier if applicable
        if "r_and_d_modifier" in config:
            event["r_and_d_modifier"] = config["r_and_d_modifier"]
            
        return event
        
    def reset_events(self):
        """Reset all events to non-triggered state."""
        super().reset_events()
        self.random_events = []
        self.event_history = []
        
    def get_event_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all events that have occurred.
        
        Returns:
            List of event history entries.
        """
        return self.event_history
        
    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about event occurrences.
        
        Returns:
            Dictionary of event statistics.
        """
        stats = {
            "total_events": len(self.event_history),
            "fixed_events": 0,
            "random_events": 0,
            "categories": {}
        }
        
        # Count events by type and category
        for entry in self.event_history:
            event = entry["event"]
            category = event.get("category")
            
            if category:
                # Random event
                stats["random_events"] += 1
                if category not in stats["categories"]:
                    stats["categories"][category] = 0
                stats["categories"][category] += 1
            else:
                # Fixed event
                stats["fixed_events"] += 1
                event_name = event.get("name", "Unknown")
                if event_name not in stats["categories"]:
                    stats["categories"][event_name] = 0
                stats["categories"][event_name] += 1
                
        return stats
        
    def run_simulation(self, num_years: int, seed: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Run a simulation of event generation for a specified number of years.
        
        Args:
            num_years: Number of years to simulate.
            seed: Optional random seed for reproducibility.
            
        Returns:
            Tuple of (event history, event statistics).
        """
        # Reset events
        self.reset_events()
        
        # Set seed if provided
        if seed is not None:
            self.random_generator = random.Random(seed)
            
        # Run simulation
        start_year = 1980
        for year in range(start_year, start_year + num_years):
            self.get_current_events(year)
            
        # Return results
        return self.get_event_history(), self.get_event_statistics()
