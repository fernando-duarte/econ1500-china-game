"""
Full simulation module for the Solow growth model.
This is a wrapper around the core implementation in solow_core.py for multi-period simulations.
"""

import numpy as np
import pandas as pd
from solow_core import solve_solow_model, get_default_parameters

def run_simulation(initial_conditions, parameters, years=None):
    """
    Run a full Solow model simulation with the given parameters.
    
    Args:
        initial_conditions: Initial values for Y, K, L, H, A.
        parameters: Model parameters.
        years: Optional array of years to simulate. Defaults to 1980-2025 in 5-year intervals.
        
    Returns:
        DataFrame containing simulated values for all periods.
    """
    # Use default years if not provided
    if years is None:
        years = np.arange(1980, 2026, 5)
    
    # Run the simulation using the core implementation
    return solve_solow_model(
        initial_year=years[0],
        initial_conditions=initial_conditions,
        parameters=parameters,
        years=years
    )

# Simple example if run directly
if __name__ == '__main__':
    # Define simulation years
    years = np.arange(1980, 2026, 5)
    
    # Get default parameters
    parameters = get_default_parameters()
    parameters['s'] = 0.3  # Set savings rate
    
    # Initial conditions
    initial_conditions = {
        'Y': 306.2,
        'K': 800,
        'L': 600,
        'H': 1.0,
        'A': 1.0,
        'NX': 3.6
    }
    
    # Solve the model
    results_df = run_simulation(initial_conditions, parameters, years)
    
    # Display results
    print("Simulation Results:")
    print(results_df[['Year', 'GDP', 'Capital', 'Labor Force', 'Human Capital', 'Net Exports']]) 