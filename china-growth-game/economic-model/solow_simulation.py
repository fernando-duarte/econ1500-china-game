# solow_simulation.py: Full simulation of the Solow Model

import numpy as np
import pandas as pd
from solow_utils import (
    calculate_exchange_rate,
    calculate_foreign_income,
    calculate_openness_ratio,
    calculate_fdi_ratio
)
from solow_core import (
    initialize_simulation, 
    simulate_solow_step,
    calculate_production,
    calculate_net_exports,
    E_1980, Y_STAR_1980
)

def solve_solow_model(initial_year, initial_conditions, parameters, years, historical_data=None):
    """
    Solves the augmented open-economy Solow model from the initial year to the present.
    NOTE: This function runs a full simulation and may not be suitable for the interactive game loop.
    Use calculate_next_round for single-step updates.

    Parameters:
    - initial_year: int, starting year for simulation.
    - initial_conditions: dict, initial values for Y, K, L, H, A.
    - parameters: dict, model parameters including Solow params (alpha, delta, g, theta, phi, n, eta)
                       NX params (X0, M0, epsilon_x, epsilon_m, mu_x, mu_m, Y_1980)
                       and a fixed savings rate 's'.
    - years: numpy array, array of years to simulate.
    - historical_data: dict, optional historical data for comparison.

    Returns:
    - DataFrame containing simulated values.
    """
    # Unpack Solow parameters (only needed for params validation and final year)
    alpha = parameters['alpha']
    s = parameters['s']
    Y_1980 = parameters.get('Y_1980', initial_conditions['Y'])
    
    # Prepare simulation
    T = len(years)
    
    # Initialize arrays
    Y, K, L, H, A, NX = initialize_simulation(initial_conditions, T)
    C = np.zeros(T)
    I = np.zeros(T)
    
    # Store exchange rates and foreign income for consistent calculations
    exchange_rates = [calculate_exchange_rate(years[t], 'market') for t in range(T)]
    foreign_incomes = [calculate_foreign_income(years[t]) for t in range(T)]
    
    # Simulation loop
    for t in range(T-1):
        year = years[t]
        openness_ratio = calculate_openness_ratio(t)
        fdi_ratio = calculate_fdi_ratio(year)
        
        # Run simulation step
        Y, K, L, H, A, NX = simulate_solow_step(
            t, Y, K, L, H, A, NX, parameters, 
            exchange_rates, foreign_incomes, 
            openness_ratio, fdi_ratio
        )
        
        # Calculate consumption and investment
        C[t] = (1 - s) * Y[t]
        I[t] = s * Y[t] + NX[t]
    
    # Final year calculations (t = T-1)
    t = T - 1
    year = years[t]
    
    # Calculate production for the final year
    Y[t] = calculate_production(A[t], K[t], L[t], H[t], alpha)
    
    # Calculate net exports for the final year
    NX[t] = calculate_net_exports(
        Y[t], Y[0], exchange_rates[t], exchange_rates[0],
        foreign_incomes[t], foreign_incomes[0],
        parameters['X0'], parameters['M0'], 
        parameters['epsilon_x'], parameters['epsilon_m'],
        parameters['mu_x'], parameters['mu_m']
    )
    
    # Final consumption and investment
    C[t] = (1 - s) * Y[t]
    I[t] = s * Y[t] + NX[t]
    
    # Create DataFrame
    results_df = pd.DataFrame({
        'Year': years,
        'GDP': Y,
        'Capital': K,
        'Labor Force': L,
        'Human Capital': H,
        'Productivity (TFP)': A,
        'Net Exports': NX,
        'Consumption': C,
        'Investment': I
    })
    
    return results_df 