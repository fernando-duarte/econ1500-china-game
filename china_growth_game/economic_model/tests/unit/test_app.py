import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os
from china_growth_game.app import app

class TestApp(unittest.TestCase):
    """Test cases for the FastAPI application."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test client using the app
        # Different TestClient versions have different signatures
        try:
            # Newer versions
            self.client = TestClient(app=app)
        except TypeError:
            try:
                # Even newer versions
                self.client = TestClient(transport=app)
            except TypeError:
                # Fallback to older version or skip tests
                self.skipTest("TestClient initialization failed, incompatible API version")
                
    def test_read_root(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "China's Growth Game Economic Model API"})
        
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "Economic model service is running"})
        
    @patch('china_growth_game.app.game_state')
    def test_initialize_game(self, mock_game_state):
        """Test the game initialization endpoint."""
        # Mock the game state
        mock_game_state.get_game_state.return_value = {
            "game_id": "test-game-id",
            "current_round": 0,
            "current_year": 1980,
            "teams": {},
            "rankings": {},
            "game_started": False,
            "game_ended": False
        }
        
        response = self.client.post("/game/init")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["game_id"], "test-game-id")
        self.assertEqual(response.json()["current_round"], 0)
        
    @patch('china_growth_game.app.game_state')
    def test_start_game(self, mock_game_state):
        """Test the game start endpoint."""
        # Mock the game state
        mock_game_state.start_game.return_value = {
            "game_id": "test-game-id",
            "current_round": 0,
            "current_year": 1980,
            "teams": {"team1": {"team_name": "Test Team"}},
            "rankings": {},
            "game_started": True,
            "game_ended": False
        }
        
        response = self.client.post("/game/start")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["game_started"], True)
        
        # Test error handling
        mock_game_state.start_game.side_effect = ValueError("No teams")
        response = self.client.post("/game/start")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "No teams")
        
    @patch('china_growth_game.app.game_state')
    def test_advance_round(self, mock_game_state):
        """Test the round advancement endpoint."""
        # Mock the game state
        mock_game_state.advance_round.return_value = {
            "round": 1,
            "year": 1985,
            "events": [],
            "rankings": {}
        }
        
        response = self.client.post("/game/next-round")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["round"], 1)
        self.assertEqual(response.json()["year"], 1985)
        
        # Test error handling
        mock_game_state.advance_round.side_effect = ValueError("Game not started")
        response = self.client.post("/game/next-round")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Game not started")
        
    @patch('china_growth_game.app.game_state')
    def test_get_game_state(self, mock_game_state):
        """Test the game state retrieval endpoint."""
        # Mock the game state
        mock_game_state.get_game_state.return_value = {
            "game_id": "test-game-id",
            "current_round": 1,
            "current_year": 1985,
            "teams": {"team1": {"team_name": "Test Team"}},
            "rankings": {},
            "game_started": True,
            "game_ended": False
        }
        
        response = self.client.get("/game/state")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["game_id"], "test-game-id")
        self.assertEqual(response.json()["current_round"], 1)
        
    @patch('china_growth_game.app.game_state')
    def test_create_team(self, mock_game_state):
        """Test the team creation endpoint."""
        # Mock the game state
        mock_game_state.create_team.return_value = {
            "team_id": "test-team-id",
            "team_name": "Test Team",
            "current_state": {},
            "history": [],
            "decisions": []
        }
        
        response = self.client.post("/teams/create", json={"team_name": "Test Team"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["team_id"], "test-team-id")
        self.assertEqual(response.json()["team_name"], "Test Team")
        
        # Test error handling
        mock_game_state.create_team.side_effect = ValueError("Team name taken")
        response = self.client.post("/teams/create", json={"team_name": "Test Team"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Team name taken")
        
    @patch('china_growth_game.app.game_state')
    def test_submit_decision(self, mock_game_state):
        """Test the decision submission endpoint."""
        # Mock the game state
        mock_game_state.submit_decision.return_value = {
            "round": 0,
            "year": 1980,
            "savings_rate": 0.3,
            "exchange_rate_policy": "market",
            "submitted_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.post("/teams/decisions", json={
            "team_id": "test-team-id",
            "savings_rate": 0.3,
            "exchange_rate_policy": "market"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["savings_rate"], 0.3)
        self.assertEqual(response.json()["exchange_rate_policy"], "market")
        
        # Test error handling
        mock_game_state.submit_decision.side_effect = ValueError("Invalid team ID")
        response = self.client.post("/teams/decisions", json={
            "team_id": "invalid-id",
            "savings_rate": 0.3,
            "exchange_rate_policy": "market"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid team ID")
        
    @patch('china_growth_game.app.game_state')
    def test_get_team_state(self, mock_game_state):
        """Test the team state retrieval endpoint."""
        # Mock the game state
        mock_game_state.get_team_state.return_value = {
            "team_id": "test-team-id",
            "team_name": "Test Team",
            "current_state": {
                "GDP": 1000.0,
                "Capital": 2000.0
            },
            "history": [],
            "decisions": []
        }
        
        response = self.client.get("/teams/test-team-id")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["team_id"], "test-team-id")
        self.assertEqual(response.json()["team_name"], "Test Team")
        
        # Test error handling
        mock_game_state.get_team_state.side_effect = ValueError("Team not found")
        response = self.client.get("/teams/invalid-id")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Team not found")
        
    @patch('china_growth_game.app.game_state')
    def test_edit_team_name(self, mock_game_state):
        """Test the team name editing endpoint."""
        # Mock the game state
        mock_game_state.team_manager.edit_team_name.return_value = {
            "team_id": "test-team-id",
            "team_name": "New Team Name",
            "current_state": {},
            "history": [],
            "decisions": []
        }
        
        response = self.client.post("/teams/test-team-id/edit-name", json={"new_name": "New Team Name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["team_name"], "New Team Name")
        
        # Test error handling
        mock_game_state.team_manager.edit_team_name.side_effect = ValueError("Team name taken")
        response = self.client.post("/teams/test-team-id/edit-name", json={"new_name": "Taken Name"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Team name taken")
        
    @patch('china_growth_game.app.game_state')
    def test_get_rankings(self, mock_game_state):
        """Test the rankings retrieval endpoint."""
        # Mock the game state
        mock_game_state.rankings_manager.rankings = {
            "gdp": ["team2", "team1", "team3"],
            "net_exports": ["team3", "team1", "team2"],
            "balanced_economy": ["team2", "team1", "team3"]
        }
        
        response = self.client.get("/results/rankings")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gdp"], ["team2", "team1", "team3"])
        self.assertEqual(response.json()["net_exports"], ["team3", "team1", "team2"])
        
    @patch('china_growth_game.app.game_state')
    def test_get_team_visualizations(self, mock_game_state):
        """Test the team visualizations retrieval endpoint."""
        # Mock the game state
        mock_game_state.get_team_visualizations.return_value = {
            "gdp_growth_chart": {
                "years": [1980, 1985, 1990],
                "gdp_growth_percent": [0.0, 3.7, 5.9]
            },
            "trade_balance_chart": {
                "years": [1980, 1985, 1990],
                "net_exports": [20.0, 25.0, 35.0]
            },
            "consumption_savings_pie": {
                "consumption": 800.0,
                "savings": 160.0
            }
        }
        
        response = self.client.get("/results/visualizations/test-team-id")
        self.assertEqual(response.status_code, 200)
        self.assertIn("gdp_growth_chart", response.json())
        self.assertIn("trade_balance_chart", response.json())
        self.assertIn("consumption_savings_pie", response.json())

if __name__ == '__main__':
    unittest.main()
