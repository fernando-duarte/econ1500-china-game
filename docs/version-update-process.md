# Version Update Process

This document outlines the procedure for updating versions of dependencies in the China Growth Game project.

## Step 1: Update the Version Management Document

First, update the central version management document:
```
docs/version-management.md
```

Make sure to:
- Update the specific version number
- Verify compatibility with other dependencies
- Note any breaking changes

## Step 2: Update Core Configuration Files

### Python Dependencies
1. Update `economic-model/requirements.txt`
2. Regenerate the lock file:
   ```bash
   cd model
   ./generate-lock.sh
   ```

### Node.js Dependencies
1. Update `frontend/package.json` and `backend/package.json`
2. Update `frontend/package-resolutions.json` if needed for security patches
3. Run `npm install` in both directories to update package-lock.json

### Docker Configuration
1. Update versions in `docker/image-versions.env` if base image versions changed

## Step 3: Run Compatibility Tests

1. Rebuild Docker images:
   ```bash
   docker-compose build
   ```

2. Run all tests:
   ```bash
   # Frontend tests
   cd frontend
   npm test
   
   # Backend tests
   cd backend
   npm test
   
   # Model tests
   cd economic-model
   pytest
   ```

## Step 4: Update Documentation

1. Update `specs.md` if the version changes are part of the core requirements
2. Update `readme.md` to reflect current versions
3. Update any version-specific documentation

## Step 5: Create Version Update PR

1. Create a branch with naming convention: `version-update-YYYY-MM-DD`
2. Commit all version changes with detailed commit message
3. Submit PR with version update checklist completed

## Version Update Checklist

- [ ] Updated central version management document
- [ ] Updated all relevant package files
- [ ] Generated new lock files
- [ ] Verified compatibility with other dependencies
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Confirmed Docker builds work
- [ ] Changelog updated with notable changes 