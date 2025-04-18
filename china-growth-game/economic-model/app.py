from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
import numpy as np
import uvicorn
from game_state import GameState

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
    return game_state.get_game_state()

@app.post("/game/start", response_model=GameStateResponse)
def start_game():
    """Start the game with registered teams."""
    try:
        result = game_state.start_game()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/game/next-round")
def advance_to_next_round():
    """Advance to the next round, processing all team decisions."""
    try:
        result = game_state.advance_round()
        # Log the result for debugging
        import logging
        logging.debug(f"Advance round result: {result}")
        
        # If we got a successful result, return it
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # More detailed error reporting for debugging
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/game/state", response_model=GameStateResponse)
def get_game_state():
    """Get the current game state."""
    return game_state.get_game_state()

# Team management endpoints
@app.post("/teams/create")
def create_team(request: TeamCreateRequest):
    """Create a new team."""
    try:
        team = game_state.create_team(request.team_name)
        return team
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
        return decision
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/teams/{team_id}")
def get_team_state(team_id: str):
    """Get the state of a specific team."""
    try:
        return game_state.get_team_state(team_id)
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
    return game_state.rankings_manager.rankings

@app.get("/results/visualizations/{team_id}")
def get_team_visualizations(team_id: str):
    """Get visualization data for a specific team."""
    try:
        return game_state.get_team_visualizations(team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 