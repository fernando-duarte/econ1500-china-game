# solow_model.py: Single-step game round calculations for the Solow Model

import numpy as np
import pandas as pd
from solow_utils import (
    E_1980, Y_STAR_1980, 
    calculate_exchange_rate, 
    calculate_foreign_income,
    calculate_fdi_ratio
)

def calculate_next_round(current_state, parameters, student_inputs, year):
    """
    Calculates the state for the next round (t+1) based on the current state (t)
    and student inputs for the current round.

    Parameters:
    - current_state: dict, current values for {'Y', 'K', 'L', 'H', 'A'}.
    - parameters: dict, model parameters including Solow {'alpha', 'delta', 'g', 'theta', 'phi', 'n', 'eta'}
                       NX {'X0', 'M0', 'epsilon_x', 'epsilon_m', 'mu_x', 'mu_m', 'Y_1980'}
                       and {'openness_ratio'}.
    - student_inputs: dict, student choices for this round {'s', 'e_policy'}.
                       'e_policy' must be 'undervalue', 'market', or 'overvalue'.
    - year: int, the current year (t), used for calculations like FDI ratio and round index.

    Returns:
    - dict containing the state for the next round {'Y_next', 'K_next', 'L_next', 'H_next', 'A_next'}
      and calculated values for the current round {'NX_t', 'C_t', 'I_t'}.
    """
    # Unpack Solow parameters
    alpha = parameters['alpha']
    delta = parameters['delta']
    g = parameters['g']
    theta = parameters['theta']
    phi = parameters['phi']
    n = parameters['n']
    eta = parameters['eta']
    openness_ratio = parameters['openness_ratio']
    # Unpack NX parameters
    X0 = parameters['X0']
    M0 = parameters['M0']
    epsilon_x = parameters['epsilon_x']
    epsilon_m = parameters['epsilon_m']
    mu_x = parameters['mu_x']
    mu_m = parameters['mu_m']
    Y_1980 = parameters['Y_1980']

    # Unpack current state
    K_t = current_state['K']
    L_t = current_state['L']
    H_t = current_state['H']
    A_t = current_state['A']

    # Get student inputs
    s_t = student_inputs['s']
    e_policy = student_inputs['e_policy']

    # --- Calculations for current round (t) based on state at start of t ---

    # Calculate time-dependent variables for NX
    e_t = calculate_exchange_rate(year, e_policy)
    Y_star_t = calculate_foreign_income(year)

    # Production (using state at t)
    K_t_safe = max(0, K_t)
    Y_t_calc = A_t * (K_t_safe**alpha) * ((L_t * H_t)**(1 - alpha))
    Y_t_calc = max(0, Y_t_calc)  # Ensure GDP is non-negative

    # Compute Net Exports (using state at t, affects K_{t+1})
    Y_t_safe = max(Y_t_calc, 1e-6)
    Y_1980_safe = max(Y_1980, 1e-6)
    exports_term = X0 * (e_t / E_1980)**epsilon_x * (Y_star_t / Y_STAR_1980)**mu_x
    imports_term = M0 * (e_t / E_1980)**(-epsilon_m) * (Y_t_safe / Y_1980_safe)**mu_m
    NX_t = exports_term - imports_term

    # Consumption (using state at t and student savings rate s_t)
    C_t = (1 - s_t) * Y_t_calc

    # Investment (using state at t, student savings rate s_t, and calculated NX_t)
    I_t = s_t * Y_t_calc + NX_t
    # Prevent investment from causing negative capital next period
    if I_t + (1 - delta) * K_t_safe < 0:
        I_t = -((1 - delta) * K_t_safe)

    # --- Calculate state for next round (t+1) ---

    # Capital accumulation
    K_next = (1 - delta) * K_t_safe + I_t

    # Labor force update
    L_next = L_t * (1 + n)

    # Human capital update
    H_next = H_t * (1 + eta)

    # Productivity update
    fdi_ratio = calculate_fdi_ratio(year)
    A_next = A_t * (1 + g + theta * openness_ratio + phi * fdi_ratio)

    # Return results
    results = {
        # State for the start of the next round
        'K_next': K_next,
        'L_next': L_next,
        'H_next': H_next,
        'A_next': A_next,
        # Calculated values for the current round (t)
        'Y_t': Y_t_calc,  # GDP generated in round t
        'NX_t': NX_t,     # Net Exports in round t
        'C_t': C_t,       # Consumption in round t
        'I_t': I_t        # Investment in round t
    }

    return results

# Simple test if run directly
if __name__ == '__main__':
    from solow_utils import get_default_parameters, calculate_openness_ratio
    
    # Get example parameters
    Y_1980_EXAMPLE = 1000
    params = get_default_parameters()
    
    # Example initial conditions
    init_cond = {'Y': Y_1980_EXAMPLE, 'K': 1500, 'L': 100, 'H': 10, 'A': 1.5}
    
    # Test a single round calculation
    test_year = 1995
    round_index = (test_year - 1980) // 5
    params['openness_ratio'] = calculate_openness_ratio(round_index)
    
    student_input = {
        's': 0.25,  # 25% savings rate
        'e_policy': 'undervalue'  # Undervalue currency
    }
    
    result = calculate_next_round(init_cond, params, student_input, test_year)
    
    print(f"Year: {test_year}")
    print(f"  Inputs: s={student_input['s']:.2f}, e_policy={student_input['e_policy']}")
    print(f"  Current: Y={init_cond['Y']:.2f}, K={init_cond['K']:.2f}, L={init_cond['L']:.2f}")
    print(f"  Results: Y={result['Y_t']:.2f}, NX={result['NX_t']:.2f}, C={result['C_t']:.2f}")
    print(f"  Next State: K={result['K_next']:.2f}, L={result['L_next']:.2f}, A={result['A_next']:.2f}")