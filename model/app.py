from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from typing import Dict, Any
import os

app = FastAPI(
    title="China's Growth Game Economic Model",
    description="Backend economic calculations for the China's Growth Game simulation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the China's Growth Game Economic Model API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/calculate")
async def calculate_growth(data: Dict[Any, Any]):
    """Calculate economic growth based on provided parameters."""
    try:
        # Sample calculation logic (replace with actual model)
        savings_rate = data.get("savings_rate", 0.3)
        capital = data.get("capital", 100)
        labor = data.get("labor", 100)
        
        # Simple Cobb-Douglas production function (Y = A * K^α * L^(1-α))
        alpha = 0.3  # Capital share
        productivity = 1.0  # Total factor productivity
        
        # Output calculation
        output = productivity * (capital ** alpha) * (labor ** (1 - alpha))
        
        # Investment and next period capital
        investment = savings_rate * output
        next_capital = capital * 0.9 + investment  # 10% depreciation
        
        return {
            "output": output,
            "investment": investment,
            "consumption": output - investment,
            "next_capital": next_capital
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 