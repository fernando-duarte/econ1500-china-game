"""
WTO accession event tests for the China Growth Game.

This module contains tests to verify that the WTO accession event
triggers at the correct year and applies the expected effects.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import uuid

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.events_manager import EventsManager
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

class TestWTOEvent(unittest.TestCase):
    """Test cases for the WTO accession event."""

    def setUp(self):
        """Set up the test environment."""
        # Create a notification manager for testing
        self.notification_manager = NotificationManager()
        
        # Initialize game state with notification manager
        self.game_state = GameState(notification_manager=self.notification_manager)
        
        # Create test teams
        self.test_team_ids = []
        for i in range(3):
            team = self.game_state.create_team(f"Test Team {i+1}")
            self.test_team_ids.append(team["team_id"])
            
        # Start the game
        self.game_state.start_game()
        
    def test_wto_event_year(self):
        """Test that the WTO event is defined for the correct year (2001)."""
        # Get the events from the events manager
        events = self.game_state.events_manager.events
        
        # Find the WTO event
        wto_event = None
        for event in events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event exists
        self.assertIsNotNone(wto_event, "WTO event not found in events manager")
        
        # Check that the WTO event is defined for the year 2001
        self.assertEqual(wto_event["year"], 2001, f"WTO event year is {wto_event['year']}, expected 2001")
        
    def test_wto_event_triggering(self):
        """Test that the WTO event triggers in the year 2001."""
        # Advance to 2001 (should be round 4 since we start in 1980 with 5-year increments)
        # 1980 -> 1985 -> 1990 -> 1995 -> 2000 -> 2005
        # Round 0 -> 1 -> 2 -> 3 -> 4 -> 5
        
        # Advance to round 3 (year 1995)
        for _ in range(3):
            self.game_state.advance_round()
            
        # Check that we're in 1995
        self.assertEqual(self.game_state.current_year, 1995, f"Current year is {self.game_state.current_year}, expected 1995")
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Advance to round 4 (year 2000)
        self.game_state.advance_round()
        
        # Check that we're in 2000
        self.assertEqual(self.game_state.current_year, 2000, f"Current year is {self.game_state.current_year}, expected 2000")
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Advance to round 5 (year 2005)
        self.game_state.advance_round()
        
        # Check that we're in 2005
        self.assertEqual(self.game_state.current_year, 2005, f"Current year is {self.game_state.current_year}, expected 2005")
        
        # Check that the WTO event was triggered
        # Since our game uses 5-year increments, the WTO event (2001) should trigger in the round that includes 2001,
        # which is the round from 2000 to 2005
        
        # Get the WTO event from the events manager
        wto_event = None
        for event in self.game_state.events_manager.events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event was triggered
        self.assertTrue(wto_event["triggered"], "WTO event was not triggered")
        
    def test_wto_event_effects(self):
        """Test that the WTO event applies the expected effects."""
        # Get the WTO event from the events manager
        wto_event = None
        for event in self.game_state.events_manager.events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event exists
        self.assertIsNotNone(wto_event, "WTO event not found in events manager")
        
        # Check that the WTO event has the expected effects
        self.assertIn("exports_multiplier", wto_event["effects"], "WTO event does not have exports_multiplier effect")
        self.assertIn("tfp_increase", wto_event["effects"], "WTO event does not have tfp_increase effect")
        
        # Check that the effects have the expected values
        self.assertGreater(wto_event["effects"]["exports_multiplier"], 1.0, 
                          "WTO event exports_multiplier should be greater than 1.0")
        self.assertGreater(wto_event["effects"]["tfp_increase"], 0.0, 
                          "WTO event tfp_increase should be greater than 0.0")
        
    def test_wto_event_application(self):
        """Test that the WTO event effects are applied to team economies."""
        # Create a game state and advance to just before the WTO event
        game_state = GameState()
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 4 (year 2000)
        for _ in range(4):
            game_state.advance_round()
            
        # Record the team's state before the WTO event
        pre_wto_state = game_state.team_manager.get_team_state(team_id)
        pre_wto_exports = pre_wto_state["current_state"].get("exports", 0)
        pre_wto_tfp = pre_wto_state["current_state"].get("A", 0)
        
        # Advance to round 5 (year 2005) to trigger the WTO event
        game_state.advance_round()
        
        # Record the team's state after the WTO event
        post_wto_state = game_state.team_manager.get_team_state(team_id)
        post_wto_exports = post_wto_state["current_state"].get("exports", 0)
        post_wto_tfp = post_wto_state["current_state"].get("A", 0)
        
        # Check that exports increased due to the WTO event
        # Note: This is a simplification, as exports are affected by many factors
        # In a real test, we would need to control for other factors
        self.assertGreater(post_wto_exports, pre_wto_exports, 
                          f"Exports did not increase after WTO event: {pre_wto_exports} -> {post_wto_exports}")
        
        # Check that TFP increased due to the WTO event
        self.assertGreater(post_wto_tfp, pre_wto_tfp, 
                          f"TFP did not increase after WTO event: {pre_wto_tfp} -> {post_wto_tfp}")
        
    def test_wto_event_notification(self):
        """Test that teams are notified when the WTO event occurs."""
        # Create a game state with notification manager
        game_state = GameState(notification_manager=self.notification_manager)
        
        # Create a test team
        team = game_state.create_team("Test Team")
        team_id = team["team_id"]
        
        # Start the game
        game_state.start_game()
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Register an event handler for event notifications
        event_notifications = []
        def event_handler(data, room):
            event_notifications.append((data, room))
            
        self.notification_manager.on("eventTriggered", event_handler)
        
        # Advance to round 5 (year 2005) to trigger the WTO event
        for _ in range(5):
            game_state.advance_round()
            
        # Check that an event notification was sent
        self.assertGreater(len(event_notifications), 0, "No event notifications were sent")
        
        # Check that at least one notification was for the WTO event
        wto_notifications = [n for n in event_notifications if "WTO" in str(n)]
        self.assertGreater(len(wto_notifications), 0, "No WTO event notifications were sent")
        
    def test_wto_event_idempotency(self):
        """Test that the WTO event is only triggered once."""
        # Create a game state
        game_state = GameState()
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 5 (year 2005) to trigger the WTO event
        for _ in range(5):
            game_state.advance_round()
            
        # Get the WTO event from the events manager
        wto_event = None
        for event in game_state.events_manager.events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event was triggered
        self.assertTrue(wto_event["triggered"], "WTO event was not triggered")
        
        # Reset the game state to round 4 (year 2000)
        game_state.current_round = 4
        game_state.current_year = 2000
        
        # Clear the processed rounds set to allow re-processing
        game_state.processed_rounds.clear()
        
        # Advance to round 5 (year 2005) again
        game_state.advance_round()
        
        # Get the current events for year 2005
        current_events = game_state.events_manager.get_current_events(2005)
        
        # Check that the WTO event is not in the current events
        wto_in_current = any("WTO" in event["name"] for event in current_events)
        self.assertFalse(wto_in_current, "WTO event was triggered again")
        
    def test_wto_event_reset(self):
        """Test that the WTO event is reset when the game is reset."""
        # Create a game state
        game_state = GameState()
        
        # Start the game
        game_state.start_game()
        
        # Advance to round 5 (year 2005) to trigger the WTO event
        for _ in range(5):
            game_state.advance_round()
            
        # Get the WTO event from the events manager
        wto_event = None
        for event in game_state.events_manager.events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event was triggered
        self.assertTrue(wto_event["triggered"], "WTO event was not triggered")
        
        # Reset the game
        game_state.reset_game()
        
        # Get the WTO event from the events manager again
        wto_event = None
        for event in game_state.events_manager.events:
            if "WTO" in event["name"]:
                wto_event = event
                break
                
        # Check that the WTO event was reset
        self.assertFalse(wto_event["triggered"], "WTO event was not reset")

if __name__ == '__main__':
    unittest.main()
