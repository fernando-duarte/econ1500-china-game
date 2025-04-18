#!/bin/bash
# Script to generate requirements.lock from requirements.txt

# Exit on error
set -e

echo "Generating requirements.lock from requirements.txt"

# Create a temporary virtual environment
python -m venv temp_venv

# Activate the virtual environment
source temp_venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Generate pinned dependencies
pip freeze > requirements.lock

# Clean up
deactivate
rm -rf temp_venv

echo "Successfully generated requirements.lock" 