"""
End-to-end tests for the API endpoints.

This module contains tests that verify the API endpoints for the game,
including team creation, game start, decision submission, round processing,
and other API functionality.
"""

import unittest
import logging
import json
from typing import Dict, List, Any
from fastapi.testclient import TestClient

from economic_model_py.app import app
from economic_model_py.economic_model.tests.e2e.test_base import EndToEndTestBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAPIEndpoints(unittest.TestCase):
    """Test cases for the API endpoints."""
    
    def setUp(self):
        """Set up the test environment."""
        self.client = TestClient(app)
        
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
    def test_create_team_endpoint(self):
        """Test the create team endpoint."""
        # Create a team
        response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("team_id", data)
        self.assertEqual(data["team_name"], "API Test Team")
        self.assertIn("current_state", data)
        
    def test_start_game_endpoint(self):
        """Test the start game endpoint."""
        # Create a team first
        self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
        )
        
        # Start the game
        response = self.client.post("/game/start")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["game_started"])
        self.assertEqual(data["current_round"], 0)
        self.assertEqual(data["current_year"], 1980)
        
    def test_submit_decision_endpoint(self):
        """Test the submit decision endpoint."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
        )
        team_id = team_response.json()["team_id"]
        
        # Start the game
        self.client.post("/game/start")
        
        # Submit a decision
        response = self.client.post(
            "/decisions/submit",
            json={
                "team_id": team_id,
                "savings_rate": 0.3,
                "exchange_rate_policy": "market"
            }
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["team_id"], team_id)
        self.assertEqual(data["round"], 0)
        self.assertEqual(data["year"], 1980)
        self.assertEqual(data["savings_rate"], 0.3)
        self.assertEqual(data["exchange_rate_policy"], "market")
        
    def test_process_round_endpoint(self):
        """Test the process round endpoint."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
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
        response = self.client.post("/game/process-round")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["round"], 1)
        self.assertEqual(data["year"], 1985)
        self.assertIn("teams", data)
        self.assertIn(team_id, data["teams"])
        
    def test_get_team_state_endpoint(self):
        """Test the get team state endpoint."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
        )
        team_id = team_response.json()["team_id"]
        
        # Get team state
        response = self.client.get(f"/teams/{team_id}")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["team_id"], team_id)
        self.assertEqual(data["team_name"], "API Test Team")
        self.assertIn("current_state", data)
        
    def test_get_game_state_endpoint(self):
        """Test the get game state endpoint."""
        # Create a team
        self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
        )
        
        # Start the game
        self.client.post("/game/start")
        
        # Get game state
        response = self.client.get("/game/state")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["game_started"])
        self.assertEqual(data["current_round"], 0)
        self.assertEqual(data["current_year"], 1980)
        self.assertIn("teams", data)
        
    def test_get_rankings_endpoint(self):
        """Test the get rankings endpoint."""
        # Create teams
        team1_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team 1"}
        )
        team1_id = team1_response.json()["team_id"]
        
        team2_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team 2"}
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
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Two teams
        
        # Verify ranking structure
        for rank in data:
            self.assertIn("team_id", rank)
            self.assertIn("team_name", rank)
            self.assertIn("rank", rank)
            self.assertIn("score", rank)
            
    def test_save_and_load_game_endpoints(self):
        """Test the save and load game endpoints."""
        # Create a team
        team_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Test Team"}
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
        
        # Save the game
        save_response = self.client.post("/game/save")
        self.assertEqual(save_response.status_code, 200)
        save_data = save_response.json()
        self.assertIn("game_id", save_data)
        game_id = save_data["game_id"]
        
        # Reset the game
        self.client.post("/game/reset")
        
        # Load the game
        load_response = self.client.post(f"/game/load/{game_id}")
        self.assertEqual(load_response.status_code, 200)
        load_data = load_response.json()
        self.assertIn("state", load_data)
        self.assertEqual(load_data["state"]["game_id"], game_id)
        self.assertEqual(load_data["state"]["current_round"], 1)
        self.assertEqual(load_data["state"]["current_year"], 1985)
        
    def test_error_handling(self):
        """Test error handling in the API."""
        # Test 404 for non-existent team
        response = self.client.get("/teams/non-existent-id")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertTrue(data["error"])
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
        self.assertTrue(data["error"])
        self.assertIn("message", data)
        
        # Test game not started error
        # Reset the game first
        self.client.post("/game/reset")
        
        # Try to process round without starting
        response = self.client.post("/game/process-round")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertTrue(data["error"])
        self.assertIn("message", data)
        
class TestAPIGameFlow(unittest.TestCase):
    """Test cases for the complete API game flow."""
    
    def setUp(self):
        """Set up the test environment."""
        self.client = TestClient(app)
        
    def test_complete_game_flow(self):
        """Test the complete game flow through the API."""
        # Create teams
        team1_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Flow Team 1"}
        )
        team1_id = team1_response.json()["team_id"]
        
        team2_response = self.client.post(
            "/teams/create",
            json={"team_name": "API Flow Team 2"}
        )
        team2_id = team2_response.json()["team_id"]
        
        # Start the game
        start_response = self.client.post("/game/start")
        self.assertEqual(start_response.status_code, 200)
        game_state = start_response.json()
        
        # Get the number of rounds from the years array
        years = game_state.get("years", [])
        num_rounds = len(years) - 1  # -1 because we start at round 0
        
        # Run through all rounds
        for round_num in range(num_rounds):
            # Submit decisions for both teams
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
            process_response = self.client.post("/game/process-round")
            self.assertEqual(process_response.status_code, 200)
            process_data = process_response.json()
            
            # Verify round advanced
            self.assertEqual(process_data["round"], round_num + 1)
            
            # Get game state
            state_response = self.client.get("/game/state")
            self.assertEqual(state_response.status_code, 200)
            state_data = state_response.json()
            
            # Verify teams in game state
            self.assertIn(team1_id, state_data["teams"])
            self.assertIn(team2_id, state_data["teams"])
            
            # Get rankings
            rankings_response = self.client.get("/results/rankings")
            self.assertEqual(rankings_response.status_code, 200)
            rankings_data = rankings_response.json()
            
            # Verify rankings
            self.assertEqual(len(rankings_data), 2)  # Two teams
            
        # Verify game ended
        final_state_response = self.client.get("/game/state")
        self.assertEqual(final_state_response.status_code, 200)
        final_state = final_state_response.json()
        self.assertTrue(final_state["game_ended"])
        
if __name__ == "__main__":
    unittest.main()
