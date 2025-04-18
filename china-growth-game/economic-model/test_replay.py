import unittest
from unittest.mock import patch, MagicMock
import copy
from replay import replay_session

class TestReplay(unittest.TestCase):
    """Test cases for the replay module."""

    def setUp(self):
        """Set up the test environment."""
        # Initial conditions for one team
        self.initial_conditions = {
            "team-1": {
                "team_name": "Test Team",
                "year": 1980,
                "round": 0,
                "Y": 306.2,
                "K": 800,
                "L": 600,
                "H": 1.0,
                "A": 1.0,
                "NX": 3.6,
                "C": 244.96,
                "initial_Y": 306.2
            }
        }

        # Decisions log: (team_id, round, savings_rate, exchange_rate_policy)
        self.decisions_log = [
            ("team-1", 1, 0.2, "market"),
            ("team-1", 2, 0.3, "undervalue"),
            ("team-1", 3, 0.25, "market")
        ]

    def test_replay_session_basic(self):
        """Test basic replay functionality."""
        result = replay_session(self.initial_conditions, self.decisions_log, num_rounds=3)

        # Check that the result contains the team
        self.assertIn("team-1", result)

        # Check that the team has the expected state
        team_result = result["team-1"]
        self.assertEqual(team_result["team_name"], "Test Team")
        self.assertEqual(team_result["current_state"]["Round"], 3)
        self.assertEqual(team_result["current_state"]["Year"], 2000)

        # Check that economic variables were updated
        self.assertGreater(team_result["current_state"]["GDP"], self.initial_conditions["team-1"]["Y"])
        self.assertGreater(team_result["current_state"]["Capital"], self.initial_conditions["team-1"]["K"])
        self.assertGreater(team_result["current_state"]["Labor Force"], self.initial_conditions["team-1"]["L"])
        self.assertGreater(team_result["current_state"]["Human Capital"], self.initial_conditions["team-1"]["H"])
        self.assertGreater(team_result["current_state"]["Productivity (TFP)"], self.initial_conditions["team-1"]["A"])

    def test_replay_session_empty_decisions(self):
        """Test replay with no decisions."""
        result = replay_session(self.initial_conditions, [], num_rounds=3)

        # Check that the result contains the team
        self.assertIn("team-1", result)

        # Check that the team has the expected state
        team_result = result["team-1"]
        self.assertEqual(team_result["team_name"], "Test Team")
        self.assertEqual(team_result["current_state"]["Round"], 3)
        self.assertEqual(team_result["current_state"]["Year"], 2000)

        # Check that economic variables were updated using default decisions
        self.assertGreater(team_result["current_state"]["GDP"], self.initial_conditions["team-1"]["Y"])

    def test_replay_session_multiple_teams(self):
        """Test replay with multiple teams."""
        # Add a second team
        initial_conditions = copy.deepcopy(self.initial_conditions)
        initial_conditions["team-2"] = {
            "team_name": "Team 2",
            "year": 1980,
            "round": 0,
            "Y": 306.2,
            "K": 800,
            "L": 600,
            "H": 1.0,
            "A": 1.0,
            "NX": 3.6,
            "C": 244.96,
            "initial_Y": 306.2
        }

        # Add decisions for the second team
        decisions_log = copy.deepcopy(self.decisions_log)
        decisions_log.extend([
            ("team-2", 1, 0.4, "undervalue"),
            ("team-2", 2, 0.5, "overvalue"),
            ("team-2", 3, 0.3, "market")
        ])

        result = replay_session(initial_conditions, decisions_log, num_rounds=3)

        # Check that the result contains both teams
        self.assertIn("team-1", result)
        self.assertIn("team-2", result)

        # Check that both teams have the expected state
        self.assertEqual(result["team-1"]["team_name"], "Test Team")
        self.assertEqual(result["team-1"]["current_state"]["Round"], 3)
        self.assertEqual(result["team-2"]["team_name"], "Team 2")
        self.assertEqual(result["team-2"]["current_state"]["Round"], 3)

        # Teams should have different results due to different decisions
        self.assertNotEqual(result["team-1"]["current_state"]["GDP"], result["team-2"]["current_state"]["GDP"])
        self.assertNotEqual(result["team-1"]["current_state"]["Capital"], result["team-2"]["current_state"]["Capital"])
        self.assertNotEqual(result["team-1"]["current_state"]["Net Exports"], result["team-2"]["current_state"]["Net Exports"])

    def test_replay_session_missing_decisions(self):
        """Test replay with missing decisions for some rounds."""
        # Remove decision for round 2
        decisions_log = [
            ("team-1", 1, 0.2, "market"),
            # Round 2 decision missing
            ("team-1", 3, 0.25, "market")
        ]

        result = replay_session(self.initial_conditions, decisions_log, num_rounds=3)

        # Check that the result contains the team
        self.assertIn("team-1", result)

        # Check that the team has the expected state
        team_result = result["team-1"]
        self.assertEqual(team_result["current_state"]["Round"], 3)

        # The simulation should have used default values for round 2

    def test_replay_session_reproducibility(self):
        """Test that replaying a session with the same inputs is deterministic."""
        result1 = replay_session(self.initial_conditions, self.decisions_log, num_rounds=3)
        result2 = replay_session(self.initial_conditions, self.decisions_log, num_rounds=3)

        # Results should be identical
        self.assertEqual(result1, result2)

    @patch('game_state.calculate_next_round')
    def test_replay_session_calls_calculate_next_round(self, mock_calculate_next_round):
        """Test that replay_session calls calculate_next_round with the correct arguments."""
        # Mock the calculate_next_round function
        mock_calculate_next_round.return_value = {
            "Y_t": 400.0,
            "K_next": 900.0,
            "L_next": 610.0,
            "H_next": 1.05,
            "A_next": 1.05,
            "NX_t": 4.0,
            "C_t": 320.0,
            "I_t": 80.0
        }

        replay_session(self.initial_conditions, self.decisions_log, num_rounds=1)

        # Check that calculate_next_round was called with the correct arguments
        mock_calculate_next_round.assert_called_once()
        args, kwargs = mock_calculate_next_round.call_args

        # Check current_state
        self.assertIn('Y', kwargs['current_state'])
        self.assertIn('K', kwargs['current_state'])
        self.assertIn('L', kwargs['current_state'])
        self.assertIn('H', kwargs['current_state'])
        self.assertIn('A', kwargs['current_state'])

        # Check student_inputs
        self.assertEqual(kwargs['student_inputs']['s'], 0.2)
        self.assertEqual(kwargs['student_inputs']['e_policy'], 'market')

        # Check year
        self.assertEqual(kwargs['year'], 1985)

    def test_replay_session_with_custom_num_rounds(self):
        """Test replay with a custom number of rounds."""
        # Run for 5 rounds
        result = replay_session(self.initial_conditions, self.decisions_log, num_rounds=5)

        # Check that the result contains the team
        self.assertIn("team-1", result)

        # Check that the team has the expected state
        team_result = result["team-1"]
        self.assertEqual(team_result["current_state"]["Round"], 5)
        self.assertEqual(team_result["current_state"]["Year"], 2010)

        # For rounds beyond the decisions log, default decisions should be used

if __name__ == '__main__':
    unittest.main()
