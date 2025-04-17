import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

# Fun team name components for auto-generation
ECONOMIC_ADJECTIVES = [
    "Prosperous", "Bullish", "Innovative", "Dynamic", "Global",
    "Sovereign", "Productive", "Efficient", "Strategic", "Booming"
]

ECONOMIC_NOUNS = [
    "Pandas", "Dragons", "Tigers", "Investors", "Economists",
    "Traders", "Planners", "Entrepreneurs", "Visionaries", "Markets"
]

# Default decision values for consistency across the codebase
DEFAULT_SAVINGS_RATE = 0.2  # 20%
DEFAULT_EXCHANGE_RATE_POLICY = "market"

class TeamManager:
    """
    Manages team creation, decision submission, and team state.
    """
    
    def __init__(self):
        self.teams = {}
    
    def generate_team_name(self) -> str:
        """Generate a fun, economics-themed team name."""
        adjective = random.choice(ECONOMIC_ADJECTIVES)
        noun = random.choice(ECONOMIC_NOUNS)
        return f"The {adjective} {noun}"
    
    def create_team(self, team_name: Optional[str] = None, current_year: int = 1980, current_round: int = 0) -> Dict[str, Any]:
        """Create a new team with initial state."""
        if len(self.teams) >= 10:
            raise ValueError("Maximum number of teams (10) already reached")
        
        team_id = str(uuid.uuid4())
        
        # Auto-generate a name if not provided
        if not team_name:
            team_name = self.generate_team_name()
        
        # Initial team state with values from specs.md
        initial_state = {
            "year": current_year,
            "round": current_round,
            "Y": 306.2,  # GDP
            "K": 800,    # Capital
            "L": 600,    # Labor Force
            "H": 1.0,    # Human Capital
            "A": 1.0,    # Productivity (TFP)
            "NX": 3.6,   # Net Exports
            "C": 306.2 * (1 - DEFAULT_SAVINGS_RATE),  # Consumption (using default savings rate)
            "initial_Y": 306.2  # Keep track of initial GDP for imports calculation
        }
        
        # Initial team state
        team = {
            "team_id": team_id,
            "team_name": team_name,
            "created_at": datetime.now().isoformat(),
            "current_state": initial_state,
            "history": [],
            "decisions": [
                {
                    "round": 0,
                    "year": 1980,
                    "savings_rate": DEFAULT_SAVINGS_RATE,
                    "exchange_rate_policy": DEFAULT_EXCHANGE_RATE_POLICY
                }
            ],
            "eliminated": False
        }
        
        self.teams[team_id] = team
        return team
    
    def submit_decision(self, team_id: str, savings_rate: float, exchange_rate_policy: str, current_round: int, current_year: int) -> Dict[str, Any]:
        """Submit a team's decision for the current round."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        if self.teams[team_id]["eliminated"]:
            raise ValueError(f"Team {team_id} has been eliminated and cannot make decisions")
        
        # Validate inputs
        if not (0.01 <= savings_rate <= 0.99):
            raise ValueError("Savings rate must be between 1% and 99%")
        
        if exchange_rate_policy not in ["undervalue", "market", "overvalue"]:
            raise ValueError("Exchange rate policy must be 'undervalue', 'market', or 'overvalue'")
        
        # Record the decision
        decision = {
            "round": current_round,
            "year": current_year,
            "savings_rate": savings_rate,
            "exchange_rate_policy": exchange_rate_policy,
            "submitted_at": datetime.now().isoformat()
        }
        
        self.teams[team_id]["decisions"].append(decision)
        return decision
    
    def get_team_state(self, team_id: str) -> Dict[str, Any]:
        """Get the state of a specific team."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        return self.teams[team_id]
        
    def get_team_data_for_game_state(self) -> Dict[str, Dict[str, Any]]:
        """Get teams data formatted for game state response."""
        return {
            team_id: {
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "current_state": team["current_state"],
                "eliminated": team["eliminated"]
            } for team_id, team in self.teams.items()
        }
    
    def update_team_state(self, team_id: str, new_state: Dict[str, Any], year: int, round_num: int):
        """Update a team's state with simulation results."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        # Archive current state to history
        self.teams[team_id]["history"].append(self.teams[team_id]["current_state"].copy())
        
        # Update current state
        self.teams[team_id]["current_state"] = new_state
        self.teams[team_id]["current_state"]["year"] = year
        self.teams[team_id]["current_state"]["round"] = round_num
    
    def get_latest_decision(self, team_id: str, round_num: int) -> Dict[str, Any]:
        """Get the latest decision for a team in a specific round."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        try:
            latest_decision = next(d for d in reversed(self.teams[team_id]["decisions"]) 
                                if d["round"] == round_num)
            return latest_decision
        except StopIteration:
            # If no decision was made, use default values
            return {
                "savings_rate": DEFAULT_SAVINGS_RATE,
                "exchange_rate_policy": DEFAULT_EXCHANGE_RATE_POLICY
            } 