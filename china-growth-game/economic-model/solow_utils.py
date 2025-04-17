# solow_utils.py: Constants and utility functions for the Solow Model
# This file now serves as a compatibility layer to avoid breaking existing imports

from solow_core import (
    E_1980, Y_STAR_1980,
    calculate_exchange_rate,
    calculate_foreign_income,
    calculate_openness_ratio,
    calculate_fdi_ratio,
    get_default_parameters
)

# Export all imported functions to maintain backwards compatibility
__all__ = [
    'E_1980', 'Y_STAR_1980',
    'calculate_exchange_rate',
    'calculate_foreign_income',
    'calculate_openness_ratio',
    'calculate_fdi_ratio',
    'get_default_parameters'
] 