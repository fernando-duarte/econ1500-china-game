# solow_model.py: Generalized solver for the augmented open-economy Solow Model

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generalized Solow Model Solver Function
def solve_solow_model(initial_year, initial_conditions, parameters, years, historical_data):
    """
    Solves the augmented open-economy Solow model from the initial year to the present.

    Parameters:
    - initial_year: int, starting year for simulation.
    - initial_conditions: dict, initial values for Y, K, L, H, A, NX.
    - parameters: dict, model parameters (alpha, delta, g, theta, phi, s, beta, n, eta).
    - years: numpy array, array of years to simulate.
    - historical_data: dict, contains historical series for GDP, Labor Force, Net Exports.

    Returns:
    - DataFrame containing simulated values.
    """
    # Unpack parameters
    alpha, delta, g, theta, phi, s, beta, n, eta = [parameters[k] for k in ['alpha', 'delta', 'g', 'theta', 'phi', 's', 'beta', 'n', 'eta']]

    T = len(years)

    # Initialize arrays
    Y, K, L, H, A, NX = [np.zeros(T) for _ in range(6)]

    # Set initial conditions
    Y[0] = initial_conditions['Y']
    K[0] = initial_conditions['K']
    L[0] = initial_conditions['L']
    H[0] = initial_conditions['H']
    A[0] = initial_conditions['A']
    NX[0] = initial_conditions['NX']

    # Simplified dynamics for openness and exchange rate
    exchange_rate = np.linspace(1.5, 7.0, T)
    foreign_income = 1000 * (1.03 ** np.arange(T))

    # Initial exports/imports
    X0, M0 = 18.1, 14.5

    # Elasticities
    epsilon_x, epsilon_m = 1.5, 1.2
    mu_x, mu_m = 1.0, 1.0

    # Simulation loop
    for t in range(T-1):
        # Compute Net Exports realistically
        exports = X0 * (exchange_rate[t]/exchange_rate[0])**epsilon_x * (foreign_income[t]/foreign_income[0])**mu_x
        imports = M0 * (exchange_rate[t]/exchange_rate[0])**(-epsilon_m) * (Y[t]/Y[0])**mu_m
        NX[t] = exports - imports

        # Production
        Y[t] = A[t] * K[t]**alpha * (L[t]*H[t])**(1-alpha)

        # Investment
        I = s * Y[t] + NX[t]

        # Capital accumulation
        K[t+1] = (1 - delta)*K[t] + I

        # Labor force and human capital updates
        L[t+1] = L[t] * (1 + n)
        H[t+1] = H[t] * (1 + eta)

        # Productivity update
        openness_ratio = (exports + imports)/Y[t]
        fdi_ratio = 0.02 if years[t] >= 1990 else 0
        A[t+1] = A[t] * (1 + g + theta*openness_ratio + phi*fdi_ratio)

    # Final year GDP
    Y[-1] = A[-1] * K[-1]**alpha * (L[-1]*H[-1])**(1-alpha)

    # Create DataFrame
    results_df = pd.DataFrame({
        'Year': years,
        'GDP': Y,
        'Capital': K,
        'Labor Force': L,
        'Human Capital': H,
        'Productivity (TFP)': A,
        'Net Exports': NX
    })

    # Plot comparisons with historical data
    for var in ['GDP', 'Labor Force', 'Net Exports']:
        plt.figure(figsize=(10,5))
        plt.plot(years, results_df[var], label=f'Model {var}', marker='o')
        if var in historical_data:
            hist_years = historical_data[var]['years']
            hist_values = historical_data[var]['values']
            plt.scatter(hist_years, hist_values, color='red', label=f'Actual {var}')
        plt.title(f'{var}: Model vs Actual')
        plt.xlabel('Year')
        plt.ylabel(var)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return results_df
