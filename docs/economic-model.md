# Economic Model

## 1. Model Validation
- Maintain a test suite that compares model outputs against known benchmarks.
  - See [`game_state.py`](../china-growth-game/economic-model/game_state.py) for round logic and output calculation.
  - See [`team_management.py`](../china-growth-game/economic-model/team_management.py) for team state and decisions.
  - (TODO: Link to test suite or add instructions for running model validation tests.)
- Include both unit tests and statistical regression tests.
- Audit all equations and logic for correctness and transparency.
- Document all validation procedures and results.

## 2. Versioned Data & Seeds
- Seed initial conditions from versioned CSVs or a small read-only database.
  - See initial state in [`TeamManager.create_team`](../china-growth-game/economic-model/team_management.py#L29)
  - (TODO: Link to data seeding scripts or CSVs if present.)
- Avoid hardcoding floating-point literals or parameters in code.
- Document the data versioning and seeding process.

## 3. Reproducibility
- Ensure round-update logic can replay a full session deterministically for debugging and audit.
  - See [`GameState.advance_round`](../china-growth-game/economic-model/game_state.py#L172)
- Log all random seeds and configuration parameters per session.
  - (TODO: Add or link to logging of random seeds in game session.)
- Provide tools/scripts to replay sessions from logs or seeds.
  - (TODO: Link to replay scripts or add instructions.)

## References
- [`game_state.py`](../china-growth-game/economic-model/game_state.py)
- [`team_management.py`](../china-growth-game/economic-model/team_management.py)
- [`events_manager.py`](../china-growth-game/economic-model/events_manager.py)
- TODO: Link to test suite, data seeding, and replay scripts. 