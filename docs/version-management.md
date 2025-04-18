# Version Management

This document serves as the single source of truth for all version information in the China Growth Game project.

## Core Technologies

| Technology | Version | Used In |
|------------|---------|---------|
| Node.js    | 20.13.1 | Frontend, Backend |
| Python     | 3.12.2  | Economic Model |
| Docker     | 26.1.4  | Deployment |

## Frontend Dependencies

| Package       | Version | Description |
|---------------|---------|-------------|
| React         | 18.2.0  | UI library |
| Material UI   | 5.15.14 | Component library |
| Chart.js      | 4.4.3   | Data visualization |
| socket.io-client | 4.7.5 | Real-time communication |

## Backend Dependencies

| Package    | Version | Description |
|------------|---------|-------------|
| Express    | 5.1.0   | Web framework |
| Socket.IO  | 4.7.5   | Real-time server |
| Axios      | 1.8.4   | HTTP client |
| Cors       | 2.8.5   | CORS middleware |

## Economic Model Dependencies

| Package    | Version | Description |
|------------|---------|-------------|
| FastAPI    | 0.110.0 | API framework |
| Uvicorn    | 0.27.1  | ASGI server |
| NumPy      | 1.26.4  | Numerical computing |
| Pandas     | 2.2.2   | Data analysis |
| Matplotlib | 3.8.3   | Data visualization |
| Pydantic   | 2.6.3   | Data validation |

## Version Update Process

1. When updating any package version, first update this document
2. Then update the relevant package.json or requirements.txt files
3. Update Docker image versions in docker/image-versions.env
4. Run dependency compatibility checks
5. Update all documentation references

## Version Compatibility Rules

- Frontend and Backend must use the same Socket.IO version
- Economic Model must use FastAPI, NumPy, and Pandas versions that are compatible with Python 3.12.2
- All Node.js packages must be compatible with Node.js 20.13.1

## Managing Docker Images

- All Docker images use the standardized versions defined in docker/image-versions.env
- Production images use the same base versions with a "-prod" suffix
- Volume names follow the pattern "solow-game-[component]-[resource]-[env]" 