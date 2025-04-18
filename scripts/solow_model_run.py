"""
Detailed script for Solow Model integration with classroom UI.
This script uses the consolidated core implementation in china-growth-game/economic-model/solow_core.py.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add the package to Python path if it's not already there
package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_path not in sys.path:
    sys.path.insert(0, package_path)

# Import from the consolidated core implementation and simulation wrapper
from china_growth_game.economic_model.core.solow_core import get_default_parameters
from china_growth_game.economic_model.core.solow_simulation import run_simulation

# Explicit Game Instructions and Prize Announcements
print("Welcome to China's Growth Game: Saving, Trade, and Prosperity (1980–2025)!")
print("Form groups of 8 and select one 'Leader Device' per group.")

print("\nPrizes:")
print("- Highest GDP Growth")
print("- Highest Net Exports")
print("- Best Balanced Economy (GDP and Consumption)")

# Define simulation years
years = np.arange(1980, 2026, 5)

# Initial conditions explicitly defined
initial_conditions = {
    'Y': 306.2,
    'K': 800,
    'L': 600,
    'H': 1.0,
    'A': 1.0,
    'NX': 3.6
}

# Get default parameters and override as needed
parameters = get_default_parameters()
parameters['s'] = 0.2  # Default savings rate

# Solve the model explicitly using the simulation wrapper
results_df = run_simulation(initial_conditions, parameters, years)

# Prepare clear outputs for UI integration
print("\nNumbers displayed on Student Screens and Professor Dashboard:")
for i, year in enumerate(years):
    print(f"\nYear: {year}")
    print(f"GDP: {results_df['GDP'].iloc[i]:.2f} bn USD")
    print(f"Capital Stock: {results_df['Capital'].iloc[i]:.2f} bn USD")
    print(f"Labor Force: {results_df['Labor Force'].iloc[i]:.2f} million")
    print(f"Human Capital: {results_df['Human Capital'].iloc[i]:.2f}")
    print(f"Productivity (TFP): {results_df['Productivity (TFP)'].iloc[i]:.2f}")
    print(f"Net Exports: {results_df['Net Exports'].iloc[i]:.2f} bn USD")

# Explicit Inputs for Each Round
print("\nExplicit Inputs Entered by Students Each Round:")
print("- Savings Rate (%)")
print("- Exchange Rate Policy (Undervalue/Market/Overvalue)")

# Explicit Prize Calculation Logic
final_year_index = -1  # index for 2025

# Calculate prizes explicitly
highest_gdp_group = results_df['GDP'].iloc[final_year_index]
highest_nx_group = results_df['Net Exports'].iloc[final_year_index]
best_balanced_score = results_df['GDP'].iloc[final_year_index] + results_df['Capital'].iloc[final_year_index]

print("\nPrize Winners Determination:")
print(f"- Highest GDP Growth Winner GDP: {highest_gdp_group:.2f} bn USD")
print(f"- Highest Net Exports Winner NX: {highest_nx_group:.2f} bn USD")
print(f"- Best Balanced Economy Winner Score: {best_balanced_score:.2f}")
