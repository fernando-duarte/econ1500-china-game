import numpy as np
import uuid
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from solow_model import calculate_next_round
from team_management import TeamManager, DEFAULT_SAVINGS_RATE, DEFAULT_EXCHANGE_RATE_POLICY
from events_manager import EventsManager
from rankings_manager import RankingsManager
from visualization_manager import VisualizationManager
from solow_core import (
    get_default_parameters,
    calculate_openness_ratio,
    calculate_fdi_ratio
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        self.years = np.arange(1980, 2026, 5)
        self.game_started = False
        self.game_ended = False
        
        # Initialize component managers
        self.team_manager = TeamManager()
        self.events_manager = EventsManager()
        self.rankings_manager = RankingsManager()
        self.visualization_manager = VisualizationManager()
        
        # Get default model parameters from the centralized utility function
        self.model_parameters = get_default_parameters()
    
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
    
    def _get_parameters_for_round(self, round_index: int) -> Dict[str, Any]:
        """
        Helper method to get parameters for the given round.
        Extracts common parameter preparation logic.
        """
        # Calculate openness ratio for the current round using the utility function
        current_openness_ratio = calculate_openness_ratio(round_index)
        
        # Prepare parameters for this specific round, including the calculated openness ratio
        params_for_round = self.model_parameters.copy()
        params_for_round['openness_ratio'] = current_openness_ratio
        
        return params_for_round
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """
        Helper method to get default decision when none is provided.
        Uses shared constants from TeamManager for consistency.
        """
        return {
            'savings_rate': DEFAULT_SAVINGS_RATE,
            'exchange_rate_policy': DEFAULT_EXCHANGE_RATE_POLICY
        }
    
    def _apply_event_effects(self, round_results: Dict[str, Any], events: List[Dict[str, Any]], team_id: str) -> Dict[str, Any]:
        """
        Helper method to apply event effects to round results.
        Returns the modified round_results and a list of applied event names.
        """
        applied_event_names = []
        
        if not events:
            return round_results, applied_event_names
            
        for event in events:
            event_name = event.get('name', 'Unknown Event')
            event_year = event.get('year', None)
            effects = event.get('effects', {})
            applied_event_names.append(event_name)
            logger.info(f"Applying effects for event: {event_name} ({event_year}) to team {team_id}")

            # Apply TFP bonus (WTO)
            if 'tfp_increase' in effects:
                tfp_bonus = effects['tfp_increase']
                round_results['A_next'] *= (1 + tfp_bonus)
                logger.debug(f"  Applied TFP bonus: {tfp_bonus}. New A_next: {round_results['A_next']}")

            # Apply GDP growth delta (GFC, COVID)
            if 'gdp_growth_delta' in effects:
                gdp_delta = effects['gdp_growth_delta']
                round_results['Y_t'] *= (1 + gdp_delta)
                logger.debug(f"  Applied GDP delta: {gdp_delta}. New Y_t: {round_results['Y_t']}")
                
        return round_results, applied_event_names
    
    def _process_team_round(self, team_id: str, team: Dict[str, Any], current_events: List[Dict[str, Any]]) -> None:
        """
        Process a single team's state for the current round.
        Extracts team processing logic from advance_round.
        """
        if team["eliminated"]:
            return
            
        logger.debug(f"Processing team {team_id}: {team['team_name']}")
        
        # Get the latest decision for this team
        # Decisions are submitted for the round *before* it is processed
        decision_round = self.current_round - 1
        latest_decision = self.team_manager.get_latest_decision(team_id, decision_round)
        if not latest_decision:
            logger.warning(f"No decision found for team {team_id} for round {decision_round}. Using default.")
            latest_decision = self._get_default_decision()

        logger.debug(f"Decision for round {decision_round}: {latest_decision}")

        # Prepare parameters for this round
        current_round_index = self.current_round - 1
        params_for_round = self._get_parameters_for_round(current_round_index)

        # Prepare current state for calculation
        current_state_for_calc = {
            'Y': team['current_state']['GDP'],
            'K': team['current_state']['Capital'],
            'L': team['current_state']['Labor Force'],
            'H': team['current_state']['Human Capital'],
            'A': team['current_state']['Productivity (TFP)']
        }
        
        # Prepare student inputs
        student_inputs_for_calc = {
            's': latest_decision['savings_rate'],
            'e_policy': latest_decision['exchange_rate_policy']
        }

        logger.debug(f"Calling calculate_next_round with state: {current_state_for_calc}, inputs: {student_inputs_for_calc}, year: {self.current_year}")

        # Calculate next round
        round_results = calculate_next_round(
            current_state=current_state_for_calc,
            parameters=params_for_round,
            student_inputs=student_inputs_for_calc,
            year=self.current_year
        )

        logger.debug(f"Results from calculate_next_round: {round_results}")

        # Apply event effects
        round_results, applied_event_names = self._apply_event_effects(round_results, current_events, team_id)

        # Prepare the full state dictionary for the next round
        next_state_data = {
            'Year': self.current_year + 5, # State is for the *start* of the next year block
            'Round': self.current_round,
            'GDP': round_results['Y_t'], # GDP achieved in the round just ended
            'Capital': round_results['K_next'],
            'Labor Force': round_results['L_next'],
            'Human Capital': round_results['H_next'],
            'Productivity (TFP)': round_results['A_next'],
            'Net Exports': round_results['NX_t'],
            'Consumption': round_results['C_t'],
            'Investment': round_results['I_t'],
            'Savings Rate Decision': latest_decision['savings_rate'],
            'Exchange Rate Decision': latest_decision['exchange_rate_policy']
        }

        logger.debug(f"Updating team {team_id} with next state: {next_state_data}")

        # Update team state
        self.team_manager.update_team_state(team_id, next_state_data, self.current_year, self.current_round)
    
    def advance_round(self) -> Dict[str, Any]:
        """Advance to the next round, simulating economic changes based on decisions."""
        if not self.game_started:
            raise ValueError("Cannot advance round: game not started")
        
        if self.current_round >= len(self.years) - 1:
            self.game_ended = True
            return {"message": "Game has ended", "final_rankings": self.calculate_rankings()}
        
        try:
            # Move to next round (0-based index)
            self.current_round += 1
            self.current_year = self.years[self.current_round]
            
            logger.debug(f"Advancing to round {self.current_round}, year {self.current_year}")
            
            # Get events for this round
            current_events = self.events_manager.get_current_events(self.current_year)
            logger.debug(f"Current events: {current_events}")
            
            # Process each team's state based on their decisions
            for team_id, team in self.team_manager.teams.items():
                try:
                    self._process_team_round(team_id, team, current_events)
                except Exception as e:
                    logger.error(f"Error processing team {team_id}: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise
            
            # Calculate rankings after processing all teams
            self.calculate_rankings()
            
            return {
                "round": self.current_round,
                "year": self.current_year,
                "events": current_events,
                "rankings": self.rankings_manager.rankings
            }
        except Exception as e:
            logger.error(f"Error in advance_round: {str(e)}")
            logger.error(traceback.format_exc())
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