# China's Growth Game

An interactive economic simulation game designed for undergraduate economics courses.

## Project Structure

```
china-growth-game/
├── app/                      # Node.js/Express backend and frontend
│   ├── public/               # Frontend assets
│   └── services/             # Backend services
├── economic-model/           # Python/FastAPI economic model
├── docker/                   # Docker configuration
└── docker-compose.yml        # Container orchestration
```

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

## Development

- The backend server uses nodemon for hot reloading
- The Python API uses uvicorn with reload enabled
- The Docker setup includes volume mounting for live code changes 