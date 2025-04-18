#!/bin/bash
# Script to start the development environment with consistent Docker image versions

set -e  # Exit on error

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load Docker image versions
source "$SCRIPT_DIR/docker/load-versions.sh"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible"
  exit 1
fi

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose down || true

# Build images with consistent versions
echo "Building Docker images..."
docker-compose build

# Start the services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
timeout=120
start_time=$(date +%s)

while true; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))
  
  if [ $elapsed -gt $timeout ]; then
    echo "Timeout waiting for services to be healthy"
    docker-compose logs
    exit 1
  fi
  
  # Check if all services are healthy
  healthy_count=$(docker-compose ps | grep -c 'healthy')
  service_count=$(docker-compose ps | grep -c 'Up')
  
  if [ "$healthy_count" -eq 3 ]; then  # 3 services: frontend, backend, model
    echo "All services are healthy!"
    break
  fi
  
  echo "Waiting for services to be healthy ($healthy_count/3 ready, elapsed: ${elapsed}s)"
  sleep 5
done

# Show service status
echo "Development environment is running:"
docker-compose ps

echo -e "\nAccess the application at: http://localhost:3000" 