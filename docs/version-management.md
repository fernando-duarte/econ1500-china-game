# Version Management

This document serves as the single source of truth for all version information in the China Growth Game project.

## Version Management Philosophy

The project follows these principles for version management:

1. **Single Source of Truth**: All version information is centralized in the `version-management.js` file
2. **Exact Version Pinning**: All dependencies use exact version numbers (no ^ or ~ prefixes)
3. **Immutable Environments**: Development, testing, and production environments use identical versions
4. **Consistent Tooling**: Node.js and Python versions are standardized across all components
5. **Automated Validation**: Version consistency is automatically validated in CI/CD pipelines

## Core Technologies

| Technology | Version | Used In |
|------------|---------|---------|
| Node.js    | 20.13.1 | Frontend, Backend |
| Python     | 3.12.2 | Economic Model |
| Docker     | 26.1.4  | Deployment |

## Frontend Dependencies

| Package       | Version | Description |
|---------------|---------|-------------|
| React         | 18.2.0 | UI library |
| Material UI   | 5.15.14 | Component library |
| Chart.js      | 4.4.3 | Data visualization |
| socket.io-client | 4.7.5 | Real-time communication |

## Backend Dependencies

| Package    | Version | Description |
|------------|---------|-------------|
| Express    | 5.1.0 | Web framework |
| Socket.IO  | 4.7.5 | Real-time server |
| Axios      | 1.8.4   | HTTP client |
| Cors       | 2.8.5   | CORS middleware |

## Economic Model Dependencies

| Package    | Version | Description |
|------------|---------|-------------|
| FastAPI    | 0.115.12 | API framework |
| Uvicorn    | 0.34.1 | ASGI server |
| NumPy      | 1.26.4 | Numerical computing |
| Pandas     | 2.2.3 | Data analysis |
| Matplotlib | 3.9.4   | Data visualization |
| Pydantic   | 2.11.3  | Data validation |

## China Growth Game Component

| Package    | Version | Description |
|------------|---------|-------------|
| Express    | 4.21.2  | Web framework |
| Material UI| 5.12.3  | Component library |
| FastAPI    | 0.110.0 | API framework |
| Uvicorn    | 0.27.1  | ASGI server |
| Pandas     | 2.2.2   | Data analysis |

## Version Management Tools

The project includes several tools to help manage versions:

### 1. Centralized Version Definition

The `version-management.js` file serves as the programmatic source of truth for all version information:

```javascript
// Example of version-management.js
module.exports = {
  core: {
    node: '20.13.1',
    python: '3.12.2',
    // ...
  },
  // ...
};
```

### 2. Version Update Script

The `scripts/update-versions.js` script updates version information across the codebase:

```bash
# Update all version information
node scripts/update-versions.js
```

### 3. Python Requirements Generator

The `scripts/generate-python-locks.sh` script generates `requirements.lock` files from `requirements.txt`:

```bash
# Generate requirements.lock files
./scripts/generate-python-locks.sh
```

### 4. Version Validation Script

The `scripts/validate-versions.js` script validates version consistency:

```bash
# Validate version consistency
node scripts/validate-versions.js
```

## Version Update Process

Follow these steps when updating versions:

1. **Update the Central Definition**:
   - Edit `version-management.js` with the new version information
   - Update this document with the new versions
   - Document any breaking changes or compatibility issues

2. **Run the Update Script**:
   ```bash
   node scripts/update-versions.js
   ```

3. **Generate Python Lock Files**:
   ```bash
   ./scripts/generate-python-locks.sh
   ```

4. **Validate Version Consistency**:
   ```bash
   node scripts/validate-versions.js
   ```

5. **Test the Changes**:
   ```bash
   # Run all tests
   npm test
   
   # Build and test with Docker
   docker-compose build
   docker-compose up -d
   # Run integration tests
   ```

6. **Update the Changelog**:
   - Document the version changes in `CHANGELOG.md`

7. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Update dependencies to latest versions"
   git push
   ```

## Version Compatibility Rules

- Frontend and Backend must use the same Socket.IO version
- Economic Model must use FastAPI, NumPy, and Pandas versions that are compatible with Python 3.12.2
- All Node.js packages must be compatible with Node.js 20.13.1
- China Growth Game component may use different versions than the main components, but these should be aligned in future releases

## Version Compatibility Matrix

| Component | Node.js | Python | React | Express | FastAPI |
|-----------|---------|--------|-------|---------|------------|
| Frontend  | 20.13.1 | -      | 18.2.0| -       | -          |
| Backend   | 20.13.1 | -      | -     | 5.1.0   | -          |
| Model     | -       | 3.12.2 | -     | -       | 0.115.12   |
| China Game| 20.13.1 | 3.12.2 | 18.2.0| 4.21.2  | 0.110.0    |

## Managing Docker Images

- All Docker images use the standardized versions defined in docker/image-versions.env
- Production images use the same base versions with a "-prod" suffix
- Volume names follow the pattern "solow-game-[component]-[resource]-[env]"

## Troubleshooting

### Common Issues

1. **Version Mismatch in Docker**:
   - Check `docker/image-versions.env` and Dockerfiles
   - Ensure Docker Compose is using the correct environment variables

2. **Python Dependency Conflicts**:
   - Check for conflicts between dependencies in `requirements.lock`
   - Consider using a tool like `pip-tools` for more advanced dependency resolution

3. **Node.js Dependency Conflicts**:
   - Check for peer dependency warnings in `npm install` output
   - Use `npm ls <package>` to check for multiple versions of the same package
