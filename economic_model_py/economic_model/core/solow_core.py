"""
Consolidated core implementation of the Solow growth model.
This is the definitive source for all economic calculations in the game.
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Tuple, Union, Optional

from economic_model_py.economic_model.utils.error_handling import (
    ModelError, CalculationError, ParameterError
)

# Import constants from centralized file
from economic_model_py.economic_model.utils.constants import (
    E_1980, Y_STAR_1980, DEFAULT_PARAMS,
    POLICY_MULTIPLIERS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# UTILITY FUNCTIONS - General helpers and parameter management
# =============================================================================
def get_default_parameters() -> Dict[str, float]:
    """Return default parameters for the Solow model."""
    return DEFAULT_PARAMS.copy()

def initialize_arrays(initial_conditions: Dict[str, float], num_periods: int) -> Tuple[np.ndarray, ...]:
    """
    Initialize arrays for Solow model simulation.

    Args:
        initial_conditions: Dictionary with initial values for Y, K, L, H, A
        num_periods: Number of periods to simulate

    Returns:
        Tuple of numpy arrays for Y, K, L, H, A, NX, C, I

    Raises:
        ParameterError: If required initial conditions are missing
    """
    # Define required and optional parameters
    required_params = ['K', 'L', 'H', 'A']
    optional_params = ['Y', 'NX']

    # Validate required parameters
    missing_params = [param for param in required_params if param not in initial_conditions]
    if missing_params:
        raise ParameterError(f"Missing required initial conditions: {', '.join(missing_params)}",
                           details={"missing_params": missing_params})

    # Initialize arrays
    Y = np.zeros(num_periods)
    K = np.zeros(num_periods)
    L = np.zeros(num_periods)
    H = np.zeros(num_periods)
    A = np.zeros(num_periods)
    NX = np.zeros(num_periods)
    C = np.zeros(num_periods)
    I = np.zeros(num_periods)

    # Set initial values with validation
    K[0] = initial_conditions['K']
    L[0] = initial_conditions['L']
    H[0] = initial_conditions['H']
    A[0] = initial_conditions['A']

    # Handle optional parameters with defaults
    Y[0] = initial_conditions.get('Y', 0)  # Will typically be calculated if not provided
    NX[0] = initial_conditions.get('NX', 0)

    return Y, K, L, H, A, NX, C, I

# =============================================================================
# CORE ECONOMIC FUNCTIONS - Pure economic calculations
# =============================================================================
def calculate_production(A: float, K: float, L: float, H: float, alpha: float) -> float:
    """
    Calculate production using the Cobb-Douglas function.

    Args:
        A: Total factor productivity
        K: Capital stock
        L: Labor force
        H: Human capital
        alpha: Capital share parameter

    Returns:
        Y: Output (GDP)

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    # Ensure all inputs are non-negative
    A_safe = max(1e-10, A)  # Ensure TFP is positive
    K_safe = max(1e-10, K)  # Ensure capital is positive
    L_safe = max(1e-10, L)  # Ensure labor is positive
    H_safe = max(1e-10, H)  # Ensure human capital is positive

    # Ensure alpha is within valid range
    alpha_safe = max(0.01, min(0.99, alpha))  # Constrain alpha to avoid numerical issues

    # Calculate production with safeguards
    try:
        Y = A_safe * (K_safe**alpha_safe) * ((L_safe * H_safe)**(1 - alpha_safe))
        return max(1e-10, Y)  # Ensure GDP is positive
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in production calculation: {str(e)}",
                            details={"A": A, "K": K, "L": L, "H": H, "alpha": alpha})

