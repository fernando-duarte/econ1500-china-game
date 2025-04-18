#!/usr/bin/env python

import numpy as np
import pandas as pd
from solow_core import solve_solow_model, get_default_parameters

def test_simulation_consistency():
    """Test that the refactored simulation produces the same results."""
    # Get default parameters
    params = get_default_parameters()
    # Add savings rate parameter needed for full simulation
    params['s'] = 0.2
    
    # Initial conditions
    initial_conditions = {
        'Y': 306.2,
        'K': 800,
        'L': 600,
        'H': 1.0,
        'A': 1.0
    }
    
    # Years to simulate
    years = np.arange(1980, 2026, 5)
    
    # Run simulation
    results = solve_solow_model(1980, initial_conditions, params, years)
    
    # Print values for key metrics
    print("Simulation Results:")
    print(f"GDP 2025: {results['GDP'].iloc[-1]:.2f}")
    print(f"Capital 2025: {results['Capital'].iloc[-1]:.2f}")
    print(f"Net Exports 2025: {results['Net Exports'].iloc[-1]:.2f}")
    
    # Calculate average growth rate
    initial_gdp = results['GDP'].iloc[0]
    final_gdp = results['GDP'].iloc[-1]
    years_elapsed = years[-1] - years[0]
    avg_growth = ((final_gdp / initial_gdp) ** (1 / years_elapsed) - 1) * 100
    print(f"Average annual GDP growth (%): {avg_growth:.2f}")
    
    return results

if __name__ == "__main__":
    test_simulation_consistency() 