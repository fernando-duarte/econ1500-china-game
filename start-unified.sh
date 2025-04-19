#!/bin/bash

# Start script for China's Growth Game Unified Implementation
# This script handles starting both the economic model and the server

# Set up environment
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
fi

# Check if Python venv exists
if [ ! -d ".venv" ]; then
  echo "Setting up Python environment..."
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  echo "Python environment already exists."
fi

# Check for Node.js dependencies
if [ ! -d "node_modules" ]; then
  echo "Installing Node.js dependencies..."
  npm install
fi

# Start the application
if [ "$1" = "dev" ]; then
  # Development mode - start everything concurrently
  echo "Starting in development mode..."
  npm run dev:all
elif [ "$1" = "model" ]; then
  # Start just the model
  echo "Starting just the economic model..."
  source .venv/bin/activate
  uvicorn economic_model_py.app:app --reload --port 8000
elif [ "$1" = "server" ]; then
  # Start just the server
  echo "Starting just the server..."
  npm run dev
elif [ "$1" = "docker" ]; then
  # Start using Docker
  echo "Starting with Docker..."
  docker-compose up -d
elif [ "$1" = "docker-prod" ]; then
  # Start using Docker in production mode
  echo "Starting with Docker in production mode..."
  docker-compose -f docker-compose.prod.yml up -d
else
  # Default - start in mock mode
  echo "Starting with mock economic model (no Python needed)..."
  export USE_MOCK_MODEL=true
  npm start
fi