"""
Solow model simulation for the China Growth Game.

This module contains the functions for running simulations
of the Solow model over multiple periods.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from china_growth_game.economic_model.core.solow_core import solve_solow_model

def run_simulation(
    initial_year: int,
    initial_conditions: Dict[str, float],
    parameters: Dict[str, float],
    years: Optional[np.ndarray] = None,
    historical_data: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Run a simulation of the Solow model over multiple periods.

    Args:
        initial_year: Starting year for simulation.
        initial_conditions: Initial values for Y, K, L, H, A.
        parameters: Model parameters.
        years: Array of years to simulate. If None, uses default years.
        historical_data: Optional historical data for comparison.

    Returns:
        DataFrame containing simulated values for all periods.
    """
    if years is None:
        # Default to 5-year periods from 1980 to 2025
        years = np.array(range(1980, 2026, 5))
    
    return solve_solow_model(
        initial_year=initial_year,
        initial_conditions=initial_conditions,
        parameters=parameters,
        years=years,
        historical_data=historical_data
    )
