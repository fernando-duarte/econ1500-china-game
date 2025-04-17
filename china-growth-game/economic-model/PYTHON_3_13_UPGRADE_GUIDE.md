# Python 3.13 Upgrade Guide for China Growth Game

This guide outlines the steps to upgrade the China Growth Game application to Python 3.13.

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) (recommended for managing Python versions)
- Access to a terminal/command line

## Step 1: Install Python 3.13

Using pyenv (recommended):

```bash
# Update pyenv
pyenv update

# Install Python 3.13
pyenv install 3.13.0

# Set Python 3.13 as local version for this project
cd /path/to/project
pyenv local 3.13.0
```

Alternatively, download Python 3.13 from [python.org](https://www.python.org/downloads/).

## Step 2: Create a New Virtual Environment

```bash
# Create a new virtual environment with Python 3.13
python -m venv venv-py313

# Activate the virtual environment
# On macOS/Linux:
source venv-py313/bin/activate
# On Windows:
# venv-py313\Scripts\activate
```

## Step 3: Install Updated Dependencies

```bash
# Install dependencies from the updated requirements.txt
pip install -r requirements.txt
```

## Step 4: Test Compatibility

Run the test script to verify all dependencies are working with Python 3.13:

```bash
python test_py313_compatibility.py
```

## Step 5: Test the Application

Start the application and verify it works correctly:

```bash
cd economic-model
uvicorn app:app --reload
```

## Troubleshooting

If you encounter any issues:

1. **TypeError: ForwardRef._evaluate() missing required keyword-only argument**:
   - Make sure you're using pydantic ≥ 2.6.3 and fastapi ≥ 0.110.0

2. **Package installation failures**:
   - Try installing packages one by one to identify problematic dependencies
   - Some packages might need to be compiled; ensure you have the necessary build tools

3. **Fallback option**:
   - If Python 3.13 compatibility issues persist, consider using Python 3.12 as an interim solution
   - Python 3.12 has better library support (70% of top packages vs. 49% for Python 3.13)

## Post-Upgrade Recommendations

1. Run comprehensive tests to ensure all functionality works as expected
2. Monitor application performance and resource usage for any changes
3. Consider updating any custom code that might rely on deprecated Python features

---

This guide was last updated on April 2025. 