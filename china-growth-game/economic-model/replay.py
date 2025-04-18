import copy
from team_management import TeamManager
from game_state import GameState

def replay_session(initial_conditions, decisions_log, num_rounds=10):
    """
    Replay a full session deterministically given initial conditions and a log of team decisions.
    - initial_conditions: dict of initial state for each team
    - decisions_log: list of (team_id, round, savings_rate, exchange_rate_policy)
    - num_rounds: number of rounds to simulate
    Returns the final game state.
    """
    # Set up game state and teams
    game = GameState()
    for team_id, team_init in initial_conditions.items():
        team = game.team_manager.create_team(team_name=team_init["team_name"], current_year=team_init["year"], current_round=team_init["round"])
        # Overwrite initial state for reproducibility
        team["current_state"].update(team_init)
        game.team_manager.teams[team["team_id"]] = team
    game.start_game()
    # Apply decisions for each round
    for round_num in range(1, num_rounds+1):
        for entry in decisions_log:
            team_id, round_idx, savings_rate, exchange_rate_policy = entry
            if round_idx == round_num:
                game.submit_decision(team_id, savings_rate, exchange_rate_policy)
        game.advance_round()
    return game.get_game_state() 