#!/bin/bash

# Start script for China's Growth Game
# This script handles starting the application

# Set up environment
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
fi

# Start options
if [ "$1" = "docker" ]; then
  # Start using Docker
  echo "Starting with Docker..."
  docker-compose up -d
elif [ "$1" = "model" ]; then
  # Start just the model
  echo "Starting just the economic model..."
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn economic_model_py.app:app --reload --port 8000
elif [ "$1" = "frontend" ]; then
  # Start just the frontend
  echo "Starting just the frontend..."
  cd china-growth-game
  npm install
  npm run start:react
else
  # Default - start everything locally
  echo "Starting all components..."
  # Setup Python environment
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  # Start the application
  npm install
  npm run start:all
fi