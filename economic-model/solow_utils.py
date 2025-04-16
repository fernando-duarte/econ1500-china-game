# solow_utils.py: Constants and utility functions for the Solow Model

import numpy as np

# Define base constants for NX calculation
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