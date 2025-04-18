# Project Structure

This document explains the structure of the China Growth Game project, including the naming conventions and the relationship between different components.

## Overview

The China Growth Game project consists of two main components:

1. A Python-based economic model (`china_growth_game`)
2. A JavaScript/React frontend application (`china-growth-game`)

The naming difference is intentional and follows the conventions of each language ecosystem:
- Python packages typically use underscores (`china_growth_game`)
- JavaScript/Node.js packages typically use hyphens (`china-growth-game`)

## Directory Structure

```
.
├── china_growth_game/           # Python package (canonical implementation)
│   ├── app.py                  # Main FastAPI application entry point
│   └── economic_model/         # Core economic simulation engine
│       ├── app/                # FastAPI application
│       ├── core/               # Core economic calculations
│       ├── game/               # Game state management
│       ├── tests/              # Unit tests
│       ├── utils/              # Utility functions
│       └── visualization/      # Visualization tools
│
├── china-growth-game/          # JavaScript/React frontend application
│   ├── app/                    # Node.js Express server
│   ├── public/                 # Static assets
│   ├── src/                    # React application source code
│   └── run_server.py           # Helper script to start the economic model API
│
├── model/                      # Wrapper module (imports from canonical implementation)
│   ├── app.py                  # Wrapper for the FastAPI application
│   └── game_state.py           # Wrapper for the game state
│
├── scripts/                    # Utility scripts
│   └── solow_model_run.py      # Standalone script for running the Solow model
│
└── docs/                       # Project documentation
    └── project-structure.md    # This document
```

## Component Details

### 1. Economic Model (Python)

**Directory:** `china_growth_game/`

This is the canonical implementation of the economic simulation model, implemented as a Python package. It contains:

- `app.py` - Main FastAPI application entry point
- `economic_model/` - Core economic simulation engine
  - `app/` - FastAPI application
  - `core/` - Core economic calculations (Solow model)
  - `game/` - Game state management
  - `tests/` - Unit tests
  - `utils/` - Utility functions
  - `visualization/` - Visualization tools

### 2. Frontend Application (React/Node.js)

**Directory:** `china-growth-game/`

This is the web application that provides the user interface for the game. It contains:

- `app/` - Node.js Express server
- `public/` - Static assets
- `src/` - React application source code
- `run_server.py` - Helper script to start the economic model API

### 3. Wrapper Module

**Directory:** `model/`

This is a wrapper module that imports from the canonical implementation. It exists for backward compatibility and to provide a simplified interface for other components.

## Integration Between Components

The components are integrated as follows:

1. The React frontend (`china-growth-game`) makes API calls to the FastAPI server provided by the economic model (`china_growth_game`).

2. The `run_server.py` script in the `china-growth-game` directory is a helper script that starts the FastAPI server from the Python package in `china_growth_game/economic_model/app`.

3. The wrapper module (`model/`) imports directly from the canonical implementation to avoid code duplication.

## Development Workflow

When developing the application:

1. Changes to the economic model should be made in the `china_growth_game` directory.
2. Changes to the frontend should be made in the `china-growth-game` directory.
3. The wrapper module (`model/`) should not contain any implementation code, only imports from the canonical implementation.

## Avoiding Duplication

To avoid duplication:

1. Do not copy code between the different components.
2. Always use imports from the canonical implementation.
3. Keep the wrapper modules thin and focused on providing compatibility.

## Future Improvements

In the future, we may consider:

1. Renaming one of the components to avoid confusion.
2. Consolidating the project structure to make it more intuitive.
3. Improving the documentation to make the relationship between components clearer.
