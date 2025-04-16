# China's Growth Game

An interactive economic simulation game designed for undergraduate economics courses.

## Project Structure

```
china-growth-game/
├── app/                      # Node.js/Express backend and frontend
│   ├── public/               # Frontend assets
│   ├── routes/               # API routes
│   └── services/             # Backend services
├── economic-model/           # Python/FastAPI economic model
│   ├── app.py                # FastAPI application
│   ├── game_state.py         # In-memory game state management
│   ├── enhanced_solow_model.py # Enhanced Solow model with student decisions
│   ├── solow_model.py        # Original Solow model
│   └── test_model.py         # Unit tests for economic model
├── docker/                   # Docker configuration
└── docker-compose.yml        # Container orchestration
```

## Features

### Game Flow
- Create and manage teams (up to 10 teams per game)
- Start game and advance through rounds
- Process student decisions (savings rate and exchange rate policy)
- Trigger economic events at specific years
- Track and display rankings

### Economic Model
- Enhanced Solow growth model with trade components
- Student decisions impact growth, capital accumulation, and trade balance
- Historical events (WTO entry, financial crisis, etc.) affect the economy
- In-memory game state management

### Visualizations
- GDP growth charts
- Trade balance visualization
- Consumption vs. savings breakdowns

## Setup Instructions

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Node.js](https://nodejs.org/) v20.11.1 or higher
- [Python](https://www.python.org/) v3.12.2 or higher

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd china-growth-game
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Install Python dependencies:
   ```
   cd economic-model
   pip install -r requirements.txt
   cd ..
   ```

### Running the Application

#### Using Docker (Recommended)

1. Build and start the containers:
   ```
   docker-compose up --build
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Economic Model API: http://localhost:8000

#### Without Docker

1. Start the Economic Model API:
   ```
   cd economic-model
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. In a separate terminal, start the Node.js server:
   ```
   npm run dev
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Economic Model API: http://localhost:8000

## API Endpoints

### Game Flow
- `POST /api/game/init` - Initialize a new game
- `POST /api/game/start` - Start the game with registered teams
- `POST /api/game/next-round` - Advance to the next round
- `GET /api/game/state` - Get current game state

### Team Management
- `POST /api/teams/create` - Create a new team
- `POST /api/teams/decisions` - Submit a team's decision
- `GET /api/teams/:teamId` - Get a team's state

### Results and Rankings
- `GET /api/results/rankings` - Get current rankings
- `GET /api/results/leaderboard` - Get formatted leaderboard
- `GET /api/results/visualizations/:teamId` - Get team visualization data

## Testing

Run unit tests for the economic model:
```
cd economic-model
python -m unittest test_model.py
```

## Development

- The backend server uses nodemon for hot reloading
- The Python API uses uvicorn with reload enabled
- The Docker setup includes volume mounting for live code changes 