# China's Growth Game - Unified Codebase

This project simulates China's economic growth from 1980 to 2025 for educational purposes, allowing students to make policy decisions and see their impact on economic outcomes.

## Codebase Structure

The codebase has been consolidated to eliminate redundancies and follow a clean architecture:

```
china-growth-game/
├── economic-model/        # Python Solow model implementation
│   ├── app.py             # FastAPI server for the economic model
│   ├── solow_core.py      # Core Solow model implementation
│   ├── constants.py       # Centralized constants
│   └── ...                # Other supporting modules
├── services/              # Node.js service layer
│   └── economic-model-service.js  # Service for interacting with the model
├── frontend/              # React frontend code
├── build/                 # Built frontend assets
├── unified-server.js      # Unified Express + Socket.IO server
├── .env.unified           # Consolidated environment configuration
└── README.md              # Documentation
```

## Key Components

### Economic Model Layer

The economic model implementation has been consolidated into a single source of truth:

- `economic-model/solow_core.py`: Core implementation of the Solow growth model
- `economic-model/app.py`: API server for the model
- `economic-model/constants.py`: Centralized economic constants and parameters

### Service Layer

- `services/economic-model-service.js`: Unified service for interacting with the economic model
  - Supports both mock mode and API integration
  - Provides consistent interface for game state management

### Unified Server

The server implementations have been consolidated into a single unified server:

- `unified-server.js`: 
  - Express server for REST API
  - Socket.IO for real-time communication
  - Integrated with the economic model service

## Getting Started

1. Clone the repository
2. Copy `.env.unified` to `.env`
3. Install dependencies:
   ```
   npm install
   cd economic-model && pip install -r requirements.txt
   ```

4. Start the economic model (in a separate terminal):
   ```
   cd economic-model
   uvicorn app:app --reload --port 8000
   ```

5. Start the unified server:
   ```
   node unified-server.js
   ```

6. Build and start the frontend (in development mode):
   ```
   cd frontend
   npm run start
   ```

## Game Flow

1. Professor/instructor creates a new game
2. Students form teams and join the game
3. Each round, teams make policy decisions:
   - Setting savings rate
   - Choosing exchange rate policy
4. After all teams submit decisions, the instructor advances to the next round
5. The economic model calculates outcomes for each team
6. Rankings are updated and visualizations are refreshed
7. After 10 rounds (1980-2025), final scores are calculated

## API Documentation

### REST API Endpoints

- `GET /api/game`: Get current game state
- `POST /api/game/start`: Start a new game
- `POST /api/game/advance`: Advance to the next round
- `GET /api/teams`: Get all teams
- `GET /api/teams/:id`: Get a specific team
- `POST /api/teams`: Create a new team
- `POST /api/teams/:teamId/decisions`: Submit a decision for a team

### Socket.IO Events

- `joinTeam`: Join a team's room
- `updateTeam`: Submit team decisions
- `startGame`: Start the game
- `pauseGame`: Pause the game
- `nextRound`: Advance to the next round
- `gameState`: Emitted when game state changes
- `teamUpdate`: Emitted when a team's state changes

## Configuration

The `.env.unified` file contains all configurable settings for the application, including:

- Server port and environment
- CORS settings
- Economic model URL
- Game parameters
- Mock mode toggle

## Mock Mode

For development or demonstration purposes, the application can run in "mock mode" without requiring the Python economic model:

1. Set `USE_MOCK_MODEL=true` in your `.env` file
2. Start only the unified server

## Testing

Run tests with:
```
npm test
```

## Deployment

For production deployment:

1. Build the frontend:
   ```
   cd frontend && npm run build
   ```

2. Use the Docker configuration:
   ```
   docker-compose -f docker-compose.prod.unified.yml up -d
   ```

## License

[MIT License](LICENSE) 