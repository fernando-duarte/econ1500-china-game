# Virtual Environment Setup

This document explains the virtual environment setup for the China Growth Game project.

## Python Version

The project uses Python 3.12 as specified in the README. This version provides a good balance of features, performance, and compatibility with the required libraries.

## Virtual Environment

A single virtual environment (`venv-py312`) is used for all Python components of the project. This simplifies dependency management and ensures consistency across different parts of the application.

## Dependencies

All dependencies are listed in the root `requirements.txt` file. This file consolidates dependencies from both the canonical and legacy model implementations.

## Setup

To set up the virtual environment, run the `setup-venv.sh` script in the project root:

```bash
./setup-venv.sh
```

This script will:
1. Check if Python 3.12 is installed
2. Remove any existing virtual environments
3. Create a new virtual environment with Python 3.12
4. Install all required dependencies
5. Create symbolic links for model directories

## Activation

To activate the virtual environment, run:

```bash
source venv-py312/bin/activate
```

## Model Directories

The script creates symbolic links from the model directories to the main virtual environment:

- `china-growth-game/economic-model/venv/bin` → `venv-py312/bin`
- `model/venv/bin` → `venv-py312/bin`

This allows the model code to use the same Python interpreter and packages while maintaining the expected directory structure.

## Troubleshooting

If you encounter issues with the virtual environment:

1. Make sure Python 3.12 is installed
2. Try removing the virtual environment and running the setup script again
3. Check for any error messages during the setup process
4. Verify that all required dependencies are installed correctly

## Legacy Virtual Environments

Previously, the project used multiple virtual environments:
- `venv-py312` (Python 3.12)
- `china-growth-game/economic-model/venv` (Python 3.12)
- `china-growth-game/economic-model/new-venv` (Python 3.9)

These have been consolidated into a single environment for simplicity and consistency.
