from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RankingsManager:
    """
    Manages rankings calculation for teams based on different metrics.
    """
    
    def __init__(self):
        self.rankings = {
            "gdp": [],
            "net_exports": [],
            "balanced_economy": []
        }
    
    def calculate_rankings(self, teams: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Calculate team rankings based on different metrics."""
        try:
            logger.debug(f"Calculating rankings for {len(teams)} teams")
            
            # If no teams, return empty rankings
            if not teams:
                logger.debug("No teams to rank")
                return self.rankings
                
            # Filter out eliminated teams and those with incomplete state
            valid_teams = []
            for team_id, team in teams.items():
                if team.get("eliminated", False):
                    logger.debug(f"Team {team_id} is eliminated, skipping")
                    continue
                    
                current_state = team.get("current_state", {})
                if "Y" not in current_state or "NX" not in current_state:
                    logger.warning(f"Team {team_id} has incomplete state data: {current_state}")
                    continue
                    
                valid_teams.append(team_id)
                
            logger.debug(f"Valid teams for ranking: {valid_teams}")
            
            # If no valid teams, return empty rankings
            if not valid_teams:
                logger.debug("No valid teams to rank")
                return self.rankings
                
            # GDP ranking
            gdp_ranking = sorted(
                valid_teams,
                key=lambda team_id: teams[team_id]["current_state"].get("Y", 0),
                reverse=True
            )
            logger.debug(f"GDP ranking: {gdp_ranking}")
            
            # Net Exports ranking
            net_exports_ranking = sorted(
                valid_teams,
                key=lambda team_id: teams[team_id]["current_state"].get("NX", 0),
                reverse=True
            )
            logger.debug(f"Net exports ranking: {net_exports_ranking}")
            
            # Balanced Economy ranking (GDP + Consumption)
            balanced_economy_ranking = sorted(
                valid_teams,
                key=lambda team_id: (
                    teams[team_id]["current_state"].get("Y", 0) + 
                    teams[team_id]["current_state"].get("C", 0)  # Use get with default for safety
                ),
                reverse=True
            )
            logger.debug(f"Balanced economy ranking: {balanced_economy_ranking}")
            
            self.rankings = {
                "gdp": gdp_ranking,
                "net_exports": net_exports_ranking,
                "balanced_economy": balanced_economy_ranking
            }
            
            return self.rankings
            
        except Exception as e:
            logger.error(f"Error calculating rankings: {str(e)}")
            # Return current rankings if there's an error
            return self.rankings 