"""
Consolidated core implementation of the Solow growth model.
This is the definitive source for all economic calculations in the game.
"""
import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define base constants for NX calculation
E_1980 = 1.5  # Baseline exchange rate in 1980
Y_STAR_1980 = 1000  # Baseline foreign income in 1980

# Default parameters - centralized definition
DEFAULT_PARAMS = {
    'alpha': 0.3,           # Capital share in production
    'delta': 0.1,           # Depreciation rate
    'g': 0.005,             # Base productivity growth
    'theta': 0.1453,        # Effect of openness on productivity
    'phi': 0.1,             # Effect of FDI on productivity
    'n': 0.00717,           # Labor force growth rate
    'eta': 0.02,            # Human capital growth rate
    'X0': 18.1,             # Initial exports
    'M0': 14.5,             # Initial imports
    'epsilon_x': 1.5,       # Exchange rate elasticity of exports
    'epsilon_m': 1.2,       # Exchange rate elasticity of imports
    'mu_x': 1.0,            # Foreign income elasticity of exports
    'mu_m': 1.0,            # Domestic income elasticity of imports
    'Y_1980': Y_STAR_1980   # Initial foreign income
}

# Core production function calculations
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

# Environmental and policy calculations
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

def calculate_openness_ratio(round_index):
    """Calculate openness ratio based on round index"""
    return 0.1 + 0.02 * round_index

def calculate_fdi_ratio(year):
    """Calculate FDI ratio based on year"""
    return 0.02 if year >= 1990 else 0

# Utility functions for simulation
def initialize_simulation(initial_conditions, T):
    """Initialize arrays for Solow model simulation."""
    Y, K, L, H, A, NX = [np.zeros(T) for _ in range(6)]
    Y[0], K[0], L[0], H[0], A[0] = [initial_conditions[k] for k in ['Y', 'K', 'L', 'H', 'A']]
    NX[0] = initial_conditions.get('NX', 0)
    return Y, K, L, H, A, NX

def get_default_parameters():
    """Return default parameters for the Solow model"""
    return DEFAULT_PARAMS.copy()

# Main calculation functions
def calculate_single_round(current_state, parameters, student_inputs, year):
    """
    Unified function to calculate a single round of the Solow model for game state.
    This is the main entry point for single-step calculations in the game.
    
    Parameters:
    - current_state: dict, current values for {'Y', 'K', 'L', 'H', 'A'}.
    - parameters: dict, model parameters including Solow and NX parameters.
    - student_inputs: dict, student choices for this round {'s', 'e_policy'}.
    - year: int, current year for the round.
    
    Returns:
    - dict containing next round state and current round calculations.
    """
    # Get openness and FDI ratios for current round
    round_index = max(0, (year - 1980) // 5)
    openness_ratio = calculate_openness_ratio(round_index)
    fdi_ratio = calculate_fdi_ratio(year)
    
    # Unpack parameters (with defaults as fallback)
    params = get_default_parameters()
    params.update(parameters)  # Override defaults with provided parameters
    
    alpha = params['alpha']
    delta = params['delta']
    g = params['g']
    theta = params['theta']
    phi = params['phi']
    X0 = params['X0']
    M0 = params['M0']
    epsilon_x = params['epsilon_x']
    epsilon_m = params['epsilon_m']
    mu_x = params['mu_x']
    mu_m = params['mu_m']
    Y_1980 = params.get('Y_1980', 1000)
    
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
    L_next = calculate_labor_next(L_t, params['n'])
    H_next = calculate_human_capital_next(H_t, params['eta'])
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

def simulate_solow_step(t, Y, K, L, H, A, NX, parameters, exchange_rates, foreign_incomes, openness_ratio, fdi_ratio):
    """Simulate a single step of the Solow model for multi-step simulations."""
    # Unpack parameters
    params = get_default_parameters()
    params.update(parameters)  # Override defaults with provided parameters
    
    alpha, delta, g, theta, phi, s, n, eta = [params[k] for k in 
        ['alpha', 'delta', 'g', 'theta', 'phi', 's', 'n', 'eta']]
    X0, M0, epsilon_x, epsilon_m, mu_x, mu_m = [params[k] for k in
        ['X0', 'M0', 'epsilon_x', 'epsilon_m', 'mu_x', 'mu_m']]
    
    # Calculate production
    Y[t] = calculate_production(A[t], K[t], L[t], H[t], alpha)
    
    # Calculate net exports
    NX[t] = calculate_net_exports(
        Y[t], Y[0], exchange_rates[t], exchange_rates[0],
        foreign_incomes[t], foreign_incomes[0],
        X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
    )
    
    # Calculate next period variables
    K[t+1] = calculate_capital_next(K[t], Y[t], NX[t], s, delta)
    L[t+1] = calculate_labor_next(L[t], n)
    H[t+1] = calculate_human_capital_next(H[t], eta)
    A[t+1] = calculate_tfp_next(A[t], g, theta, openness_ratio, phi, fdi_ratio)
    
    return Y, K, L, H, A, NX

def solve_solow_model(initial_year, initial_conditions, parameters, years, historical_data=None):
    """
    Solves the augmented open-economy Solow model for multiple periods.
    Used for full simulations and game initialization.
    
    Parameters:
    - initial_year: int, starting year for simulation.
    - initial_conditions: dict, initial values for Y, K, L, H, A.
    - parameters: dict, model parameters.
    - years: numpy array, array of years to simulate.
    - historical_data: dict, optional historical data for comparison.
    
    Returns:
    - DataFrame containing simulated values for all periods.
    """
    # Merge with default parameters 
    params = get_default_parameters()
    params.update(parameters)  # Override defaults with provided parameters
    
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
            t, Y, K, L, H, A, NX, params, 
            exchange_rates, foreign_incomes, 
            openness_ratio, fdi_ratio
        )
        
        # Calculate consumption and investment
        C[t] = (1 - params['s']) * Y[t]
        I[t] = params['s'] * Y[t] + NX[t]
    
    # Final year calculations (t = T-1)
    t = T - 1
    year = years[t]
    
    # Calculate production for the final year
    Y[t] = calculate_production(A[t], K[t], L[t], H[t], params['alpha'])
    
    # Calculate net exports for the final year
    NX[t] = calculate_net_exports(
        Y[t], Y[0], exchange_rates[t], exchange_rates[0],
        foreign_incomes[t], foreign_incomes[0],
        params['X0'], params['M0'], 
        params['epsilon_x'], params['epsilon_m'],
        params['mu_x'], params['mu_m']
    )
    
    # Final consumption and investment
    C[t] = (1 - params['s']) * Y[t]
    I[t] = params['s'] * Y[t] + NX[t]
    
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