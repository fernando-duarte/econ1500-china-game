"""
Constants and configuration for the China Growth Game.
This file centralizes all constants used throughout the codebase to avoid duplication.
"""

# Base economic constants
E_1980 = 1.5  # Baseline exchange rate in 1980
Y_STAR_1980 = 1000  # Baseline foreign income in 1980 (billion USD)

# Default Solow model parameters
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

# Default initial conditions for China in 1980
DEFAULT_INITIAL_CONDITIONS = {
    'Y': 306.2,  # Initial GDP (billion USD)
    'K': 800,    # Initial capital stock (billion USD)
    'L': 600,    # Initial labor force (million workers)
    'H': 1.0,    # Initial human capital (index)
    'A': 1.0,    # Initial productivity (TFP index)
    'NX': 3.6    # Initial net exports (billion USD)
}

# Game configuration
DEFAULT_YEARS = list(range(1980, 2026, 5))  # Default simulation years: 1980, 1985, ..., 2025
MAX_ROUNDS = 10  # Maximum number of game rounds
DEFAULT_SAVINGS_RATE = 0.2  # Default savings rate if none provided by student
DEFAULT_EXCHANGE_RATE_POLICY = 'market'  # Default exchange rate policy

# Event years - for event-based game mechanics
WTO_EVENT_YEAR = 2000
GFC_EVENT_YEAR = 2010
COVID_EVENT_YEAR = 2020

# Exchange rate policy values
EXCHANGE_RATE_POLICIES = ['undervalue', 'market', 'overvalue']
POLICY_MULTIPLIERS = {
    'undervalue': 1.2,  # 20% undervaluation
    'market': 1.0,      # Market rate
    'overvalue': 0.8    # 20% overvaluation
} 