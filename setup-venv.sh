#!/bin/bash

# Script to set up a Python 3.12 virtual environment for the China Growth Game

# Exit on error
set -e

echo "Setting up Python 3.12 virtual environment..."

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is not installed. Please install it first."
    echo "On macOS: brew install python@3.12"
    echo "On Ubuntu: sudo apt install python3.12 python3.12-venv"
    exit 1
fi

# Remove existing virtual environments
echo "Removing existing virtual environments..."
rm -rf venv-py312 china-growth-game/economic-model/venv china-growth-game/economic-model/new-venv

# Create a new virtual environment
echo "Creating new virtual environment with Python 3.12..."
python3.12 -m venv venv-py312

# Activate the virtual environment
echo "Activating virtual environment..."
source venv-py312/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create symbolic links for the model directories
echo "Creating symbolic links for model directories..."
mkdir -p china-growth-game/economic-model/venv
ln -sf ../../../venv-py312/bin china-growth-game/economic-model/venv/bin
mkdir -p model/venv
ln -sf ../../venv-py312/bin model/venv/bin

echo "Virtual environment setup complete!"
echo "To activate the environment, run: source venv-py312/bin/activate"
