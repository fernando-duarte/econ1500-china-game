import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import re
import html

import sys
import os
import traceback

# Add economic-model to Python path if it's not already there
economic_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'china-growth-game/economic-model')
if economic_model_path not in sys.path:
    sys.path.insert(0, economic_model_path)

# Import the consolidated Solow model implementation
from solow_core import calculate_single_round, get_default_parameters

class TeamManager:
    """
    Manages team creation, decision submission, and team state.
    """

    def __init__(self):
        self.teams = {}

    def sanitize_team_name(self, team_name: str) -> str:
        """Sanitize team name to prevent XSS and other injection attacks."""
        if not team_name:
            return f"Team {len(self.teams) + 1}"

        # HTML escape to prevent XSS
        sanitized = html.escape(team_name)

        # Remove any potentially harmful characters
        sanitized = re.sub(r'[^\w\s\-_.,!?]', '', sanitized)

        # Limit length
        sanitized = sanitized[:50]

        # If sanitization removed everything, provide a default
        if not sanitized.strip():
            sanitized = f"Team {len(self.teams) + 1}"

        return sanitized

    def create_team(self, team_name: Optional[str] = None, current_year: int = 1980, current_round: int = 0) -> Dict[str, Any]:
        """Create a new team with initial state."""
        sanitized_name = self.sanitize_team_name(team_name) if team_name else f"Team {len(self.teams) + 1}"

        team_id = str(uuid.uuid4())

        # Initial team state
        team = {
            "team_id": team_id,
            "team_name": sanitized_name,
            "created_at": datetime.now().isoformat(),
            "current_state": {
                "GDP": 306.2,
                "Capital": 800,
                "Labor Force": 600,
                "Human Capital": 1.0,
                "Productivity (TFP)": 1.0,
                "Net Exports": 3.6,
                "Consumption": 244.96
            },
            "history": [],
            "decisions": [
                {
                    "round": 0,
                    "year": 1980,
                    "savings_rate": 0.3,
                    "exchange_rate_policy": "market"
                }
            ],
            "eliminated": False
        }

        self.teams[team_id] = team
        return team

    def edit_team_name(self, team_id: str, new_name: str) -> Dict[str, Any]:
        """Edit a team's name with proper sanitization."""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")

        sanitized_name = self.sanitize_team_name(new_name)
        self.teams[team_id]["team_name"] = sanitized_name

        return self.teams[team_id]

    def submit_decision(self, team_id: str, savings_rate: float, exchange_rate_policy: str,
                       current_round: int, current_year: int) -> Dict[str, Any]:
        """Submit a team's decision for the current round."""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")

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
            raise ValueError(f"Team {team_id} not found")
        return self.teams[team_id]

    def get_team_data_for_game_state(self) -> Dict[str, Dict[str, Any]]:
        """Get all team data formatted for the game state response."""
        return self.teams

class EventsManager:
    """
    Manages game events.
    """

    def __init__(self):
        self.events = []

    def get_current_events(self, year: int) -> List[Dict[str, Any]]:
        """Get events for the current year."""
        return []

