"""
Solow model implementation for the China Growth Game.

This module contains the functions for calculating the next round
of the Solow model based on the current state and student inputs.
"""

from typing import Dict, Any

def calculate_next_round(
    current_state: Dict[str, float],
    parameters: Dict[str, float],
    student_inputs: Dict[str, Any],
    year: int
) -> Dict[str, float]:
    """
    Calculate the next round of the Solow model.

    Args:
        current_state: Current values for {'K', 'L', 'H', 'A'}.
        parameters: Model parameters including Solow and NX parameters.
        student_inputs: Student choices for this round {'s', 'e_policy'} or {'savings_rate', 'exchange_rate_policy'}.
        year: Current year for the round.

    Returns:
        Dictionary containing next round state and current round calculations.
    """
    # Import here to avoid circular imports
    from china_growth_game.economic_model.core.solow_core import calculate_single_round

    return calculate_single_round(
        current_state=current_state,
        parameters=parameters,
        student_inputs=student_inputs,
        year=year
    )
