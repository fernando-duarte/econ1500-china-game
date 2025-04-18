import unittest
from unittest.mock import patch, MagicMock
import logging
import numpy as np
from china_growth_game.economic_model.game.rankings_manager import RankingsManager

class TestRankingsManager(unittest.TestCase):
    """Test cases for the RankingsManager class."""

    def setUp(self):
        """Set up the test environment."""
        self.rankings_manager = RankingsManager()
        
        # Create mock teams data
        self.mock_teams = {
            "team1": {
                "team_id": "team1",
                "team_name": "Team 1",
                "current_state": {
                    "Y": 1000.0,
                    "NX": 50.0,
                    "C": 800.0
                },
                "eliminated": False
            },
            "team2": {
                "team_id": "team2",
                "team_name": "Team 2",
                "current_state": {
                    "Y": 1200.0,
                    "NX": 40.0,
                    "C": 900.0
                },
                "eliminated": False
            },
            "team3": {
                "team_id": "team3",
                "team_name": "Team 3",
                "current_state": {
                    "Y": 800.0,
                    "NX": 60.0,
                    "C": 700.0
                },
                "eliminated": False
            }
        }
        
    def test_init(self):
        """Test the initialization of RankingsManager."""
        self.assertIsInstance(self.rankings_manager.rankings, dict)
        self.assertIn("gdp", self.rankings_manager.rankings)
        self.assertIn("net_exports", self.rankings_manager.rankings)
        self.assertIn("balanced_economy", self.rankings_manager.rankings)
        self.assertEqual(len(self.rankings_manager.rankings["gdp"]), 0)
        self.assertEqual(len(self.rankings_manager.rankings["net_exports"]), 0)
        self.assertEqual(len(self.rankings_manager.rankings["balanced_economy"]), 0)
        
    def test_calculate_rankings_empty(self):
        """Test ranking calculation with no teams."""
        rankings = self.rankings_manager.calculate_rankings({})
        self.assertEqual(rankings["gdp"], [])
        self.assertEqual(rankings["net_exports"], [])
        self.assertEqual(rankings["balanced_economy"], [])
        
    def test_calculate_rankings(self):
        """Test ranking calculation with teams."""
        rankings = self.rankings_manager.calculate_rankings(self.mock_teams)
        
        # Check GDP ranking (team2 > team1 > team3)
        self.assertEqual(rankings["gdp"], ["team2", "team1", "team3"])
        
        # Check Net Exports ranking (team3 > team1 > team2)
        self.assertEqual(rankings["net_exports"], ["team3", "team1", "team2"])
        
        # Check Balanced Economy ranking (team2 > team1 > team3)
        # Balanced Economy = GDP + Consumption
        self.assertEqual(rankings["balanced_economy"], ["team2", "team1", "team3"])
        
    def test_calculate_rankings_with_eliminated(self):
        """Test ranking calculation with eliminated teams."""
        # Mark team2 as eliminated
        teams_with_eliminated = self.mock_teams.copy()
        teams_with_eliminated["team2"] = teams_with_eliminated["team2"].copy()
        teams_with_eliminated["team2"]["eliminated"] = True
        
        rankings = self.rankings_manager.calculate_rankings(teams_with_eliminated)
        
        # team2 should not be in any rankings
        self.assertEqual(rankings["gdp"], ["team1", "team3"])
        self.assertEqual(rankings["net_exports"], ["team3", "team1"])
        self.assertEqual(rankings["balanced_economy"], ["team1", "team3"])
        
    def test_calculate_rankings_with_incomplete_data(self):
        """Test ranking calculation with teams missing data."""
        # Create a team with incomplete state
        teams_with_incomplete = self.mock_teams.copy()
        teams_with_incomplete["team4"] = {
            "team_id": "team4",
            "team_name": "Team 4",
            "current_state": {
                # Missing Y and NX
                "C": 600.0
            },
            "eliminated": False
        }
        
        rankings = self.rankings_manager.calculate_rankings(teams_with_incomplete)
        
        # team4 should not be in any rankings
        self.assertEqual(rankings["gdp"], ["team2", "team1", "team3"])
        self.assertEqual(rankings["net_exports"], ["team3", "team1", "team2"])
        self.assertEqual(rankings["balanced_economy"], ["team2", "team1", "team3"])
        
    @patch('china_growth_game.economic_model.game.rankings_manager.logger')
    def test_calculate_rankings_with_error(self, mock_logger):
        """Test ranking calculation with an error."""
        # Create a mock that raises an exception when accessed
        error_teams = MagicMock()
        error_teams.__len__.return_value = 3  # Pretend we have 3 teams
        error_teams.items.side_effect = Exception("Test error")
        
        # Calculate rankings with the error-generating teams
        rankings = self.rankings_manager.calculate_rankings(error_teams)
        
        # Should log the error and return current rankings
        mock_logger.error.assert_called()
        self.assertEqual(rankings, self.rankings_manager.rankings)
        
    def test_calculate_rankings_with_ties(self):
        """Test ranking calculation with tied values."""
        # Create teams with tied values
        teams_with_ties = {
            "team1": {
                "team_id": "team1",
                "team_name": "Team 1",
                "current_state": {
                    "Y": 1000.0,
                    "NX": 50.0,
                    "C": 800.0
                },
                "eliminated": False
            },
            "team2": {
                "team_id": "team2",
                "team_name": "Team 2",
                "current_state": {
                    "Y": 1000.0,  # Same as team1
                    "NX": 50.0,   # Same as team1
                    "C": 800.0    # Same as team1
                },
                "eliminated": False
            }
        }
        
        rankings = self.rankings_manager.calculate_rankings(teams_with_ties)
        
        # Check that both teams are in the rankings
        self.assertEqual(len(rankings["gdp"]), 2)
        self.assertEqual(len(rankings["net_exports"]), 2)
        self.assertEqual(len(rankings["balanced_economy"]), 2)
        
        # The order might be arbitrary for ties, but both should be present
        self.assertIn("team1", rankings["gdp"])
        self.assertIn("team2", rankings["gdp"])
        self.assertIn("team1", rankings["net_exports"])
        self.assertIn("team2", rankings["net_exports"])
        self.assertIn("team1", rankings["balanced_economy"])
        self.assertIn("team2", rankings["balanced_economy"])

if __name__ == '__main__':
    unittest.main()
