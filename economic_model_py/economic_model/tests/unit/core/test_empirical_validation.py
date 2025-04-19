"""
Empirical validation tests for the Solow growth model.

This module contains tests to validate the economic model against
empirical data and stylized facts from economic growth literature.
"""

import unittest
import numpy as np
import pandas as pd
import math
from typing import Dict, Any

from economic_model_py.economic_model.core.solow_core import (
    get_default_parameters,
    solve_solow_model
)

class TestEmpiricalValidation(unittest.TestCase):
    """Validation tests comparing model predictions with empirical data."""

    def setUp(self):
        """Set up the test environment."""
        self.default_params = get_default_parameters()
        
        # Standard initial conditions for China circa 1980
        self.initial_conditions = {
            'K': 1000.0,  # Initial capital stock
            'L': 100.0,   # Initial labor force (100 million)
            'H': 1.0,     # Initial human capital
            'A': 1.0,     # Initial TFP
            'Y': 100.0    # Initial GDP
        }
        
        # Years for simulation
        self.years = np.arange(1980, 2021, 5)  # Up to 2020 for comparison with historical data
        
        # Stylized facts about China's growth
        self.china_facts = {
            'avg_gdp_growth': 0.09,  # Average annual GDP growth rate (9%)
            'investment_share': 0.40,  # Investment share of GDP (40%)
            'capital_output_ratio': 2.5,  # Capital-output ratio
            'tfp_contribution': 0.30,  # TFP contribution to growth (30%)
        }
        
    def test_china_growth_pattern(self):
        """Test that the model can reproduce China's growth pattern."""
        # Calibrate parameters to match China's growth experience
        china_params = self.default_params.copy()
        china_params.update({
            'alpha': 0.5,    # Higher capital share for China
            's': 0.40,       # High savings/investment rate
            'g': 0.03,       # Base TFP growth
            'theta': 0.02,   # Strong effect of openness
            'phi': 0.01,     # Effect of FDI
            'n': 0.01,       # Labor force growth
            'eta': 0.02,     # Human capital growth
            'delta': 0.05    # Depreciation rate
        })
        
        # Run simulation
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=china_params,
            years=self.years
        )
        
        # Calculate average annual GDP growth rate
        initial_gdp = results.iloc[0]['GDP']
        final_gdp = results.iloc[-1]['GDP']
        years_elapsed = self.years[-1] - self.years[0]
        
        avg_annual_growth = (final_gdp / initial_gdp) ** (1 / years_elapsed) - 1
        
        # Check if growth rate is close to China's historical average
        self.assertAlmostEqual(avg_annual_growth, self.china_facts['avg_gdp_growth'], delta=0.02,
                              msg=f"Model growth rate ({avg_annual_growth}) differs from China's historical rate ({self.china_facts['avg_gdp_growth']})")
        
        # Calculate average investment share
        investment_shares = results['Investment'] / results['GDP']
        avg_investment_share = investment_shares.mean()
        
        # Check if investment share is close to China's historical average
        self.assertAlmostEqual(avg_investment_share, self.china_facts['investment_share'], delta=0.1,
                              msg=f"Model investment share ({avg_investment_share}) differs from China's historical share ({self.china_facts['investment_share']})")
        
        # Calculate final capital-output ratio
        final_k_y = results.iloc[-1]['Capital'] / results.iloc[-1]['GDP']
        
        # Check if capital-output ratio is reasonable
        self.assertAlmostEqual(final_k_y, self.china_facts['capital_output_ratio'], delta=1.0,
                              msg=f"Model capital-output ratio ({final_k_y}) differs significantly from China's ratio ({self.china_facts['capital_output_ratio']})")
                              
    def test_growth_accounting(self):
        """Test that the model's growth accounting is consistent with empirical findings."""
        # Run simulation with calibrated parameters
        china_params = self.default_params.copy()
        china_params.update({
            'alpha': 0.5,    # Higher capital share for China
            's': 0.40,       # High savings/investment rate
            'g': 0.03,       # Base TFP growth
            'theta': 0.02,   # Strong effect of openness
            'phi': 0.01,     # Effect of FDI
            'n': 0.01,       # Labor force growth
            'eta': 0.02,     # Human capital growth
            'delta': 0.05    # Depreciation rate
        })
        
        results = solve_solow_model(
            initial_year=1980,
            initial_conditions=self.initial_conditions,
            parameters=china_params,
            years=self.years
        )
        
        # Perform growth accounting
        # Calculate contributions of capital, labor, human capital, and TFP to growth
        alpha = china_params['alpha']
        
        # Calculate growth rates
        gdp_growth = []
        k_contribution = []
        l_contribution = []
        h_contribution = []
        tfp_contribution = []
        
        for i in range(1, len(results)):
            # Growth rates
            y_growth = results.iloc[i]['GDP'] / results.iloc[i-1]['GDP'] - 1
            k_growth = results.iloc[i]['Capital'] / results.iloc[i-1]['Capital'] - 1
            l_growth = results.iloc[i]['Labor Force'] / results.iloc[i-1]['Labor Force'] - 1
            h_growth = results.iloc[i]['Human Capital'] / results.iloc[i-1]['Human Capital'] - 1
            a_growth = results.iloc[i]['Productivity (TFP)'] / results.iloc[i-1]['Productivity (TFP)'] - 1
            
            gdp_growth.append(y_growth)
            
            # Contributions to growth
            k_contrib = alpha * k_growth / y_growth
            l_contrib = (1 - alpha) * l_growth / y_growth
            h_contrib = (1 - alpha) * h_growth / y_growth
            tfp_contrib = a_growth / y_growth
            
            k_contribution.append(k_contrib)
            l_contribution.append(l_contrib)
            h_contribution.append(h_contrib)
            tfp_contribution.append(tfp_contrib)
            
        # Average contributions
        avg_k_contrib = np.mean(k_contribution)
        avg_l_contrib = np.mean(l_contribution)
        avg_h_contrib = np.mean(h_contribution)
        avg_tfp_contrib = np.mean(tfp_contribution)
        
        # Check if TFP contribution is close to empirical estimates
        self.assertAlmostEqual(avg_tfp_contrib, self.china_facts['tfp_contribution'], delta=0.15,
                              msg=f"Model TFP contribution ({avg_tfp_contrib}) differs from empirical estimates ({self.china_facts['tfp_contribution']})")
                              
        # Check that contributions sum to approximately 1
        total_contrib = avg_k_contrib + avg_l_contrib + avg_h_contrib + avg_tfp_contrib
        self.assertAlmostEqual(total_contrib, 1.0, delta=0.1,
                              msg=f"Growth accounting contributions ({total_contrib}) do not sum to 1")
                              
    def test_convergence_hypothesis(self):
        """Test that the model exhibits conditional convergence."""
        # Create two economies with different initial conditions but same parameters
        # They should converge to the same growth rate
        
        # Rich economy initial conditions
        rich_conditions = self.initial_conditions.copy()
        rich_conditions['K'] = 5000.0  # 5x more capital
        rich_conditions['Y'] = 500.0   # 5x more output
        
        # Poor economy initial conditions
        poor_conditions = self.initial_conditions.copy()
        
        # Common parameters
        params = self.default_params.copy()
        params.update({
            'g': 0.02,  # TFP growth
            'n': 0.01,  # Labor force growth
            'eta': 0.01,  # Human capital growth
            's': 0.3,
            'delta': 0.05
        })
        
        # Run simulations
        rich_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=rich_conditions,
            parameters=params,
            years=self.years
        )
        
        poor_results = solve_solow_model(
            initial_year=1980,
            initial_conditions=poor_conditions,
            parameters=params,
            years=self.years
        )
        
        # Calculate growth rates for each period
        rich_growth = []
        poor_growth = []
        
        for i in range(1, len(rich_results)):
            rich_growth.append(rich_results.iloc[i]['GDP'] / rich_results.iloc[i-1]['GDP'] - 1)
            poor_growth.append(poor_results.iloc[i]['GDP'] / poor_results.iloc[i-1]['GDP'] - 1)
            
        # Poor economy should grow faster initially
        self.assertGreater(poor_growth[0], rich_growth[0],
                          "Poor economy should grow faster initially (convergence)")
                          
        # Growth rates should converge over time
        rich_final_growth = rich_growth[-1]
        poor_final_growth = poor_growth[-1]
        
        self.assertAlmostEqual(rich_final_growth, poor_final_growth, delta=0.01,
                              msg=f"Growth rates should converge over time, but got {rich_final_growth} vs {poor_final_growth}")
                              
        # Calculate income gap reduction
        initial_gap = rich_results.iloc[0]['GDP'] / poor_results.iloc[0]['GDP']
        final_gap = rich_results.iloc[-1]['GDP'] / poor_results.iloc[-1]['GDP']
        
        self.assertLess(final_gap, initial_gap,
                       "Income gap should decrease over time (convergence)")
                       
    def test_investment_growth_correlation(self):
        """Test that the model reproduces the empirical correlation between investment and growth."""
        # Run simulations with different investment rates
        investment_rates = [0.1, 0.2, 0.3, 0.4, 0.5]
        growth_rates = []
        
        for s in investment_rates:
            params = self.default_params.copy()
            params['s'] = s
            
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )
            
            # Calculate average annual growth rate
            initial_gdp = results.iloc[0]['GDP']
            final_gdp = results.iloc[-1]['GDP']
            years_elapsed = self.years[-1] - self.years[0]
            
            avg_growth = (final_gdp / initial_gdp) ** (1 / years_elapsed) - 1
            growth_rates.append(avg_growth)
            
        # Calculate correlation between investment rates and growth rates
        correlation = np.corrcoef(investment_rates, growth_rates)[0, 1]
        
        # Check that correlation is positive and strong
        self.assertGreater(correlation, 0.7,
                          f"Investment-growth correlation ({correlation}) should be strongly positive")
                          
    def test_diminishing_returns(self):
        """Test that the model exhibits diminishing returns to capital."""
        # Run simulations with different initial capital stocks
        capital_levels = [500.0, 1000.0, 2000.0, 4000.0, 8000.0]
        marginal_products = []
        
        for K in capital_levels:
            # Create initial conditions with different capital
            conditions = self.initial_conditions.copy()
            conditions['K'] = K
            
            # Import the production function
            from economic_model_py.economic_model.core.solow_core import calculate_production
            
            # Calculate output
            Y = calculate_production(
                A=conditions['A'],
                K=conditions['K'],
                L=conditions['L'],
                H=conditions['H'],
                alpha=self.default_params['alpha']
            )
            
            # Calculate marginal product of capital (MPK)
            # For Cobb-Douglas: MPK = alpha * Y / K
            mpk = self.default_params['alpha'] * Y / K
            marginal_products.append(mpk)
            
        # Check that MPK decreases as K increases
        for i in range(1, len(marginal_products)):
            self.assertLess(marginal_products[i], marginal_products[i-1],
                           f"MPK should decrease as K increases, but got {marginal_products[i]} > {marginal_products[i-1]}")
                           
        # Check that the relationship follows the expected power law
        # MPK = alpha * A * (K/L)^(alpha-1) = alpha * A * K^(alpha-1) * L^(1-alpha)
        # So log(MPK) = log(alpha*A*L^(1-alpha)) + (alpha-1)*log(K)
        # The slope should be approximately (alpha-1)
        
        log_K = np.log(capital_levels)
        log_MPK = np.log(marginal_products)
        
        # Fit a line to log(MPK) vs log(K)
        from scipy import stats
        slope, _, _, _, _ = stats.linregress(log_K, log_MPK)
        
        # Expected slope: alpha - 1
        expected_slope = self.default_params['alpha'] - 1
        
        self.assertAlmostEqual(slope, expected_slope, delta=0.05,
                              msg=f"Slope of log(MPK) vs log(K) ({slope}) differs from expected ({expected_slope})")
                              
    def test_trade_openness_effects(self):
        """Test that the model reproduces the empirical effects of trade openness on growth."""
        # Run simulations with different openness effects
        openness_effects = [0.0, 0.01, 0.02, 0.03, 0.04]
        growth_rates = []
        
        for theta in openness_effects:
            params = self.default_params.copy()
            params['theta'] = theta
            
            results = solve_solow_model(
                initial_year=1980,
                initial_conditions=self.initial_conditions,
                parameters=params,
                years=self.years
            )
            
            # Calculate average annual growth rate
            initial_gdp = results.iloc[0]['GDP']
            final_gdp = results.iloc[-1]['GDP']
            years_elapsed = self.years[-1] - self.years[0]
            
            avg_growth = (final_gdp / initial_gdp) ** (1 / years_elapsed) - 1
            growth_rates.append(avg_growth)
            
        # Calculate correlation between openness effects and growth rates
        correlation = np.corrcoef(openness_effects, growth_rates)[0, 1]
        
        # Check that correlation is positive and strong
        self.assertGreater(correlation, 0.9,
                          f"Openness-growth correlation ({correlation}) should be strongly positive")
                          
        # Check that the growth premium from openness is reasonable
        # Empirical studies suggest a 1-2 percentage point growth premium for open economies
        growth_premium = growth_rates[-1] - growth_rates[0]
        
        self.assertGreater(growth_premium, 0.01,
                          f"Growth premium from openness ({growth_premium}) should be at least 1 percentage point")
        self.assertLess(growth_premium, 0.05,
                       f"Growth premium from openness ({growth_premium}) should be less than 5 percentage points")

if __name__ == '__main__':
    unittest.main()
