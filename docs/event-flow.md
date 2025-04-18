# Event-Driven Architecture: Events & Handlers

This document describes the main events and handlers in the China Growth Game, focusing on real-time game flow and logic.

## Event Flow Diagram

```
[Client] --(joinTeam)--> [Server]
[Client] --(updateTeam)--> [Server]
[Client] --(startGame)--> [Server]
[Client] --(submitDecision)--> [Server]
[Server] --(gameState)--> [Client]
[Server] --(teamUpdate)--> [Client]
[Server] --(calculationResults)--> [Client]
[Server] --(roundAdvanced)--> [Client]
[Server] --(decisionSubmitted)--> [Client]
```

## Event Table

| Event Name         | Emitter   | Handler Location         | Description                                      |
|-------------------|-----------|-------------------------|--------------------------------------------------|
| joinTeam          | Client    | backend/server.js        | Join a team; updates team membership             |
| updateTeam        | Client    | backend/server.js        | Update team decisions (savings, exchange rate)   |
| startGame         | Client    | backend/server.js        | Professor starts the game                        |
| submitDecision    | Client    | backend/server.js        | Team submits round decision                      |
| gameState         | Server    | backend/server.js        | Broadcasts current game state to all clients     |
| teamUpdate        | Server    | backend/server.js        | Sends updated team info to relevant clients      |
| calculationResults| Server    | backend/server.js        | Sends economic model results to team             |
| roundAdvanced     | Server    | backend/server.js        | Notifies clients of round advancement            |
| decisionSubmitted | Server    | backend/server.js        | Notifies of a team's decision submission         |

## Idempotency & Ordering
- All event handlers should be idempotent (safe to process the same event twice).
- Event ordering is critical for game state consistency; see backend/server.js for implementation details.

---

_Last updated: [auto-generated]_ 