def calculate_net_exports(
    Y: float,
    Y_initial: float,
    exchange_rate: float,
    exchange_rate_initial: float,
    foreign_income: float,
    foreign_income_initial: float,
    X0: float,
    M0: float,
    epsilon_x: float,
    epsilon_m: float,
    mu_x: float,
    mu_m: float
) -> float:
    """
    Calculate net exports based on current state and parameters.

    Args:
        Y: Current GDP
        Y_initial: Initial/base GDP
        exchange_rate: Current exchange rate
        exchange_rate_initial: Initial/base exchange rate
        foreign_income: Current foreign income
        foreign_income_initial: Initial/base foreign income
        X0: Initial exports
        M0: Initial imports
        epsilon_x: Exchange rate elasticity of exports
        epsilon_m: Exchange rate elasticity of imports
        mu_x: Foreign income elasticity of exports
        mu_m: Domestic income elasticity of imports

    Returns:
        NX: Net exports

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    try:
        # Apply safety bounds to all inputs
        Y_safe = max(Y, 1e-6)
        Y_initial_safe = max(Y_initial, 1e-6)
        exchange_rate_safe = max(exchange_rate, 1e-6)
        exchange_rate_initial_safe = max(exchange_rate_initial, 1e-6)
        foreign_income_safe = max(foreign_income, 1e-6)
        foreign_income_initial_safe = max(foreign_income_initial, 1e-6)
        X0_safe = max(X0, 0)
        M0_safe = max(M0, 0)

        # Constrain elasticities to reasonable ranges
        epsilon_x_safe = max(-10, min(10, epsilon_x))
        epsilon_m_safe = max(-10, min(10, epsilon_m))
        mu_x_safe = max(-10, min(10, mu_x))
        mu_m_safe = max(-10, min(10, mu_m))

        # Calculate exports and imports with safeguards
        exports_ratio = exchange_rate_safe / exchange_rate_initial_safe
        income_ratio = foreign_income_safe / foreign_income_initial_safe
        gdp_ratio = Y_safe / Y_initial_safe

        exports_term = X0_safe * (exports_ratio**epsilon_x_safe) * (income_ratio**mu_x_safe)
        imports_term = M0_safe * (exports_ratio**(-epsilon_m_safe)) * (gdp_ratio**mu_m_safe)

        # Ensure exports and imports don't exceed reasonable bounds
        exports_term = min(exports_term, Y_safe * 2)  # Exports shouldn't exceed 200% of GDP
        imports_term = min(imports_term, Y_safe * 2)  # Imports shouldn't exceed 200% of GDP

        return exports_term - imports_term
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in net exports calculation: {str(e)}",
                            details={"Y": Y, "exchange_rate": exchange_rate, "foreign_income": foreign_income})

def calculate_capital_next(K: float, Y: float, NX: float, s: float, delta: float) -> Tuple[float, float]:
    """
    Calculate next period capital stock and the investment amount.

    Args:
        K: Current capital stock
        Y: Current GDP
        NX: Current net exports
        s: Savings rate
        delta: Depreciation rate

    Returns:
        Tuple[K_next, I]: Next period capital stock and Investment amount

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    try:
        # Apply safety bounds to inputs
        K_safe = max(0, K)
        Y_safe = max(0, Y)

        # Constrain savings rate and depreciation rate to valid ranges
        s_safe = max(0.01, min(0.99, s))
        delta_safe = max(0.01, min(0.99, delta))

        # Calculate investment with safeguards
        I = s_safe * Y_safe + NX

        # Ensure capital doesn't go negative
        remaining_capital = (1 - delta_safe) * K_safe
        if I + remaining_capital < 0:
            # Limit disinvestment to available capital
            I = -remaining_capital

        # Ensure investment doesn't exceed reasonable bounds
        I = max(-Y_safe, min(Y_safe * 2, I))  # Investment between -100% and 200% of GDP

        # Calculate next period capital
        K_next = remaining_capital + I
        K_next = max(1e-10, K_next)  # Ensure capital is positive

        return K_next, I
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in capital calculation: {str(e)}",
                            details={"K": K, "Y": Y, "NX": NX, "s": s, "delta": delta})

def calculate_labor_next(L: float, n: float) -> float:
    """
    Calculate next period labor force.

    Args:
        L: Current labor force
        n: Labor force growth rate

    Returns:
        L_next: Next period labor force

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    try:
        # Apply safety bounds
        L_safe = max(1e-10, L)  # Ensure labor is positive
        n_safe = max(-0.5, min(0.5, n))  # Constrain growth rate to reasonable range

        # Calculate next period labor
        L_next = L_safe * (1 + n_safe)
        return max(1e-10, L_next)  # Ensure result is positive
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in labor calculation: {str(e)}",
                            details={"L": L, "n": n})

def calculate_human_capital_next(H: float, eta: float) -> float:
    """
    Calculate next period human capital.

    Args:
        H: Current human capital
        eta: Human capital growth rate

    Returns:
        H_next: Next period human capital

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    try:
        # Apply safety bounds
        H_safe = max(1e-10, H)  # Ensure human capital is positive
        eta_safe = max(-0.5, min(0.5, eta))  # Constrain growth rate to reasonable range

        # Calculate next period human capital
        H_next = H_safe * (1 + eta_safe)
        return max(1e-10, H_next)  # Ensure result is positive
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in human capital calculation: {str(e)}",
                            details={"H": H, "eta": eta})

