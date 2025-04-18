# Update Guide

This document provides guidance on updating the China Growth Game application components.

## Version 1.1.0 Update

The 1.1.0 update includes several dependency updates to improve security, performance, and maintainability.

### What's Updated

- **Node.js**: Updated from 20.10.0 to 20.12.1 (LTS)
- **FastAPI**: Updated from 0.100.0 to 0.110.0
- **Uvicorn**: Updated from 0.27.1 to 0.34.1
- **Pydantic**: Updated from 2.6.3 to 2.11.3
- **Pandas**: Updated from 2.2.2 to 2.2.3
- **Matplotlib**: Updated from 3.8.3 to 3.9.4
- **Python-dotenv**: Updated from 1.0.1 to 1.1.0
- **Typing-extensions**: Updated from 4.10.0 to 4.13.2

### Update Process

1. **Backup Your Data**
   - Before updating, ensure you have a backup of your data
   - Export any important game state if needed

2. **Update Dependencies**
   - Pull the latest code from the repository
   - Rebuild Docker images with the updated dependencies

   ```bash
   git pull
   docker-compose build --no-cache
   ```

3. **Test the Update**
   - Run the test script to verify all components work correctly

   ```bash
   ./test-updates.sh
   ```

4. **Deploy the Update**
   - Once testing is complete, deploy the updated application

   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Compatibility Notes

- **NumPy**: We've maintained NumPy at version 1.26.4 instead of upgrading to 2.0.x to ensure stability. NumPy 2.0 includes breaking changes that require more extensive testing.

- **API Compatibility**: The FastAPI and Pydantic updates maintain backward compatibility with existing API endpoints.

- **Frontend Dependencies**: All frontend dependencies remain compatible with the updated Node.js version.

## Troubleshooting

If you encounter issues after updating:

1. **Check Logs**
   ```bash
   docker-compose logs
   ```

2. **Verify Versions**
   ```bash
   # Check Node.js version
   docker-compose exec backend node --version
   
   # Check Python packages
   docker-compose exec model pip list
   ```

3. **Rollback if Necessary**
   ```bash
   # Revert to previous version
   git checkout v1.0.0
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Future Updates

- **NumPy 2.0**: We plan to evaluate NumPy 2.0.x in a future update after thorough testing
- **React 19**: We'll consider updating to React 19 once it's stable and well-tested with our dependencies
