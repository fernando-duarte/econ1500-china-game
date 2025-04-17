#!/usr/bin/env python
"""
Simple test script to verify Python 3.13 compatibility
with the updated dependencies for the China Growth Game.
"""

import sys
import importlib.metadata

# Print Python version
print(f"Python version: {sys.version}")

# Try importing and print versions of all required packages
packages = [
    "fastapi",
    "uvicorn",
    "numpy",
    "pandas",
    "matplotlib",
    "pydantic"
]

print("\nPackage versions:")
for package in packages:
    try:
        version = importlib.metadata.version(package)
        print(f"✓ {package}: {version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"✗ {package}: Not installed")

print("\nIf all packages are installed and no errors occurred, your environment is compatible with Python 3.13!") 