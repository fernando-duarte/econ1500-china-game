import unittest
import numpy as np
import pandas as pd
import os
import json
from solow_model import calculate_next_round
from replay import replay_session

class BenchmarkTests(unittest.TestCase):
    """Test cases that validate the model against real benchmark data."""

    def setUp(self):
        """Set up the benchmark test environment."""
        # Load historical data from CSV
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(current_dir, '..', '..', 'Data', 'china_economic_data.csv')
        self.historical_data = pd.read_csv(data_file)
        
        # Default parameters based on specs.md
        self.parameters = {
            'alpha': 0.3, 'delta': 0.1, 'g': 0.005, 'theta': 0.1453, 'phi': 0.1,
            'n': 0.00717, 'eta': 0.02,
            'X0': 18.1, 'M0': 14.5,
            'epsilon_x': 1.5, 'epsilon_m': 1.2,
            'mu_x': 1.0, 'mu_m': 1.0,
            'Y_1980': self.historical_data.loc[0, 'GDP (bn USD)'],
            'openness_ratio': 0.1  # Will be adjusted per round
        }

    def test_model_against_historical_data(self):
        """Test the model's output against historical data for key metrics."""
        # Start with 1980 data as initial state
        initial_year = 1980
        initial_row = self.historical_data[self.historical_data['Year'] == initial_year].iloc[0]
        
        initial_state = {
            'K': initial_row['Capital Stock (2017 USD bn)'],
            'L': initial_row['Labor Force (million)'],
            'H': initial_row['Human Capital Index'],
            'A': initial_row['TFP (2017=1)']
        }
        
        # Test each 5-year period from 1980 to 2020
        for i in range(1, 9):  # 1985, 1990, ..., 2020
            year = 1980 + (i * 5)
            round_index = i - 1
            
            # Get historical row for this year
            historical_row = self.historical_data[self.historical_data['Year'] == year].iloc[0]
            
            # Determine typical student inputs for this period (simplified for testing)
            student_inputs = self._get_estimated_student_inputs(year)
            
            # Update parameters for this round
            params_for_round = self.parameters.copy()
            params_for_round['openness_ratio'] = 0.1 + 0.02 * round_index
            
            # Run the model
            result = calculate_next_round(
                current_state=initial_state,
                parameters=params_for_round,
                student_inputs=student_inputs,
                year=year
            )
            
            # Compare with historical data (with tolerance)
            # We expect some deviation since the model is simplified
            self._compare_with_tolerance(result['Y_t'], historical_row['GDP (bn USD)'], 'GDP', year, tolerance=0.4)
            self._compare_with_tolerance(result['NX_t'], historical_row['Net Exports (bn USD)'], 'Net Exports', year, tolerance=0.5)
            
            # Update initial state for next iteration
            initial_state = {
                'K': result['K_next'],
                'L': result['L_next'],
                'H': result['H_next'],
                'A': result['A_next']
            }
    
    def test_model_sensitivity(self):
        """Test the model's sensitivity to different parameter values."""
        # Start with 2000 data for sensitivity testing
        year = 2000
        initial_row = self.historical_data[self.historical_data['Year'] == year].iloc[0]
        
        initial_state = {
            'K': initial_row['Capital Stock (2017 USD bn)'],
            'L': initial_row['Labor Force (million)'],
            'H': initial_row['Human Capital Index'],
            'A': initial_row['TFP (2017=1)']
        }
        
        # Parameter variations to test
        variations = [
            {'alpha': 0.25},  # Lower capital share
            {'alpha': 0.35},  # Higher capital share
            {'delta': 0.08},  # Lower depreciation
            {'delta': 0.12},  # Higher depreciation
            {'theta': 0.12},  # Lower openness impact
            {'theta': 0.17}   # Higher openness impact
        ]
        
        baseline_params = self.parameters.copy()
        baseline_params['openness_ratio'] = 0.2  # For year 2000
        
        # Student inputs for baseline
        student_inputs = {'s': 0.35, 'e_policy': 'market'}
        
        # Get baseline result
        baseline_result = calculate_next_round(
            current_state=initial_state,
            parameters=baseline_params,
            student_inputs=student_inputs,
            year=year
        )
        
        # Test each parameter variation
        for variation in variations:
            # Apply the variation
            test_params = baseline_params.copy()
            for param, value in variation.items():
                test_params[param] = value
            
            # Run the model with the variation
            test_result = calculate_next_round(
                current_state=initial_state,
                parameters=test_params,
                student_inputs=student_inputs,
                year=year
            )
            
            # Log the effect of this parameter change
            param_name = list(variation.keys())[0]
            param_value = list(variation.values())[0]
            gdp_change = (test_result['Y_t'] - baseline_result['Y_t']) / baseline_result['Y_t']
            nx_change = test_result['NX_t'] - baseline_result['NX_t']
            
            # Basic validation that parameters affect outputs in expected ways
            if param_name == 'alpha' and param_value > baseline_params['alpha']:
                self.assertGreater(test_result['Y_t'], baseline_result['Y_t'], 
                              f"Higher alpha should lead to higher GDP")
            
            if param_name == 'delta' and param_value > baseline_params['delta']:
                self.assertLess(test_result['K_next'], baseline_result['K_next'],
                           f"Higher depreciation should lead to lower next-period capital")
    
    def test_standard_policy_experiments(self):
        """Test well-known policy experiments and their outcomes."""
        # 1. High savings strategy (East Asian model)
        # 2. Export-oriented strategy (undervalued currency)
        # 3. Balanced approach
        
        initial_year = 2000
        initial_row = self.historical_data[self.historical_data['Year'] == initial_year].iloc[0]
        
        initial_state = {
            'K': initial_row['Capital Stock (2017 USD bn)'],
            'L': initial_row['Labor Force (million)'],
            'H': initial_row['Human Capital Index'],
            'A': initial_row['TFP (2017=1)']
        }
        
        params = self.parameters.copy()
        params['openness_ratio'] = 0.2  # For year 2000
        
        # Run the three policy experiments
        high_savings = calculate_next_round(
            current_state=initial_state,
            parameters=params,
            student_inputs={'s': 0.5, 'e_policy': 'market'},
            year=initial_year
        )
        
        export_oriented = calculate_next_round(
            current_state=initial_state,
            parameters=params,
            student_inputs={'s': 0.3, 'e_policy': 'undervalue'},
            year=initial_year
        )
        
        balanced = calculate_next_round(
            current_state=initial_state,
            parameters=params,
            student_inputs={'s': 0.35, 'e_policy': 'market'},
            year=initial_year
        )
        
        # Test expected outcomes
        self.assertGreater(high_savings['K_next'], export_oriented['K_next'],
                      "High savings strategy should lead to more capital accumulation")
        
        self.assertGreater(export_oriented['NX_t'], high_savings['NX_t'],
                      "Export-oriented strategy should lead to higher net exports")
        
        self.assertGreater(balanced['C_t'], high_savings['C_t'],
                      "Balanced approach should have higher consumption than high savings")
    
    def _get_estimated_student_inputs(self, year):
        """Generate reasonable student inputs for historical simulation."""
        # This is a simplified estimation of what policies China might have chosen
        # In a real benchmark, you'd want to derive these from historical policy data
        if year < 1995:
            return {'s': 0.35, 'e_policy': 'undervalue'}
        elif year < 2005:
            return {'s': 0.45, 'e_policy': 'undervalue'}
        else:
            return {'s': 0.42, 'e_policy': 'market'}
    
    def _compare_with_tolerance(self, model_value, historical_value, metric_name, year, tolerance=0.3):
        """Compare model output to historical value with percentage tolerance."""
        if historical_value == 0:
            return  # Avoid division by zero
        
        # Calculate percentage difference
        pct_diff = abs(model_value - historical_value) / historical_value
        
        # Log the comparison
        comparison_msg = (f"{metric_name} for {year}: model={model_value:.1f}, "
                        f"historical={historical_value:.1f}, diff={pct_diff:.2%}")
        
        # Assert with tolerance
        self.assertLessEqual(pct_diff, tolerance, 
                        f"{comparison_msg} - difference exceeds tolerance of {tolerance:.0%}")


if __name__ == '__main__':
    unittest.main() 