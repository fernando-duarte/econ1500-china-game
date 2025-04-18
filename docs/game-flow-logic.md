# Game Flow & Logic

## 1. Acceptance Criteria
- **Group Naming UI**
  - Auto-generated names must be unique, pronounceable, and persisted to the DB.
    - See [`team_management.py::TeamManager.generate_team_name`](../china-growth-game/economic-model/team_management.py#L18)
  - Manual names must be validated for uniqueness and appropriateness.
    - See [`TeamManager.create_team`](../china-growth-game/economic-model/team_management.py#L29)
  - All names must be retrievable and editable by authorized users.
    - See API: [`/teams/create`](../china-growth-game/economic-model/app.py#L126)
- **Prize Logic**
  - Prizes must be awarded based on clear, deterministic rules.
  - Prize assignment must be atomic and idempotent (no double-awards).
  - All prize events must be logged and auditable.
    - See [`game_state.py::GameState.advance_round`](../china-growth-game/economic-model/game_state.py#L172)

## 2. Event-Driven Architecture
- **Events**
  - Game events are defined and managed in [`events_manager.py`](../china-growth-game/economic-model/events_manager.py).
  - Example events: `group_created`, `prize_awarded`, `round_completed`, and economic events (WTO, GFC, Trade War, COVID).
- **Handlers**
  - Event triggers and handlers are coordinated in [`game_state.py`](../china-growth-game/economic-model/game_state.py) and [`events_manager.py`](../china-growth-game/economic-model/events_manager.py).
  - Example: `advance_round` triggers event effects via [`_apply_event_effects`](../china-growth-game/economic-model/game_state.py#L85).
- **Diagram**
  - ```mermaid
    graph TD
      A[UI Action] --> B[Backend API]
      B --> C[Game State]
      C --> D[Events Manager]
      D -->|WTO Event| E[Apply Event Effects]
      D -->|GFC Event| E
      D -->|Trade War| E
      D -->|COVID-19| E
      E --> F[Update Economic Model]
      F --> G[Calculate New State]
      G --> H[Emit Results]
      H --> I[UI Update]
      C --> J[Round Completion]
      J --> K[Prize Calculation]
      K --> L[Update Leaderboard]
      L --> I
    ```

## 3. Edge Cases & Fault Injection
- **Duplicate Events**
  - All event handlers should check for idempotency, e.g., by marking events as `triggered` in [`EventsManager.get_current_events`](../china-growth-game/economic-model/events_manager.py#L36).
- **Concurrency**
  - Prize logic and state updates use in-memory and DB checks to prevent double-awards. See [`GameState.advance_round`](../china-growth-game/economic-model/game_state.py#L172).
- **Fault Injection**
  - See [`server.test.js`](../backend/server.test.js) for tests that simulate duplicate event handling, verifying that events are only processed once even when sent multiple times.
  - Test cases cover: duplicate team updates, duplicate game start events, and duplicate round progression.

## References
- [`team_management.py`](../china-growth-game/economic-model/team_management.py)
- [`game_state.py`](../china-growth-game/economic-model/game_state.py)
- [`events_manager.py`](../china-growth-game/economic-model/events_manager.py)
- [`app.py` API endpoints](../china-growth-game/economic-model/app.py)
- [`server.test.js`](../backend/server.test.js) 