#!/bin/bash
# Script to migrate to the unified Docker configuration

set -e

echo "=== Migrating to Unified Docker Configuration ==="

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
fi

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down 2>/dev/null || true
docker-compose -f china-growth-game/docker-compose.yml down 2>/dev/null || true

# Create symbolic links to the unified docker-compose files
echo "Creating symbolic links to unified docker-compose files..."
ln -sf docker-compose.unified.yml docker-compose.yml
ln -sf docker-compose.prod.unified.yml docker-compose.prod.yml

echo "=== Migration Complete ==="
echo ""
echo "You can now use the following commands:"
echo "  docker-compose up -d                       # Start main application"
echo "  docker-compose --profile china-game up -d  # Start with China Growth Game"
echo ""
echo "For more information, see docker/README.md"
