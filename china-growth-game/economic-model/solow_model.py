# solow_model.py: Single-step game round calculations for the Solow Model

import numpy as np
import pandas as pd
from solow_utils import (
    calculate_exchange_rate, 
    calculate_foreign_income,
    calculate_fdi_ratio
)
from solow_core import calculate_single_round

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
    # Get openness and FDI ratios for current round
    openness_ratio = parameters['openness_ratio']
    fdi_ratio = calculate_fdi_ratio(year)
    
    # Use the unified core function to calculate the round
    return calculate_single_round(
        current_state=current_state,
        parameters=parameters,
        student_inputs=student_inputs,
        year=year,
        openness_ratio=openness_ratio,
        fdi_ratio=fdi_ratio
    )

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