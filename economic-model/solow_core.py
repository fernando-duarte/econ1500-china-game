# Shared core logic for Solow model simulation
import numpy as np
import pandas as pd

# Define base constants for NX calculation that were in solow_utils
E_1980 = 1.5  # Baseline exchange rate in 1980
Y_STAR_1980 = 1000  # Baseline foreign income in 1980

def calculate_exchange_rate(year, e_policy):
    """Calculate exchange rate based on policy and year"""
    # Round index (0-based) from year
    round_index = max(0, (year - 1980) // 5)
    # Baseline market exchange rate (linear interpolation 1.5 to 7.0 over 10 rounds, 0-9)
    # Max rounds = 10 (index 0 to 9)
    num_rounds = 10
    e_market_t = E_1980 + (7.0 - E_1980) * round_index / (num_rounds - 1)
    
    # Determine actual exchange rate based on policy
    if e_policy == 'undervalue':
        return e_market_t * 1.2
    elif e_policy == 'overvalue':
        return e_market_t * 0.8
    else:  # market
        return e_market_t

def calculate_foreign_income(year):
    """Calculate foreign income based on year (3% annual growth)"""
    round_index = max(0, (year - 1980) // 5)
    return Y_STAR_1980 * (1.03**(5 * round_index))

def initialize_simulation(initial_conditions, T):
    """Initialize arrays for Solow model simulation."""
    Y, K, L, H, A, NX = [np.zeros(T) for _ in range(6)]
    Y[0], K[0], L[0], H[0], A[0] = [initial_conditions[k] for k in ['Y', 'K', 'L', 'H', 'A']]
    NX[0] = initial_conditions.get('NX', 0)
    return Y, K, L, H, A, NX

def calculate_production(A, K, L, H, alpha):
    """Calculate production using the Cobb-Douglas function."""
    K_safe = max(0, K)
    Y = A * (K_safe**alpha) * ((L * H)**(1 - alpha))
    return max(0, Y)  # Ensure GDP is non-negative

def calculate_net_exports(Y, Y_initial, exchange_rate, exchange_rate_initial, 
                        foreign_income, foreign_income_initial, X0, M0, 
                        epsilon_x, epsilon_m, mu_x, mu_m):
    """Calculate net exports based on current state and parameters."""
    Y_safe = max(Y, 1e-6)
    Y_initial_safe = max(Y_initial, 1e-6)
    
    exports_term = X0 * (exchange_rate/exchange_rate_initial)**epsilon_x * (foreign_income/foreign_income_initial)**mu_x
    imports_term = M0 * (exchange_rate/exchange_rate_initial)**(-epsilon_m) * (Y_safe/Y_initial_safe)**mu_m
    
    return exports_term - imports_term

def calculate_capital_next(K, Y, NX, s, delta):
    """Calculate next period capital stock."""
    K_safe = max(0, K)
    I = s * Y + NX
    
    # Ensure capital doesn't go negative
    if I + (1 - delta) * K_safe < 0:
        I = -((1 - delta) * K_safe)
        
    return (1 - delta) * K_safe + I

def calculate_labor_next(L, n):
    """Calculate next period labor force."""
    return L * (1 + n)

def calculate_human_capital_next(H, eta):
    """Calculate next period human capital."""
    return H * (1 + eta)

def calculate_tfp_next(A, g, theta, openness_ratio, phi, fdi_ratio):
    """Calculate next period total factor productivity (TFP)."""
    return A * (1 + g + theta * openness_ratio + phi * fdi_ratio)

def calculate_openness_ratio(round_index):
    """Calculate openness ratio based on round index"""
    return 0.1 + 0.02 * round_index

def calculate_fdi_ratio(year):
    """Calculate FDI ratio based on year"""
    return 0.02 if year >= 1990 else 0

def get_default_parameters():
    """Return default parameters for the Solow model"""
    return {
        'alpha': 0.3, 'delta': 0.1, 'g': 0.005, 'theta': 0.1453, 'phi': 0.1,
        'n': 0.00717, 'eta': 0.02,
        'X0': 18.1, 'M0': 14.5,
        'epsilon_x': 1.5, 'epsilon_m': 1.2,
        'mu_x': 1.0, 'mu_m': 1.0,
        'Y_1980': Y_STAR_1980
    }

def simulate_solow_step(t, Y, K, L, H, A, NX, parameters, exchange_rate, foreign_income, openness_ratio, fdi_ratio):
    """Simulate a single step of the Solow model."""
    # Unpack parameters
    alpha, delta, g, theta, phi, s, n, eta = [parameters[k] for k in 
        ['alpha', 'delta', 'g', 'theta', 'phi', 's', 'n', 'eta']]
    X0, M0, epsilon_x, epsilon_m, mu_x, mu_m = [parameters[k] for k in
        ['X0', 'M0', 'epsilon_x', 'epsilon_m', 'mu_x', 'mu_m']]
    
    # Calculate production
    Y[t] = calculate_production(A[t], K[t], L[t], H[t], alpha)
    
    # Calculate net exports
    NX[t] = calculate_net_exports(
        Y[t], Y[0], exchange_rate[t], exchange_rate[0],
        foreign_income[t], foreign_income[0],
        X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
    )
    
    # Calculate next period variables
    K[t+1] = calculate_capital_next(K[t], Y[t], NX[t], s, delta)
    L[t+1] = calculate_labor_next(L[t], n)
    H[t+1] = calculate_human_capital_next(H[t], eta)
    A[t+1] = calculate_tfp_next(A[t], g, theta, openness_ratio, phi, fdi_ratio)
    
    return Y, K, L, H, A, NX

def calculate_single_round(current_state, parameters, student_inputs, year, openness_ratio, fdi_ratio):
    """
    Unified function to calculate a single round of the Solow model for game state.
    This replaces the duplicate logic in solow_model.py and is used by both single-step and multi-step simulations.
    
    Parameters:
    - current_state: dict, current values for {'Y', 'K', 'L', 'H', 'A'}.
    - parameters: dict, model parameters including Solow and NX parameters.
    - student_inputs: dict, student choices for this round {'s', 'e_policy'}.
    - year: int, current year for the round.
    - openness_ratio: float, openness ratio for the current round.
    - fdi_ratio: float, FDI ratio for the current year.
    
    Returns:
    - dict containing next round state and current round calculations.
    """
    # Unpack parameters
    alpha = parameters['alpha']
    delta = parameters['delta']
    g = parameters['g']
    theta = parameters['theta']
    phi = parameters['phi']
    X0 = parameters['X0']
    M0 = parameters['M0']
    epsilon_x = parameters['epsilon_x']
    epsilon_m = parameters['epsilon_m']
    mu_x = parameters['mu_x']
    mu_m = parameters['mu_m']
    Y_1980 = parameters.get('Y_1980', 1000)
    
    # Unpack current state
    K_t = current_state['K']
    L_t = current_state['L']
    H_t = current_state['H']
    A_t = current_state['A']
    
    # Get student inputs
    s_t = student_inputs['s']
    e_policy = student_inputs['e_policy']
    
    # Calculate exchange rate and foreign income based on policy
    e_t = calculate_exchange_rate(year, e_policy)
    Y_star_t = calculate_foreign_income(year)
    
    # Production
    Y_t = calculate_production(A_t, K_t, L_t, H_t, alpha)
    
    # Net Exports
    NX_t = calculate_net_exports(
        Y_t, Y_1980, e_t, E_1980, Y_star_t, Y_STAR_1980,
        X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
    )
    
    # Consumption
    C_t = (1 - s_t) * Y_t
    
    # Investment 
    I_t = s_t * Y_t + NX_t
    K_safe = max(0, K_t)
    # Prevent negative capital
    if I_t + (1 - delta) * K_safe < 0:
        I_t = -((1 - delta) * K_safe)
    
    # Calculate next period variables
    K_next = calculate_capital_next(K_t, Y_t, NX_t, s_t, delta)
    L_next = calculate_labor_next(L_t, parameters['n'])
    H_next = calculate_human_capital_next(H_t, parameters['eta'])
    A_next = calculate_tfp_next(A_t, g, theta, openness_ratio, phi, fdi_ratio)
    
    # Return results
    return {
        # State for the start of the next round
        'K_next': K_next,
        'L_next': L_next,
        'H_next': H_next,
        'A_next': A_next,
        # Calculated values for the current round (t)
        'Y_t': Y_t,     # GDP generated in round t
        'NX_t': NX_t,   # Net Exports in round t
        'C_t': C_t,     # Consumption in round t
        'I_t': I_t      # Investment in round t
    } 