# Economic Model

## 1. Model Validation
- Maintain a test suite that compares model outputs against known benchmarks.
  - See [`game_state.py`](../china-growth-game/economic-model/game_state.py) for round logic and output calculation.
  - See [`team_management.py`](../china-growth-game/economic-model/team_management.py) for team state and decisions.
  - See [`test_model.py`](../china-growth-game/economic-model/test_model.py) for a comprehensive test suite that validates the economic model calculations, including tests for basic calculations, exchange rate policy impact, savings rate impact, and replay session reproducibility.
- Include both unit tests and statistical regression tests.
- Audit all equations and logic for correctness and transparency.
- Document all validation procedures and results.

## 2. Versioned Data & Seeds
- Seed initial conditions from versioned CSVs or a small read-only database.
  - See initial state in [`TeamManager.create_team`](../china-growth-game/economic-model/team_management.py#L29)
  - See [`initial_conditions_v1.csv`](../china-growth-game/economic-model/initial_conditions_v1.csv) for the versioned initial state data.
- Avoid hardcoding floating-point literals or parameters in code.
- Document the data versioning and seeding process.

## 3. Reproducibility
- Ensure round-update logic can replay a full session deterministically for debugging and audit.
  - See [`GameState.advance_round`](../china-growth-game/economic-model/game_state.py#L172)
- Log all random seeds and configuration parameters per session.
  - Random seed used for team name generation in [`team_management.py`](../china-growth-game/economic-model/team_management.py#L2-L3) (uses Python's random module).
  - Note: The core economic model is deterministic and does not use random values for calculations, ensuring reproducibility.
- Provide tools/scripts to replay sessions from logs or seeds.
  - See [`replay.py`](../china-growth-game/economic-model/replay.py) for the implementation of the session replay functionality.
  - Usage: `replay_session(initial_conditions, decisions_log, num_rounds=10)` returns the final game state after replaying all decisions.

## References
- [`game_state.py`](../china-growth-game/economic-model/game_state.py)
- [`team_management.py`](../china-growth-game/economic-model/team_management.py)
- [`events_manager.py`](../china-growth-game/economic-model/events_manager.py)
- [`test_model.py`](../china-growth-game/economic-model/test_model.py)
- [`replay.py`](../china-growth-game/economic-model/replay.py)
- [`initial_conditions_v1.csv`](../china-growth-game/economic-model/initial_conditions_v1.csv) 