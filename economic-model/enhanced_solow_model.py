import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

class EnhancedSolowModel:
    """
    Enhanced Solow Model for the China's Growth Game simulation.
    This model processes economic simulation in incremental rounds,
    with support for student decisions and economic events.
    """
    
    def __init__(self):
        # Model parameters from specs.md
        self.default_parameters = {
            'alpha': 0.3,       # Capital share in production function
            'delta': 0.1,       # Capital depreciation rate
            'g': 0.005,         # Base TFP growth rate
            'theta': 0.1453,    # TFP contribution from openness
            'phi': 0.1,         # TFP contribution from FDI
            'beta': -90,        # Interest rate sensitivity parameter
            'n': 0.00717,       # Labor force growth rate
            'eta': 0.02         # Human capital growth rate
        }
        
        # Initial elasticities
        self.epsilon_x = 1.5    # Export price elasticity
        self.epsilon_m = 1.2    # Import price elasticity
        self.mu_x = 1.0         # Export income elasticity
        self.mu_m = 1.0         # Import income elasticity
        
        # Initial export/import values
        self.X0 = 18.1          # Initial exports
        self.M0 = 14.5          # Initial imports
        
        # Baseline exchange rate sequence (can be modified by policies)
        self.base_exchange_rate = np.linspace(1.5, 7.0, 10)  # For 10 periods (1980-2025)
        
        # Foreign income growth (3% per year)
        self.foreign_income_growth = 0.03
    
    def simulate_round(
        self,
        current_state: Dict[str, float],
        decision: Dict[str, Any],
        events: List[Dict[str, Any]],
        period_index: int
    ) -> Dict[str, float]:
        """
        Simulate a single 5-year round of economic development based on 
        current state, student decisions, and economic events.
        
        Parameters:
        - current_state: Current economic state (Y, K, L, H, A, NX, C)
        - decision: Student decisions for savings rate and exchange rate policy
        - events: List of economic events triggering in this round
        - period_index: Index of the current period in the simulation sequence (0-9)
        
        Returns:
        - New economic state after the round
        """
        # Create a copy of the current state to modify
        new_state = current_state.copy()
        
        # Extract current state variables
        Y = current_state['Y']    # GDP
        K = current_state['K']    # Capital stock
        L = current_state['L']    # Labor force
        H = current_state['H']    # Human capital
        A = current_state['A']    # Total factor productivity
        NX = current_state['NX']  # Net exports
        
        # Get decision parameters
        savings_rate = decision.get('savings_rate', 0.2)  # Default 20% if not specified
        exchange_rate_policy = decision.get('exchange_rate_policy', 'market')  # Default market-based
        
        # Apply exchange rate policy
        exchange_rate_multiplier = self._get_exchange_rate_multiplier(exchange_rate_policy)
        exchange_rate = self.base_exchange_rate[period_index] * exchange_rate_multiplier
        
        # Calculate foreign income for this period (compound growth from initial)
        years_elapsed = period_index * 5  # Each period is 5 years
        foreign_income = 1000 * ((1 + self.foreign_income_growth) ** years_elapsed)
        
        # Process events to determine modifiers
        exports_multiplier = 1.0
        gdp_growth_delta = 0.0
        tfp_increase = 0.0
        
        for event in events:
            effects = event.get('effects', {})
            if 'exports_multiplier' in effects:
                exports_multiplier *= effects['exports_multiplier']
            if 'gdp_growth_delta' in effects:
                gdp_growth_delta += effects['gdp_growth_delta']
            if 'tfp_increase' in effects:
                tfp_increase += effects['tfp_increase']
        
        # Compute exports and imports with policy and event effects
        # Note: For undervalued currency, the actual exchange rate is lower,
        # but this makes exports cheaper in foreign markets, so exports increase.
        # For overvalued currency, exports become more expensive, so exports decrease.
        # We need to correct the sign of the elasticity to match this economic logic.
        exports_base = self.X0 * (exchange_rate/self.base_exchange_rate[0])**(-self.epsilon_x) * \
                      (foreign_income/1000)**self.mu_x
        
        imports_base = self.M0 * (exchange_rate/self.base_exchange_rate[0])**(self.epsilon_m) * \
                      (Y/current_state.get('initial_Y', 306.2))**self.mu_m
        
        # Apply event multipliers
        exports = exports_base * exports_multiplier
        imports = imports_base
        
        # Calculate net exports
        NX = exports - imports
        
        # Production function (Cobb-Douglas)
        Y = A * (K ** self.default_parameters['alpha']) * \
            ((L * H) ** (1 - self.default_parameters['alpha']))
        
        # Apply any direct GDP modifiers
        if gdp_growth_delta != 0:
            Y = Y * (1 + gdp_growth_delta)
        
        # Calculate consumption
        C = (1 - savings_rate) * Y
        
        # Calculate investment
        I = savings_rate * Y + NX
        
        # Capital accumulation
        K_new = (1 - self.default_parameters['delta']) * K + I
        
        # Labor force growth
        L_new = L * (1 + self.default_parameters['n'])
        
        # Human capital growth
        H_new = H * (1 + self.default_parameters['eta'])
        
        # Productivity update
        openness_ratio = (exports + imports) / Y
        fdi_ratio = 0.02 if period_index >= 2 else 0  # FDI starts after 1990 (period 2)
        
        A_new = A * (1 + self.default_parameters['g'] + 
                     self.default_parameters['theta'] * openness_ratio + 
                     self.default_parameters['phi'] * fdi_ratio +
                     tfp_increase)
        
        # Update the state
        new_state.update({
            'Y': Y,
            'K': K_new,
            'L': L_new,
            'H': H_new,
            'A': A_new,
            'NX': NX,
            'C': C,
            'exports': exports,
            'imports': imports
        })
        
        return new_state
    
    def _get_exchange_rate_multiplier(self, policy: str) -> float:
        """Convert exchange rate policy to a numerical multiplier."""
        if policy == "undervalue":
            return 0.8  # 20% lower
        elif policy == "overvalue":
            return 1.2  # 20% higher
        else:  # market
            return 1.0
    
    def get_visualization_data(self, team_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process team history to generate data for visualizations.
        
        Parameters:
        - team_history: List of state snapshots from a team's history
        
        Returns:
        - Formatted data for various visualizations
        """
        # Extract key metrics
        years = [state['year'] for state in team_history]
        gdp = [state['Y'] for state in team_history]
        net_exports = [state['NX'] for state in team_history]
        consumption = [state.get('C', 0) for state in team_history]
        
        # Calculate GDP growth rates
        gdp_growth = [0]  # No growth rate for first period
        for i in range(1, len(gdp)):
            # Convert 5-year growth to annual growth rate
            five_year_growth = (gdp[i] / gdp[i-1]) - 1
            annual_growth = (1 + five_year_growth) ** (1/5) - 1
            gdp_growth.append(annual_growth * 100)  # Convert to percentage
        
        # Calculate savings
        savings = [state['Y'] - state.get('C', 0) for state in team_history]
        
        # Prepare visualization data
        visualizations = {
            'gdp_growth': {
                'labels': years,
                'data': gdp_growth,
                'title': 'GDP Growth Rate (%)',
                'type': 'line'
            },
            'trade_balance': {
                'labels': years,
                'data': net_exports,
                'title': 'Trade Balance (bn USD)',
                'type': 'bar'
            },
            'consumption_vs_savings': {
                'labels': ['Consumption', 'Savings'],
                'data': [consumption[-1], savings[-1]],  # Latest values
                'title': 'Consumption vs Savings (bn USD)',
                'type': 'pie'
            }
        }
        
        return visualizations 