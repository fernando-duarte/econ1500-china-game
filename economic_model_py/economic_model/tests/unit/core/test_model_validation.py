"""
Model validation tests for the Solow growth model.

This module contains comprehensive tests to validate the economic model
against theoretical predictions and expected behavior.
"""

import unittest
import numpy as np
import pandas as pd
import math
from typing import Dict, Any

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
    calculate_openness_ratio,
    calculate_fdi_ratio,
    solve_solow_model
)

class TestModelValidation(unittest.TestCase):
    """Comprehensive validation tests for the Solow growth model."""

    def setUp(self):
        """Set up the test environment."""
        self.default_params = get_default_parameters()
        
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
        
    def test_steady_state_convergence(self):
        """Test that the model converges to a steady state with constant parameters."""
        # Create parameters with no growth in TFP, labor, or human capital
        params = self.default_params.copy()
        params.update({
            'g': 0.0,  # No TFP growth
            'n': 0.0,  # No labor force growth
            'eta': 0.0,  # No human capital growth
            's': 0.2,  # Fixed savings rate
            'delta': 0.05  # Fixed depreciation rate
        })
        
        # Run a long simulation (200 years) to ensure convergence
        long_years = np.arange(1980, 2180, 5)
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=long_years
        )
        
        # In steady state, capital per effective worker should be constant
        # Calculate capital per effective worker: k = K / (L*H*A)
        k_values = []
        for i in range(len(results)):
            K = results.iloc[i]['Capital']
            L = results.iloc[i]['Labor Force']
            H = results.iloc[i]['Human Capital']
            A = results.iloc[i]['Productivity (TFP)']
            k = K / (L * H * A)
            k_values.append(k)
            
        # Check if k converges (last few values should be very close)
        k_final_values = k_values[-5:]
        k_mean = np.mean(k_final_values)
        k_std = np.std(k_final_values)
        
        # Standard deviation should be very small relative to the mean
        self.assertLess(k_std / k_mean, 0.01, 
                       f"Capital per effective worker not converging: std/mean = {k_std/k_mean}")
        
        # Calculate theoretical steady state k*
        # In steady state: s*f(k) = (delta+n+g)*k
        # For Cobb-Douglas: s*A*k^alpha = (delta+n+g)*k
        # Solving for k: k* = [s*A/(delta+n+g)]^(1/(1-alpha))
        alpha = params['alpha']
        s = params['s']
        delta = params['delta']
        n = params['n']
        g = params['g']
        A = self.initial_conditions['A']
        
        k_star_theory = (s * A / (delta + n + g)) ** (1 / (1 - alpha))
        
        # Check if simulated k converges to theoretical k*
        self.assertAlmostEqual(k_mean, k_star_theory, delta=k_star_theory*0.05,
                              msg=f"Simulated k ({k_mean}) differs from theoretical k* ({k_star_theory})")
                              
    def test_balanced_growth_path(self):
        """Test that the model exhibits balanced growth with constant growth rates."""
        # Create parameters with constant growth rates
        params = self.default_params.copy()
        params.update({
            'g': 0.02,  # 2% TFP growth
            'n': 0.01,  # 1% labor force growth
            'eta': 0.01,  # 1% human capital growth
            's': 0.3,  # Fixed savings rate
            'delta': 0.05  # Fixed depreciation rate
        })
        
        # Run a long simulation to observe balanced growth
        long_years = np.arange(1980, 2180, 5)
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=long_years
        )
        
        # On a balanced growth path, output per worker should grow at rate g + eta
        # Calculate growth rates of output per worker
        y_per_worker = results['GDP'] / results['Labor Force']
        growth_rates = []
        
        # Calculate 5-year growth rates (since we use 5-year periods)
        for i in range(1, len(y_per_worker)):
            growth_rate = (y_per_worker.iloc[i] / y_per_worker.iloc[i-1]) - 1
            growth_rates.append(growth_rate)
            
        # After convergence, growth rates should stabilize
        # Use the last 10 periods (50 years)
        recent_growth_rates = growth_rates[-10:]
        mean_growth_rate = np.mean(recent_growth_rates)
        
        # Expected 5-year growth rate: (1+g+eta)^5 - 1
        expected_growth_rate = (1 + params['g'] + params['eta'])**5 - 1
        
        # Check if growth rate converges to expected rate
        self.assertAlmostEqual(mean_growth_rate, expected_growth_rate, delta=0.01,
                              msg=f"Growth rate ({mean_growth_rate}) differs from expected ({expected_growth_rate})")
                              
    def test_golden_rule_savings_rate(self):
        """Test that the golden rule savings rate maximizes consumption."""
        # The golden rule savings rate maximizes steady-state consumption
        # For Cobb-Douglas: s_gold = alpha
        
        alpha = self.default_params['alpha']
        
        # Test a range of savings rates around the golden rule
        savings_rates = np.linspace(alpha - 0.2, alpha + 0.2, 9)
        steady_state_consumption = []
        
        for s in savings_rates:
            params = self.default_params.copy()
            params.update({
                'g': 0.0,  # No TFP growth for simplicity
                'n': 0.0,  # No labor force growth
                'eta': 0.0,  # No human capital growth
                's': s,
                'delta': 0.05
            })
            
            # Run a long simulation to reach steady state
            long_years = np.arange(1980, 2180, 5)
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=long_years
            )
            
            # Get steady-state consumption (last period)
            steady_state_consumption.append(results.iloc[-1]['Consumption'])
            
        # Find savings rate with maximum consumption
        max_consumption_index = np.argmax(steady_state_consumption)
        optimal_s = savings_rates[max_consumption_index]
        
        # Check if optimal savings rate is close to golden rule
        self.assertAlmostEqual(optimal_s, alpha, delta=0.05,
                              msg=f"Optimal savings rate ({optimal_s}) differs from golden rule ({alpha})")
                              
    def test_solow_residual(self):
        """Test that the Solow residual (TFP) is calculated correctly."""
        # The Solow residual is the portion of output growth not explained by 
        # growth in capital and labor inputs
        
        # Create a simulation with known TFP growth
        params = self.default_params.copy()
        params.update({
            'g': 0.02,  # 2% TFP growth
            'n': 0.01,  # 1% labor force growth
            'eta': 0.01,  # 1% human capital growth
            's': 0.3,
            'delta': 0.05
        })
        
        # Run simulation
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=self.years
        )
        
        # Calculate Solow residual for each period
        alpha = params['alpha']
        residuals = []
        
        for i in range(1, len(results)):
            # Growth rates
            y_growth = results.iloc[i]['GDP'] / results.iloc[i-1]['GDP'] - 1
            k_growth = results.iloc[i]['Capital'] / results.iloc[i-1]['Capital'] - 1
            l_growth = results.iloc[i]['Labor Force'] / results.iloc[i-1]['Labor Force'] - 1
            h_growth = results.iloc[i]['Human Capital'] / results.iloc[i-1]['Human Capital'] - 1
            
            # Solow residual: dY/Y - alpha*dK/K - (1-alpha)*d(L*H)/(L*H)
            residual = y_growth - alpha * k_growth - (1 - alpha) * (l_growth + h_growth + l_growth * h_growth)
            residuals.append(residual)
            
        # Calculate average residual
        mean_residual = np.mean(residuals)
        
        # Expected residual: g (TFP growth rate)
        # For 5-year periods: (1+g)^5 - 1
        expected_residual = (1 + params['g'])**5 - 1
        
        # Check if calculated residual matches expected TFP growth
        self.assertAlmostEqual(mean_residual, expected_residual, delta=0.02,
                              msg=f"Solow residual ({mean_residual}) differs from expected ({expected_residual})")
                              
    def test_capital_output_ratio(self):
        """Test that the capital-output ratio converges to the expected value."""
        # In steady state, the capital-output ratio should be s/(n+g+delta)
        
        # Create parameters for steady state
        params = self.default_params.copy()
        params.update({
            'g': 0.02,  # 2% TFP growth
            'n': 0.01,  # 1% labor force growth
            'eta': 0.0,  # No human capital growth for simplicity
            's': 0.3,
            'delta': 0.05
        })
        
        # Run a long simulation to reach steady state
        long_years = np.arange(1980, 2180, 5)
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=long_years
        )
        
        # Calculate capital-output ratio for last few periods
        k_y_ratios = []
        for i in range(-5, 0):
            k_y = results.iloc[i]['Capital'] / results.iloc[i]['GDP']
            k_y_ratios.append(k_y)
            
        # Average capital-output ratio
        mean_k_y = np.mean(k_y_ratios)
        
        # Expected capital-output ratio: s/(n+g+delta)
        expected_k_y = params['s'] / (params['n'] + params['g'] + params['delta'])
        
        # Check if capital-output ratio converges to expected value
        self.assertAlmostEqual(mean_k_y, expected_k_y, delta=expected_k_y*0.1,
                              msg=f"Capital-output ratio ({mean_k_y}) differs from expected ({expected_k_y})")
                              
    def test_exchange_rate_effects(self):
        """Test that exchange rate policies have the expected effects on trade."""
        # Undervalued exchange rate should increase net exports
        # Overvalued exchange rate should decrease net exports
        
        # Run simulations with different exchange rate policies
        policies = ['undervalue', 'market', 'overvalue']
        net_exports = {}
        
        for policy in policies:
            # Create initial state and parameters
            current_state = {
                'K': 1000.0,
                'L': 100.0,
                'H': 1.0,
                'A': 1.0
            }
            
            # Import the necessary function
            from economic_model_py.economic_model.core.solow_core import calculate_single_round
            
            # Calculate one round with the given exchange rate policy
            result = calculate_single_round(
                current_state=current_state,
                parameters=self.default_params,
                student_inputs={'savings_rate': 0.3, 'exchange_rate_policy': policy},
                year=2000
            )
            
            # Store net exports
            net_exports[policy] = result['NX_t']
            
        # Check that undervalued exchange rate increases net exports
        self.assertGreater(net_exports['undervalue'], net_exports['market'],
                          "Undervalued exchange rate should increase net exports")
                          
        # Check that overvalued exchange rate decreases net exports
        self.assertLess(net_exports['overvalue'], net_exports['market'],
                       "Overvalued exchange rate should decrease net exports")
                       
    def test_savings_rate_effects(self):
        """Test that higher savings rates lead to higher investment and capital accumulation."""
        # Higher savings rates should lead to higher investment and faster capital accumulation
        
        # Run simulations with different savings rates
        savings_rates = [0.1, 0.2, 0.3, 0.4]
        capital_growth = {}
        
        for s in savings_rates:
            params = self.default_params.copy()
            params['s'] = s
            
            # Run a short simulation
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )
            
            # Calculate capital growth rate
            initial_capital = results.iloc[0]['Capital']
            final_capital = results.iloc[-1]['Capital']
            growth_rate = (final_capital / initial_capital) - 1
            
            capital_growth[s] = growth_rate
            
        # Check that higher savings rates lead to higher capital growth
        for i in range(1, len(savings_rates)):
            self.assertGreater(capital_growth[savings_rates[i]], capital_growth[savings_rates[i-1]],
                              f"Higher savings rate {savings_rates[i]} should lead to faster capital growth than {savings_rates[i-1]}")
                              
    def test_convergence_speed(self):
        """Test that the model exhibits the expected convergence speed to steady state."""
        # The speed of convergence to steady state should be approximately (1-alpha)*(n+g+delta)
        
        # Create parameters
        params = self.default_params.copy()
        params.update({
            'g': 0.02,  # 2% TFP growth
            'n': 0.01,  # 1% labor force growth
            'eta': 0.0,  # No human capital growth for simplicity
            's': 0.3,
            'delta': 0.05
        })
        
        # Create two initial conditions: one close to steady state, one far from it
        # First, calculate theoretical steady state capital
        alpha = params['alpha']
        s = params['s']
        delta = params['delta']
        n = params['n']
        g = params['g']
        A = self.initial_conditions['A']
        L = self.initial_conditions['L']
        H = self.initial_conditions['H']
        
        # Steady state capital per effective worker: k* = [s/(n+g+delta)]^(1/(1-alpha))
        k_star = (s / (n + g + delta)) ** (1 / (1 - alpha))
        
        # Steady state capital: K* = k* * L * H * A
        K_star = k_star * L * H * A
        
        # Create initial conditions: 50% and 150% of steady state
        initial_conditions_low = self.initial_conditions.copy()
        initial_conditions_low['K'] = 0.5 * K_star
        
        initial_conditions_high = self.initial_conditions.copy()
        initial_conditions_high['K'] = 1.5 * K_star
        
        # Run simulations
        years = np.arange(1980, 2030, 5)  # Shorter simulation
        
        results_low = solve_solow_model(
            initial_year=1980,
            initial_conditions=initial_conditions_low,
            parameters=params,
            years=years
        )
        
        results_high = solve_solow_model(
            initial_year=1980,
            initial_conditions=initial_conditions_high,
            parameters=params,
            years=years
        )
        
        # Calculate convergence rates
        # For each period, calculate: ln(k_t/k*) = (1-λ)^t * ln(k_0/k*)
        # where λ is the convergence rate
        
        # Calculate k_t/k* for each period
        k_ratio_low = []
        k_ratio_high = []
        
        for i in range(len(years)):
            # Calculate capital per effective worker
            k_low = results_low.iloc[i]['Capital'] / (results_low.iloc[i]['Labor Force'] * 
                                                    results_low.iloc[i]['Human Capital'] * 
                                                    results_low.iloc[i]['Productivity (TFP)'])
            k_high = results_high.iloc[i]['Capital'] / (results_high.iloc[i]['Labor Force'] * 
                                                      results_high.iloc[i]['Human Capital'] * 
                                                      results_high.iloc[i]['Productivity (TFP)'])
            
            # Calculate ln(k_t/k*)
            k_ratio_low.append(np.log(k_low / k_star))
            k_ratio_high.append(np.log(k_high / k_star))
            
        # Estimate convergence rate from the data
        # For low initial capital
        t_values = np.arange(0, len(years))
        
        # Fit a line to ln(k_ratio) vs t
        from scipy import stats
        slope_low, _, _, _, _ = stats.linregress(t_values, k_ratio_low)
        slope_high, _, _, _, _ = stats.linregress(t_values, k_ratio_high)
        
        # Convergence rate: λ = 1 - e^slope (for 5-year periods)
        lambda_low = 1 - np.exp(slope_low)
        lambda_high = 1 - np.exp(slope_high)
        
        # Average convergence rate
        lambda_avg = (lambda_low + lambda_high) / 2
        
        # Expected convergence rate: (1-alpha)*(n+g+delta)
        # For 5-year periods: 1 - e^(-5*(1-alpha)*(n+g+delta))
        expected_lambda = 1 - np.exp(-5 * (1 - alpha) * (n + g + delta))
        
        # Check if convergence rate is close to expected
        self.assertAlmostEqual(lambda_avg, expected_lambda, delta=0.05,
                              msg=f"Convergence rate ({lambda_avg}) differs from expected ({expected_lambda})")
                              
    def test_openness_and_fdi_effects(self):
        """Test that openness and FDI have the expected effects on TFP growth."""
        # Higher openness and FDI should lead to faster TFP growth
        
        # Create parameters with different openness and FDI effects
        base_params = self.default_params.copy()
        
        # Baseline: no openness or FDI effects
        params_baseline = base_params.copy()
        params_baseline.update({
            'theta': 0.0,  # No openness effect
            'phi': 0.0     # No FDI effect
        })
        
        # With openness effect
        params_openness = base_params.copy()
        params_openness.update({
            'theta': 0.1,  # Positive openness effect
            'phi': 0.0     # No FDI effect
        })
        
        # With FDI effect
        params_fdi = base_params.copy()
        params_fdi.update({
            'theta': 0.0,  # No openness effect
            'phi': 0.1     # Positive FDI effect
        })
        
        # With both effects
        params_both = base_params.copy()
        params_both.update({
            'theta': 0.1,  # Positive openness effect
            'phi': 0.1     # Positive FDI effect
        })
        
        # Run simulations
        results_baseline = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params_baseline,
            years=self.years
        )
        
        results_openness = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params_openness,
            years=self.years
        )
        
        results_fdi = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params_fdi,
            years=self.years
        )
        
        results_both = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params_both,
            years=self.years
        )
        
        # Compare final TFP values
        tfp_baseline = results_baseline.iloc[-1]['Productivity (TFP)']
        tfp_openness = results_openness.iloc[-1]['Productivity (TFP)']
        tfp_fdi = results_fdi.iloc[-1]['Productivity (TFP)']
        tfp_both = results_both.iloc[-1]['Productivity (TFP)']
        
        # Check that openness increases TFP
        self.assertGreater(tfp_openness, tfp_baseline,
                          "Openness should increase TFP growth")
                          
        # Check that FDI increases TFP
        self.assertGreater(tfp_fdi, tfp_baseline,
                          "FDI should increase TFP growth")
                          
        # Check that combined effects are greater than individual effects
        self.assertGreater(tfp_both, tfp_openness,
                          "Combined effects should be greater than openness alone")
        self.assertGreater(tfp_both, tfp_fdi,
                          "Combined effects should be greater than FDI alone")
                          
    def test_model_robustness(self):
        """Test that the model is robust to extreme parameter values."""
        # The model should handle extreme parameter values without crashing
        
        # Test with extreme savings rates
        extreme_savings = [0.0, 0.01, 0.99, 1.0]
        
        for s in extreme_savings:
            params = self.default_params.copy()
            params['s'] = s
            
            # This should not raise an exception
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )
            
            # Check that results are reasonable
            self.assertTrue(all(results['GDP'] >= 0), f"GDP should be non-negative with s={s}")
            self.assertTrue(all(results['Capital'] >= 0), f"Capital should be non-negative with s={s}")
            
        # Test with extreme depreciation rates
        extreme_depreciation = [0.0, 0.01, 0.5, 0.99]
        
        for delta in extreme_depreciation:
            params = self.default_params.copy()
            params['delta'] = delta
            
            # This should not raise an exception
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )
            
            # Check that results are reasonable
            self.assertTrue(all(results['GDP'] >= 0), f"GDP should be non-negative with delta={delta}")
            self.assertTrue(all(results['Capital'] >= 0), f"Capital should be non-negative with delta={delta}")
            
    def test_negative_shocks(self):
        """Test that the model handles negative shocks appropriately."""
        # The model should recover from negative shocks to capital
        
        # Run a normal simulation for a few periods
        params = self.default_params.copy()
        years = np.arange(1980, 2000, 5)
        
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=params,
            years=years
        )
        
        # Create a shock by reducing capital by 50%
        shocked_conditions = {
            'K': results.iloc[2]['Capital'] * 0.5,  # 50% reduction
            'L': results.iloc[2]['Labor Force'],
            'H': results.iloc[2]['Human Capital'],
            'A': results.iloc[2]['Productivity (TFP)'],
            'Y': results.iloc[2]['GDP']
        }
        
        # Continue simulation after shock
        post_shock_years = np.arange(1995, 2025, 5)
        
        post_shock_results = solve_solow_model(
            initial_year=1995,
            initial_conditions=shocked_conditions,
            parameters=params,
            years=post_shock_years
        )
        
        # Check that capital recovers (growth rate should be positive)
        initial_capital = post_shock_results.iloc[0]['Capital']
        final_capital = post_shock_results.iloc[-1]['Capital']
        
        self.assertGreater(final_capital, initial_capital,
                          "Capital should recover after a negative shock")
                          
        # Check that GDP also recovers
        initial_gdp = post_shock_results.iloc[0]['GDP']
        final_gdp = post_shock_results.iloc[-1]['GDP']
        
        self.assertGreater(final_gdp, initial_gdp,
                          "GDP should recover after a negative shock")
                          
    def test_parameter_sensitivity(self):
        """Test the sensitivity of the model to parameter changes."""
        # Small changes in parameters should lead to predictable changes in outcomes
        
        # Baseline parameters
        base_params = self.default_params.copy()
        
        # Run baseline simulation
        base_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=base_params,
            years=self.years
        )
        
        # Test sensitivity to alpha (capital share)
        alpha_change = 0.05  # 5 percentage point increase
        alpha_params = base_params.copy()
        alpha_params['alpha'] += alpha_change
        
        alpha_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=alpha_params,
            years=self.years
        )
        
        # Higher alpha should lead to higher steady-state capital and output
        self.assertGreater(alpha_results.iloc[-1]['Capital'], base_results.iloc[-1]['Capital'],
                          "Higher capital share should lead to higher steady-state capital")
        self.assertGreater(alpha_results.iloc[-1]['GDP'], base_results.iloc[-1]['GDP'],
                          "Higher capital share should lead to higher steady-state output")
                          
        # Test sensitivity to savings rate
        s_change = 0.05  # 5 percentage point increase
        s_params = base_params.copy()
        s_params['s'] += s_change
        
        s_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=s_params,
            years=self.years
        )
        
        # Higher savings rate should lead to higher steady-state capital and output
        self.assertGreater(s_results.iloc[-1]['Capital'], base_results.iloc[-1]['Capital'],
                          "Higher savings rate should lead to higher steady-state capital")
        self.assertGreater(s_results.iloc[-1]['GDP'], base_results.iloc[-1]['GDP'],
                          "Higher savings rate should lead to higher steady-state output")
                          
        # Test sensitivity to TFP growth rate
        g_change = 0.01  # 1 percentage point increase
        g_params = base_params.copy()
        g_params['g'] += g_change
        
        g_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=g_params,
            years=self.years
        )
        
        # Higher TFP growth should lead to higher final TFP and output
        self.assertGreater(g_results.iloc[-1]['Productivity (TFP)'], base_results.iloc[-1]['Productivity (TFP)'],
                          "Higher TFP growth rate should lead to higher final TFP")
        self.assertGreater(g_results.iloc[-1]['GDP'], base_results.iloc[-1]['GDP'],
                          "Higher TFP growth rate should lead to higher final output")

if __name__ == '__main__':
    unittest.main()
