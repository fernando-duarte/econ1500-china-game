"""
Enhanced wrapper for the canonical economic model API.
This file redirects to the canonical implementation in china-growth-game/economic-model/app.py
while adding security features like API keys and rate limiting.
"""
import sys
import os
import logging
import importlib.util
import uvicorn
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path to the canonical implementation
canonical_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'china_growth_game', 'economic_model', 'app')

# Add the canonical path to sys.path if it's not already there
if canonical_path not in sys.path:
    sys.path.insert(0, canonical_path)
    logger.info(f"Added canonical path to sys.path: {canonical_path}")

# Import the app from the canonical implementation
try:
    # Check if the canonical implementation exists
    if not os.path.exists(os.path.join(canonical_path, 'app.py')):
        raise ImportError(f"Canonical implementation not found at {canonical_path}")

    # Import the app from the canonical implementation
    spec = importlib.util.spec_from_file_location("canonical_app",
                                                 os.path.join(canonical_path, 'app.py'))
    canonical_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canonical_app)

    # Get the FastAPI app from the canonical implementation
    app = canonical_app.app
    logger.info("Successfully imported canonical implementation")

    # Import the GameState class from the canonical implementation
    from game_state import GameState
    from china_growth_game.economic_model.utils.json_utils import (
        convert_numpy_values,
        numpy_safe_json_dumps,
        numpy_safe_json_loads,
        NumpyEncoder,
        CustomJSONResponse
    )

    # Create a single instance of the game state to be used for all requests
    game_state = GameState()

    # Import FastAPI components for security enhancements
    from fastapi import FastAPI, HTTPException, Depends, Path, Header, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import APIKeyHeader
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, field_validator
    from typing import Dict, List, Optional, Any

    # Simple API key authorization
    API_KEY_NAME = "X-API-Key"
    api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

    # Get API key from environment variable
    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
    if not ADMIN_API_KEY:
        if os.environ.get("ENVIRONMENT") == "production":
            raise ValueError("ADMIN_API_KEY must be set in production")
        else:
            ADMIN_API_KEY = "admin-dev-key"  # Only for development

    # Team authorization mapping (in production, this would be in a database)
    team_api_keys = {}

    # Simple rate limiting implementation
    class RateLimiter:
        def __init__(self, requests_per_minute=60):
            self.requests_per_minute = requests_per_minute
            self.request_counts = defaultdict(list)

        def is_rate_limited(self, client_id):
            # Get current timestamp
            now = time.time()
            minute_ago = now - 60

            # Clean up old requests
            self.request_counts[client_id] = [ts for ts in self.request_counts[client_id] if ts > minute_ago]

            # Check if rate limit exceeded
            if len(self.request_counts[client_id]) >= self.requests_per_minute:
                return True

            # Add current request
            self.request_counts[client_id].append(now)
            return False

    # Create rate limiter instance
    rate_limiter = RateLimiter(requests_per_minute=60)

    # Rate limiting middleware
    async def rate_limit_middleware(request: Request, call_next):
        # Get client IP or API key for rate limiting
        client_id = request.headers.get(API_KEY_NAME, request.client.host)

        # Check if rate limited
        if rate_limiter.is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )

        # Process the request
        response = await call_next(request)
        return response

    async def get_api_key(api_key_header: str = Header(None, alias=API_KEY_NAME)):
        return api_key_header

    async def verify_admin_api_key(api_key: str = Depends(get_api_key)):
        if api_key != ADMIN_API_KEY:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key",
            )
        return api_key

    async def verify_team_api_key(request: Request, api_key: str = Depends(get_api_key)):
        # Get team_id from path parameters
        team_id = request.path_params.get("team_id")

        # Admin key can access any team
        if api_key == ADMIN_API_KEY:
            return api_key

        # Check if this is a valid team key
        if team_id not in team_api_keys or team_api_keys[team_id] != api_key:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key for this team",
            )
        return api_key

    # Add rate limiting middleware
    app.middleware("http")(rate_limit_middleware)

    # Configure CORS
    # Get allowed origins from environment or use default for development
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Override the create_team endpoint to add API key generation
    from pydantic import BaseModel, Field
    from typing import Optional, Dict, List, Any

    class TeamCreateRequest(BaseModel):
        team_name: Optional[str] = None

    # We're not actually overriding the endpoint, just adding our own handler
    # that will be called before the canonical one due to middleware order
    @app.post("/teams/create")
    def create_team_with_api_key(request: TeamCreateRequest, api_key: str = Depends(verify_admin_api_key)):  # api_key used for authorization
        """Create a new team with API key."""
        try:
            team = game_state.create_team(request.team_name)

            # Generate and store API key for this team
            import secrets
            import hashlib
            import time

            # Generate a secure API key
            team_api_key = secrets.token_urlsafe(32)
            team_id = team["team_id"]
            team_api_keys[team_id] = team_api_key

            # Create a temporary access token with expiration
            token_expiry = int(time.time()) + 300  # 5 minutes
            token_data = f"{team_id}:{token_expiry}"
            token_signature = hashlib.sha256(f"{token_data}:{ADMIN_API_KEY}".encode()).hexdigest()
            secure_token = f"{token_data}:{token_signature}"

            # Add secure token to response instead of raw API key
            response = dict(team)
            response["secure_token"] = secure_token
            response["token_expiry"] = token_expiry

            return response
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    logger.info("Enhanced the canonical implementation with security features")

