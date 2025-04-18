# Modularization Plan for Unified Server

This document outlines a plan to refactor the unified-server.js file into a more modular structure to improve maintainability.

## Proposed Directory Structure

```
/server
  /controllers
    game-controller.js
    team-controller.js
  /socket
    socket-handlers.js
  /middleware
    auth-middleware.js
    error-middleware.js
    rate-limit-middleware.js
    csrf-middleware.js
  /routes
    game-routes.js
    team-routes.js
  /utils
    idempotency-utils.js
    error-utils.js
  /models
    game-state.js
  server.js
```

## Module Responsibilities

### Controllers

- **game-controller.js**: Handle game-related business logic (starting game, advancing rounds, etc.)
- **team-controller.js**: Handle team-related business logic (creating teams, submitting decisions, etc.)

### Socket

- **socket-handlers.js**: Define all Socket.IO event handlers

### Middleware

- **auth-middleware.js**: Handle authentication and authorization
- **error-middleware.js**: Centralized error handling
- **rate-limit-middleware.js**: Rate limiting functionality
- **csrf-middleware.js**: CSRF protection

### Routes

- **game-routes.js**: Define game-related REST API routes
- **team-routes.js**: Define team-related REST API routes

### Utils

- **idempotency-utils.js**: Idempotency helper functions
- **error-utils.js**: Error handling utilities

### Models

- **game-state.js**: Game state management

### Server

- **server.js**: Main entry point, sets up Express and Socket.IO

## Implementation Steps

1. Create the directory structure
2. Extract idempotency and error handling utilities
3. Create the game state model
4. Implement controllers with business logic
5. Create socket handlers
6. Set up middleware
7. Define routes
8. Update the main server file to use the modular components

## Benefits

- Improved code organization
- Better separation of concerns
- Easier testing
- Simplified maintenance
- Better scalability

## Risks and Mitigations

- **Risk**: Breaking existing functionality during refactoring
  - **Mitigation**: Comprehensive testing after each module is extracted

- **Risk**: Circular dependencies between modules
  - **Mitigation**: Careful design of module interfaces and dependencies

- **Risk**: Performance impact from additional module loading
  - **Mitigation**: Benchmark before and after to ensure no significant performance degradation
