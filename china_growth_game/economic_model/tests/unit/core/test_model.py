import unittest
import numpy as np
from china_growth_game.economic_model.core.solow_model import calculate_next_round
from china_growth_game.economic_model.core.solow_core import get_default_parameters, calculate_openness_ratio
from china_growth_game.economic_model.utils.replay import replay_session

class TestSolowModel(unittest.TestCase):
    """Test cases for the calculate_next_round function."""

    def setUp(self):
        """Set up the test environment."""
        # Initial GDP for Y_1980 parameter
        self.y_1980 = 1000.0

        # Get default parameters and override as needed for tests
        self.parameters = get_default_parameters()
        self.parameters['Y_1980'] = self.y_1980

        # Define a base initial state (start of round)
        self.initial_state = {
            # 'Y' is calculated, not an input state variable for the *next* calculation
            'K': 1500.0,    # Capital
            'L': 100.0,    # Labor Force
            'H': 10.0,    # Human Capital
            'A': 1.5     # Productivity (TFP)
        }

        # Default student inputs
        self.student_inputs_market = {
            'savings_rate': 0.2, # Default savings rate
            'exchange_rate_policy': 'market'
        }

    def _get_params_for_round(self, round_index):
        """Helper to calculate round-specific parameters."""
        params = self.parameters.copy()
        params['openness_ratio'] = calculate_openness_ratio(round_index)
        return params

    def test_basic_calculation(self):
        """Test simulation of a single round with default inputs."""
        current_year = 1985 # Example: 2nd round (index 1)
        round_index = 1
        params_round = self._get_params_for_round(round_index)

        # Call the function
        result = calculate_next_round(
            current_state=self.initial_state,
            parameters=params_round,
            student_inputs=self.student_inputs_market,
            year=current_year
        )

        # Verify outputs exist and have plausible relationships
        self.assertIn('Y_t', result)
        self.assertIn('K_next', result)
        self.assertIn('L_next', result)
        self.assertIn('H_next', result)
        self.assertIn('A_next', result)
        self.assertIn('NX_t', result)
        self.assertIn('C_t', result)
        self.assertIn('I_t', result)

        self.assertGreater(result['K_next'], self.initial_state['K'] * (1 - self.parameters['delta']),
                          "Capital next should generally be greater than depreciated capital")
        self.assertGreater(result['L_next'], self.initial_state['L'],
                          "Labor should grow")
        self.assertGreater(result['H_next'], self.initial_state['H'],
                          "Human Capital should grow")
        self.assertGreater(result['A_next'], self.initial_state['A'],
                          "TFP should grow")
        self.assertAlmostEqual(result['C_t'], (1 - self.student_inputs_market['savings_rate']) * result['Y_t'],
                              places=5, msg="Consumption should be (1-s)*Y_t")
        self.assertAlmostEqual(result['I_t'], self.student_inputs_market['savings_rate'] * result['Y_t'] + result['NX_t'],
                              places=5, msg="Investment should be s*Y_t + NX_t")
        # Check capital accumulation links I_t and K_next
        expected_K_next = (1 - self.parameters['delta']) * max(0, self.initial_state['K']) + result['I_t']
        self.assertAlmostEqual(result['K_next'], expected_K_next,
                              places=5, msg="K_next should equal (1-d)K_t + I_t")

    def test_exchange_rate_policy_impact(self):
        """Test the impact of different exchange rate policies on Net Exports."""
        current_year = 1990 # Example: 3rd round (index 2)
        round_index = 2
        params_round = self._get_params_for_round(round_index)

        # Simulate with market exchange rate
        inputs_market = {'savings_rate': 0.2, 'exchange_rate_policy': 'market'}
        result_market = calculate_next_round(self.initial_state, params_round, inputs_market, current_year)

        # Simulate with undervalued exchange rate
        inputs_undervalue = {'savings_rate': 0.2, 'exchange_rate_policy': 'undervalue'}
        result_undervalue = calculate_next_round(self.initial_state, params_round, inputs_undervalue, current_year)

        # Simulate with overvalued exchange rate
        inputs_overvalue = {'savings_rate': 0.2, 'exchange_rate_policy': 'overvalue'}
        result_overvalue = calculate_next_round(self.initial_state, params_round, inputs_overvalue, current_year)

        # Undervalued should have higher NX than market
        self.assertGreater(result_undervalue["NX_t"], result_market["NX_t"],
                      "Undervalued policy should yield higher NX than market")

        # Market should have higher NX than overvalued
        self.assertGreater(result_market["NX_t"], result_overvalue["NX_t"],
                      "Market policy should yield higher NX than overvalued")

    def test_savings_rate_impact(self):
        """Test the impact of different savings rates on K_next and C_t."""
        current_year = 1995 # Example: 4th round (index 3)
        round_index = 3
        params_round = self._get_params_for_round(round_index)

        # Simulate with low savings rate
        inputs_low_s = {'savings_rate': 0.1, 'exchange_rate_policy': 'market'}
        result_low_s = calculate_next_round(self.initial_state, params_round, inputs_low_s, current_year)

        # Simulate with high savings rate
        inputs_high_s = {'savings_rate': 0.5, 'exchange_rate_policy': 'market'}
        result_high_s = calculate_next_round(self.initial_state, params_round, inputs_high_s, current_year)

        # Higher savings should lead to more capital accumulation next period
        self.assertGreater(result_high_s["K_next"], result_low_s["K_next"],
                      "Higher savings rate should lead to more K_next")

        # Higher savings should lead to less consumption this period
        self.assertLess(result_high_s["C_t"], result_low_s["C_t"],
                    "Higher savings rate should lead to less C_t")

    def test_replay_session_reproducibility(self):
        """Test that replaying a session with the same inputs is deterministic."""
        # Initial conditions for one team
        initial_conditions = {
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
        decisions_log = [
            ("team-1", 1, 0.2, "market"),
            ("team-1", 2, 0.3, "undervalue"),
            ("team-1", 3, 0.25, "market")
        ]
        result1 = replay_session(initial_conditions, decisions_log, num_rounds=3)
        result2 = replay_session(initial_conditions, decisions_log, num_rounds=3)
        self.assertEqual(result1, result2, "Replay should be deterministic and reproducible")

if __name__ == '__main__':
    unittest.main()