import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import uuid

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.prize_manager import PrizeManager, PRIZE_TYPES
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

class TestPrizeNotification(unittest.TestCase):
    """Test cases for prize notifications."""

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
        
    def test_notification_on_prize_award(self):
        """Test that notifications are sent when prizes are awarded."""
        # Mock the check_prize_eligibility method to return eligible prizes
        def mock_check(*args, **kwargs):
            return {
                self.test_team_ids[0]: [
                    {
                        "type": "gdp_growth",
                        "name": PRIZE_TYPES["gdp_growth"]["name"],
                        "description": PRIZE_TYPES["gdp_growth"]["description"],
                        "effects": PRIZE_TYPES["gdp_growth"]["effects"],
                        "game_id": self.game_state.game_id
                    }
                ]
            }
            
        original_check = self.game_state.prize_manager.check_prize_eligibility
        self.game_state.prize_manager.check_prize_eligibility = mock_check
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Advance the round to trigger prize awarding
        self.game_state.advance_round()
        
        # Restore the original method
        self.game_state.prize_manager.check_prize_eligibility = original_check
        
        # Check that a notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check that the notification was sent to the correct team
        event = prize_events[0]
        self.assertEqual(event["room"], f"team-{self.test_team_ids[0]}")
        self.assertEqual(event["data"]["team_id"], self.test_team_ids[0])
        self.assertEqual(event["data"]["prize_type"], "gdp_growth")
        
        # Check that a global notification was also sent
        global_events = self.notification_manager.get_events("prizeAwardedGlobal")
        self.assertEqual(len(global_events), 1)
        
    def test_gdp_growth_prize_notification(self):
        """Test notification for GDP growth achievement prize."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        prize_type = "gdp_growth"
        prize_data = {
            "awarded_at": datetime.now().isoformat(),
            "name": PRIZE_TYPES[prize_type]["name"],
            "description": PRIZE_TYPES[prize_type]["description"],
            "effects": PRIZE_TYPES[prize_type]["effects"]
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Manually emit the notification
        self.notification_manager.emit_prize_awarded(team_id, prize_type, prize_data)
        
        # Check that the notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check notification content
        event = prize_events[0]
        self.assertEqual(event["room"], f"team-{team_id}")
        self.assertEqual(event["data"]["team_id"], team_id)
        self.assertEqual(event["data"]["prize_type"], prize_type)
        self.assertEqual(event["data"]["prize_name"], PRIZE_TYPES[prize_type]["name"])
        self.assertEqual(event["data"]["prize_description"], PRIZE_TYPES[prize_type]["description"])
        self.assertEqual(event["data"]["effects"], PRIZE_TYPES[prize_type]["effects"])
        
    def test_tech_leadership_prize_notification(self):
        """Test notification for tech leadership prize."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        prize_type = "tech_leadership"
        prize_data = {
            "awarded_at": datetime.now().isoformat(),
            "name": PRIZE_TYPES[prize_type]["name"],
            "description": PRIZE_TYPES[prize_type]["description"],
            "effects": PRIZE_TYPES[prize_type]["effects"]
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Manually emit the notification
        self.notification_manager.emit_prize_awarded(team_id, prize_type, prize_data)
        
        # Check that the notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check notification content
        event = prize_events[0]
        self.assertEqual(event["data"]["prize_type"], prize_type)
        self.assertEqual(event["data"]["prize_name"], PRIZE_TYPES[prize_type]["name"])
        
    def test_sustainable_growth_prize_notification(self):
        """Test notification for sustainable growth prize."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        prize_type = "sustainable_growth"
        prize_data = {
            "awarded_at": datetime.now().isoformat(),
            "name": PRIZE_TYPES[prize_type]["name"],
            "description": PRIZE_TYPES[prize_type]["description"],
            "effects": PRIZE_TYPES[prize_type]["effects"]
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Manually emit the notification
        self.notification_manager.emit_prize_awarded(team_id, prize_type, prize_data)
        
        # Check that the notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check notification content
        event = prize_events[0]
        self.assertEqual(event["data"]["prize_type"], prize_type)
        self.assertEqual(event["data"]["prize_name"], PRIZE_TYPES[prize_type]["name"])
        
    def test_crisis_management_prize_notification(self):
        """Test notification for crisis management prize."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        prize_type = "crisis_management"
        prize_data = {
            "awarded_at": datetime.now().isoformat(),
            "name": PRIZE_TYPES[prize_type]["name"],
            "description": PRIZE_TYPES[prize_type]["description"],
            "effects": PRIZE_TYPES[prize_type]["effects"]
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Manually emit the notification
        self.notification_manager.emit_prize_awarded(team_id, prize_type, prize_data)
        
        # Check that the notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check notification content
        event = prize_events[0]
        self.assertEqual(event["data"]["prize_type"], prize_type)
        self.assertEqual(event["data"]["prize_name"], PRIZE_TYPES[prize_type]["name"])
        
    def test_export_champion_prize_notification(self):
        """Test notification for export champion prize."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        prize_type = "export_champion"
        prize_data = {
            "awarded_at": datetime.now().isoformat(),
            "name": PRIZE_TYPES[prize_type]["name"],
            "description": PRIZE_TYPES[prize_type]["description"],
            "effects": PRIZE_TYPES[prize_type]["effects"]
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Manually emit the notification
        self.notification_manager.emit_prize_awarded(team_id, prize_type, prize_data)
        
        # Check that the notification was sent
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 1)
        
        # Check notification content
        event = prize_events[0]
        self.assertEqual(event["data"]["prize_type"], prize_type)
        self.assertEqual(event["data"]["prize_name"], PRIZE_TYPES[prize_type]["name"])
        
    def test_notification_to_correct_team_only(self):
        """Test that notifications are sent only to the correct team."""
        # Add mock prizes to multiple teams
        team1_id = self.test_team_ids[0]
        team2_id = self.test_team_ids[1]
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Emit notifications for different teams
        self.notification_manager.emit_prize_awarded(
            team1_id, 
            "gdp_growth", 
            {
                "awarded_at": datetime.now().isoformat(),
                "name": PRIZE_TYPES["gdp_growth"]["name"],
                "description": PRIZE_TYPES["gdp_growth"]["description"],
                "effects": PRIZE_TYPES["gdp_growth"]["effects"]
            }
        )
        
        self.notification_manager.emit_prize_awarded(
            team2_id, 
            "tech_leadership", 
            {
                "awarded_at": datetime.now().isoformat(),
                "name": PRIZE_TYPES["tech_leadership"]["name"],
                "description": PRIZE_TYPES["tech_leadership"]["description"],
                "effects": PRIZE_TYPES["tech_leadership"]["effects"]
            }
        )
        
        # Check that notifications were sent to the correct teams
        prize_events = self.notification_manager.get_events("prizeAwarded")
        self.assertEqual(len(prize_events), 2)
        
        # Check team 1 notification
        team1_events = [e for e in prize_events if e["room"] == f"team-{team1_id}"]
        self.assertEqual(len(team1_events), 1)
        self.assertEqual(team1_events[0]["data"]["team_id"], team1_id)
        self.assertEqual(team1_events[0]["data"]["prize_type"], "gdp_growth")
        
        # Check team 2 notification
        team2_events = [e for e in prize_events if e["room"] == f"team-{team2_id}"]
        self.assertEqual(len(team2_events), 1)
        self.assertEqual(team2_events[0]["data"]["team_id"], team2_id)
        self.assertEqual(team2_events[0]["data"]["prize_type"], "tech_leadership")
        
    def test_notification_on_prizes_loaded(self):
        """Test that notifications are sent when prizes are loaded."""
        # Add mock prizes to the prize manager
        team_prizes = {
            self.test_team_ids[0]: {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            },
            self.test_team_ids[1]: {
                "tech_leadership": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                }
            }
        }
        
        # Clear any existing events
        self.notification_manager.clear_events()
        
        # Emit the prizes loaded notification
        self.notification_manager.emit_prizes_loaded(team_prizes)
        
        # Check that the notification was sent
        prizes_loaded_events = self.notification_manager.get_events("prizesLoaded")
        self.assertEqual(len(prizes_loaded_events), 1)
        
        # Check notification content
        event = prizes_loaded_events[0]
        self.assertEqual(len(event["data"]["prizes"]), 2)
        self.assertIn(self.test_team_ids[0], event["data"]["prizes"])
        self.assertIn(self.test_team_ids[1], event["data"]["prizes"])
        self.assertIn("gdp_growth", event["data"]["prizes"][self.test_team_ids[0]])
        self.assertIn("tech_leadership", event["data"]["prizes"][self.test_team_ids[1]])

if __name__ == '__main__':
    unittest.main()
