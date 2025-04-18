#!/bin/bash
# Unified build script for the China Growth Game

set -e

ENV=${1:-development}
COMPONENTS=("model" "frontend" "backend")

# Display header
echo "=========================================="
echo "China Growth Game - Build Script"
echo "Environment: $ENV"
echo "=========================================="

# Check if required tools are installed
command -v node >/dev/null 2>&1 || { echo "Error: Node.js is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is required but not installed."; exit 1; }

# Ensure version files are up to date
echo "Updating version files..."
if [ ! -f "versions.yaml" ]; then
  echo "Error: versions.yaml not found. This file is required."
  exit 1
fi

# Install js-yaml if needed
if ! node -e "require('js-yaml')" >/dev/null 2>&1; then
  echo "Installing js-yaml package..."
  npm install --no-save js-yaml
fi

# Parse versions
echo "Parsing version information..."
node scripts/parse-versions.js

# Source environment variables
source docker/image-versions.env
echo "Using Node.js version: $NODE_VERSION"
echo "Using Python version: $PYTHON_VERSION"

# Generate Dockerfiles for each component
echo "Generating Dockerfiles..."
for component in "${COMPONENTS[@]}"; do
  echo "- Generating $component Dockerfile for $ENV environment"
  ./scripts/generate-dockerfile.sh "$component" "$ENV"
done

# Build Docker images
echo "Building Docker images..."
if [ "$ENV" == "production" ]; then
  export ENV_SUFFIX="prod"
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
else
  export ENV_SUFFIX="dev"
  docker-compose build
fi

echo "=========================================="
echo "Build completed successfully!"
echo "To start the services, run:"
if [ "$ENV" == "production" ]; then
  echo "docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
else
  echo "docker-compose up -d"
fi
echo "=========================================="