def calculate_tfp_next(A: float, g: float, theta: float, openness_ratio: float, phi: float, fdi_ratio: float) -> float:
    """
    Calculate next period total factor productivity (TFP).

    Args:
        A: Current TFP
        g: Base productivity growth rate
        theta: Effect of openness on productivity
        openness_ratio: Openness ratio (trade/GDP)
        phi: Effect of FDI on productivity
        fdi_ratio: FDI ratio (FDI/GDP)

    Returns:
        A_next: Next period TFP

    Raises:
        CalculationError: If inputs would lead to numerical instability
    """
    try:
        # Apply safety bounds
        A_safe = max(1e-10, A)  # Ensure TFP is positive
        g_safe = max(-0.1, min(0.2, g))  # Constrain base growth rate
        theta_safe = max(-0.5, min(0.5, theta))  # Constrain openness effect
        phi_safe = max(-0.5, min(0.5, phi))  # Constrain FDI effect
        openness_ratio_safe = max(0, min(2, openness_ratio))  # Constrain openness ratio
        fdi_ratio_safe = max(0, min(1, fdi_ratio))  # Constrain FDI ratio

        # Calculate growth factors with safeguards
        growth_factor = 1 + g_safe + theta_safe * openness_ratio_safe + phi_safe * fdi_ratio_safe

        # Ensure growth factor is reasonable
        growth_factor = max(0.5, min(1.5, growth_factor))  # Limit to 50% decline or 50% growth

        # Calculate next period TFP
        A_next = A_safe * growth_factor
        return max(1e-10, A_next)  # Ensure result is positive
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise CalculationError(f"Numerical error in TFP calculation: {str(e)}",
                            details={"A": A, "g": g, "theta": theta, "openness_ratio": openness_ratio,
                                     "phi": phi, "fdi_ratio": fdi_ratio})

