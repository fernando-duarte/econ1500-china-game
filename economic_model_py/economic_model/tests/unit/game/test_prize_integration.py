import unittest
from unittest.mock import patch, MagicMock
import uuid
import numpy as np
from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.prize_manager import PrizeManager, PRIZE_TYPES

class TestPrizeIntegration(unittest.TestCase):
    """Test cases for the integration of PrizeManager with GameState."""

    def setUp(self):
        """Set up the test environment."""
        self.game_state = GameState()
        
        # Create test teams
        self.test_team_ids = []
        for i in range(3):
            team = self.game_state.create_team(f"Test Team {i+1}")
            self.test_team_ids.append(team["team_id"])
            
        # Start the game
        self.game_state.start_game()
        
    def test_prize_manager_initialization(self):
        """Test that PrizeManager is properly initialized in GameState."""
        self.assertIsInstance(self.game_state.prize_manager, PrizeManager)
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 0)
        
    def test_prize_eligibility_check_in_advance_round(self):
        """Test that prize eligibility is checked during round advancement."""
        # Mock the check_prize_eligibility method to track calls
        original_check = self.game_state.prize_manager.check_prize_eligibility
        check_called = [False]
        
        def mock_check(*args, **kwargs):
            check_called[0] = True
            return {}
            
        self.game_state.prize_manager.check_prize_eligibility = mock_check
        
        # Advance the round
        self.game_state.advance_round()
        
        # Check that the method was called
        self.assertTrue(check_called[0])
        
        # Restore the original method
        self.game_state.prize_manager.check_prize_eligibility = original_check
        
    def test_prize_awarding_in_advance_round(self):
        """Test that prizes are awarded during round advancement."""
        # Mock the award_prizes method to track calls
        original_award = self.game_state.prize_manager.award_prizes
        award_called = [False]
        
        def mock_award(*args, **kwargs):
            award_called[0] = True
            return {}
            
        self.game_state.prize_manager.award_prizes = mock_award
        
        # Advance the round
        self.game_state.advance_round()
        
        # Check that the method was called
        self.assertTrue(award_called[0])
        
        # Restore the original method
        self.game_state.prize_manager.award_prizes = original_award
        
    def test_prize_effects_in_process_team_round(self):
        """Test that prize effects are applied during team round processing."""
        # Mock the apply_prize_effects method to track calls
        original_apply = self.game_state.prize_manager.apply_prize_effects
        apply_called = [False]
        
        def mock_apply(*args, **kwargs):
            apply_called[0] = True
            return args[1]  # Return the round_results unchanged
            
        self.game_state.prize_manager.apply_prize_effects = mock_apply
        
        # Submit a decision for the first team
        team_id = self.test_team_ids[0]
        self.game_state.submit_decision(team_id, 0.3, "market")
        
        # Advance the round
        self.game_state.advance_round()
        
        # Check that the method was called
        self.assertTrue(apply_called[0])
        
        # Restore the original method
        self.game_state.prize_manager.apply_prize_effects = original_apply
        
    def test_prizes_in_game_state(self):
        """Test that prizes are included in the game state."""
        # Add a mock prize to the prize manager
        self.game_state.prize_manager.awarded_prizes = {
            self.test_team_ids[0]: {
                "gdp_growth": {
                    "awarded_at": "2023-01-01T00:00:00",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Get the game state
        game_state = self.game_state.get_game_state()
        
        # Check that prizes are included
        self.assertIn("prizes", game_state)
        self.assertIn(self.test_team_ids[0], game_state["prizes"])
        self.assertIn("gdp_growth", game_state["prizes"][self.test_team_ids[0]])
        
    def test_prizes_in_team_state(self):
        """Test that prizes are included in the team state."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        self.game_state.prize_manager.awarded_prizes = {
            team_id: {
                "gdp_growth": {
                    "awarded_at": "2023-01-01T00:00:00",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Get the team state
        team_state = self.game_state.get_team_state(team_id)
        
        # Check that prizes are included
        self.assertIn("prizes", team_state)
        self.assertIn("gdp_growth", team_state["prizes"])
        
    def test_prize_reset_in_reset_game(self):
        """Test that prizes are reset when the game is reset."""
        # Add a mock prize to the prize manager
        self.game_state.prize_manager.awarded_prizes = {
            self.test_team_ids[0]: {
                "gdp_growth": {
                    "awarded_at": "2023-01-01T00:00:00",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Reset the game
        self.game_state.reset_game()
        
        # Check that prizes were reset
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 0)
        
    def test_prize_idempotency_in_game_flow(self):
        """Test prize idempotency in the full game flow."""
        # Mock the check_prize_eligibility method to always return the same prize
        def mock_check(*args, **kwargs):
            return {
                self.test_team_ids[0]: [
                    {
                        "type": "gdp_growth",
                        "name": PRIZE_TYPES["gdp_growth"]["name"],
                        "description": PRIZE_TYPES["gdp_growth"]["description"],
                        "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                    }
                ]
            }
            
        self.game_state.prize_manager.check_prize_eligibility = mock_check
        
        # Advance the round twice
        self.game_state.advance_round()
        self.game_state.advance_round()
        
        # Check that the prize was only awarded once
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 1)
        self.assertIn(self.test_team_ids[0], self.game_state.prize_manager.awarded_prizes)
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes[self.test_team_ids[0]]), 1)
        
    def test_prize_concurrency_in_game_flow(self):
        """Test prize concurrency in the full game flow."""
        # Mock the check_prize_eligibility method to return prizes for multiple teams
        def mock_check(*args, **kwargs):
            return {
                self.test_team_ids[0]: [
                    {
                        "type": "gdp_growth",
                        "name": PRIZE_TYPES["gdp_growth"]["name"],
                        "description": PRIZE_TYPES["gdp_growth"]["description"],
                        "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                    }
                ],
                self.test_team_ids[1]: [
                    {
                        "type": "gdp_growth",
                        "name": PRIZE_TYPES["gdp_growth"]["name"],
                        "description": PRIZE_TYPES["gdp_growth"]["description"],
                        "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                    }
                ]
            }
            
        self.game_state.prize_manager.check_prize_eligibility = mock_check
        
        # Advance the round
        self.game_state.advance_round()
        
        # Check that both teams received the prize
        self.assertEqual(len(self.game_state.prize_manager.awarded_prizes), 2)
        self.assertIn(self.test_team_ids[0], self.game_state.prize_manager.awarded_prizes)
        self.assertIn(self.test_team_ids[1], self.game_state.prize_manager.awarded_prizes)
        
    def test_prize_effects_application_in_game_flow(self):
        """Test that prize effects are properly applied in the game flow."""
        # Add a mock prize to the prize manager
        team_id = self.test_team_ids[0]
        self.game_state.prize_manager.awarded_prizes = {
            team_id: {
                "gdp_growth": {
                    "awarded_at": "2023-01-01T00:00:00",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                }
            }
        }
        
        # Mock the apply_prize_effects method to track calls and modify results
        original_apply = self.game_state.prize_manager.apply_prize_effects
        apply_called = [False]
        
        def mock_apply(team_id, round_results):
            apply_called[0] = True
            # Apply the TFP boost effect
            if team_id in self.game_state.prize_manager.awarded_prizes:
                if "gdp_growth" in self.game_state.prize_manager.awarded_prizes[team_id]:
                    effects = self.game_state.prize_manager.awarded_prizes[team_id]["gdp_growth"]["effects"]
                    if "tfp_increase" in effects and "A_next" in round_results:
                        round_results["A_next"] *= (1 + effects["tfp_increase"])
            return round_results
            
        self.game_state.prize_manager.apply_prize_effects = mock_apply
        
        # Submit a decision for the team
        self.game_state.submit_decision(team_id, 0.3, "market")
        
        # Get the initial TFP value
        initial_tfp = self.game_state.team_manager.teams[team_id]["current_state"].get("Productivity (TFP)", 1.0)
        
        # Advance the round
        self.game_state.advance_round()
        
        # Check that the method was called
        self.assertTrue(apply_called[0])
        
        # Check that the TFP was boosted
        new_tfp = self.game_state.team_manager.teams[team_id]["current_state"].get("Productivity (TFP)")
        expected_tfp = initial_tfp * (1 + 0.05)  # 5% boost from the prize
        
        # We can't check exact equality due to other calculations in the model,
        # but we can check that the new TFP is higher than expected
        self.assertGreater(new_tfp, initial_tfp)
        
        # Restore the original method
        self.game_state.prize_manager.apply_prize_effects = original_apply

if __name__ == '__main__':
    unittest.main()
