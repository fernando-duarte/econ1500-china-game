# Immutable Environments

This document describes our approach to ensuring immutable environments between CI and local development.

## Overview

Immutable environments are critical for reliable software development and testing. They ensure that:

1. Code that works in development will work the same way in CI and production
2. Bugs can be more easily reproduced across environments
3. "Works on my machine" problems are minimized

## Implementation

Our approach uses these key techniques:

### 1. Shared Image Version Configuration

All Docker image versions are defined in a single source of truth:
- Location: `docker/image-versions.env`
- Usage: This file is imported by both the local development environment and CI

### 2. Docker-in-Docker for CI

Our GitHub Actions workflow uses Docker-in-Docker to run the same containers as local development:
- Builds images with the same versions and tags
- Runs services with the same docker-compose configuration
- Tests against the running containers

### 3. Versioned Base Images

All Dockerfiles accept version arguments to ensure consistent base images:
- Frontend and Backend: Uses specific Node.js version
- Model: Uses specific Python version

### 4. Environment Variables

The system imports version environment variables in a consistent way:
- Local development: Variables loaded via `.env` file
- CI: Variables loaded and exported to GitHub Actions environment

## Usage

### Local Development

Run local development with:

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps
```

### Updating Versions

To update Docker image versions:

1. Edit `docker/image-versions.env`
2. Rebuild images with `docker-compose build`
3. Restart services with `docker-compose up -d`

### CI Pipeline

The CI pipeline automatically:

1. Loads the same image versions as local development
2. Builds Docker images with those versions
3. Runs tests against those same images

## Benefits

This approach provides several advantages:

- **Consistency**: Development and CI environments use exactly the same images
- **Versioning**: All dependency versions are explicitly defined in one place
- **Reproducibility**: CI runs and local development use identical environments
- **Simplicity**: Single source of truth for all versions 