# =============================================================================
# ENVIRONMENTAL AND POLICY FUNCTIONS - Game-specific calculations
# =============================================================================
def calculate_exchange_rate(year: int, e_policy: str) -> float:
    """
    Calculate exchange rate based on policy and year.

    Args:
        year: Current year
        e_policy: Exchange rate policy ('undervalue', 'market', or 'overvalue')

    Returns:
        Exchange rate

    Raises:
        ParameterError: If e_policy is not a valid policy
    """
    # Validate policy
    valid_policies = ['market', 'undervalue', 'overvalue']
    if e_policy not in valid_policies:
        raise ParameterError(f"Exchange rate policy must be one of {valid_policies}, got {e_policy}",
                           details={"valid_policies": valid_policies, "provided_policy": e_policy})

    # Round index (0-based) from year
    round_index = max(0, (year - 1980) // 5)
    # Baseline market exchange rate (linear interpolation 1.5 to 7.0 over 10 rounds)
    num_rounds = 10
    e_market_t = E_1980 + (7.0 - E_1980) * round_index / (num_rounds - 1)

    # Determine actual exchange rate based on policy using the policy multipliers
    multiplier = POLICY_MULTIPLIERS[e_policy]  # Now we can safely use direct lookup
    return e_market_t * multiplier

def calculate_foreign_income(year: int) -> float:
    """
    Calculate foreign income based on year (3% annual growth).

    Args:
        year: Current year

    Returns:
        Foreign income
    """
    round_index = max(0, (year - 1980) // 5)
    return Y_STAR_1980 * (1.03**(5 * round_index))

def calculate_openness_ratio(round_index: int) -> float:
    """
    Calculate openness ratio based on round index.

    Args:
        round_index: Current round index (0-based)

    Returns:
        Openness ratio
    """
    # Handle negative round indices by treating them as 0
    round_index = max(0, round_index)
    return 0.1 + 0.02 * round_index

def calculate_fdi_ratio(year: int) -> float:
    """
    Calculate FDI ratio based on year.

    Args:
        year: Current year

    Returns:
        FDI ratio
    """
    return 0.02 if year >= 1990 else 0

# =============================================================================
# MAIN CALCULATION FUNCTIONS - Primary interfaces for simulations and game
# =============================================================================
def _calculate_step(
    current_state: Dict[str, float],
    parameters: Dict[str, float],
    savings_rate: float,
    exchange_rate_policy: str,
    year: int
) -> Dict[str, float]:
    """
    Internal function to calculate one step/round of the model.
    Handles both game rounds (with student inputs) and simulation steps.

    Args:
        current_state: Current values for {'K', 'L', 'H', 'A'}.
        parameters: Model parameters including Solow and NX parameters.
        savings_rate: The savings rate to use for this step.
        exchange_rate_policy: The exchange rate policy ('market', 'undervalue', etc.).
        year: Current year for the step.

    Returns:
        Dictionary containing results for the current step (Y_t, C_t, I_t, NX_t)
        and state for the next step (K_next, L_next, H_next, A_next).

    Raises:
        ParameterError: If inputs or parameters are invalid.
        CalculationError: If calculations result in invalid states.
    """
    # Validate inputs
    if not isinstance(current_state, dict):
        raise ParameterError(f"Current state must be a dictionary, got {type(current_state)}",
                           details={"provided_type": str(type(current_state))})

    required_state_keys = ['K', 'L', 'H', 'A']
    for key in required_state_keys:
        if key not in current_state:
            raise ParameterError(f"Current state missing required key: {key}",
                               details={"missing_key": key, "required_keys": required_state_keys})
        if not isinstance(current_state[key], (int, float)):
            raise ParameterError(f"Current state value for {key} must be a number, got {type(current_state[key])}",
                               details={"key": key, "provided_type": str(type(current_state[key]))})
        if current_state[key] < 0:
            raise ParameterError(f"Current state value for {key} must be non-negative, got {current_state[key]}",
                               details={"key": key, "provided_value": current_state[key]})

    if not isinstance(parameters, dict):
        raise ParameterError(f"Parameters must be a dictionary, got {type(parameters)}",
                           details={"provided_type": str(type(parameters))})

    if not isinstance(savings_rate, (int, float)):
        raise ParameterError(f"Savings rate must be a number, got {type(savings_rate)}",
                           details={"provided_type": str(type(savings_rate))})

    if savings_rate < 0.01 or savings_rate > 0.99:
        raise ParameterError(f"Savings rate must be between 0.01 and 0.99, got {savings_rate}",
                           details={"provided_value": savings_rate, "min_value": 0.01, "max_value": 0.99})

    if not isinstance(exchange_rate_policy, str):
        raise ParameterError(f"Exchange rate policy must be a string, got {type(exchange_rate_policy)}",
                           details={"provided_type": str(type(exchange_rate_policy))})

    valid_policies = ['market', 'undervalue', 'overvalue']
    if exchange_rate_policy not in valid_policies:
        raise ParameterError(f"Exchange rate policy must be one of {valid_policies}, got {exchange_rate_policy}",
                           details={"valid_policies": valid_policies, "provided_policy": exchange_rate_policy})

    # Convert numpy.int64 to Python int
    if hasattr(year, 'item'):
        year = year.item()

    if not isinstance(year, int):
        raise ParameterError(f"Year must be an integer, got {type(year)}",
                           details={"provided_type": str(type(year))})

    if year < 1980 or year > 2025:
        raise ParameterError(f"Year must be between 1980 and 2025, got {year}",
                           details={"provided_value": year, "min_value": 1980, "max_value": 2025})

    # Get context-dependent variables
    round_index = max(0, (year - 1980) // 5)
    openness_ratio = calculate_openness_ratio(round_index)
    fdi_ratio = calculate_fdi_ratio(year)

    # Unpack parameters (with defaults as fallback)
    params = get_default_parameters()
    params.update(parameters)  # Override defaults with provided parameters

    # Validate critical parameters
    required_params = ['alpha', 'delta', 'g', 'theta', 'phi', 'X0', 'M0',
                      'epsilon_x', 'epsilon_m', 'mu_x', 'mu_m', 'n', 'eta']
    for param in required_params:
        if param not in params:
            raise ParameterError(f"Required parameter missing: {param}",
                               details={"missing_param": param, "required_params": required_params})
        if not isinstance(params[param], (int, float)):
            raise ParameterError(f"Parameter {param} must be a number, got {type(params[param])}",
                               details={"param": param, "provided_type": str(type(params[param]))})

    # Validate specific parameter constraints
    if params['alpha'] <= 0 or params['alpha'] >= 1:
        raise ParameterError(f"Alpha must be between 0 and 1, got {params['alpha']}",
                           details={"provided_value": params['alpha'], "min_value": 0, "max_value": 1})

    if params['delta'] < 0 or params['delta'] > 1:
        raise ParameterError(f"Depreciation rate must be between 0 and 1, got {params['delta']}",
                           details={"provided_value": params['delta'], "min_value": 0, "max_value": 1})

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
    Y_1980 = params.get('Y_1980', 1000) # Use a default if not present

    # Unpack current state with safety checks
    K_t = max(0, current_state['K'])  # Ensure non-negative
    L_t = max(0.1, current_state['L'])  # Ensure positive labor
    H_t = max(0.1, current_state['H'])  # Ensure positive human capital
    A_t = max(0.1, current_state['A'])  # Ensure positive TFP

    try:
        # Calculate exchange rate and foreign income
        e_t = calculate_exchange_rate(year, exchange_rate_policy)
        Y_star_t = calculate_foreign_income(year)

        # Production
        Y_t = calculate_production(A_t, K_t, L_t, H_t, alpha)

        # Net Exports
        NX_t = calculate_net_exports(
            Y_t, Y_1980, e_t, E_1980, Y_star_t, Y_STAR_1980,
            X0, M0, epsilon_x, epsilon_m, mu_x, mu_m
        )

        # Consumption (using the provided savings rate for this step)
        C_t = (1 - savings_rate) * Y_t

        # Calculate next period variables using the modified capital function
        K_next, I_t = calculate_capital_next(K_t, Y_t, NX_t, savings_rate, delta)
        L_next = calculate_labor_next(L_t, params['n'])
        H_next = calculate_human_capital_next(H_t, params['eta'])
        A_next = calculate_tfp_next(A_t, g, theta, openness_ratio, phi, fdi_ratio)

        # Final validation of results
        if Y_t < 0 or K_next < 0 or L_next <= 0 or H_next <= 0 or A_next <= 0:
            raise CalculationError(f"Invalid calculation results: Y={Y_t}, K_next={K_next}, L_next={L_next}, H_next={H_next}, A_next={A_next}",
                                details={"Y": Y_t, "K_next": K_next, "L_next": L_next, "H_next": H_next, "A_next": A_next})

        # Return results
        return {
            # State for the start of the next step/round
            'K_next': K_next,
            'L_next': L_next,
            'H_next': H_next,
            'A_next': A_next,
            # Calculated values for the current step/round (t)
            'Y_t': Y_t,
            'NX_t': NX_t,
            'C_t': C_t,
            'I_t': I_t
        }
    except ParameterError as e:
        # Re-raise parameter errors directly
        raise
    except CalculationError as e:
        # Re-raise calculation errors directly
        raise
    except Exception as e:
        # Catch any other exceptions during calculation and convert to CalculationError
        raise CalculationError(f"Error in economic calculations: {str(e)}",
                            details={"original_error": str(e), "error_type": type(e).__name__})

def calculate_single_round(
    current_state: Dict[str, float],
    parameters: Dict[str, float],
    student_inputs: Dict[str, Any],
    year: int
) -> Dict[str, float]:
    """
    Unified function to calculate a single round of the Solow model for game state.
    This is the main entry point for single-step calculations in the game.

    Args:
        current_state: Current values for {'K', 'L', 'H', 'A'}.
        parameters: Model parameters including Solow and NX parameters.
        student_inputs: Student choices for this round {'savings_rate'/'s', 'exchange_rate_policy'/'e_policy'}.
        year: Current year for the round.

    Returns:
        Dictionary containing next round state and current round calculations.
    """
    # Get savings rate from student_inputs, supporting both key naming formats
    savings_rate = None
    if 'savings_rate' in student_inputs:
        savings_rate = student_inputs['savings_rate']
    elif 's' in student_inputs:
        savings_rate = student_inputs['s']
    else:
        raise ParameterError("Missing savings rate in student inputs",
                           details={"missing_key": "savings_rate or s", "provided_keys": list(student_inputs.keys())})

    # Get exchange rate policy from student_inputs, supporting both key naming formats
    exchange_rate_policy = None
    if 'exchange_rate_policy' in student_inputs:
        exchange_rate_policy = student_inputs['exchange_rate_policy']
    elif 'e_policy' in student_inputs:
        exchange_rate_policy = student_inputs['e_policy']
    else:
        raise ParameterError("Missing exchange rate policy in student inputs",
                           details={"missing_key": "exchange_rate_policy or e_policy", "provided_keys": list(student_inputs.keys())})

    # Use the internal step calculation function with student inputs
    return _calculate_step(
        current_state=current_state,
        parameters=parameters,
        savings_rate=savings_rate,
        exchange_rate_policy=exchange_rate_policy,
        year=year
    )

def solve_solow_model(
    initial_year: int,
    initial_conditions: Dict[str, float],
    parameters: Dict[str, float],
    years: np.ndarray,
    historical_data: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Solves the augmented open-economy Solow model for multiple periods.
    Used for full simulations and game initialization.

    Args:
        initial_year: Starting year for simulation.
        initial_conditions: Initial values for Y, K, L, H, A.
        parameters: Model parameters.
        years: Array of years to simulate.
        historical_data: Optional historical data for comparison.

    Returns:
        DataFrame containing simulated values for all periods.
    """
    # Merge with default parameters
    params = get_default_parameters()
    params.update(parameters)  # Override defaults with provided parameters

    # Prepare simulation
    T = len(years)

    # Initialize arrays using initial conditions for period 0
    Y, K, L, H, A, NX, C, I = initialize_arrays(initial_conditions, T)

    # Simulation loop using the internal step calculation function
    for t in range(T - 1):
        current_state = {'K': K[t], 'L': L[t], 'H': H[t], 'A': A[t]}

        # Use the simulation's fixed savings rate and 'market' exchange rate
        step_results = _calculate_step(
            current_state=current_state,
            parameters=params,
            savings_rate=params['s'], # Use the fixed simulation savings rate
            exchange_rate_policy='market', # Use 'market' for baseline simulation
            year=years[t]
        )

        # Store results for period t
        Y[t] = step_results['Y_t']
        NX[t] = step_results['NX_t']
        C[t] = step_results['C_t']
        I[t] = step_results['I_t']

        # Update state for period t+1
        K[t+1] = step_results['K_next']
        L[t+1] = step_results['L_next']
        H[t+1] = step_results['H_next']
        A[t+1] = step_results['A_next']

    # Final year calculations (t = T-1)
    # We need to calculate Y, C, I, NX for the final period using the state variables already computed
    t = T - 1
    current_state = {'K': K[t], 'L': L[t], 'H': H[t], 'A': A[t]}

    # Calculate final Y
    Y[t] = calculate_production(A[t], K[t], L[t], H[t], params['alpha'])

    # Calculate final NX (using market exchange rate for consistency in this simulation)
    final_exchange_rate = calculate_exchange_rate(years[t], 'market')
    final_foreign_income = calculate_foreign_income(years[t])
    initial_exchange_rate = calculate_exchange_rate(years[0], 'market') # Base exchange rate at start
    initial_foreign_income = calculate_foreign_income(years[0]) # Base foreign income at start
    Y_initial = initial_conditions.get('Y', params.get('Y_1980', 1000)) # Use initial Y if available, else Y_1980

    NX[t] = calculate_net_exports(
        Y[t], Y_initial, final_exchange_rate, initial_exchange_rate,
        final_foreign_income, initial_foreign_income,
        params['X0'], params['M0'],
        params['epsilon_x'], params['epsilon_m'],
        params['mu_x'], params['mu_m']
    )

    # Final C and I
    C[t] = (1 - params['s']) * Y[t]
    I[t] = params['s'] * Y[t] + NX[t] # Direct calculation as K_next is not needed

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
