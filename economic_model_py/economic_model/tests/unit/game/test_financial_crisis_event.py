"""
Financial crisis event tests for the China Growth Game.

This module contains tests to verify that financial crisis events
trigger with appropriate probabilities and apply the expected effects.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import uuid
import random

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.events_manager import EventsManager
from economic_model_py.economic_model.game.randomized_events_manager import RandomizedEventsManager, EVENT_CATEGORIES
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

class TestFinancialCrisisEvent(unittest.TestCase):
    """Test cases for financial crisis events."""

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
        
    def test_fixed_financial_crisis_event(self):
        """Test that the fixed financial crisis event (2008) is defined correctly."""
        # Get the events from the events manager
        events = self.game_state.events_manager.events
        
        # Find the financial crisis event
        crisis_event = None
        for event in events:
            if "Financial Crisis" in event["name"]:
                crisis_event = event
                break
                
        # Check that the financial crisis event exists
        self.assertIsNotNone(crisis_event, "Financial crisis event not found in events manager")
        
        # Check that the financial crisis event is defined for the year 2008
        self.assertEqual(crisis_event["year"], 2008, f"Financial crisis event year is {crisis_event['year']}, expected 2008")
        
        # Check that the financial crisis event has the expected effects
        self.assertIn("exports_multiplier", crisis_event["effects"], "Financial crisis event does not have exports_multiplier effect")
        self.assertIn("gdp_growth_delta", crisis_event["effects"], "Financial crisis event does not have gdp_growth_delta effect")
        
        # Check that the effects have the expected values
        self.assertLess(crisis_event["effects"]["exports_multiplier"], 1.0, 
                       "Financial crisis event exports_multiplier should be less than 1.0")
        self.assertLess(crisis_event["effects"]["gdp_growth_delta"], 0.0, 
                       "Financial crisis event gdp_growth_delta should be negative")
        
    def test_fixed_financial_crisis_triggering(self):
        """Test that the fixed financial crisis event triggers in the year 2008."""
        # Advance to 2008 (should be round 5 or 6 since we start in 1980 with 5-year increments)
        # 1980 -> 1985 -> 1990 -> 1995 -> 2000 -> 2005 -> 2010
        # Round 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
        
        # Advance to round 5 (year 2005)
        for _ in range(5):
            self.game_state.advance_round()
            
        # Check that we're in 2005
        self.assertEqual(self.game_state.current_year, 2005, f"Current year is {self.game_state.current_year}, expected 2005")
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Advance to round 6 (year 2010)
        self.game_state.advance_round()
        
        # Check that we're in 2010
        self.assertEqual(self.game_state.current_year, 2010, f"Current year is {self.game_state.current_year}, expected 2010")
        
        # Check that the financial crisis event was triggered
        # Since our game uses 5-year increments, the financial crisis event (2008) should trigger in the round that includes 2008,
        # which is the round from 2005 to 2010
        
        # Get the financial crisis event from the events manager
        crisis_event = None
        for event in self.game_state.events_manager.events:
            if "Financial Crisis" in event["name"]:
                crisis_event = event
                break
                
        # Check that the financial crisis event was triggered
        self.assertTrue(crisis_event["triggered"], "Financial crisis event was not triggered")
        
    def test_fixed_financial_crisis_effects(self):
        """Test that the fixed financial crisis event applies the expected effects."""
        # Create a game state and advance to just before the financial crisis event
        game_state = GameState()
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 5 (year 2005)
        for _ in range(5):
            game_state.advance_round()
            
        # Record the team's state before the financial crisis event
        pre_crisis_state = game_state.team_manager.get_team_state(team_id)
        pre_crisis_gdp = pre_crisis_state["current_state"].get("Y", 0)
        pre_crisis_exports = pre_crisis_state["current_state"].get("exports", 0)
        
        # Advance to round 6 (year 2010) to trigger the financial crisis event
        game_state.advance_round()
        
        # Record the team's state after the financial crisis event
        post_crisis_state = game_state.team_manager.get_team_state(team_id)
        post_crisis_gdp = post_crisis_state["current_state"].get("Y", 0)
        post_crisis_exports = post_crisis_state["current_state"].get("exports", 0)
        
        # Calculate what GDP would have been without the crisis
        # This is a simplification, as GDP is affected by many factors
        # In a real test, we would need to control for other factors
        expected_gdp_growth = 0.15  # Assume 15% growth over 5 years without crisis
        expected_gdp = pre_crisis_gdp * (1 + expected_gdp_growth)
        
        # Check that GDP growth was lower than expected due to the financial crisis
        # We can't assert that GDP decreased, as other growth factors might outweigh the crisis effect
        # But we can check that it's lower than what we would expect without the crisis
        self.assertLess(post_crisis_gdp, expected_gdp, 
                       f"GDP was not affected by financial crisis: {post_crisis_gdp} >= {expected_gdp}")
        
        # Check that exports were affected by the financial crisis
        # Again, we can't assert that exports decreased, but we can check that they're lower than expected
        expected_exports_growth = 0.15  # Assume 15% growth over 5 years without crisis
        expected_exports = pre_crisis_exports * (1 + expected_exports_growth)
        
        self.assertLess(post_crisis_exports, expected_exports, 
                       f"Exports were not affected by financial crisis: {post_crisis_exports} >= {expected_exports}")
        
    def test_random_economic_recession_event(self):
        """Test that random economic recession events have appropriate probability and effects."""
        # Check that the economic recession event category exists
        self.assertIn("economic_recession", EVENT_CATEGORIES, "Economic recession event category not found")
        
        # Check that the economic recession event has the expected probability
        recession_config = EVENT_CATEGORIES["economic_recession"]
        self.assertGreater(recession_config["probability"], 0.0, "Economic recession probability should be greater than 0")
        self.assertLess(recession_config["probability"], 0.5, "Economic recession probability should be less than 0.5")
        
        # Check that the economic recession event has the expected effects
        self.assertIn("gdp_growth_delta", recession_config["effects"], "Economic recession does not have gdp_growth_delta effect")
        self.assertIn("exports_multiplier", recession_config["effects"], "Economic recession does not have exports_multiplier effect")
        
        # Check that the effects have the expected ranges
        gdp_delta_range = recession_config["effects"]["gdp_growth_delta"]
        exports_multiplier_range = recession_config["effects"]["exports_multiplier"]
        
        self.assertLess(gdp_delta_range[0], 0.0, "Economic recession gdp_growth_delta lower bound should be negative")
        self.assertLess(gdp_delta_range[1], 0.0, "Economic recession gdp_growth_delta upper bound should be negative")
        self.assertLess(exports_multiplier_range[0], 1.0, "Economic recession exports_multiplier lower bound should be less than 1.0")
        self.assertLess(exports_multiplier_range[1], 1.0, "Economic recession exports_multiplier upper bound should be less than 1.0")
        
    def test_random_economic_recession_probability(self):
        """Test that random economic recession events occur with the expected probability."""
        # Create a randomized events manager with a fixed seed
        events_manager = RandomizedEventsManager(seed=42)
        
        # Get the expected probability of economic recession
        expected_prob = EVENT_CATEGORIES["economic_recession"]["probability"]
        
        # Run a large number of simulations to get statistically significant results
        num_simulations = 1000
        num_years = 20
        recession_count = 0
        total_years = num_simulations * num_years
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=42 + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Count economic recession events
            for entry in history:
                event = entry["event"]
                if event.get("category") == "economic_recession":
                    recession_count += 1
                    
        # Calculate observed probability
        observed_prob = recession_count / total_years
        
        # Check that observed probability is close to expected probability
        # Allow for some statistical variation (within 20% of expected)
        margin = 0.2 * expected_prob
        self.assertAlmostEqual(observed_prob, expected_prob, delta=margin,
                              msg=f"Economic recession probability: expected {expected_prob}, observed {observed_prob}")
                              
    def test_random_economic_recession_effects(self):
        """Test that random economic recession events apply the expected effects."""
        # Create a game state with randomized events
        game_state = GameState(use_randomized_events=True, random_seed=42)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Mock the _generate_random_events method to force an economic recession
        original_generate = game_state.events_manager._generate_random_events
        
        def mock_generate(year):
            # Create a recession event
            recession_config = EVENT_CATEGORIES["economic_recession"]
            event = {
                "year": year,
                "name": recession_config["name"],
                "description": recession_config["description"],
                "category": "economic_recession",
                "effects": {
                    "gdp_growth_delta": -0.05,  # 5% GDP decline
                    "exports_multiplier": 0.8   # 20% exports decline
                },
                "triggered": True
            }
            return [event]
            
        # Replace the method
        game_state.events_manager._generate_random_events = mock_generate
        
        # Record the team's state before the recession
        pre_recession_state = game_state.team_manager.get_team_state(team_id)
        pre_recession_gdp = pre_recession_state["current_state"].get("Y", 0)
        pre_recession_exports = pre_recession_state["current_state"].get("exports", 0)
        
        # Advance a round to trigger the recession
        game_state.advance_round()
        
        # Record the team's state after the recession
        post_recession_state = game_state.team_manager.get_team_state(team_id)
        post_recession_gdp = post_recession_state["current_state"].get("Y", 0)
        post_recession_exports = post_recession_state["current_state"].get("exports", 0)
        
        # Calculate what GDP would have been without the recession
        # This is a simplification, as GDP is affected by many factors
        expected_gdp_growth = 0.15  # Assume 15% growth over 5 years without recession
        expected_gdp = pre_recession_gdp * (1 + expected_gdp_growth)
        
        # Check that GDP growth was lower than expected due to the recession
        self.assertLess(post_recession_gdp, expected_gdp, 
                       f"GDP was not affected by recession: {post_recession_gdp} >= {expected_gdp}")
        
        # Check that exports were affected by the recession
        expected_exports_growth = 0.15  # Assume 15% growth over 5 years without recession
        expected_exports = pre_recession_exports * (1 + expected_exports_growth)
        
        self.assertLess(post_recession_exports, expected_exports, 
                       f"Exports were not affected by recession: {post_recession_exports} >= {expected_exports}")
        
        # Restore the original method
        game_state.events_manager._generate_random_events = original_generate
        
    def test_financial_crisis_notification(self):
        """Test that teams are notified when a financial crisis event occurs."""
        # Create a game state with notification manager
        game_state = GameState(notification_manager=self.notification_manager)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 5 (year 2005)
        for _ in range(5):
            game_state.advance_round()
            
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Register an event handler for event notifications
        event_notifications = []
        def event_handler(data, room):
            event_notifications.append((data, room))
            
        self.notification_manager.on("eventTriggered", event_handler)
        
        # Advance to round 6 (year 2010) to trigger the financial crisis event
        game_state.advance_round()
        
        # Check that an event notification was sent
        self.assertGreater(len(event_notifications), 0, "No event notifications were sent")
        
        # Check that at least one notification was for the financial crisis event
        crisis_notifications = [n for n in event_notifications if "Financial Crisis" in str(n)]
        self.assertGreater(len(crisis_notifications), 0, "No financial crisis event notifications were sent")
        
    def test_financial_crisis_idempotency(self):
        """Test that the financial crisis event is only triggered once."""
        # Create a game state
        game_state = GameState()
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 6 (year 2010) to trigger the financial crisis event
        for _ in range(6):
            game_state.advance_round()
            
        # Get the financial crisis event from the events manager
        crisis_event = None
        for event in game_state.events_manager.events:
            if "Financial Crisis" in event["name"]:
                crisis_event = event
                break
                
        # Check that the financial crisis event was triggered
        self.assertTrue(crisis_event["triggered"], "Financial crisis event was not triggered")
        
        # Reset the game state to round 5 (year 2005)
        game_state.current_round = 5
        game_state.current_year = 2005
        
        # Clear the processed rounds set to allow re-processing
        game_state.processed_rounds.clear()
        
        # Advance to round 6 (year 2010) again
        game_state.advance_round()
        
        # Get the current events for year 2010
        current_events = game_state.events_manager.get_current_events(2010)
        
        # Check that the financial crisis event is not in the current events
        crisis_in_current = any("Financial Crisis" in event["name"] for event in current_events)
        self.assertFalse(crisis_in_current, "Financial crisis event was triggered again")
        
    def test_financial_crisis_reset(self):
        """Test that the financial crisis event is reset when the game is reset."""
        # Create a game state
        game_state = GameState()
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 6 (year 2010) to trigger the financial crisis event
        for _ in range(6):
            game_state.advance_round()
            
        # Get the financial crisis event from the events manager
        crisis_event = None
        for event in game_state.events_manager.events:
            if "Financial Crisis" in event["name"]:
                crisis_event = event
                break
                
        # Check that the financial crisis event was triggered
        self.assertTrue(crisis_event["triggered"], "Financial crisis event was not triggered")
        
        # Reset the game
        game_state.reset_game()
        
        # Get the financial crisis event from the events manager again
        crisis_event = None
        for event in game_state.events_manager.events:
            if "Financial Crisis" in event["name"]:
                crisis_event = event
                break
                
        # Check that the financial crisis event was reset
        self.assertFalse(crisis_event["triggered"], "Financial crisis event was not reset")

if __name__ == '__main__':
    unittest.main()
