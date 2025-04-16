# solow_simulation.py: Full simulation of the Solow Model

import numpy as np
import pandas as pd
from solow_utils import E_1980, Y_STAR_1980

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
    # Unpack Solow parameters
    alpha, delta, g, theta, phi, n, eta, s = [parameters[k] for k in ['alpha', 'delta', 'g', 'theta', 'phi', 'n', 'eta', 's']]
    # Unpack NX parameters
    X0, M0, epsilon_x, epsilon_m, mu_x, mu_m, Y_1980 = [parameters[k] for k in ['X0', 'M0', 'epsilon_x', 'epsilon_m', 'mu_x', 'mu_m', 'Y_1980']]

    T = len(years)

    # Initialize arrays
    Y, K, L, H, A, NX = [np.zeros(T) for _ in range(6)]
    C, I = [np.zeros(T) for _ in range(2)]  # Added Consumption and Investment tracking

    # Set initial conditions
    Y[0] = initial_conditions['Y']
    K[0] = initial_conditions['K']
    L[0] = initial_conditions['L']
    H[0] = initial_conditions['H']
    A[0] = initial_conditions['A']
    # NX[0] calculated below for t=0

    # Simulation loop
    for t in range(T-1):  # Calculate state for t+1 based on t
        # Calculate time-dependent variables for NX
        round_index = t  # 0-based index for the period
        e_market_t = E_1980 + (7.0 - E_1980) * round_index / (T - 1)  # Linear interpolation for market rate
        Y_star_t = Y_STAR_1980 * (1.03**(5 * round_index))
        # Assume 'market' policy for the full simulation run
        e_t = e_market_t

        # Production (Calculate Y[t] needed for NX[t])
        K_t_safe = max(0, K[t])
        Y[t] = A[t] * (K_t_safe**alpha) * ((L[t]*H[t])**(1-alpha))
        Y[t] = max(0, Y[t])

        # Compute Net Exports using the new formula
        # Ensure Y[t] and Y_1980 are non-zero before division
        Y_t_safe = max(Y[t], 1e-6)  # Avoid division by zero
        Y_1980_safe = max(Y_1980, 1e-6)

        exports_term = X0 * (e_t / E_1980)**epsilon_x * (Y_star_t / Y_STAR_1980)**mu_x
        imports_term = M0 * (e_t / E_1980)**(-epsilon_m) * (Y_t_safe / Y_1980_safe)**mu_m
        NX[t] = exports_term - imports_term

        # Consumption and Investment
        C[t] = (1 - s) * Y[t]
        I[t] = s * Y[t] + NX[t]
        if I[t] + (1-delta)*K[t] < 0: I[t] = -(1-delta)*K[t]  # Prevent negative capital next period

        # Capital accumulation
        K[t+1] = (1 - delta)*K_t_safe + I[t]

        # Labor force and human capital updates
        L[t+1] = L[t] * (1 + n)
        H[t+1] = H[t] * (1 + eta)

        # Productivity update - Use exogenous openness_ratio
        openness_ratio = 0.1 + 0.02 * t
        fdi_ratio = 0.02 if years[t] >= 1990 else 0
        A[t+1] = A[t] * (1 + g + theta*openness_ratio + phi*fdi_ratio)

    # Final year calculations (t = T-1)
    t = T - 1
    round_index = t
    e_market_t = E_1980 + (7.0 - E_1980) * round_index / (T - 1)
    Y_star_t = Y_STAR_1980 * (1.03**(5 * round_index))
    e_t = e_market_t

    K_t_safe = max(0, K[t])
    Y[t] = A[t] * K_t_safe**alpha * (L[t]*H[t])**(1-alpha)
    Y[t] = max(0, Y[t])

    Y_t_safe = max(Y[t], 1e-6)
    Y_1980_safe = max(Y_1980, 1e-6)
    exports_term = X0 * (e_t / E_1980)**epsilon_x * (Y_star_t / Y_STAR_1980)**mu_x
    imports_term = M0 * (e_t / E_1980)**(-epsilon_m) * (Y_t_safe / Y_1980_safe)**mu_m
    NX[t] = exports_term - imports_term

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