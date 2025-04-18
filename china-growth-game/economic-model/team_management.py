import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import os

# Import from centralized constants file
from constants import (
    DEFAULT_SAVINGS_RATE,
    DEFAULT_EXCHANGE_RATE_POLICY,
    DEFAULT_INITIAL_CONDITIONS,
    EXCHANGE_RATE_POLICIES
)

# Fun team name components for auto-generation
ECONOMIC_ADJECTIVES = [
    "Prosperous", "Bullish", "Innovative", "Dynamic", "Global",
    "Sovereign", "Productive", "Efficient", "Strategic", "Booming"
]

ECONOMIC_NOUNS = [
    "Pandas", "Dragons", "Tigers", "Investors", "Economists",
    "Traders", "Planners", "Entrepreneurs", "Visionaries", "Markets"
]

# Add a basic list of inappropriate words (can be expanded)
INAPPROPRIATE_WORDS = {"badword", "inappropriate", "offensive"}

def is_name_appropriate(name: str) -> bool:
    """Check if the name contains any inappropriate words (case-insensitive)."""
    lowered = name.lower()
    return not any(bad in lowered for bad in INAPPROPRIATE_WORDS)

class TeamManager:
    """
    Manages team creation, decision submission, and team state.
    """
    
    def __init__(self):
        self.teams = {}
        # Try to load initial conditions from CSV file, or use defaults if not found
        try:
            csv_path = os.path.join(os.path.dirname(__file__), 'initial_conditions_v1.csv')
            if os.path.exists(csv_path):
                self.initial_conditions = pd.read_csv(csv_path).iloc[0].to_dict()
            else:
                self.initial_conditions = DEFAULT_INITIAL_CONDITIONS
        except Exception as e:
            # Fallback to default initial conditions if there's an error
            self.initial_conditions = DEFAULT_INITIAL_CONDITIONS
    
    def generate_team_name(self) -> str:
        """Generate a fun, economics-themed team name."""
        adjective = random.choice(ECONOMIC_ADJECTIVES)
        noun = random.choice(ECONOMIC_NOUNS)
        return f"The {adjective} {noun}"
    
    def is_name_unique(self, name: str) -> bool:
        """Check if the team name is unique among all teams (case-insensitive)."""
        lowered = name.lower()
        return all(team["team_name"].lower() != lowered for team in self.teams.values())

    def create_team(self, team_name: Optional[str] = None, current_year: int = 1980, current_round: int = 0) -> Dict[str, Any]:
        """Create a new team with initial state, enforcing uniqueness and appropriateness."""
        if len(self.teams) >= 10:
            raise ValueError("Maximum number of teams (10) already reached")
        
        # Auto-generate a name if not provided, and ensure uniqueness
        if not team_name:
            attempts = 0
            while True:
                team_name = self.generate_team_name()
                if self.is_name_unique(team_name):
                    break
                attempts += 1
                if attempts > 100:
                    raise ValueError("Could not generate a unique team name after 100 attempts")
        else:
            if not self.is_name_unique(team_name):
                raise ValueError(f"Team name '{team_name}' is already taken")
            if not is_name_appropriate(team_name):
                raise ValueError("Team name contains inappropriate language")
        
        team_id = str(uuid.uuid4())
        
        # Get initial conditions from default
        initial_cond = self.initial_conditions.copy()
        
        # Transform initial conditions to the expected format
        # Map from economics naming convention to game API naming convention
        initial_state = {
            "GDP": initial_cond.get("Y", 306.2),  # Y → GDP 
            "Capital": initial_cond.get("K", 800),  # K → Capital
            "Labor Force": initial_cond.get("L", 600),  # L → Labor Force
            "Human Capital": initial_cond.get("H", 1.0),  # H → Human Capital
            "Productivity (TFP)": initial_cond.get("A", 1.0),  # A → Productivity (TFP)
            "Net Exports": initial_cond.get("NX", 3.6),  # NX → Net Exports
            "year": current_year,
            "round": current_round
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
        
        if exchange_rate_policy not in EXCHANGE_RATE_POLICIES:
            raise ValueError(f"Exchange rate policy must be one of: {', '.join(EXCHANGE_RATE_POLICIES)}")
        
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

    def edit_team_name(self, team_id: str, new_name: str) -> Dict[str, Any]:
        """Edit a team's name, enforcing uniqueness and appropriateness."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        if not self.is_name_unique(new_name):
            raise ValueError(f"Team name '{new_name}' is already taken")
        if not is_name_appropriate(new_name):
            raise ValueError("Team name contains inappropriate language")
        self.teams[team_id]["team_name"] = new_name
        return self.teams[team_id] 