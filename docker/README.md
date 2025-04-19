# Docker Configuration

This directory contains the Docker configuration for the China Growth Game project.

## Directory Structure

The project uses the following Dockerfiles located in their respective component directories:

- `frontend/Dockerfile`: Frontend development Dockerfile
- `frontend/Dockerfile.prod`: Frontend production Dockerfile
- `backend/Dockerfile`: Backend development Dockerfile
- `backend/Dockerfile.prod`: Backend production Dockerfile
- `model/Dockerfile`: Model development Dockerfile
- `model/Dockerfile.prod`: Model production Dockerfile

## Environment Variables

Environment variables are defined in the `.env` file (copy from `.env.example`). The main variables are:

- `NODE_VERSION`: Node.js version for frontend and backend
- `PYTHON_VERSION`: Python version for model services
- `FRONTEND_IMAGE`, `BACKEND_IMAGE`, `MODEL_IMAGE`: Docker image names
- `FRONTEND_VERSION`, `BACKEND_VERSION`, `MODEL_VERSION`: Docker image versions
- `FRONTEND_PORT`, `BACKEND_PORT`, `MODEL_PORT`: Service ports
- `ENABLE_CHINA_GAME`: Set to "true" to enable China Growth Game services
- `ENV_SUFFIX`: Suffix for volume names (dev, staging, prod)

## Docker Compose Files

- `docker-compose.yml`: Main Docker Compose file for development
- `docker-compose.prod.yml`: Production Docker Compose file

## Usage

### Development

```bash
# Start the main application
docker-compose up -d

# Stop all services
docker-compose down
```

### Production

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Stop all services
docker-compose -f docker-compose.prod.yml down
```

## Volumes

The following Docker volumes are used:

- `solow-game-frontend-modules-{env}`: Frontend node modules
- `solow-game-backend-modules-{env}`: Backend node modules
- `solow-game-model-deps-{env}`: Model Python dependencies
- `solow_game_model_data_{env}`: Model data (production only)

## Networks

All services are connected to the `solow-network` bridge network.

## Health Checks

All services include health checks to ensure they are running properly:

- Frontend: Checks if the web server is responding
- Backend: Checks the `/health` endpoint
- Model: Checks the `/health` endpoint

## Resource Limits

Production services have resource limits defined:

- Frontend: 0.5 CPU, 512MB memory
- Backend: 0.5 CPU, 512MB memory
- Model: 1.0 CPU, 1GB memory
