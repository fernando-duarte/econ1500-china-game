# China Growth Game

Interactive economic simulation game for undergraduate economics courses focused on China's economic growth.

## Overview

This project is an educational simulation that allows students to experience firsthand the economic challenges and policy decisions that shaped China's remarkable growth through a gamified Solow model. Teams compete to achieve the highest GDP growth by making strategic decisions about savings rates and exchange rate policies.

## Project Structure

This project consists of two main components:

### 1. Economic Model (Python)

- `china_growth_game/` - The canonical implementation of the economic model (Python package)
  - `app.py` - Main FastAPI application entry point
  - `economic_model/` - Python-based economic simulation engine
    - `app/` - FastAPI application
    - `core/` - Core economic calculations
    - `game/` - Game state management
    - `tests/` - Unit tests
    - `utils/` - Utility functions
    - `visualization/` - Visualization tools

### 2. Frontend Application (React/Node.js)

- `china-growth-game/` - The frontend web application
  - `app/` - Node.js Express server
  - `public/` - Static assets
  - `src/` - React application source code
  - `run_server.py` - Helper script to start the economic model API

### Additional Components

- `model/` - Wrapper module that imports from the canonical implementation
- `docs/` - Project documentation

**Note:** The naming difference (`china_growth_game` vs `china-growth-game`) is intentional:
- `china_growth_game` uses underscores as per Python package naming conventions
- `china-growth-game` uses hyphens as per JavaScript/Node.js package naming conventions

**Note:** The legacy components have been updated to use the canonical implementation to avoid code duplication and ensure consistency.

### Configuration

- `.env.example` - Consolidated environment configuration template
- `docker-compose.unified.yml` - Unified Docker Compose configuration

## Key Documentation

- [Acceptance Criteria](docs/acceptance-criteria.md) - Detailed requirements for features including team naming and prize logic
- [Performance Budget](docs/performance-budget.md) - Performance targets for bundle size, load times, and API response times
- [Code Review Checklist](docs/code-review-checklist.md) - Standard checklist for reviewing code changes
- [Version Management](docs/version-management.md) - Single source of truth for all version information
- [Version Update Process](docs/version-update-process.md) - Procedure for updating dependencies
- [Secrets Management](app/config/secrets.js) - Secure storage for production credentials
- [Feature Flags](app/config/featureFlags.js) - Feature toggling system for controlled rollouts
- [Accessibility](src/components/common/AccessibilityProvider.jsx) - WCAG 2.1 AA compliance features
- [Immutable Environments](docs/immutable-environments.md) - Ensuring consistent environments between development and CI

## Technology Stack

- **Frontend**: React 18.2.0, Material UI 5.15.14, Chart.js 4.4.3
- **Backend**: Node.js 20.13.1, Express 5.1.0, Socket.IO 4.7.5
- **Economic Model**: Python 3.12.2, FastAPI 0.110.0, NumPy 1.26.4, Pandas 2.2.2
- **Infrastructure**: Docker 26.1.4, GitHub Actions

## Security Features

- Environment-specific configurations
- Secrets management for production credentials (HashiCorp Vault/AWS Secrets Manager)
- API key-based authentication and role-based authorization
- Comprehensive input validation and sanitization
- CORS restrictions and CSRF protection to prevent cross-site attacks
- Rate limiting to prevent API abuse
- Non-root Docker containers with health checks
- Secure error handling that doesn't expose implementation details
- Exact version pinning for all dependencies

## Quality Assurance

- Comprehensive test suite for all components:
  - Economic model: Unit tests, integration tests, and benchmark tests
  - Backend: Unit tests, API tests, and Socket.IO tests
  - Frontend: Component tests, context tests, and service tests
- End-to-end tests for complete game flow
- Deterministic simulation replay for debugging
- Automated CI pipeline with linting, formatting and testing
- Performance budgets and monitoring
- Immutable environments between CI and development
- Standardized JSON serialization for consistent data handling
- Consolidated codebase structure to eliminate duplication

## Accessibility

- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- High contrast mode
- Large text support
- Reduced motion option

## Development Prerequisites

- Node.js 20.13.1 or later
- Python 3.12.2 or later
- Docker & Docker Compose

## Installation & Setup

1. Clone the repository
2. Set up the Python virtual environment:

```bash
./setup-venv.sh
```

This script will:
- Create a Python 3.12 virtual environment
- Install all required dependencies
- Set up symbolic links for model directories

3. Run the development environment startup script:

```bash
./start-unified.sh
```

This script will:
- Load consistent Docker image versions
- Build and start all services
- Wait for services to be healthy
- Provide access information

## Running Tests

Run all tests with the master test runner script:

```bash
./run_all_tests.sh
```

Or run tests for specific components:

```bash
# Run only economic model tests
./run_all_tests.sh --model

# Run only backend tests
./run_all_tests.sh --backend

# Run only frontend tests
./run_all_tests.sh --frontend

# Run tests with coverage reports
./run_all_tests.sh --coverage
```

Component-specific test runners are also available:

```bash
# Economic model tests
cd china-growth-game/economic-model
python run_tests.py

# Backend tests
cd backend
node run_tests.js

# Frontend tests
cd frontend
node run_tests.js
```

## Deployment

For production deployment, use the production Docker Compose configuration:

```
docker-compose -f docker-compose.prod.unified.yml up -d
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes following our [code review checklist](docs/code-review-checklist.md)
3. Ensure all tests pass and lint checks succeed
4. Submit a pull request using the PR template

## License

This project is licensed under the MIT License - see the LICENSE file for details.
