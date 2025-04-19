# Docker Configuration

This directory contains the Docker configuration for the China Growth Game project.

## Directory Structure

The project uses the following Dockerfiles located in their respective component directories:

- `frontend/Dockerfile`: Frontend Dockerfile
- `backend/Dockerfile`: Backend Dockerfile
- `model/Dockerfile`: Model Dockerfile

## Environment Variables

Environment variables are defined in the `.env` file (copy from `.env.example`). The main variables are:

- `NODE_VERSION`: Node.js version for frontend and backend
- `PYTHON_VERSION`: Python version for model services
- `FRONTEND_IMAGE`, `BACKEND_IMAGE`, `MODEL_IMAGE`: Docker image names
- `FRONTEND_VERSION`, `BACKEND_VERSION`, `MODEL_VERSION`: Docker image versions
- `FRONTEND_PORT`, `BACKEND_PORT`, `MODEL_PORT`: Service ports
- `ENABLE_CHINA_GAME`: Set to "true" to enable China Growth Game services
- `ENV_SUFFIX`: Suffix for volume names (dev, staging, prod)

## Docker Compose File

- `docker-compose.yml`: Docker Compose file for the application

## Usage

```bash
# Start the application
docker-compose up -d

# Stop all services
docker-compose down
```

## Volumes

The following Docker volumes are used:

- `frontend_node_modules`: Frontend node modules
- `backend_node_modules`: Backend node modules
- `model_python_deps`: Model Python dependencies

## Networks

All services are connected to the `solow-network` bridge network.

## Health Checks

All services include health checks to ensure they are running properly:

- Frontend: Checks if the web server is responding
- Backend: Checks the `/health` endpoint
- Model: Checks the `/health` endpoint


