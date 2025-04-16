import numpy as np
import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from enhanced_solow_model import EnhancedSolowModel

# Fun team name components for auto-generation
ECONOMIC_ADJECTIVES = [
    "Prosperous", "Bullish", "Innovative", "Dynamic", "Global",
    "Sovereign", "Productive", "Efficient", "Strategic", "Booming"
]

ECONOMIC_NOUNS = [
    "Pandas", "Dragons", "Tigers", "Investors", "Economists",
    "Traders", "Planners", "Entrepreneurs", "Visionaries", "Markets"
]

class GameState:
    """
    Manages the in-memory state for a single game session with multiple teams.
    """
    
    def __init__(self):
        self.game_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.current_round = 0
        self.current_year = 1980
        self.years = np.arange(1980, 2026, 5)
        self.teams = {}
        self.events = self._initialize_events()
        self.rankings = {
            "gdp": [],
            "net_exports": [],
            "balanced_economy": []
        }
        self.game_started = False
        self.game_ended = False
        self.solow_model = EnhancedSolowModel()
    
    def _initialize_events(self) -> List[Dict[str, Any]]:
        """Initialize economic events that will occur during the game."""
        return [
            {
                "year": 2001,
                "name": "China Joins WTO",
                "description": "China joins the World Trade Organization",
                "effects": {
                    "exports_multiplier": 1.25,
                    "tfp_increase": 0.02
                },
                "triggered": False
            },
            {
                "year": 2008,
                "name": "Global Financial Crisis",
                "description": "Global financial markets collapse",
                "effects": {
                    "exports_multiplier": 0.8,
                    "gdp_growth_delta": -0.03
                },
                "triggered": False
            },
            {
                "year": 2018,
                "name": "US-China Trade War",
                "description": "Escalating tariffs between the US and China",
                "effects": {
                    "exports_multiplier": 0.9
                },
                "triggered": False
            },
            {
                "year": 2020,
                "name": "COVID-19 Pandemic",
                "description": "Global pandemic disrupts economies",
                "effects": {
                    "gdp_growth_delta": -0.04
                },
                "triggered": False
            }
        ]
    
    def get_current_events(self) -> List[Dict[str, Any]]:
        """Get events that should be triggered in the current round."""
        current_events = []
        for event in self.events:
            if event["year"] == self.current_year and not event["triggered"]:
                event["triggered"] = True
                current_events.append(event)
        return current_events
    
    def generate_team_name(self) -> str:
        """Generate a fun, economics-themed team name."""
        adjective = random.choice(ECONOMIC_ADJECTIVES)
        noun = random.choice(ECONOMIC_NOUNS)
        return f"The {adjective} {noun}"
    
    def create_team(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new team with initial state."""
        if len(self.teams) >= 10:
            raise ValueError("Maximum number of teams (10) already reached")
        
        team_id = str(uuid.uuid4())
        
        # Auto-generate a name if not provided
        if not team_name:
            team_name = self.generate_team_name()
        
        # Initial team state with values from specs.md
        initial_state = {
            "year": self.current_year,
            "round": self.current_round,
            "Y": 306.2,  # GDP
            "K": 800,    # Capital
            "L": 600,    # Labor Force
            "H": 1.0,    # Human Capital
            "A": 1.0,    # Productivity (TFP)
            "NX": 3.6,   # Net Exports
            "C": 306.2 * 0.8,  # Consumption (assuming default savings rate of 20%)
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
                    "savings_rate": 0.2,  # Default 20%
                    "exchange_rate_policy": "market"  # Default market-based
                }
            ],
            "eliminated": False
        }
        
        self.teams[team_id] = team
        return team
    
    def submit_decision(self, team_id: str, savings_rate: float, exchange_rate_policy: str) -> Dict[str, Any]:
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
            "round": self.current_round,
            "year": self.current_year,
            "savings_rate": savings_rate,
            "exchange_rate_policy": exchange_rate_policy,
            "submitted_at": datetime.now().isoformat()
        }
        
        self.teams[team_id]["decisions"].append(decision)
        return decision
    
    def get_exchange_rate_multiplier(self, policy: str) -> float:
        """Convert exchange rate policy to a numerical multiplier."""
        if policy == "undervalue":
            return 0.8  # 20% lower
        elif policy == "overvalue":
            return 1.2  # 20% higher
        else:  # market
            return 1.0
    
    def start_game(self) -> Dict[str, Any]:
        """Start the game with registered teams."""
        if len(self.teams) == 0:
            raise ValueError("Cannot start game with no teams")
        
        self.game_started = True
        self.current_round = 1
        
        # Archive initial state to history for all teams
        for team_id, team in self.teams.items():
            team["history"].append(team["current_state"].copy())
        
        game_state = self.get_game_state()
        return game_state
    
    def advance_round(self) -> Dict[str, Any]:
        """Advance to the next round, simulating economic changes based on decisions."""
        if not self.game_started:
            raise ValueError("Cannot advance round: game not started")
        
        if self.current_round >= len(self.years) - 1:
            self.game_ended = True
            return {"message": "Game has ended", "final_rankings": self.calculate_rankings()}
        
        # Move to next round
        self.current_round += 1
        self.current_year = self.years[self.current_round]
        
        # Get events for this round
        current_events = self.get_current_events()
        
        # Process each team's state based on their decisions
        for team_id, team in self.teams.items():
            if team["eliminated"]:
                continue
                
            # Get the latest decision for this team
            try:
                latest_decision = next(d for d in reversed(team["decisions"]) 
                                    if d["round"] == self.current_round - 1)
            except StopIteration:
                # If no decision was made, use default values
                latest_decision = {
                    "savings_rate": 0.2,
                    "exchange_rate_policy": "market"
                }
            
            # Archive current state to history
            team["history"].append(team["current_state"].copy())
            
            # Use the Solow model to simulate this round
            new_state = self.solow_model.simulate_round(
                current_state=team["current_state"],
                decision=latest_decision,
                events=current_events,
                period_index=self.current_round - 1  # 0-based index for the period
            )
            
            # Update current state with simulation results
            team["current_state"] = new_state
            team["current_state"]["year"] = self.current_year
            team["current_state"]["round"] = self.current_round
        
        # Calculate rankings after processing all teams
        self.calculate_rankings()
        
        return {
            "round": self.current_round,
            "year": self.current_year,
            "events": current_events,
            "rankings": self.rankings
        }
    
    def calculate_rankings(self) -> Dict[str, List[str]]:
        """Calculate team rankings based on different metrics."""
        # GDP ranking
        gdp_ranking = sorted(
            [team_id for team_id, team in self.teams.items() if not team["eliminated"]],
            key=lambda team_id: self.teams[team_id]["current_state"]["Y"],
            reverse=True
        )
        
        # Net Exports ranking
        net_exports_ranking = sorted(
            [team_id for team_id, team in self.teams.items() if not team["eliminated"]],
            key=lambda team_id: self.teams[team_id]["current_state"]["NX"],
            reverse=True
        )
        
        # Balanced Economy ranking (GDP + Consumption)
        balanced_economy_ranking = sorted(
            [team_id for team_id, team in self.teams.items() if not team["eliminated"]],
            key=lambda team_id: (
                self.teams[team_id]["current_state"]["Y"] + 
                self.teams[team_id]["current_state"]["C"]
            ),
            reverse=True
        )
        
        self.rankings = {
            "gdp": gdp_ranking,
            "net_exports": net_exports_ranking,
            "balanced_economy": balanced_economy_ranking
        }
        
        return self.rankings
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state."""
        return {
            "game_id": self.game_id,
            "created_at": self.created_at,
            "current_round": self.current_round,
            "current_year": self.current_year,
            "teams": {team_id: {
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "current_state": team["current_state"],
                "eliminated": team["eliminated"]
            } for team_id, team in self.teams.items()},
            "rankings": self.rankings,
            "game_started": self.game_started,
            "game_ended": self.game_ended
        }
        
    def get_team_state(self, team_id: str) -> Dict[str, Any]:
        """Get the state of a specific team."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        return self.teams[team_id]
    
    def get_team_visualizations(self, team_id: str) -> Dict[str, Any]:
        """Get visualization data for a specific team."""
        if team_id not in self.teams:
            raise ValueError(f"Team with ID {team_id} does not exist")
        
        team = self.teams[team_id]
        history = team["history"] + [team["current_state"]]
        
        return self.solow_model.get_visualization_data(history) 