"""
Full simulation module for the Solow growth model.
This is a wrapper around the core implementation in solow_core.py for multi-period simulations.
"""

import numpy as np
import pandas as pd
from solow_core import solve_solow_model

# Simple example if run directly
if __name__ == '__main__':
    from solow_core import get_default_parameters
    
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
    results_df = solve_solow_model(1980, initial_conditions, parameters, years)
    
    # Display results
    print("Simulation Results:")
    print(results_df[['Year', 'GDP', 'Capital', 'Labor Force', 'Human Capital', 'Net Exports']]) 