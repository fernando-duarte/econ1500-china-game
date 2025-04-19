import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime
import uuid

from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.prize_manager import PrizeManager, PRIZE_TYPES
from economic_model_py.economic_model.utils.persistence import PersistenceManager

class TestPrizePersistence(unittest.TestCase):
    """Test cases for prize persistence."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database file
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp()
        
        # Initialize persistence manager with the temporary database
        self.persistence_manager = PersistenceManager(db_path=self.temp_db_path)
        
        # Initialize game state with persistence manager
        self.game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Create test teams
        self.test_team_ids = []
        for i in range(3):
            team = self.game_state.create_team(f"Test Team {i+1}")
            self.test_team_ids.append(team["team_id"])
            
        # Start the game
        self.game_state.start_game()
        
    def tearDown(self):
        """Clean up after the test."""
        # Close the persistence manager
        self.persistence_manager.close()
        
        # Remove the temporary database file
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
    def test_save_and_load_prizes(self):
        """Test saving and loading prizes to/from the database."""
        # Add mock prizes to the prize manager
        team_id = self.test_team_ids[0]
        self.game_state.prize_manager.awarded_prizes = {
            team_id: {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Save prizes to the database
        success = self.game_state.prize_manager.save_prizes(self.game_state.game_id)
        self.assertTrue(success)
        
        # Reset prizes in memory
        self.game_state.prize_manager.reset_prizes()
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 0)
        
        # Load prizes from the database
        success = self.game_state.prize_manager.load_prizes(self.game_state.game_id)
        self.assertTrue(success)
        
        # Check that prizes were loaded correctly
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 1)
        self.assertIn(team_id, self.game_state.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", self.game_state.prize_manager.awarded_prizes[team_id])
        
    def test_prize_persistence_across_game_restart(self):
        """Test that prizes persist across game restarts."""
        # Add mock prizes to the prize manager
        team_id = self.test_team_ids[0]
        self.game_state.prize_manager.awarded_prizes = {
            team_id: {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Save the game state
        success = self.game_state.save_game()
        self.assertTrue(success)
        
        # Get the game ID
        game_id = self.game_state.game_id
        
        # Create a new game state instance
        new_game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Load the game
        success = new_game_state.load_game(game_id)
        self.assertTrue(success)
        
        # Check that prizes were loaded correctly
        self.assertEqual(len(new_game_state.prize_manager.awarded_prizes), 1)
        self.assertIn(team_id, new_game_state.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", new_game_state.prize_manager.awarded_prizes[team_id])
        
    def test_prize_persistence_with_multiple_prizes(self):
        """Test persistence with multiple prizes for multiple teams."""
        # Add mock prizes to the prize manager
        team1_id = self.test_team_ids[0]
        team2_id = self.test_team_ids[1]
        
        self.game_state.prize_manager.awarded_prizes = {
            team1_id: {
                "gdp_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                },
                "tech_leadership": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                }
            },
            team2_id: {
                "sustainable_growth": {
                    "awarded_at": datetime.now().isoformat(),
                    "name": PRIZE_TYPES["sustainable_growth"]["name"],
                    "description": PRIZE_TYPES["sustainable_growth"]["description"],
                    "effects": PRIZE_TYPES["sustainable_growth"]["effects"]
                }
            }
        }
        
        # Save the game state
        success = self.game_state.save_game()
        self.assertTrue(success)
        
        # Get the game ID
        game_id = self.game_state.game_id
        
        # Create a new game state instance
        new_game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Load the game
        success = new_game_state.load_game(game_id)
        self.assertTrue(success)
        
        # Check that prizes were loaded correctly
        self.assertEqual(len(new_game_state.prize_manager.awarded_prizes), 2)
        
        # Check team 1 prizes
        self.assertIn(team1_id, new_game_state.prize_manager.awarded_prizes)
        self.assertEqual(len(new_game_state.prize_manager.awarded_prizes[team1_id]), 2)
        self.assertIn("gdp_growth", new_game_state.prize_manager.awarded_prizes[team1_id])
        self.assertIn("tech_leadership", new_game_state.prize_manager.awarded_prizes[team1_id])
        
        # Check team 2 prizes
        self.assertIn(team2_id, new_game_state.prize_manager.awarded_prizes)
        self.assertEqual(len(new_game_state.prize_manager.awarded_prizes[team2_id]), 1)
        self.assertIn("sustainable_growth", new_game_state.prize_manager.awarded_prizes[team2_id])
        
    def test_prize_data_integrity_across_restarts(self):
        """Test that prize data maintains integrity across restarts."""
        # Add mock prizes to the prize manager with specific effects
        team_id = self.test_team_ids[0]
        
        # Create a prize with custom effects
        custom_effects = {
            "tfp_increase": 0.1,  # Custom value different from default
            "custom_effect": "test_value"  # Additional custom effect
        }
        
        self.game_state.prize_manager.awarded_prizes = {
            team_id: {
                "gdp_growth": {
                    "awarded_at": "2023-01-01T12:00:00",  # Fixed timestamp for comparison
                    "name": "Custom Prize Name",  # Custom name
                    "description": "Custom Prize Description",  # Custom description
                    "effects": custom_effects
                }
            }
        }
        
        # Save the game state
        success = self.game_state.save_game()
        self.assertTrue(success)
        
        # Get the game ID
        game_id = self.game_state.game_id
        
        # Create a new game state instance
        new_game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Load the game
        success = new_game_state.load_game(game_id)
        self.assertTrue(success)
        
        # Check that prize data maintains integrity
        self.assertIn(team_id, new_game_state.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", new_game_state.prize_manager.awarded_prizes[team_id])
        
        prize = new_game_state.prize_manager.awarded_prizes[team_id]["gdp_growth"]
        
        # Check timestamp
        self.assertEqual(prize["awarded_at"], "2023-01-01T12:00:00")
        
        # Check name and description
        self.assertEqual(prize["name"], "Custom Prize Name")
        self.assertEqual(prize["description"], "Custom Prize Description")
        
        # Check effects
        self.assertEqual(prize["effects"]["tfp_increase"], 0.1)
        self.assertEqual(prize["effects"]["custom_effect"], "test_value")
        
    def test_automatic_prize_persistence_during_award(self):
        """Test that prizes are automatically persisted when awarded."""
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
        
        # Advance the round to trigger prize awarding
        self.game_state.advance_round()
        
        # Restore the original method
        self.game_state.prize_manager.check_prize_eligibility = original_check
        
        # Create a new game state instance
        new_game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Load the game
        success = new_game_state.load_game(self.game_state.game_id)
        self.assertTrue(success)
        
        # Check that prizes were automatically persisted
        self.assertIn(self.test_team_ids[0], new_game_state.prize_manager.awarded_prizes)
        self.assertIn("gdp_growth", new_game_state.prize_manager.awarded_prizes[self.test_team_ids[0]])
        
    def test_persistence_with_no_prizes(self):
        """Test persistence behavior when no prizes have been awarded."""
        # Save the game state with no prizes
        success = self.game_state.save_game()
        self.assertTrue(success)
        
        # Get the game ID
        game_id = self.game_state.game_id
        
        # Create a new game state instance
        new_game_state = GameState(persistence_manager=self.persistence_manager)
        
        # Load the game
        success = new_game_state.load_game(game_id)
        self.assertTrue(success)
        
        # Check that no prizes were loaded
        self.assertEqual(len(new_game_state.prize_manager.awarded_prizes), 0)

if __name__ == '__main__':
    unittest.main()
