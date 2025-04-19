"""
Natural disaster event tests for the China Growth Game.

This module contains tests to verify that natural disaster events
trigger with appropriate probabilities and apply the expected effects.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import uuid
import random
import numpy as np

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.events_manager import EventsManager
from economic_model_py.economic_model.game.randomized_events_manager import RandomizedEventsManager, EVENT_CATEGORIES
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

class TestNaturalDisasterEvent(unittest.TestCase):
    """Test cases for natural disaster events."""

    def setUp(self):
        """Set up the test environment."""
        # Create a notification manager for testing
        self.notification_manager = NotificationManager()
        
        # Initialize game state with notification manager and randomized events
        self.game_state = GameState(
            notification_manager=self.notification_manager,
            use_randomized_events=True,
            random_seed=42  # Use a fixed seed for reproducibility
        )
        
        # Create test teams
        self.test_team_ids = []
        for i in range(3):
            team = self.game_state.create_team(f"Test Team {i+1}")
            self.test_team_ids.append(team["team_id"])
            
        # Start the game
        self.game_state.start_game()
        
    def test_natural_disaster_event_category(self):
        """Test that the natural disaster event category is defined correctly."""
        # Check that the natural disaster event category exists
        self.assertIn("natural_disaster", EVENT_CATEGORIES, "Natural disaster event category not found")
        
        # Check that the natural disaster event has the expected probability
        disaster_config = EVENT_CATEGORIES["natural_disaster"]
        self.assertGreater(disaster_config["probability"], 0.0, "Natural disaster probability should be greater than 0")
        self.assertLess(disaster_config["probability"], 0.2, "Natural disaster probability should be less than 0.2")
        
        # Check that the natural disaster event has the expected effects
        self.assertIn("gdp_growth_delta", disaster_config["effects"], "Natural disaster does not have gdp_growth_delta effect")
        self.assertIn("capital_damage", disaster_config["effects"], "Natural disaster does not have capital_damage effect")
        
        # Check that the effects have the expected ranges
        gdp_delta_range = disaster_config["effects"]["gdp_growth_delta"]
        capital_damage_range = disaster_config["effects"]["capital_damage"]
        
        self.assertLess(gdp_delta_range[0], 0.0, "Natural disaster gdp_growth_delta lower bound should be negative")
        self.assertLess(gdp_delta_range[1], 0.0, "Natural disaster gdp_growth_delta upper bound should be negative")
        self.assertGreater(capital_damage_range[0], 0.0, "Natural disaster capital_damage lower bound should be positive")
        self.assertGreater(capital_damage_range[1], 0.0, "Natural disaster capital_damage upper bound should be positive")
        
        # Check that the natural disaster event has regional impact
        self.assertIn("regional_impact", disaster_config, "Natural disaster does not have regional impact")
        
        # Check that regional impact has the expected regions
        regional_impact = disaster_config["regional_impact"]
        self.assertIn("coastal", regional_impact, "Natural disaster regional impact does not include coastal regions")
        self.assertIn("inland", regional_impact, "Natural disaster regional impact does not include inland regions")
        self.assertIn("western", regional_impact, "Natural disaster regional impact does not include western regions")
        
        # Check that regional impact has the expected values
        self.assertGreater(regional_impact["coastal"], 1.0, "Coastal regions should have higher impact")
        self.assertLess(regional_impact["inland"], 1.0, "Inland regions should have lower impact")
        
    def test_natural_disaster_probability(self):
        """Test that natural disaster events occur with the expected probability."""
        # Create a randomized events manager with a fixed seed
        events_manager = RandomizedEventsManager(seed=42)
        
        # Get the expected probability of natural disaster
        expected_prob = EVENT_CATEGORIES["natural_disaster"]["probability"]
        
        # Run a large number of simulations to get statistically significant results
        num_simulations = 1000
        num_years = 20
        disaster_count = 0
        total_years = num_simulations * num_years
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=42 + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Count natural disaster events
            for entry in history:
                event = entry["event"]
                if event.get("category") == "natural_disaster":
                    disaster_count += 1
                    
        # Calculate observed probability
        observed_prob = disaster_count / total_years
        
        # Check that observed probability is close to expected probability
        # Allow for some statistical variation (within 20% of expected)
        margin = 0.2 * expected_prob
        self.assertAlmostEqual(observed_prob, expected_prob, delta=margin,
                              msg=f"Natural disaster probability: expected {expected_prob}, observed {observed_prob}")
                              
    def test_natural_disaster_effects(self):
        """Test that natural disaster events apply the expected effects."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force a natural disaster
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a natural disaster event
            disaster_config = EVENT_CATEGORIES["natural_disaster"]
            event = {
                "year": year,
                "name": disaster_config["name"],
                "description": disaster_config["description"],
                "category": "natural_disaster",
                "effects": {
                    "gdp_growth_delta": -0.05,  # 5% GDP decline
                    "capital_damage": 0.03      # 3% capital damage
                },
                "regional_impact": disaster_config["regional_impact"],
                "triggered": True
            }
            return [event]
            
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the team's state before the disaster
        pre_disaster_state = game_state.team_manager.get_team_state(team_id)
        pre_disaster_gdp = pre_disaster_state["current_state"].get("Y", 0)
        pre_disaster_capital = pre_disaster_state["current_state"].get("K", 0)
        
        # Advance a round to trigger the disaster
        game_state.advance_round()
        
        # Record the team's state after the disaster
        post_disaster_state = game_state.team_manager.get_team_state(team_id)
        post_disaster_gdp = post_disaster_state["current_state"].get("Y", 0)
        post_disaster_capital = post_disaster_state["current_state"].get("K", 0)
        
        # Calculate what GDP would have been without the disaster
        # This is a simplification, as GDP is affected by many factors
        expected_gdp_growth = 0.15  # Assume 15% growth over 5 years without disaster
        expected_gdp = pre_disaster_gdp * (1 + expected_gdp_growth)
        
        # Check that GDP growth was lower than expected due to the disaster
        self.assertLess(post_disaster_gdp, expected_gdp, 
                       f"GDP was not affected by natural disaster: {post_disaster_gdp} >= {expected_gdp}")
        
        # Calculate what capital would have been without the disaster
        # This is a simplification, as capital is affected by many factors
        expected_capital_growth = 0.15  # Assume 15% growth over 5 years without disaster
        expected_capital = pre_disaster_capital * (1 + expected_capital_growth)
        
        # Check that capital was affected by the disaster
        self.assertLess(post_disaster_capital, expected_capital, 
                       f"Capital was not affected by natural disaster: {post_disaster_capital} >= {expected_capital}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_regional_impact(self):
        """Test that natural disaster events have different impacts based on region."""
        # Create a randomized events manager
        events_manager = RandomizedEventsManager(seed=42)
        
        # Create a natural disaster event with regional impact
        disaster_config = EVENT_CATEGORIES["natural_disaster"]
        disaster_event = {
            "year": 2000,
            "name": disaster_config["name"],
            "description": disaster_config["description"],
            "category": "natural_disaster",
            "effects": {
                "gdp_growth_delta": -0.05,  # 5% GDP decline
                "capital_damage": 0.03      # 3% capital damage
            },
            "regional_impact": disaster_config["regional_impact"],
            "triggered": True
        }
        
        # Create mock team states for different regions
        coastal_state = {"region": "coastal", "current_state": {"Y": 100, "K": 1000}}
        inland_state = {"region": "inland", "current_state": {"Y": 100, "K": 1000}}
        western_state = {"region": "western", "current_state": {"Y": 100, "K": 1000}}
        
        # Create a mock function to apply event effects
        def apply_event_effects(state, event):
            # Get the base effects
            gdp_delta = event["effects"]["gdp_growth_delta"]
            capital_damage = event["effects"]["capital_damage"]
            
            # Apply regional impact if applicable
            if "regional_impact" in event and "region" in state:
                region = state["region"]
                if region in event["regional_impact"]:
                    regional_multiplier = event["regional_impact"][region]
                    gdp_delta *= regional_multiplier
                    capital_damage *= regional_multiplier
                    
            # Apply effects to state
            state["current_state"]["Y"] *= (1 + gdp_delta)
            state["current_state"]["K"] *= (1 - capital_damage)
            
            return state
            
        # Apply the disaster event to each region
        coastal_result = apply_event_effects(coastal_state.copy(), disaster_event)
        inland_result = apply_event_effects(inland_state.copy(), disaster_event)
        western_result = apply_event_effects(western_state.copy(), disaster_event)
        
        # Check that coastal regions are affected more severely
        self.assertLess(coastal_result["current_state"]["Y"], inland_result["current_state"]["Y"],
                       "Coastal regions should have more severe GDP impact than inland regions")
        self.assertLess(coastal_result["current_state"]["K"], inland_result["current_state"]["K"],
                       "Coastal regions should have more severe capital damage than inland regions")
        
        # Check that western regions are affected differently than inland regions
        self.assertNotEqual(western_result["current_state"]["Y"], inland_result["current_state"]["Y"],
                          "Western regions should have different GDP impact than inland regions")
        self.assertNotEqual(western_result["current_state"]["K"], inland_result["current_state"]["K"],
                          "Western regions should have different capital damage than inland regions")
        
    def test_natural_disaster_notification(self):
        """Test that teams are notified when a natural disaster event occurs."""
        # Create a game state with notification manager and randomized events
        game_state = GameState(
            notification_manager=self.notification_manager,
            use_randomized_events=True,
            random_seed=42
        )
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force a natural disaster
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a natural disaster event
            disaster_config = EVENT_CATEGORIES["natural_disaster"]
            event = {
                "year": year,
                "name": disaster_config["name"],
                "description": disaster_config["description"],
                "category": "natural_disaster",
                "effects": {
                    "gdp_growth_delta": -0.05,  # 5% GDP decline
                    "capital_damage": 0.03      # 3% capital damage
                },
                "regional_impact": disaster_config["regional_impact"],
                "triggered": True
            }
            return [event]
            
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Register an event handler for event notifications
        event_notifications = []
        def event_handler(data, room):
            event_notifications.append((data, room))
            
        self.notification_manager.on("eventTriggered", event_handler)
        
        # Advance a round to trigger the disaster
        game_state.advance_round()
        
        # Check that an event notification was sent
        self.assertGreater(len(event_notifications), 0, "No event notifications were sent")
        
        # Check that at least one notification was for the natural disaster event
        disaster_notifications = [n for n in event_notifications if "Natural Disaster" in str(n)]
        self.assertGreater(len(disaster_notifications), 0, "No natural disaster event notifications were sent")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_multiple_natural_disasters(self):
        """Test that multiple natural disasters can occur over time."""
        # Create a randomized events manager with a fixed seed
        events_manager = RandomizedEventsManager(seed=42)
        
        # Run a long simulation
        num_years = 100
        history, stats = events_manager.run_simulation(num_years)
        
        # Count natural disaster events
        disaster_events = [entry for entry in history if entry["event"].get("category") == "natural_disaster"]
        
        # Check that multiple disasters occurred
        self.assertGreater(len(disaster_events), 1, "Multiple natural disasters should occur over a long period")
        
        # Check that disasters occurred in different years
        disaster_years = [entry["year"] for entry in disaster_events]
        unique_years = set(disaster_years)
        self.assertEqual(len(unique_years), len(disaster_years), "Natural disasters should occur in different years")
        
    def test_natural_disaster_recovery(self):
        """Test that economies recover from natural disasters over time."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force a natural disaster in the first round only
        original_generate = game_state.events_manager._generate_random_events
        disaster_triggered = False
        
        def mock_generate(year):
            nonlocal disaster_triggered
            if not disaster_triggered:
                # Create a natural disaster event
                disaster_config = EVENT_CATEGORIES["natural_disaster"]
                event = {
                    "year": year,
                    "name": disaster_config["name"],
                    "description": disaster_config["description"],
                    "category": "natural_disaster",
                    "effects": {
                        "gdp_growth_delta": -0.05,  # 5% GDP decline
                        "capital_damage": 0.03      # 3% capital damage
                    },
                    "regional_impact": disaster_config["regional_impact"],
                    "triggered": True
                }
                disaster_triggered = True
                return [event]
            else:
                return []
                
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the team's state before the disaster
        pre_disaster_state = game_state.team_manager.get_team_state(team_id)
        pre_disaster_gdp = pre_disaster_state["current_state"].get("Y", 0)
        pre_disaster_capital = pre_disaster_state["current_state"].get("K", 0)
        
        # Advance a round to trigger the disaster
        game_state.advance_round()
        
        # Record the team's state immediately after the disaster
        post_disaster_state = game_state.team_manager.get_team_state(team_id)
        post_disaster_gdp = post_disaster_state["current_state"].get("Y", 0)
        post_disaster_capital = post_disaster_state["current_state"].get("K", 0)
        
        # Advance several more rounds to allow for recovery
        for _ in range(3):
            game_state.advance_round()
            
        # Record the team's state after recovery
        recovery_state = game_state.team_manager.get_team_state(team_id)
        recovery_gdp = recovery_state["current_state"].get("Y", 0)
        recovery_capital = recovery_state["current_state"].get("K", 0)
        
        # Check that GDP and capital have recovered and grown beyond the pre-disaster levels
        self.assertGreater(recovery_gdp, pre_disaster_gdp, 
                          f"GDP should recover and grow beyond pre-disaster levels: {recovery_gdp} <= {pre_disaster_gdp}")
        self.assertGreater(recovery_capital, pre_disaster_capital, 
                          f"Capital should recover and grow beyond pre-disaster levels: {recovery_capital} <= {pre_disaster_capital}")
        
        # Check that GDP and capital have grown since the immediate post-disaster state
        self.assertGreater(recovery_gdp, post_disaster_gdp, 
                          f"GDP should grow after the disaster: {recovery_gdp} <= {post_disaster_gdp}")
        self.assertGreater(recovery_capital, post_disaster_capital, 
                          f"Capital should grow after the disaster: {recovery_capital} <= {post_disaster_capital}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_natural_disaster_distribution(self):
        """Test that natural disaster effects are distributed within the expected ranges."""
        # Create a randomized events manager
        events_manager = RandomizedEventsManager(seed=42)
        
        # Run a large number of simulations
        num_simulations = 100
        num_years = 20
        gdp_deltas = []
        capital_damages = []
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=42 + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Collect effects from natural disaster events
            for entry in history:
                event = entry["event"]
                if event.get("category") == "natural_disaster":
                    gdp_deltas.append(event["effects"]["gdp_growth_delta"])
                    capital_damages.append(event["effects"]["capital_damage"])
                    
        # Check that we have a reasonable number of disaster events
        self.assertGreater(len(gdp_deltas), 10, "Should have a reasonable number of disaster events")
        
        # Check that effects are within the expected ranges
        disaster_config = EVENT_CATEGORIES["natural_disaster"]
        gdp_range = disaster_config["effects"]["gdp_growth_delta"]
        capital_range = disaster_config["effects"]["capital_damage"]
        
        # Check GDP effects
        self.assertGreaterEqual(min(gdp_deltas), gdp_range[0], 
                              f"Minimum GDP effect {min(gdp_deltas)} should be >= {gdp_range[0]}")
        self.assertLessEqual(max(gdp_deltas), gdp_range[1], 
                           f"Maximum GDP effect {max(gdp_deltas)} should be <= {gdp_range[1]}")
        
        # Check capital damage effects
        self.assertGreaterEqual(min(capital_damages), capital_range[0], 
                              f"Minimum capital damage {min(capital_damages)} should be >= {capital_range[0]}")
        self.assertLessEqual(max(capital_damages), capital_range[1], 
                           f"Maximum capital damage {max(capital_damages)} should be <= {capital_range[1]}")
        
        # Check that effects are distributed across the range (not all at min or max)
        gdp_std = np.std(gdp_deltas)
        capital_std = np.std(capital_damages)
        
        self.assertGreater(gdp_std, 0.001, "GDP effects should be distributed across the range")
        self.assertGreater(capital_std, 0.001, "Capital damage effects should be distributed across the range")

if __name__ == '__main__':
    unittest.main()
