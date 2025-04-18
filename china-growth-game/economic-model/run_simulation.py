"""
Simple runner script to demonstrate the refactored Solow model.
This shows how to use the solow_simulation.py wrapper to run simulations.
"""

import numpy as np
import pandas as pd
from constants import DEFAULT_INITIAL_CONDITIONS, DEFAULT_PARAMS
from solow_simulation import run_simulation

def main():
    """Run a simple simulation and print the results."""
    print("Running Solow model simulation...")
    
    # Use default parameters but override the savings rate
    parameters = DEFAULT_PARAMS.copy()
    parameters['s'] = 0.3  # Set savings rate to 30%
    
    # Use default initial conditions
    initial_conditions = DEFAULT_INITIAL_CONDITIONS.copy()
    
    # Define simulation years (1980-2025 in 5-year intervals)
    years = np.arange(1980, 2026, 5)
    
    # Run the simulation
    results_df = run_simulation(initial_conditions, parameters, years)
    
    # Display results
    print("\nSimulation Results:")
    print("\nYear\tGDP\t\tCapital\t\tNet Exports")
    print("-" * 50)
    for i, year in enumerate(years):
        print(f"{year}\t{results_df['GDP'].iloc[i]:.2f}\t\t{results_df['Capital'].iloc[i]:.2f}\t\t{results_df['Net Exports'].iloc[i]:.2f}")
    
    # Calculate the final GDP growth rate
    initial_gdp = results_df['GDP'].iloc[0]
    final_gdp = results_df['GDP'].iloc[-1]
    total_growth = (final_gdp / initial_gdp - 1) * 100
    annual_growth = ((final_gdp / initial_gdp) ** (1 / ((len(years) - 1) * 5)) - 1) * 100
    
    print(f"\nTotal GDP Growth (1980-2025): {total_growth:.2f}%")
    print(f"Average Annual Growth Rate: {annual_growth:.2f}%")

if __name__ == "__main__":
    main() 