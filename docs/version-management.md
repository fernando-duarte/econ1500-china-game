# Version Management

This document describes how to manage versions in the project.

## Overview

All version information is stored in a single source of truth: `versions.yaml`.
This file is used to generate all other version-specific files.

## Current Versions

### Core Technologies

| Technology | Version |
|------------|---------|
| Node.js    | 20.13.1 |
| Python     | 3.12.2 |
| Docker     | 26.1.4 |

### Frontend Dependencies

| Package       | Version |
|---------------|---------|
| React         | 18.2.0 |
| Material UI   | 5.15.14 |
| Chart.js      | 4.4.3 |
| Socket.IO Client | 4.7.5 |
| Axios         | 1.8.4 |

### Backend Dependencies

| Package    | Version |
|------------|---------|
| Express    | 5.1.0 |
| Socket.IO  | 4.7.5 |
| AWS SDK    | 2.1571.0 |
| Node Vault | 0.10.2 |
| Axios      | 1.8.4 |

### Model Dependencies

| Package    | Version |
|------------|---------|
| FastAPI    | 0.115.12 |
| Uvicorn    | 0.34.1 |
| NumPy      | 1.26.4 |
| Pandas     | 2.2.3 |
| Matplotlib | 3.9.4 |
| Pydantic   | 2.11.3 |

### Docker Images

| Image     | Version |
|-----------|---------|
| Frontend  | 1.1.0 |
| Backend   | 1.1.0 |
| Model     | 1.1.0 |

## Updating Versions

To update a version, use the provided script:

```bash
./scripts/update-version.sh <component> <package> <version>
```

Example:
```bash
./scripts/update-version.sh frontend react 18.2.0
```

This will:
1. Update the version in `versions.yaml`
2. Regenerate all derived files:
   - `version-management.js`
   - `docker/image-versions.env`
   - `model/requirements.txt`
   - etc.

## Generated Files

The following files are automatically generated from `versions.yaml`:

- `version-management.js` - JavaScript module for Node.js applications
- `docker/image-versions.env` - Environment variables for Docker
- `model/requirements.txt` - Python dependencies
- `china-growth-game/economic-model/requirements.txt` - Python dependencies for China Growth Game

**Important:** Do not edit these files directly. Always edit `versions.yaml` instead.

_Last updated: 2025-04-18_