except Exception as e:
    logger.error(f"Error importing canonical implementation: {str(e)}")
    # Fallback to a minimal implementation
    from fastapi import FastAPI
    app = FastAPI(title="China's Growth Game Economic Model API (Fallback)")

    @app.get("/")
    def read_root():
        return {"message": "Fallback API - Canonical implementation not available"}

    @app.get("/health")
    def health_check():
        return {"status": "warning",
                "message": "Fallback API running - Canonical implementation not available",
                "error": str(e)}

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
def initialize_game(api_key: str = Depends(verify_admin_api_key)):  # api_key is used by the dependency for authorization
    """Initialize a new game."""
    global game_state
    game_state = GameState()  # Reset the game state
    return game_state.get_game_state()

@app.post("/game/start", response_model=GameStateResponse)
def start_game(api_key: str = Depends(verify_admin_api_key)):  # api_key is used by the dependency for authorization
    """Start the game with registered teams."""
    try:
        result = game_state.start_game()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/game/next-round")
def advance_to_next_round(api_key: str = Depends(verify_admin_api_key)):  # api_key is used by the dependency for authorization
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
        # Log the detailed error for server-side debugging
        import traceback
        logger = logging.getLogger("app")
        logger.error(f"Error in advance_to_next_round: {str(e)}")
        logger.error(traceback.format_exc())

        # Return a generic error message to the client
        raise HTTPException(status_code=500, detail={"error": "An internal server error occurred"})

@app.get("/game/state", response_model=GameStateResponse)
def get_game_state():
    """Get the current game state."""
    return game_state.get_game_state()

# Team management endpoints
@app.post("/teams/create")
def create_team(request: TeamCreateRequest, api_key: str = Depends(verify_admin_api_key)):  # api_key is used by the dependency for authorization
    """Create a new team."""
    try:
        team = game_state.create_team(request.team_name)

        # Generate and store API key for this team
        import secrets
        import hashlib
        import time

        # Generate a secure API key
        team_api_key = secrets.token_urlsafe(32)
        team_id = team["team_id"]
        team_api_keys[team_id] = team_api_key

        # Create a temporary access token with expiration
        token_expiry = int(time.time()) + 300  # 5 minutes
        token_data = f"{team_id}:{token_expiry}"
        token_signature = hashlib.sha256(f"{token_data}:{ADMIN_API_KEY}".encode()).hexdigest()
        secure_token = f"{token_data}:{token_signature}"

        # Add secure token to response instead of raw API key
        response = dict(team)
        response["secure_token"] = secure_token
        response["token_expiry"] = token_expiry

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/teams/decisions")
def submit_decision(request: DecisionSubmitRequest, api_key: str = Depends(get_api_key)):
    """Submit a team's decision for the current round."""
    # Check if this is the admin key or the team's key
    team_id = request.team_id
    if api_key != ADMIN_API_KEY and (team_id not in team_api_keys or team_api_keys[team_id] != api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key for this team",
        )
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
def get_team_state(team_id: str, api_key: str = Depends(verify_team_api_key)):  # api_key is used by the dependency for authorization
    """Get the state of a specific team."""
    try:
        return game_state.get_team_state(team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/teams/{team_id}/edit-name")
def edit_team_name(team_id: str = Path(...), request: TeamEditNameRequest = None, api_key: str = Depends(verify_team_api_key)):  # api_key is used by the dependency for authorization
    """Edit a team's name, enforcing uniqueness and appropriateness."""
    try:
        team = game_state.team_manager.edit_team_name(team_id, request.new_name)
        return team
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# For backward compatibility with the old API
@app.post("/calculate")
async def calculate_growth(data: Dict[Any, Any]):
    """Calculate economic growth based on provided parameters (legacy endpoint)."""
    try:
        # Extract parameters from the request
        savings_rate = data.get("savings_rate", 0.3)
        capital = data.get("capital", 100)
        labor = data.get("labor", 100)
        exchange_rate = data.get("exchange_rate", "market")

        # Create a temporary team for calculation
        temp_team_id = "temp-" + str(hash(str(data)))
        team = game_state.create_team("Temp Calculation Team")

        # Override the team's state with the provided values
        team["current_state"]["K"] = capital
        team["current_state"]["L"] = labor

        # Submit a decision for this team
        game_state.submit_decision(temp_team_id, savings_rate, exchange_rate)

        # Calculate the results for this team
        results = game_state.calculate_team_results(temp_team_id)

        # Clean up the temporary team
        game_state.team_manager.teams.pop(temp_team_id, None)

        # Return the results in the old format for compatibility
        return {
            "output": results["Y_t"],
            "investment": results["I_t"],
            "consumption": results["C_t"],
            "next_capital": results["K_next"]
        }
    except Exception as e:
        # Log the detailed error for server-side debugging
        import traceback
        logger = logging.getLogger("app")
        logger.error(f"Error in calculate_growth: {str(e)}")
        logger.error(traceback.format_exc())

        # Return a generic error message to the client
        raise HTTPException(status_code=500, detail={"error": "An internal server error occurred"})

# Results and visualization endpoints
@app.get("/results/rankings")
def get_rankings():
    """Get current rankings."""
    return game_state.rankings_manager.rankings

@app.get("/results/visualizations/{team_id}")
def get_team_visualizations(team_id: str, api_key: str = Depends(verify_team_api_key)):  # api_key is used by the dependency for authorization
    """Get visualization data for a specific team."""
    try:
        return game_state.get_team_visualizations(team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)