class RankingsManager:
    """
    Manages team rankings.
    """

    def __init__(self):
        self.rankings = {
            "gdp": [],
            "growth": [],
            "consumption": []
        }

    def calculate_rankings(self, teams: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Calculate team rankings based on different metrics."""
        # Simple ranking by GDP
        gdp_ranking = sorted(
            teams.keys(),
            key=lambda team_id: teams[team_id]["current_state"]["GDP"],
            reverse=True
        )

        self.rankings["gdp"] = gdp_ranking
        self.rankings["growth"] = gdp_ranking.copy()  # Simplified
        self.rankings["consumption"] = gdp_ranking.copy()  # Simplified

        return self.rankings

class VisualizationManager:
    """
    Manages data visualization.
    """

    def __init__(self):
        pass

    def get_team_visualizations(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Get visualization data for a specific team."""
        return {
            "gdp_over_time": self._extract_metric_over_time(team, "GDP"),
            "capital_over_time": self._extract_metric_over_time(team, "Capital"),
            "consumption_over_time": self._extract_metric_over_time(team, "Consumption")
        }

    def _extract_metric_over_time(self, team: Dict[str, Any], metric: str) -> Dict[str, List[Any]]:
        """Extract a specific metric over time from team history."""
        years = []
        values = []

        # Add current state
        years.append(team["current_state"].get("Year", 1980))
        values.append(team["current_state"].get(metric, 0))

        # Add historical data
        for entry in team.get("history", []):
            years.append(entry.get("Year", 0))
            values.append(entry.get(metric, 0))

        return {
            "years": years,
            "values": values
        }

class GameState:
    """
    Manages the in-memory state for a single game session with multiple teams.
    Uses modular components for team management, events, and rankings.
    """

    def __init__(self):
        self.game_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.current_round = 0
        self.current_year = 1980
        self.years = [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]
        self.game_started = False
        self.game_ended = False
        self.processed_rounds = set()  # Track processed rounds for idempotency

        # Initialize component managers
        self.team_manager = TeamManager()
        self.events_manager = EventsManager()
        self.rankings_manager = RankingsManager()
        self.visualization_manager = VisualizationManager()

    def create_team(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new team with initial state."""
        return self.team_manager.create_team(team_name, self.current_year, self.current_round)

    def submit_decision(self, team_id: str, savings_rate: float, exchange_rate_policy: str) -> Dict[str, Any]:
        """Submit a team's decision for the current round."""
        return self.team_manager.submit_decision(
            team_id, savings_rate, exchange_rate_policy,
            self.current_round, self.current_year
        )

    def start_game(self) -> Dict[str, Any]:
        """Start the game with registered teams."""
        if len(self.team_manager.teams) == 0:
            raise ValueError("Cannot start game with no teams")

        self.game_started = True
        self.current_round = 0  # Start with round 0 (first round)
        self.current_year = self.years[self.current_round]  # Set year to 1980

        # Archive initial state to history for all teams
        for team_id, team in self.team_manager.teams.items():
            team["history"].append(team["current_state"].copy())

        game_state = self.get_game_state()
        return game_state

    def calculate_team_results(self, team_id: str) -> Dict[str, Any]:
        """Calculate results for a specific team."""
        team = self.team_manager.get_team_state(team_id)
        current_state = team["current_state"]

        # Get the latest decision
        latest_decision = team["decisions"][-1]
        savings_rate = latest_decision["savings_rate"]
        exchange_rate_policy = latest_decision["exchange_rate_policy"]

        # Prepare current state for Solow model
        solow_state = {
            'Y': current_state["GDP"],
            'K': current_state["Capital"],
            'L': current_state["Labor Force"],
            'H': current_state["Human Capital"],
            'A': current_state["Productivity (TFP)"]
        }

        # Prepare student inputs for Solow model
        student_inputs = {
            's': savings_rate,
            'e_policy': exchange_rate_policy
        }

        # Get default parameters - could be customized per team in the future
        parameters = get_default_parameters()

        # Use the consolidated core model to calculate results
        result = calculate_single_round(
            current_state=solow_state,
            parameters=parameters,
            student_inputs=student_inputs,
            year=self.current_year
        )

        # Map the result to the expected output format
        return {
            "Y_t": result["Y_t"],           # GDP
            "I_t": result["I_t"],           # Investment
            "C_t": result["C_t"],           # Consumption
            "K_next": result["K_next"],     # Next capital
            "L_next": result["L_next"],     # Next labor
            "H_next": result["H_next"],     # Next human capital
            "A_next": result["A_next"],     # Next productivity
            "NX_t": result["NX_t"]          # Net exports
        }

    def advance_round(self) -> Dict[str, Any]:
        """Advance to the next round, simulating economic changes based on decisions."""
        if not self.game_started:
            raise ValueError("Cannot advance round: game not started")
        if self.current_round >= len(self.years) - 1:
            self.game_ended = True
            return {"message": "Game has ended", "final_rankings": self.calculate_rankings()}

        # Idempotency check: if this round has already been processed, return current state
        if self.current_round in self.processed_rounds:
            logger.warning(f"Round {self.current_round} has already been processed. Skipping.")
            return {
                "round": self.current_round,
                "year": self.current_year,
                "events": self.events_manager.get_current_events(self.current_year),
                "rankings": self.rankings_manager.rankings
            }

        try:
            # Move to next round
            self.current_round += 1
            self.current_year = self.years[self.current_round]

            # Get events for this round
            current_events = self.events_manager.get_current_events(self.current_year)

            # Process each team's state based on their decisions
            for team_id, team in self.team_manager.teams.items():
                if team["eliminated"]:
                    continue

                # Calculate results for this team
                results = self.calculate_team_results(team_id)

                # Prepare the next state
                next_state = {
                    "Year": self.current_year,
                    "Round": self.current_round,
                    "GDP": results["Y_t"],
                    "Capital": results["K_next"],
                    "Labor Force": results["L_next"],
                    "Human Capital": results["H_next"],
                    "Productivity (TFP)": results["A_next"],
                    "Net Exports": results["NX_t"],
                    "Consumption": results["C_t"],
                    "Investment": results["I_t"]
                }

                # Save current state to history
                team["history"].append(team["current_state"].copy())

                # Update current state
                team["current_state"] = next_state

            # Calculate rankings
            self.calculate_rankings()

            # Mark this round as processed
            self.processed_rounds.add(self.current_round)

            return {
                "round": self.current_round,
                "year": self.current_year,
                "events": current_events,
                "rankings": self.rankings_manager.rankings
            }
        except Exception as e:
            logger.error(f"Error in advance_round: {str(e)}")
            raise

    def calculate_rankings(self) -> Dict[str, List[str]]:
        """Calculate team rankings based on different metrics."""
        return self.rankings_manager.calculate_rankings(self.team_manager.teams)

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state."""
        return {
            "game_id": self.game_id,
            "created_at": self.created_at,
            "current_round": self.current_round,
            "current_year": self.current_year,
            "teams": self.team_manager.get_team_data_for_game_state(),
            "rankings": self.rankings_manager.rankings,
            "game_started": self.game_started,
            "game_ended": self.game_ended
        }

    def get_team_state(self, team_id: str) -> Dict[str, Any]:
        """Get the state of a specific team."""
        return self.team_manager.get_team_state(team_id)

    def get_team_visualizations(self, team_id: str) -> Dict[str, Any]:
        """Get visualization data for a specific team."""
        team = self.team_manager.get_team_state(team_id)
        return self.visualization_manager.get_team_visualizations(team)
