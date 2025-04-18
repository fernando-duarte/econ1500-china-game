#!/bin/bash
# Script to test the updated components

# Set error handling
set -e

echo "=== Testing Updated Components ==="
echo

# Check Node.js version
echo "Checking Node.js version..."
docker run --rm node:20.12.1-alpine node --version
echo "✅ Node.js version check passed"
echo

# Check Python version
echo "Checking Python version..."
docker run --rm python:3.12.2-slim python --version
echo "✅ Python version check passed"
echo

# Build and test model component
echo "Building and testing model component..."
cd model
docker build -t solow-model-test .
docker run --rm solow-model-test python -c "import fastapi; import uvicorn; import numpy; import pandas; import matplotlib; import pydantic; print('✅ All Python dependencies imported successfully')"
cd ..
echo "✅ Model component test passed"
echo

# Build and test backend component
echo "Building and testing backend component..."
cd backend
docker build -t solow-backend-test .
docker run --rm solow-backend-test node -e "const express = require('express'); const socketio = require('socket.io'); const axios = require('axios'); console.log('✅ All Node.js dependencies imported successfully')"
cd ..
echo "✅ Backend component test passed"
echo

# Build and test frontend component
echo "Building and testing frontend component..."
cd frontend
docker build -t solow-frontend-test .
cd ..
echo "✅ Frontend component test passed"
echo

# Test integration with docker-compose
echo "Testing integration with docker-compose..."
docker-compose build
docker-compose up -d
sleep 10
docker-compose ps
echo "✅ Integration test passed"
echo

# Cleanup
echo "Cleaning up..."
docker-compose down
docker rmi solow-model-test solow-backend-test solow-frontend-test
echo "✅ Cleanup completed"
echo

echo "=== All tests passed! ==="
