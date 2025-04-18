# China Growth Game

Interactive economic simulation game for undergraduate economics courses focused on China's economic growth.

## Overview

This project is an educational simulation that allows students to experience firsthand the economic challenges and policy decisions that shaped China's remarkable growth through a gamified Solow model. Teams compete to achieve the highest GDP growth by making strategic decisions about savings rates and exchange rate policies.

## Project Structure

- `app/` - Node.js Express backend
- `src/` - React frontend
- `economic-model/` - Python-based economic simulation engine
- `docs/` - Documentation files

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
- CORS restrictions to prevent cross-site request forgery
- Rate limiting to prevent API abuse
- Non-root Docker containers with health checks
- Secure error handling that doesn't expose implementation details
- Exact version pinning for all dependencies

## Quality Assurance

- Extensive test coverage for economic model
- Deterministic simulation replay for debugging
- Automated CI pipeline with linting, formatting and testing
- Performance budgets and monitoring
- Immutable environments between CI and development

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
2. Run the development environment startup script:

```bash
./start-dev.sh
```

This script will:
- Load consistent Docker image versions
- Build and start all services
- Wait for services to be healthy
- Provide access information

## Deployment

For production deployment, use the production Docker Compose configuration:

```
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes following our [code review checklist](docs/code-review-checklist.md)
3. Ensure all tests pass and lint checks succeed
4. Submit a pull request using the PR template

## License

This project is licensed under the MIT License - see the LICENSE file for details.

