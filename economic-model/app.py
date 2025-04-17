from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
import numpy as np
import uvicorn
import sys
import os

# Add the current directory to sys.path if it's not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import the GameState
from game_state import GameState

# Create a single instance of the game state to be used for all requests
# This implements in-memory state management as requested
game_state = GameState()

app = FastAPI(title="China's Growth Game Economic Model API")

# Pydantic models for API requests and responses 

# Add a main block to start the server when run directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 