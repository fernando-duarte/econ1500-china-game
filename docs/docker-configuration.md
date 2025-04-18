# Docker Configuration

This document describes the Docker configuration system used in the China Growth Game project.

## Overview

The project uses a template-based approach to Docker configuration to ensure consistency across environments and reduce redundancy. All Docker-related files are generated from templates, which are then customized for different environments.

## Key Components

### 1. Dockerfile Templates

Templates are stored in `docker/templates/` and include:

- `model.Dockerfile.template` - Template for the Python economic model service
- `frontend.Dockerfile.template` - Template for the React frontend
- `backend.Dockerfile.template` - Template for the Node.js backend

### 2. Docker Compose Files

- `docker-compose.yml` - Base configuration for all environments
- `docker-compose.prod.yml` - Production-specific overrides

### 3. Scripts

- `scripts/generate-dockerfile.sh` - Generates Dockerfiles from templates
- `scripts/build.sh` - Unified build script that handles the entire build process

## Usage

### Building for Development

```bash
./scripts/build.sh development
```

This will:
1. Parse version information from `versions.yaml`
2. Generate development Dockerfiles
3. Build Docker images using `docker-compose.yml`

### Building for Production

```bash
./scripts/build.sh production
```

This will:
1. Parse version information from `versions.yaml`
2. Generate production Dockerfiles
3. Build Docker images using both `docker-compose.yml` and `docker-compose.prod.yml`

### Running the Services

For development:
```bash
docker-compose up -d
```

For production:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Template Variables

The Dockerfile templates use the following variables:

### Common Variables
- `${NODE_VERSION}` - Node.js version
- `${PYTHON_VERSION}` - Python version
- `${SYSTEM_DEPENDENCIES}` - System dependencies to install
- `${CREATE_USER}` - Whether to create a non-root user
- `${PORT}` - Port to expose
- `${INCLUDE_HEALTHCHECK}` - Whether to include health checks

### Model-specific Variables
- `${USE_VENV}` - Whether to use a Python virtual environment
- `${REQUIREMENTS_PATH}` - Path to requirements files
- `${APP_PATH}` - Path to application code
- `${START_COMMAND}` - Command to start the application

### Frontend/Backend-specific Variables
- `${PACKAGE_PATH}` - Path to package.json
- `${BUILD_FOR_PRODUCTION}` - Whether to build for production

## Customization

To customize the Docker configuration:

1. Edit the template files in `docker/templates/`
2. Update the variable values in `scripts/generate-dockerfile.sh`
3. Run `./scripts/build.sh` to regenerate the Dockerfiles

## Benefits

This approach provides several advantages:

1. **Consistency** - All Dockerfiles follow the same pattern
2. **Maintainability** - Changes can be made in one place
3. **Environment-specific customization** - Different configurations for development and production
4. **Version management** - All versions are defined in a single source of truth

_Last updated: ${new Date().toISOString().split('T')[0]}_
