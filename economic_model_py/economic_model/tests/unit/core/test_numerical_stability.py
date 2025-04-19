"""
Numerical stability tests for the Solow growth model.

This module contains tests to verify the numerical stability and
performance of the economic model under various conditions.
"""

import unittest
import numpy as np
import pandas as pd
import time
import math
from typing import Dict, Any

from economic_model_py.economic_model.utils.error_handling import (
    CalculationError, ParameterError
)

from economic_model_py.economic_model.core.solow_core import (
    calculate_production,
    calculate_capital_next,
    calculate_labor_next,
    calculate_human_capital_next,
    calculate_tfp_next,
    calculate_exchange_rate,
    calculate_foreign_income,
    calculate_net_exports,
    get_default_parameters,
    solve_solow_model
)

class TestNumericalStability(unittest.TestCase):
    """Tests for numerical stability and performance of the economic model."""

    def setUp(self):
        """Set up the test environment."""
        self.default_params = get_default_parameters()
        # Add savings rate parameter which is required by solve_solow_model
        self.default_params['s'] = 0.2

        # Standard initial conditions
        self.initial_conditions = {
            'K': 1000.0,
            'L': 100.0,
            'H': 1.0,
            'A': 1.0,
            'Y': 100.0
        }

        # Years for simulation
        self.years = np.arange(1980, 2026, 5)

    def test_extreme_initial_conditions(self):
        """Test that the model is stable with extreme initial conditions."""
        # Test with very small initial values
        small_conditions = {
            'K': 1e-6,
            'L': 1e-6,
            'H': 1e-6,
            'A': 1e-6,
            'Y': 1e-6
        }

        # This should not raise an exception
        small_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=small_conditions,
            parameters=self.default_params,
            years=self.years
        )

        # Check that results are non-negative
        self.assertTrue(all(small_results['GDP'] >= 0), "GDP should be non-negative with small initial conditions")
        self.assertTrue(all(small_results['Capital'] >= 0), "Capital should be non-negative with small initial conditions")

        # Test with very large initial values
        large_conditions = {
            'K': 1e12,
            'L': 1e6,
            'H': 1e3,
            'A': 1e3,
            'Y': 1e12
        }

        # This should not raise an exception
        large_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=large_conditions,
            parameters=self.default_params,
            years=self.years
        )

        # Check that results are finite
        self.assertTrue(all(np.isfinite(large_results['GDP'])), "GDP should be finite with large initial conditions")
        self.assertTrue(all(np.isfinite(large_results['Capital'])), "Capital should be finite with large initial conditions")

    def test_extreme_parameters(self):
        """Test that the model is stable with extreme parameter values."""
        # Test with extreme alpha values
        alpha_values = [0.01, 0.99]

        for alpha in alpha_values:
            params = self.default_params.copy()
            params['alpha'] = alpha

            # This should not raise an exception
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )

            # Check that results are reasonable
            self.assertTrue(all(results['GDP'] >= 0), f"GDP should be non-negative with alpha={alpha}")
            self.assertTrue(all(results['Capital'] >= 0), f"Capital should be non-negative with alpha={alpha}")

        # Test with extreme growth rates
        growth_values = [-0.1, 0.0, 0.2]

        for g in growth_values:
            params = self.default_params.copy()
            params['g'] = g

            # This should not raise an exception
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )

            # Check that results are reasonable
            self.assertTrue(all(results['GDP'] >= 0), f"GDP should be non-negative with g={g}")
            self.assertTrue(all(np.isfinite(results['GDP'])), f"GDP should be finite with g={g}")

    def test_numerical_precision(self):
        """Test the numerical precision of the model calculations."""
        # Run the same simulation with different floating-point precisions
        # and check that the results are consistent

        # Standard double precision
        double_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=self.years
        )

        # Convert to single precision and back to double
        single_conditions = {k: np.float32(v) for k, v in self.initial_conditions.items()}
        single_params = {k: np.float32(v) if isinstance(v, (int, float)) else v
                        for k, v in self.default_params.items()}

        # Convert back to double for the calculation
        single_double_conditions = {k: float(v) for k, v in single_conditions.items()}
        single_double_params = {k: float(v) if isinstance(v, (np.float32, float, int)) else v
                              for k, v in single_params.items()}

        single_double_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=single_double_conditions,
            parameters=single_double_params,
            years=self.years
        )

        # Compare results - they should be close but not identical due to precision differences
        for col in ['GDP', 'Capital', 'Labor Force', 'Human Capital', 'Productivity (TFP)']:
            # Calculate relative difference
            rel_diff = np.abs((double_results[col] - single_double_results[col]) / double_results[col])
            max_rel_diff = rel_diff.max()

            # Relative difference should be small (less than 0.1%)
            self.assertLess(max_rel_diff, 0.001,
                           f"Maximum relative difference for {col} is {max_rel_diff}, which exceeds 0.1%")

    def test_long_term_stability(self):
        """Test the stability of the model over very long time horizons."""
        # Run a simulation for the maximum allowed years (1980-2025)
        long_years = np.arange(1980, 2026, 1)  # Use 1-year steps to get more periods

        # Use standard parameters
        params = self.default_params.copy()

        # This should not raise an exception
        long_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=long_years
        )

        # Check that results remain finite and non-negative
        self.assertTrue(all(np.isfinite(long_results['GDP'])), "GDP should remain finite over long time horizons")
        self.assertTrue(all(long_results['GDP'] >= 0), "GDP should remain non-negative over long time horizons")
        self.assertTrue(all(np.isfinite(long_results['Capital'])), "Capital should remain finite over long time horizons")
        self.assertTrue(all(long_results['Capital'] >= 0), "Capital should remain non-negative over long time horizons")

        # Check that growth rates remain reasonable
        gdp_values = long_results['GDP'].values
        growth_rates = [gdp_values[i+1]/gdp_values[i] - 1 for i in range(len(gdp_values)-1)]

        self.assertTrue(all(np.isfinite(growth_rates)), "Growth rates should remain finite")
        self.assertTrue(all(np.array(growth_rates) > -1), "Growth rates should be greater than -100%")
        self.assertTrue(all(np.array(growth_rates) < 10), "Growth rates should be less than 1000%")

    def test_performance(self):
        """Test the performance of the model calculations."""
        # Measure the time taken to run simulations of different lengths

        # Short simulation (5 periods)
        short_years = np.arange(1980, 2000, 5)

        start_time = time.time()
        solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=short_years
        )
        short_time = time.time() - start_time

        # Medium simulation (10 periods)
        medium_years = np.arange(1980, 2025, 5)

        start_time = time.time()
        solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=medium_years
        )
        medium_time = time.time() - start_time

        # Long simulation (46 periods)
        long_years = np.arange(1980, 2026, 1)

        start_time = time.time()
        solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=long_years
        )
        long_time = time.time() - start_time

        # Check that performance scales reasonably with simulation length
        # Time should increase less than quadratically with simulation length
        short_periods = len(short_years)
        medium_periods = len(medium_years)
        long_periods = len(long_years)

        # Calculate time per period
        short_time_per_period = short_time / short_periods
        medium_time_per_period = medium_time / medium_periods
        long_time_per_period = long_time / long_periods

        # Time per period should not increase too much with simulation length
        # Allow for some increase due to memory allocation and other factors
        self.assertLess(medium_time_per_period / short_time_per_period, 2.0,
                       f"Medium simulation time per period ({medium_time_per_period}) is too much higher than short simulation ({short_time_per_period})")
        self.assertLess(long_time_per_period / medium_time_per_period, 2.0,
                       f"Long simulation time per period ({long_time_per_period}) is too much higher than medium simulation ({medium_time_per_period})")

        # Overall performance should be reasonable (less than 1 second for short simulation)
        self.assertLess(short_time, 1.0, f"Short simulation took too long: {short_time} seconds")

    def test_memory_usage(self):
        """Test that the model uses a reasonable amount of memory."""
        # This is a simplified test that just checks if we can run simulations of different lengths
        # without running out of memory

        # Run simulations of different lengths
        short_years = np.arange(1980, 2000, 5)  # 5 periods
        long_years = np.arange(1980, 2026, 1)   # 46 periods

        # Run the short simulation
        short_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=short_years
        )

        # Run the long simulation
        long_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=long_years
        )

        # Check that both simulations completed successfully
        self.assertEqual(len(short_results), len(short_years))
        self.assertEqual(len(long_results), len(long_years))

        # Check that memory usage scales reasonably (by proxy of being able to complete both simulations)
        self.assertTrue(True, "Both simulations completed without memory errors")

    def test_reproducibility(self):
        """Test that the model produces the same results when run multiple times with the same inputs."""
        # Run the same simulation multiple times and check that the results are identical

        results1 = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=self.years
        )

        results2 = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=self.default_params,
            years=self.years
        )

        # Results should be identical
        pd.testing.assert_frame_equal(results1, results2)

    def test_edge_cases(self):
        """Test that the model handles edge cases correctly."""
        # Test with zero initial capital
        zero_capital = self.initial_conditions.copy()
        zero_capital['K'] = 0.0

        # This should not raise an exception
        zero_capital_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=zero_capital,
            parameters=self.default_params,
            years=self.years
        )

        # Capital should recover from zero
        self.assertGreater(zero_capital_results.iloc[-1]['Capital'], 0,
                          "Capital should recover from zero initial value")

        # Test with minimum savings rate
        min_savings = self.default_params.copy()
        min_savings['s'] = 0.01  # Minimum allowed value

        # This should not raise an exception
        min_savings_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=min_savings,
            years=self.years
        )

        # With minimal savings, capital should still be positive
        self.assertGreater(min_savings_results.iloc[-1]['Capital'], 0,
                          "Capital should remain positive with minimal savings rate")

        # Test with 100% depreciation
        full_depreciation = self.default_params.copy()
        full_depreciation['delta'] = 1.0

        # This should not raise an exception
        full_depreciation_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=full_depreciation,
            years=self.years
        )

        # Capital should still be positive (from current period investment)
        self.assertTrue(all(full_depreciation_results['Capital'] > 0),
                       "Capital should remain positive even with 100% depreciation")

    def test_custom_exceptions(self):
        """Test that the model raises appropriate custom exceptions."""
        # Test missing required initial conditions
        incomplete_conditions = {
            'K': 1000.0,
            'L': 100.0,
            # Missing 'H' and 'A'
        }

        # This should raise a ParameterError
        with self.assertRaises(ParameterError):
            solve_solow_model(
                initial_year=1980,
                initial_conditions=incomplete_conditions,
                parameters=self.default_params,
                years=self.years
            )

        # Test invalid parameter values
        invalid_params = self.default_params.copy()
        invalid_params['alpha'] = 1.5  # Alpha must be between 0 and 1

        # This should raise a ParameterError
        with self.assertRaises(ParameterError):
            solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=invalid_params,
                years=self.years
            )

        # Test with negative initial values
        negative_conditions = self.initial_conditions.copy()
        negative_conditions['K'] = -1000.0

        # This should raise a ParameterError
        with self.assertRaises(ParameterError):
            solve_solow_model(
                initial_year=1980,
                initial_conditions=negative_conditions,
                parameters=self.default_params,
                years=self.years
            )

        # Test with invalid year
        with self.assertRaises(ParameterError):
            solve_solow_model(
                initial_year=1800,  # Too early
                initial_conditions=self.initial_conditions,
                parameters=self.default_params,
                years=np.array([1800, 1805, 1810])
            )

    def test_parameter_consistency(self):
        """Test that the model maintains parameter consistency throughout the simulation."""
        # Run a simulation with fixed parameters
        params = self.default_params.copy()

        # Add a distinctive value to check
        params['alpha'] = 0.42  # Specific value to check

        # Run simulation
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=self.years
        )

        # Check that the results are consistent with the parameters
        # For Cobb-Douglas: Y = A * K^alpha * (L*H)^(1-alpha)
        # So alpha = log(Y/(A*(L*H)^(1-alpha)))/log(K)

        for i in range(len(results)):
            Y = results.iloc[i]['GDP']
            K = results.iloc[i]['Capital']
            L = results.iloc[i]['Labor Force']
            H = results.iloc[i]['Human Capital']
            A = results.iloc[i]['Productivity (TFP)']

            # Calculate implied alpha
            # Y = A * K^alpha * (L*H)^(1-alpha)
            # Y/(A*(L*H)^(1-alpha)) = K^alpha
            # log(Y/(A*(L*H)^(1-alpha)))/log(K) = alpha

            # First, guess alpha to calculate (L*H)^(1-alpha)
            alpha_guess = params['alpha']
            LH_term = (L * H) ** (1 - alpha_guess)

            # Then calculate implied alpha
            if K > 0 and A > 0 and LH_term > 0:
                implied_alpha = math.log(Y / (A * LH_term)) / math.log(K)

                # Check that implied alpha is close to the parameter value
                # Allow for some numerical error
                self.assertAlmostEqual(implied_alpha, params['alpha'], delta=0.1,
                                     msg=f"Implied alpha ({implied_alpha}) differs from parameter value ({params['alpha']}) at period {i}")

if __name__ == '__main__':
    unittest.main()
