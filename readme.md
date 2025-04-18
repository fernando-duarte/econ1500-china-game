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
- [Secrets Management](app/config/secrets.js) - Secure storage for production credentials
- [Feature Flags](app/config/featureFlags.js) - Feature toggling system for controlled rollouts
- [Accessibility](src/components/common/AccessibilityProvider.jsx) - WCAG 2.1 AA compliance features

## Technology Stack

- **Frontend**: React 18, Material UI, Chart.js
- **Backend**: Node.js, Express
- **Economic Model**: Python, FastAPI, NumPy
- **Infrastructure**: Docker, GitHub Actions

## Security Features

- Environment-specific configurations
- Secrets management for production credentials (HashiCorp Vault/AWS Secrets Manager)
- Authentication and authorization middleware
- Input validation and sanitization

## Quality Assurance

- Extensive test coverage for economic model
- Deterministic simulation replay for debugging
- Automated CI pipeline with linting, formatting and testing
- Performance budgets and monitoring

## Accessibility

- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- High contrast mode
- Large text support
- Reduced motion option

## Development Prerequisites

- Node.js 20.x or later
- Python 3.12 or later
- Docker & Docker Compose

## Installation & Setup

1. Clone the repository:
   ```
   git clone https://github.com/username/china-growth-game.git
   cd china-growth-game
   ```

2. Install dependencies:
   ```
   # Backend dependencies
   npm install
   
   # Frontend dependencies
   cd src && npm install
   cd ..
   
   # Economic model dependencies
   cd economic-model
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```

3. Set up environment:
   Create a `.env` file in the project root with the following variables:
   ```
   PORT=3000
   ECONOMIC_MODEL_URL=http://localhost:8000
   NODE_ENV=development
   ```

4. Start the development servers:
   ```
   # Start all services with Docker Compose
   docker-compose up
   
   # Or start services individually
   # Backend
   npm run dev
   
   # Frontend
   npm run start:react
   
   # Economic Model
   cd economic-model
   uvicorn app:app --reload --port 8000
   ```

5. Access the application:
   - Main application: http://localhost:3001
   - Backend API: http://localhost:3000
   - Economic model API: http://localhost:8000

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

