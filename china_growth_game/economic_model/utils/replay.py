"""
Replay functionality for the China Growth Game.

This module provides functions for replaying a game session
with a given set of initial conditions and decisions.
"""

# No imports needed at module level

def replay_session(initial_conditions, decisions_log, num_rounds=10):
    """
    Replay a full session deterministically given initial conditions and a log of team decisions.

    Args:
        initial_conditions: dict of initial state for each team
        decisions_log: list of (team_id, round, savings_rate, exchange_rate_policy)
        num_rounds: number of rounds to simulate

    Returns:
        The final game state.
    """
    # Import here to avoid circular imports
    from china_growth_game.economic_model.game.game_state import GameState

    # Set up game state and teams
    game = GameState()

    # Override random elements with fixed values for reproducibility
    game.game_id = "fixed-game-id-for-testing"
    game.created_at = "2023-01-01T00:00:00"
    for team_id, team_init in initial_conditions.items():
        # Create a team with the provided ID instead of generating a new one
        team = game.team_manager.create_team(team_name=team_init["team_name"], current_year=team_init["year"], current_round=team_init["round"])

        # Map the test's keys to the expected keys in the game state
        # This handles the mismatch between test data and game state expectations
        mapped_state = {}
        key_mapping = {
            "Y": "GDP",
            "K": "Capital",
            "L": "Labor Force",
            "H": "Human Capital",
            "A": "Productivity (TFP)",
            "NX": "Net Exports",
            "C": "Consumption"
        }

        # Copy over basic fields
        for key in ["team_name", "year", "round"]:
            if key in team_init:
                mapped_state[key] = team_init[key]

        # Map the economic variables using the key mapping
        for test_key, game_key in key_mapping.items():
            if test_key in team_init:
                mapped_state[game_key] = team_init[test_key]

        # Add any additional fields that might be needed
        if "initial_Y" in team_init:
            mapped_state["initial_Y"] = team_init["initial_Y"]

        # Overwrite initial state for reproducibility with the mapped state
        team["current_state"].update(mapped_state)

        # Replace the auto-generated team_id with the one from initial_conditions
        original_team_id = team["team_id"]
        team["team_id"] = team_id
        # Update the teams dictionary with the correct key
        del game.team_manager.teams[original_team_id]
        game.team_manager.teams[team_id] = team
    game.start_game()
    # Apply decisions for each round
    for round_num in range(1, num_rounds+1):
        for entry in decisions_log:
            team_id, round_idx, savings_rate, exchange_rate_policy = entry
            if round_idx == round_num:
                # Directly submit to team_manager to avoid parameter mismatch
                game.team_manager.submit_decision(
                    team_id,
                    savings_rate,
                    exchange_rate_policy,
                    round_idx,  # Use the round from the decision log
                    game.current_year  # Use the current year from the game state
                )
        game.advance_round()
    return game.get_game_state()
