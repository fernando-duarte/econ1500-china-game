"""
End-to-end tests for frontend integration.

This module contains tests that verify the integration between the frontend and backend,
focusing on the API endpoints that the frontend uses and the data formats expected by
the frontend components.
"""

import unittest
import logging
import json
from typing import Dict, List, Any
from fastapi.testclient import TestClient

from economic_model_py.app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFrontendIntegration(unittest.TestCase):
    """Test cases for frontend integration."""
    
    def setUp(self):
        """Set up the test environment."""
        self.client = TestClient(app)
        
    def test_game_state_format_for_frontend(self):
        """Test that the game state format is compatible with frontend expectations."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "Frontend Test Team"}
        )
        team_id = team_response.json()["team_id"]
        
        # Start the game
        self.client.post("/game/start")
        
        # Get game state
        response = self.client.get("/game/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify game state structure for frontend compatibility
        self.assertIn("game_id", data)
        self.assertIn("current_round", data)
        self.assertIn("current_year", data)
        self.assertIn("game_started", data)
        self.assertIn("game_ended", data)
        self.assertIn("teams", data)
        self.assertIn("years", data)
        
        # Verify team structure
        team = data["teams"][team_id]
        self.assertIn("team_id", team)
        self.assertIn("team_name", team)
        self.assertIn("current_state", team)
        self.assertIn("history", team)
        
        # Verify current state structure
        current_state = team["current_state"]
        self.assertIn("gdp", current_state)
        self.assertIn("capital", current_state)
        self.assertIn("labor", current_state)
        self.assertIn("tfp", current_state)
        self.assertIn("round", current_state)
        self.assertIn("year", current_state)
        
        # Verify history structure
        history = team["history"]
        self.assertGreater(len(history), 0)
        history_item = history[0]
        self.assertIn("gdp", history_item)
        self.assertIn("capital", history_item)
        self.assertIn("labor", history_item)
        self.assertIn("tfp", history_item)
        self.assertIn("round", history_item)
        self.assertIn("year", history_item)
        
    def test_rankings_format_for_frontend(self):
        """Test that the rankings format is compatible with frontend expectations."""
        # Create teams
        team1_response = self.client.post(
            "/teams/create",
            json={"team_name": "Frontend Test Team 1"}
        )
        team1_id = team1_response.json()["team_id"]
        
        team2_response = self.client.post(
            "/teams/create",
            json={"team_name": "Frontend Test Team 2"}
        )
        team2_id = team2_response.json()["team_id"]
        
        # Start the game
        self.client.post("/game/start")
        
        # Submit decisions
        self.client.post(
            "/decisions/submit",
            json={
                "team_id": team1_id,
                "savings_rate": 0.3,
                "exchange_rate_policy": "market"
            }
        )
        
        self.client.post(
            "/decisions/submit",
            json={
                "team_id": team2_id,
                "savings_rate": 0.4,
                "exchange_rate_policy": "fixed"
            }
        )
        
        # Process the round
        self.client.post("/game/process-round")
        
        # Get rankings
        response = self.client.get("/results/rankings")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify rankings structure for frontend compatibility
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Two teams
        
        for rank in data:
            self.assertIn("team_id", rank)
            self.assertIn("team_name", rank)
            self.assertIn("rank", rank)
            self.assertIn("score", rank)
            
    def test_team_visualizations_format(self):
        """Test that the team visualizations format is compatible with frontend expectations."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "Frontend Test Team"}
        )
        team_id = team_response.json()["team_id"]
        
        # Start the game
        self.client.post("/game/start")
        
        # Submit a decision
        self.client.post(
            "/decisions/submit",
            json={
                "team_id": team_id,
                "savings_rate": 0.3,
                "exchange_rate_policy": "market"
            }
        )
        
        # Process the round
        self.client.post("/game/process-round")
        
        # Get team visualizations
        response = self.client.get(f"/visualizations/team/{team_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify visualizations structure for frontend compatibility
        self.assertIn("gdp_chart", data)
        self.assertIn("capital_chart", data)
        self.assertIn("labor_chart", data)
        self.assertIn("tfp_chart", data)
        
        # Verify chart structure
        for chart_name in ["gdp_chart", "capital_chart", "labor_chart", "tfp_chart"]:
            chart = data[chart_name]
            self.assertIn("title", chart)
            self.assertIn("x_label", chart)
            self.assertIn("y_label", chart)
            self.assertIn("data", chart)
            
            # Verify data structure
            chart_data = chart["data"]
            self.assertIn("x", chart_data)
            self.assertIn("y", chart_data)
            self.assertEqual(len(chart_data["x"]), len(chart_data["y"]))
            
    def test_prize_documentation_endpoint(self):
        """Test the prize documentation endpoint."""
        response = self.client.get("/documentation/prizes")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
    def test_replay_endpoints_format(self):
        """Test that the replay endpoints format is compatible with frontend expectations."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "Replay Test Team"}
        )
        team_id = team_response.json()["team_id"]
        
        # Start the game
        self.client.post("/game/start")
        
        # Submit a decision
        self.client.post(
            "/decisions/submit",
            json={
                "team_id": team_id,
                "savings_rate": 0.3,
                "exchange_rate_policy": "market"
            }
        )
        
        # Process the round
        self.client.post("/game/process-round")
        
        # List replays
        list_response = self.client.get("/replay/list")
        self.assertEqual(list_response.status_code, 200)
        list_data = list_response.json()
        
        # Verify list structure
        self.assertIsInstance(list_data, list)
        
        # If there are replays, test the replay endpoints
        if len(list_data) > 0:
            replay_id = list_data[0]["replay_id"]
            
            # Start replay
            start_response = self.client.post(f"/replay/start/{replay_id}")
            self.assertEqual(start_response.status_code, 200)
            
            # Get metadata
            metadata_response = self.client.get("/replay/metadata")
            self.assertEqual(metadata_response.status_code, 200)
            metadata = metadata_response.json()
            
            # Verify metadata structure
            self.assertIn("replay_id", metadata)
            self.assertIn("game_id", metadata)
            self.assertIn("state_count", metadata)
            self.assertIn("current_index", metadata)
            
            # Next state
            next_response = self.client.get("/replay/next")
            self.assertEqual(next_response.status_code, 200)
            
            # Previous state
            prev_response = self.client.get("/replay/previous")
            self.assertEqual(prev_response.status_code, 200)
            
    def test_error_response_format(self):
        """Test that error responses are formatted consistently for frontend handling."""
        # Test 404 for non-existent team
        response = self.client.get("/teams/non-existent-id")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        
        # Verify error structure
        self.assertTrue(data["error"])
        self.assertIn("code", data)
        self.assertIn("message", data)
        
        # Test validation error
        response = self.client.post(
            "/decisions/submit",
            json={
                "team_id": "some-id",
                "savings_rate": 2.0,  # Invalid value, should be between 0 and 1
                "exchange_rate_policy": "market"
            }
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        
        # Verify error structure
        self.assertTrue(data["error"])
        self.assertIn("code", data)
        self.assertIn("message", data)
        
if __name__ == "__main__":
    unittest.main()
