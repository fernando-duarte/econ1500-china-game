#!/usr/bin/env python
"""
Run script for the China Growth Game API.

This script starts the FastAPI application using uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("economic_model_py.app:app", host="0.0.0.0", port=8000, reload=True)
