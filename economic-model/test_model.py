import unittest
import numpy as np # Add numpy import if needed for assertions
from solow_model import calculate_next_round

class TestSolowModel(unittest.TestCase):
    """Test cases for the calculate_next_round function."""

    def setUp(self):
        """Set up the test environment."""
        # Initial GDP for Y_1980 parameter
        self.y_1980 = 1000.0

        # Define parameters based on specs.md
        self.parameters = {
            'alpha': 0.3, 'delta': 0.1, 'g': 0.005, 'theta': 0.1453, 'phi': 0.1,
            'n': 0.00717, 'eta': 0.02,
            'X0': 18.1, 'M0': 14.5,
            'epsilon_x': 1.5, 'epsilon_m': 1.2,
            'mu_x': 1.0, 'mu_m': 1.0,
            'Y_1980': self.y_1980,
            # 'openness_ratio' is calculated per round below
        }

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
            's': 0.2, # Default savings rate
            'e_policy': 'market'
        }

    def _get_params_for_round(self, round_index):
        "Helper to calculate round-specific parameters." 
        params = self.parameters.copy()
        params['openness_ratio'] = 0.1 + 0.02 * round_index
        return params

    # Renamed test
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

        self.assertGreater(result['K_next'], self.initial_state['K'] * (1 - self.parameters['delta']), "Capital next should generally be greater than depreciated capital")
        self.assertGreater(result['L_next'], self.initial_state['L'], "Labor should grow")
        self.assertGreater(result['H_next'], self.initial_state['H'], "Human Capital should grow")
        self.assertGreater(result['A_next'], self.initial_state['A'], "TFP should grow")
        self.assertAlmostEqual(result['C_t'], (1 - self.student_inputs_market['s']) * result['Y_t'], places=5, msg="Consumption should be (1-s)*Y_t")
        self.assertAlmostEqual(result['I_t'], self.student_inputs_market['s'] * result['Y_t'] + result['NX_t'], places=5, msg="Investment should be s*Y_t + NX_t")
        # Check capital accumulation links I_t and K_next
        expected_K_next = (1 - self.parameters['delta']) * max(0, self.initial_state['K']) + result['I_t']
        self.assertAlmostEqual(result['K_next'], expected_K_next, places=5, msg="K_next should equal (1-d)K_t + I_t")


    def test_exchange_rate_policy_impact(self):
        """Test the impact of different exchange rate policies on Net Exports."""
        current_year = 1990 # Example: 3rd round (index 2)
        round_index = 2
        params_round = self._get_params_for_round(round_index)

        # Simulate with market exchange rate
        inputs_market = {'s': 0.2, 'e_policy': 'market'}
        result_market = calculate_next_round(self.initial_state, params_round, inputs_market, current_year)

        # Simulate with undervalued exchange rate
        inputs_undervalue = {'s': 0.2, 'e_policy': 'undervalue'}
        result_undervalue = calculate_next_round(self.initial_state, params_round, inputs_undervalue, current_year)

        # Simulate with overvalued exchange rate
        inputs_overvalue = {'s': 0.2, 'e_policy': 'overvalue'}
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
        inputs_low_s = {'s': 0.1, 'e_policy': 'market'}
        result_low_s = calculate_next_round(self.initial_state, params_round, inputs_low_s, current_year)

        # Simulate with high savings rate
        inputs_high_s = {'s': 0.5, 'e_policy': 'market'}
        result_high_s = calculate_next_round(self.initial_state, params_round, inputs_high_s, current_year)

        # Higher savings should lead to more capital accumulation next period
        self.assertGreater(result_high_s["K_next"], result_low_s["K_next"],
                      "Higher savings rate should lead to more K_next")

        # Higher savings should lead to less consumption this period
        self.assertLess(result_high_s["C_t"], result_low_s["C_t"],
                    "Higher savings rate should lead to less C_t")

    # Removed WTO event test as event logic is outside the tested function
    # def test_wto_event_impact(self): ...

    # Removed visualization test as it tested a method on the old class
    # def test_visualization_data(self): ...

if __name__ == '__main__':
    unittest.main() 