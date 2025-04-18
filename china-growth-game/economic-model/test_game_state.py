import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime
from game_state import GameState
from team_management import TeamManager
from events_manager import EventsManager
from rankings_manager import RankingsManager
from visualization_manager import VisualizationManager

class TestGameState(unittest.TestCase):
    """Test cases for the GameState class."""

    def setUp(self):
        """Set up the test environment."""
        self.game_state = GameState()

        # Create a test team
        self.test_team = self.game_state.create_team("Test Team")
        self.test_team_id = self.test_team["team_id"]

    def test_init(self):
        """Test the initialization of GameState."""
        self.assertIsInstance(self.game_state.game_id, str)
        self.assertIsInstance(self.game_state.created_at, str)
        self.assertEqual(self.game_state.current_round, 0)
        self.assertEqual(self.game_state.current_year, 1980)
        self.assertFalse(self.game_state.game_started)
        self.assertFalse(self.game_state.game_ended)
        self.assertIsInstance(self.game_state.team_manager, TeamManager)
        self.assertIsInstance(self.game_state.events_manager, EventsManager)
        self.assertIsInstance(self.game_state.rankings_manager, RankingsManager)
        self.assertIsInstance(self.game_state.visualization_manager, VisualizationManager)

    def test_create_team(self):
        """Test team creation."""
        team = self.game_state.create_team("New Team")
        self.assertIsInstance(team, dict)
        self.assertIn("team_id", team)
        self.assertEqual(team["team_name"], "New Team")
        self.assertIn(team["team_id"], self.game_state.team_manager.teams)

        # Test auto-generated name
        auto_team = self.game_state.create_team()
        self.assertIsInstance(auto_team["team_name"], str)
        self.assertGreater(len(auto_team["team_name"]), 0)

    def test_submit_decision(self):
        """Test decision submission."""
        decision = self.game_state.submit_decision(
            self.test_team_id, 0.3, "market"
        )
        self.assertIsInstance(decision, dict)
        self.assertEqual(decision["savings_rate"], 0.3)
        self.assertEqual(decision["exchange_rate_policy"], "market")

        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.game_state.submit_decision("invalid-id", 0.3, "market")

        # Test invalid savings rate
        with self.assertRaises(ValueError):
            self.game_state.submit_decision(self.test_team_id, 1.5, "market")

        # Test invalid exchange rate policy
        with self.assertRaises(ValueError):
            self.game_state.submit_decision(self.test_team_id, 0.3, "invalid")

    def test_start_game(self):
        """Test game start."""
        game_state = self.game_state.start_game()
        self.assertTrue(self.game_state.game_started)
        self.assertEqual(self.game_state.current_round, 0)
        self.assertEqual(self.game_state.current_year, 1980)

        # Test starting a game with no teams
        empty_game = GameState()
        with self.assertRaises(ValueError):
            empty_game.start_game()

    def test_get_parameters_for_round(self):
        """Test parameter retrieval for a specific round."""
        params = self.game_state._get_parameters_for_round(0)
        self.assertIsInstance(params, dict)
        self.assertIn("openness_ratio", params)

        # Test that openness ratio increases with round index
        params_later = self.game_state._get_parameters_for_round(5)
        self.assertGreater(params_later["openness_ratio"], params["openness_ratio"])

    def test_get_default_decision(self):
        """Test default decision retrieval."""
        decision = self.game_state._get_default_decision()
        self.assertIsInstance(decision, dict)
        self.assertIn("savings_rate", decision)
        self.assertIn("exchange_rate_policy", decision)

    def test_apply_event_effects(self):
        """Test application of event effects."""
        # Create a test event
        test_event = {
            "name": "Test Event",
            "effects": {
                "tfp_increase": 0.05,
                "gdp_growth_delta": 0.02
            }
        }

        # Create test round results
        round_results = {
            "Y_t": 1000.0,
            "A_next": 1.5
        }

        # Apply event effects
        modified_results, applied_events = self.game_state._apply_event_effects(
            round_results, [test_event], self.test_team_id
        )

        # Check that effects were applied correctly
        self.assertAlmostEqual(modified_results["Y_t"], 1000.0 * 1.02, places=5)
        self.assertAlmostEqual(modified_results["A_next"], 1.5 * 1.05, places=5)
        self.assertEqual(applied_events, ["Test Event"])

        # Test with no events
        unmodified_results, applied_events = self.game_state._apply_event_effects(
            round_results.copy(), [], self.test_team_id
        )
        self.assertEqual(unmodified_results, round_results)
        self.assertEqual(applied_events, [])

    @patch('game_state.calculate_next_round')
    def test_process_team_round(self, mock_calculate_next_round):
        """Test processing a team's round."""
        # Mock the calculate_next_round function
        mock_calculate_next_round.return_value = {
            "Y_t": 1100.0,
            "K_next": 2200.0,
            "L_next": 110.0,
            "H_next": 1.1,
            "A_next": 1.6,
            "NX_t": 50.0,
            "C_t": 880.0,
            "I_t": 220.0
        }

        # Submit a decision for the team
        self.game_state.submit_decision(self.test_team_id, 0.2, "market")

        # Process the team's round
        self.game_state._process_team_round(
            self.test_team_id,
            self.game_state.team_manager.teams[self.test_team_id],
            [],
            0
        )

        # Check that the team's state was updated
        team_state = self.game_state.team_manager.teams[self.test_team_id]["current_state"]
        self.assertEqual(team_state["GDP"], 1100.0)
        self.assertEqual(team_state["Capital"], 2200.0)
        self.assertEqual(team_state["Labor Force"], 110.0)
        self.assertEqual(team_state["Human Capital"], 1.1)
        self.assertEqual(team_state["Productivity (TFP)"], 1.6)
        self.assertEqual(team_state["Net Exports"], 50.0)
        self.assertEqual(team_state["Consumption"], 880.0)
        self.assertEqual(team_state["Investment"], 220.0)

    def test_advance_round(self):
        """Test advancing to the next round."""
        # Start the game
        self.game_state.start_game()

        # Advance to the next round
        result = self.game_state.advance_round()

        # Check that the round was advanced
        self.assertEqual(self.game_state.current_round, 1)
        self.assertEqual(self.game_state.current_year, 1985)
        self.assertIn("round", result)
        self.assertIn("year", result)
        self.assertIn("events", result)
        self.assertIn("rankings", result)

        # Test advancing without starting the game
        new_game = GameState()
        new_game.create_team("Test Team")
        with self.assertRaises(ValueError):
            new_game.advance_round()

        # Test idempotency (advancing the same round twice)
        # First, remove the round from processed_rounds to allow it to advance again
        self.game_state.processed_rounds.remove(1)
        self.game_state.advance_round()  # Now at round 2
        self.assertEqual(self.game_state.current_round, 2)

        # Try to advance round 2 again (should be idempotent)
        self.game_state.processed_rounds.remove(2)  # Manually remove to test
        self.game_state.current_round = 1  # Reset to round 1
        result = self.game_state.advance_round()  # Should advance to round 2 again
        self.assertEqual(self.game_state.current_round, 2)

        # Test game end
        while self.game_state.current_round < len(self.game_state.years) - 1:
            self.game_state.advance_round()

        self.assertFalse(self.game_state.game_ended)
        final_result = self.game_state.advance_round()
        self.assertTrue(self.game_state.game_ended)
        self.assertIn("message", final_result)
        self.assertIn("final_rankings", final_result)

    def test_calculate_rankings(self):
        """Test ranking calculation."""
        rankings = self.game_state.calculate_rankings()
        self.assertIsInstance(rankings, dict)
        self.assertIn("gdp", rankings)
        self.assertIn("net_exports", rankings)
        self.assertIn("balanced_economy", rankings)

    def test_get_game_state(self):
        """Test game state retrieval."""
        state = self.game_state.get_game_state()
        self.assertIsInstance(state, dict)
        self.assertEqual(state["game_id"], self.game_state.game_id)
        self.assertEqual(state["current_round"], self.game_state.current_round)
        self.assertEqual(state["current_year"], self.game_state.current_year)
        self.assertIn("teams", state)
        self.assertIn("rankings", state)
        self.assertEqual(state["game_started"], self.game_state.game_started)
        self.assertEqual(state["game_ended"], self.game_state.game_ended)

    def test_get_team_state(self):
        """Test team state retrieval."""
        team_state = self.game_state.get_team_state(self.test_team_id)
        self.assertIsInstance(team_state, dict)
        self.assertEqual(team_state["team_id"], self.test_team_id)
        self.assertEqual(team_state["team_name"], "Test Team")
        self.assertIn("current_state", team_state)
        self.assertIn("history", team_state)
        self.assertIn("decisions", team_state)

        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.game_state.get_team_state("invalid-id")

    def test_get_team_visualizations(self):
        """Test team visualization data retrieval."""
        # Start the game and advance a few rounds to generate data
        self.game_state.start_game()
        self.game_state.advance_round()
        self.game_state.advance_round()

        # Get visualization data
        vis_data = self.game_state.get_team_visualizations(self.test_team_id)
        self.assertIsInstance(vis_data, dict)
        self.assertIn("gdp_growth_chart", vis_data)
        self.assertIn("trade_balance_chart", vis_data)
        self.assertIn("consumption_savings_pie", vis_data)

        # Test invalid team ID
        with self.assertRaises(ValueError):
            self.game_state.get_team_visualizations("invalid-id")

if __name__ == '__main__':
    unittest.main()
