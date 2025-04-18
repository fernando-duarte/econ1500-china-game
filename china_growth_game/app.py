"""
FastAPI application for the China Growth Game.

This module contains the FastAPI application that serves as the API
for the China Growth Game.
"""

from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
import numpy as np
import uvicorn
import logging
import sys
import json
import traceback
from china_growth_game.economic_model.game.game_state import GameState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Helper function to handle numpy serialization
def numpy_safe_encoder(obj):
    """Convert numpy types to standard Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):
        return obj.item()
    return obj

# Add the canonical path to facilitate imports when running from different directories
import os
import sys
canonical_path = os.path.dirname(os.path.abspath(__file__))
if canonical_path not in sys.path:
    sys.path.append(canonical_path)
    logger.info(f"Added canonical path to sys.path: {canonical_path}")

try:
    from china_growth_game.economic_model.core.solow_core import get_default_parameters
    logger.info("Successfully imported canonical implementation")
except ImportError as e:
    logger.error(f"Error importing canonical implementation: {e}")

# Create a single instance of the game state to be used for all requests
# This implements in-memory state management as requested
game_state = GameState()

app = FastAPI(title="China's Growth Game Economic Model API")

# Pydantic models for API requests and responses
class InitialConditions(BaseModel):
    Y: float
    K: float
    L: float
    H: float
    A: float
    NX: float

class Parameters(BaseModel):
    alpha: float
    delta: float
    g: float
    theta: float
    phi: float
    s: float  # Savings rate (set by students)
    beta: float
    n: float
    eta: float

class SimulationRequest(BaseModel):
    initial_year: int
    initial_conditions: InitialConditions
    parameters: Parameters
    years: List[int]
    historical_data: Optional[Dict] = None

class SimulationResponse(BaseModel):
    results: Dict[str, List[float]]

class TeamCreateRequest(BaseModel):
    team_name: Optional[str] = None

class DecisionSubmitRequest(BaseModel):
    team_id: str
    savings_rate: float = Field(..., ge=0.01, le=0.99)
    exchange_rate_policy: str = Field(..., pattern='^(undervalue|market|overvalue)$')

    @field_validator('savings_rate')
    @classmethod
    def validate_savings_rate(cls, v):
        if not (0.01 <= v <= 0.99):
            raise ValueError("Savings rate must be between 1% and 99%")
        return v

    @field_validator('exchange_rate_policy')
    @classmethod
    def validate_exchange_rate_policy(cls, v):
        if v not in ["undervalue", "market", "overvalue"]:
            raise ValueError("Exchange rate policy must be 'undervalue', 'market', or 'overvalue'")
        return v

class GameStateResponse(BaseModel):
    game_id: str
    current_round: int
    current_year: int
    teams: Dict[str, Dict[str, Any]]
    rankings: Dict[str, List[str]]
    game_started: bool
    game_ended: bool

class TeamEditNameRequest(BaseModel):
    new_name: str

@app.get("/")
def read_root():
    return {"message": "China's Growth Game Economic Model API"}

@app.get("/health")
def health_check():
    """Health check endpoint for container health monitoring."""
    return {"status": "ok", "message": "Economic model service is running"}

# Game flow endpoints
@app.post("/game/init", response_model=GameStateResponse)
def initialize_game():
    """Initialize a new game."""
    global game_state
    game_state = GameState()  # Reset the game state
    state = game_state.get_game_state()
    # Convert numpy types to Python types
    return json.loads(json.dumps(state, default=numpy_safe_encoder))

@app.post("/game/start", response_model=GameStateResponse)
def start_game():
    """Start the game with registered teams."""
    try:
        result = game_state.start_game()
        # Convert numpy types to Python types
        return json.loads(json.dumps(result, default=numpy_safe_encoder))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/game/next-round")
def advance_to_next_round():
    """Advance to the next round, processing all team decisions."""
    try:
        # Add more detailed logging
        logger.info("Starting advance_to_next_round()")
        print("Starting advance_to_next_round()", file=sys.stderr)
        sys.stderr.flush()

        try:
            result = game_state.advance_round()
            logger.info(f"advance_round() returned: {result}")
            print(f"advance_round() returned", file=sys.stderr)
            sys.stderr.flush()
        except Exception as internal_e:
            logger.error(f"Exception in game_state.advance_round(): {str(internal_e)}")
            print(f"Exception in game_state.advance_round(): {str(internal_e)}", file=sys.stderr)
            tb = traceback.format_exc()
            logger.error(f"Traceback: {tb}")
            print(f"Traceback: {tb}", file=sys.stderr)
            sys.stderr.flush()
            raise

        # Ensure result can be serialized
        try:
            # Test if the result can be serialized - this will raise an exception if it fails
            json.dumps(result, default=numpy_safe_encoder)
            logger.info("Result successfully serialized to JSON")
            print("Result successfully serialized to JSON", file=sys.stderr)
            sys.stderr.flush()
            # Convert numpy types to Python types
            return json.loads(json.dumps(result, default=numpy_safe_encoder))
        except TypeError as e:
            # If serialization fails, log the error and handle it
            logger.error(f"JSON serialization error: {str(e)}")
            print(f"JSON serialization error: {str(e)}", file=sys.stderr)
            sys.stderr.flush()
            # Try to identify problematic values
            fixed_result = {}
            for key, value in result.items():
                try:
                    json.dumps({key: value}, default=numpy_safe_encoder)
                    fixed_result[key] = value
                except TypeError:
                    logger.error(f"Key {key} has non-serializable value: {value}")
                    print(f"Key {key} has non-serializable value: {value}", file=sys.stderr)
                    sys.stderr.flush()
                    # Try to convert problematic types
                    if hasattr(value, 'tolist'):  # For numpy arrays
                        fixed_result[key] = value.tolist()
                    elif hasattr(value, 'item'):  # For numpy scalars
                        fixed_result[key] = value.item()
                    else:
                        fixed_result[key] = str(value)  # Last resort: convert to string
            return fixed_result

    except ValueError as e:
        logger.error(f"ValueError in advance_to_next_round: {str(e)}")
        print(f"ValueError in advance_to_next_round: {str(e)}", file=sys.stderr)
        tb = traceback.format_exc()
        logger.error(tb)
        print(tb, file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # More detailed error reporting for debugging
        logger.error(f"Exception in advance_to_next_round: {str(e)}")
        print(f"Exception in advance_to_next_round: {str(e)}", file=sys.stderr)
        tb = traceback.format_exc()
        logger.error(tb)
        print(tb, file=sys.stderr)
        sys.stderr.flush()
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/game/state", response_model=GameStateResponse)
def get_game_state():
    """Get the current game state."""
    state = game_state.get_game_state()
    # Convert numpy types to Python types
    return json.loads(json.dumps(state, default=numpy_safe_encoder))

# Team management endpoints
@app.post("/teams/create")
def create_team(request: TeamCreateRequest):
    """Create a new team."""
    try:
        team = game_state.create_team(request.team_name)
        # Convert numpy types to Python types
        return json.loads(json.dumps(team, default=numpy_safe_encoder))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/teams/decisions")
def submit_decision(request: DecisionSubmitRequest):
    """Submit a team's decision for the current round."""
    try:
        decision = game_state.submit_decision(
            request.team_id,
            request.savings_rate,
            request.exchange_rate_policy
        )
        # Convert numpy types to Python types
        return json.loads(json.dumps(decision, default=numpy_safe_encoder))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/teams/{team_id}")
def get_team_state(team_id: str):
    """Get the state of a specific team."""
    try:
        team_state = game_state.get_team_state(team_id)
        # Convert numpy types to Python types
        return json.loads(json.dumps(team_state, default=numpy_safe_encoder))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/teams/{team_id}/edit-name")
def edit_team_name(team_id: str = Path(...), request: TeamEditNameRequest = None):
    """Edit a team's name, enforcing uniqueness and appropriateness."""
    try:
        team = game_state.team_manager.edit_team_name(team_id, request.new_name)
        return team
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Results and visualization endpoints
@app.get("/results/rankings")
def get_rankings():
    """Get current rankings."""
    rankings = game_state.rankings_manager.rankings
    # Convert numpy types to Python types
    return json.loads(json.dumps(rankings, default=numpy_safe_encoder))

@app.get("/results/visualizations/{team_id}")
def get_team_visualizations(team_id: str):
    """Get visualization data for a specific team."""
    try:
        visualizations = game_state.get_team_visualizations(team_id)
        # Convert numpy types to Python types
        return json.loads(json.dumps(visualizations, default=numpy_safe_encoder))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
