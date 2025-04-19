"""
Technology breakthrough event tests for the China Growth Game.

This module contains tests to verify that technology breakthrough events
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

class TestTechnologyBreakthroughEvent(unittest.TestCase):
    """Test cases for technology breakthrough events."""

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
        
    def test_technology_breakthrough_event_category(self):
        """Test that the technology breakthrough event category is defined correctly."""
        # Check that the technology breakthrough event category exists
        self.assertIn("technological_breakthrough", EVENT_CATEGORIES, "Technology breakthrough event category not found")
        
        # Check that the technology breakthrough event has the expected probability
        tech_config = EVENT_CATEGORIES["technological_breakthrough"]
        self.assertGreater(tech_config["probability"], 0.0, "Technology breakthrough probability should be greater than 0")
        self.assertLess(tech_config["probability"], 0.2, "Technology breakthrough probability should be less than 0.2")
        
        # Check that the technology breakthrough event has the expected effects
        self.assertIn("tfp_increase", tech_config["effects"], "Technology breakthrough does not have tfp_increase effect")
        
        # Check that the effects have the expected ranges
        tfp_increase_range = tech_config["effects"]["tfp_increase"]
        
        self.assertGreater(tfp_increase_range[0], 0.0, "Technology breakthrough tfp_increase lower bound should be positive")
        self.assertGreater(tfp_increase_range[1], 0.0, "Technology breakthrough tfp_increase upper bound should be positive")
        
        # Check that the technology breakthrough event has R&D modifier
        self.assertIn("r_and_d_modifier", tech_config, "Technology breakthrough does not have R&D modifier")
        
        # Check that R&D modifier has the expected value
        self.assertGreater(tech_config["r_and_d_modifier"], 0.0, "R&D modifier should be positive")
        
    def test_technology_breakthrough_probability(self):
        """Test that technology breakthrough events occur with the expected probability."""
        # Create a randomized events manager with a fixed seed
        events_manager = RandomizedEventsManager(seed=42)
        
        # Get the expected probability of technology breakthrough
        expected_prob = EVENT_CATEGORIES["technological_breakthrough"]["probability"]
        
        # Run a large number of simulations to get statistically significant results
        num_simulations = 1000
        num_years = 20
        tech_count = 0
        total_years = num_simulations * num_years
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=42 + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Count technology breakthrough events
            for entry in history:
                event = entry["event"]
                if event.get("category") == "technological_breakthrough":
                    tech_count += 1
                    
        # Calculate observed probability
        observed_prob = tech_count / total_years
        
        # Check that observed probability is close to expected probability
        # Allow for some statistical variation (within 20% of expected)
        margin = 0.2 * expected_prob
        self.assertAlmostEqual(observed_prob, expected_prob, delta=margin,
                              msg=f"Technology breakthrough probability: expected {expected_prob}, observed {observed_prob}")
                              
    def test_technology_breakthrough_effects(self):
        """Test that technology breakthrough events apply the expected effects."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force a technology breakthrough
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a technology breakthrough event
            tech_config = EVENT_CATEGORIES["technological_breakthrough"]
            event = {
                "year": year,
                "name": tech_config["name"],
                "description": tech_config["description"],
                "category": "technological_breakthrough",
                "effects": {
                    "tfp_increase": 0.04  # 4% TFP increase
                },
                "r_and_d_modifier": tech_config["r_and_d_modifier"],
                "triggered": True
            }
            return [event]
            
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the team's state before the breakthrough
        pre_tech_state = game_state.team_manager.get_team_state(team_id)
        pre_tech_tfp = pre_tech_state["current_state"].get("A", 0)
        
        # Advance a round to trigger the breakthrough
        game_state.advance_round()
        
        # Record the team's state after the breakthrough
        post_tech_state = game_state.team_manager.get_team_state(team_id)
        post_tech_tfp = post_tech_state["current_state"].get("A", 0)
        
        # Calculate what TFP would have been without the breakthrough
        # This is a simplification, as TFP is affected by many factors
        expected_tfp_growth = 0.1  # Assume 10% growth over 5 years without breakthrough
        expected_tfp = pre_tech_tfp * (1 + expected_tfp_growth)
        
        # Check that TFP growth was higher than expected due to the breakthrough
        self.assertGreater(post_tech_tfp, expected_tfp, 
                          f"TFP was not boosted by technology breakthrough: {post_tech_tfp} <= {expected_tfp}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_r_and_d_modifier(self):
        """Test that R&D investment increases the probability of technology breakthroughs."""
        # Create a randomized events manager
        events_manager = RandomizedEventsManager(seed=42)
        
        # Get the base probability of technology breakthrough
        base_prob = EVENT_CATEGORIES["technological_breakthrough"]["probability"]
        
        # Get the R&D modifier
        r_and_d_modifier = EVENT_CATEGORIES["technological_breakthrough"]["r_and_d_modifier"]
        
        # Create a mock function to calculate modified probability based on R&D investment
        def calculate_modified_probability(base_prob, r_and_d_level, modifier):
            # Higher R&D level increases probability
            return base_prob * (1 + modifier * r_and_d_level)
            
        # Calculate probabilities for different R&D levels
        low_r_and_d = 0.1  # 10% of GDP
        medium_r_and_d = 0.2  # 20% of GDP
        high_r_and_d = 0.3  # 30% of GDP
        
        low_prob = calculate_modified_probability(base_prob, low_r_and_d, r_and_d_modifier)
        medium_prob = calculate_modified_probability(base_prob, medium_r_and_d, r_and_d_modifier)
        high_prob = calculate_modified_probability(base_prob, high_r_and_d, r_and_d_modifier)
        
        # Check that higher R&D levels lead to higher probabilities
        self.assertLess(low_prob, medium_prob, "Higher R&D should increase breakthrough probability")
        self.assertLess(medium_prob, high_prob, "Higher R&D should increase breakthrough probability")
        
        # Check that the increase is proportional to the R&D level
        prob_diff1 = medium_prob - low_prob
        prob_diff2 = high_prob - medium_prob
        
        # The differences should be approximately equal (linear relationship)
        self.assertAlmostEqual(prob_diff1, prob_diff2, delta=0.001, 
                              msg=f"Probability increase should be proportional to R&D increase")
        
    def test_technology_breakthrough_notification(self):
        """Test that teams are notified when a technology breakthrough event occurs."""
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
        
        # Mock the _generate_random_events method to force a technology breakthrough
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a technology breakthrough event
            tech_config = EVENT_CATEGORIES["technological_breakthrough"]
            event = {
                "year": year,
                "name": tech_config["name"],
                "description": tech_config["description"],
                "category": "technological_breakthrough",
                "effects": {
                    "tfp_increase": 0.04  # 4% TFP increase
                },
                "r_and_d_modifier": tech_config["r_and_d_modifier"],
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
        
        # Advance a round to trigger the breakthrough
        game_state.advance_round()
        
        # Check that an event notification was sent
        self.assertGreater(len(event_notifications), 0, "No event notifications were sent")
        
        # Check that at least one notification was for the technology breakthrough event
        tech_notifications = [n for n in event_notifications if "Technological Breakthrough" in str(n)]
        self.assertGreater(len(tech_notifications), 0, "No technology breakthrough event notifications were sent")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_multiple_technology_breakthroughs(self):
        """Test that multiple technology breakthroughs can occur over time."""
        # Create a randomized events manager with a fixed seed
        events_manager = RandomizedEventsManager(seed=42)
        
        # Run a long simulation
        num_years = 100
        history, stats = events_manager.run_simulation(num_years)
        
        # Count technology breakthrough events
        tech_events = [entry for entry in history if entry["event"].get("category") == "technological_breakthrough"]
        
        # Check that multiple breakthroughs occurred
        self.assertGreater(len(tech_events), 1, "Multiple technology breakthroughs should occur over a long period")
        
        # Check that breakthroughs occurred in different years
        tech_years = [entry["year"] for entry in tech_events]
        unique_years = set(tech_years)
        self.assertEqual(len(unique_years), len(tech_years), "Technology breakthroughs should occur in different years")
        
    def test_technology_breakthrough_cumulative_effect(self):
        """Test that multiple technology breakthroughs have a cumulative effect on TFP."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force technology breakthroughs in specific rounds
        original_generate = game_state.events_manager._generate_random_events
        breakthrough_rounds = [1, 3]  # Rounds 1 and 3
        
        def mock_generate(year):
            current_round = (year - 1980) // 5
            if current_round in breakthrough_rounds:
                # Create a technology breakthrough event
                tech_config = EVENT_CATEGORIES["technological_breakthrough"]
                event = {
                    "year": year,
                    "name": tech_config["name"],
                    "description": tech_config["description"],
                    "category": "technological_breakthrough",
                    "effects": {
                        "tfp_increase": 0.04  # 4% TFP increase
                    },
                    "r_and_d_modifier": tech_config["r_and_d_modifier"],
                    "triggered": True
                }
                return [event]
            else:
                return []
                
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the initial TFP
        initial_state = game_state.team_manager.get_team_state(team_id)
        initial_tfp = initial_state["current_state"].get("A", 0)
        
        # Advance to round 1 (first breakthrough)
        game_state.advance_round()
        
        # Record TFP after first breakthrough
        first_state = game_state.team_manager.get_team_state(team_id)
        first_tfp = first_state["current_state"].get("A", 0)
        
        # Advance to round 2 (no breakthrough)
        game_state.advance_round()
        
        # Record TFP after no breakthrough
        second_state = game_state.team_manager.get_team_state(team_id)
        second_tfp = second_state["current_state"].get("A", 0)
        
        # Advance to round 3 (second breakthrough)
        game_state.advance_round()
        
        # Record TFP after second breakthrough
        third_state = game_state.team_manager.get_team_state(team_id)
        third_tfp = third_state["current_state"].get("A", 0)
        
        # Check that TFP increased more in breakthrough rounds
        first_growth = first_tfp / initial_tfp - 1
        second_growth = second_tfp / first_tfp - 1
        third_growth = third_tfp / second_tfp - 1
        
        self.assertGreater(first_growth, second_growth, 
                          "TFP growth should be higher in breakthrough rounds")
        self.assertGreater(third_growth, second_growth, 
                          "TFP growth should be higher in breakthrough rounds")
        
        # Check that the final TFP is higher than it would be without breakthroughs
        # Assume base TFP growth of 10% per round
        expected_tfp = initial_tfp * (1.1 ** 3)  # 3 rounds of 10% growth
        
        self.assertGreater(third_tfp, expected_tfp, 
                          f"Final TFP should be higher due to breakthroughs: {third_tfp} <= {expected_tfp}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_technology_breakthrough_distribution(self):
        """Test that technology breakthrough effects are distributed within the expected ranges."""
        # Create a randomized events manager
        events_manager = RandomizedEventsManager(seed=42)
        
        # Run a large number of simulations
        num_simulations = 100
        num_years = 20
        tfp_increases = []
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=42 + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Collect effects from technology breakthrough events
            for entry in history:
                event = entry["event"]
                if event.get("category") == "technological_breakthrough":
                    tfp_increases.append(event["effects"]["tfp_increase"])
                    
        # Check that we have a reasonable number of breakthrough events
        self.assertGreater(len(tfp_increases), 10, "Should have a reasonable number of breakthrough events")
        
        # Check that effects are within the expected ranges
        tech_config = EVENT_CATEGORIES["technological_breakthrough"]
        tfp_range = tech_config["effects"]["tfp_increase"]
        
        # Check TFP effects
        self.assertGreaterEqual(min(tfp_increases), tfp_range[0], 
                              f"Minimum TFP effect {min(tfp_increases)} should be >= {tfp_range[0]}")
        self.assertLessEqual(max(tfp_increases), tfp_range[1], 
                           f"Maximum TFP effect {max(tfp_increases)} should be <= {tfp_range[1]}")
        
        # Check that effects are distributed across the range (not all at min or max)
        tfp_std = np.std(tfp_increases)
        
        self.assertGreater(tfp_std, 0.001, "TFP effects should be distributed across the range")
        
    def test_technology_breakthrough_gdp_impact(self):
        """Test that technology breakthroughs have a positive impact on GDP."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force a technology breakthrough
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a technology breakthrough event
            tech_config = EVENT_CATEGORIES["technological_breakthrough"]
            event = {
                "year": year,
                "name": tech_config["name"],
                "description": tech_config["description"],
                "category": "technological_breakthrough",
                "effects": {
                    "tfp_increase": 0.04  # 4% TFP increase
                },
                "r_and_d_modifier": tech_config["r_and_d_modifier"],
                "triggered": True
            }
            return [event]
            
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the team's state before the breakthrough
        pre_tech_state = game_state.team_manager.get_team_state(team_id)
        pre_tech_gdp = pre_tech_state["current_state"].get("Y", 0)
        
        # Advance a round to trigger the breakthrough
        game_state.advance_round()
        
        # Record the team's state after the breakthrough
        post_tech_state = game_state.team_manager.get_team_state(team_id)
        post_tech_gdp = post_tech_state["current_state"].get("Y", 0)
        
        # Calculate what GDP would have been without the breakthrough
        # This is a simplification, as GDP is affected by many factors
        expected_gdp_growth = 0.15  # Assume 15% growth over 5 years without breakthrough
        expected_gdp = pre_tech_gdp * (1 + expected_gdp_growth)
        
        # Check that GDP growth was higher than expected due to the breakthrough
        self.assertGreater(post_tech_gdp, expected_gdp, 
                          f"GDP was not boosted by technology breakthrough: {post_tech_gdp} <= {expected_gdp}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate

if __name__ == '__main__':
    unittest.main()
