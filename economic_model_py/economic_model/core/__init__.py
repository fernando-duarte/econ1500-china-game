"""
Core economic model components for the China Growth Game.

This module contains the core economic functions and models
that power the simulation.
"""

from economic_model_py.economic_model.core.solow_core import (
    calculate_production,
    calculate_capital_next,
    calculate_labor_next,
    calculate_human_capital_next,
    calculate_tfp_next,
    calculate_exchange_rate,
    calculate_foreign_income,
    calculate_net_exports,
    get_default_parameters,
    calculate_openness_ratio,
    calculate_fdi_ratio,
    solve_solow_model
)

from economic_model_py.economic_model.core.solow_model import (
    calculate_next_round
)

from economic_model_py.economic_model.core.solow_simulation import (
    run_simulation
)
