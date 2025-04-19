"""
Prize management for the China Growth Game.

This module contains the PrizeManager class, which manages
prize awarding and effects for teams based on their performance.
"""

from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime
from economic_model_py.economic_model.utils.persistence import PersistenceManager
from economic_model_py.economic_model.utils.notification_manager import NotificationManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Prize types
PRIZE_TYPES = {
    "gdp_growth": {
        "name": "GDP Growth Achievement",
        "description": "Awarded for achieving high GDP growth for 3 consecutive rounds",
        "effects": {
            "tfp_increase": 0.05  # 5% TFP boost
        }
    },
    "tech_leadership": {
        "name": "Technology Leadership",
        "description": "Awarded for achieving the highest TFP growth across all teams",
        "effects": {
            "fdi_ratio_multiplier": 1.1  # 10% improvement in capital inflow
        }
    },
    "sustainable_growth": {
        "name": "Sustainable Growth",
        "description": "Awarded for balanced growth with high consumption and GDP",
        "effects": {
            "consumption_utility_multiplier": 1.1  # 10% increase in consumption utility
        }
    },
    "crisis_management": {
        "name": "Crisis Management",
        "description": "Awarded for recovering from negative shock events",
        "effects": {
            "shock_resistance": 0.15  # 15% reduction in negative event impacts
        }
    },
    "export_champion": {
        "name": "Export Champion",
        "description": "Awarded for highest cumulative exports",
        "effects": {
            "terms_of_trade_multiplier": 1.1  # 10% improvement in terms of trade
        }
    }
}

class PrizeManager:
    """
    Manages prize awarding and effects for teams based on their performance.
    """

    def __init__(self, persistence_manager: Optional[PersistenceManager] = None, notification_manager: Optional[NotificationManager] = None):
        self.awarded_prizes = {}  # Dict[team_id, Dict[prize_type, award_info]]
        self.persistence_manager = persistence_manager
        self.notification_manager = notification_manager

    def check_prize_eligibility(self, teams: Dict[str, Dict[str, Any]],
                               current_round: int, current_year: int,
                               rankings: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check if any teams are eligible for prizes in the current round.

        Args:
            teams: Dictionary of team data
            current_round: Current game round
            current_year: Current game year
            rankings: Current rankings

        Returns:
            Dictionary mapping team_ids to lists of prizes they are eligible for
        """
        eligible_prizes = {}

        # Skip if we're in the first few rounds (need history for some prizes)
        if current_round < 3:
            return eligible_prizes

        # Check each team for prize eligibility
        for team_id, team in teams.items():
            if team.get("eliminated", False):
                continue

            team_eligible_prizes = []

            # Check GDP growth achievement (8% growth for 3 consecutive rounds)
            if self._check_gdp_growth_achievement(team, current_round):
                team_eligible_prizes.append({
                    "type": "gdp_growth",
                    "name": PRIZE_TYPES["gdp_growth"]["name"],
                    "description": PRIZE_TYPES["gdp_growth"]["description"],
                    "effects": PRIZE_TYPES["gdp_growth"]["effects"]
                })

            # Check tech leadership (highest TFP)
            if self._check_tech_leadership(team_id, teams, rankings):
                team_eligible_prizes.append({
                    "type": "tech_leadership",
                    "name": PRIZE_TYPES["tech_leadership"]["name"],
                    "description": PRIZE_TYPES["tech_leadership"]["description"],
                    "effects": PRIZE_TYPES["tech_leadership"]["effects"]
                })

            # Check sustainable growth (balanced economy)
            if self._check_sustainable_growth(team_id, rankings):
                team_eligible_prizes.append({
                    "type": "sustainable_growth",
                    "name": PRIZE_TYPES["sustainable_growth"]["name"],
                    "description": PRIZE_TYPES["sustainable_growth"]["description"],
                    "effects": PRIZE_TYPES["sustainable_growth"]["effects"]
                })

            # Check crisis management (recovery from negative events)
            if self._check_crisis_management(team, current_round):
                team_eligible_prizes.append({
                    "type": "crisis_management",
                    "name": PRIZE_TYPES["crisis_management"]["name"],
                    "description": PRIZE_TYPES["crisis_management"]["description"],
                    "effects": PRIZE_TYPES["crisis_management"]["effects"]
                })

            # Check export champion (highest net exports)
            if self._check_export_champion(team_id, rankings):
                team_eligible_prizes.append({
                    "type": "export_champion",
                    "name": PRIZE_TYPES["export_champion"]["name"],
                    "description": PRIZE_TYPES["export_champion"]["description"],
                    "effects": PRIZE_TYPES["export_champion"]["effects"]
                })

            if team_eligible_prizes:
                eligible_prizes[team_id] = team_eligible_prizes

        return eligible_prizes

    def award_prizes(self, eligible_prizes: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Award prizes to eligible teams.

        Args:
            eligible_prizes: Dictionary mapping team_ids to lists of prizes they are eligible for

        Returns:
            Dictionary mapping team_ids to lists of prizes that were actually awarded
        """
        awarded = {}

        for team_id, prizes in eligible_prizes.items():
            team_awarded = []

            for prize in prizes:
                prize_type = prize["type"]

                # Check if this team already has this prize (idempotency)
                if team_id in self.awarded_prizes and prize_type in self.awarded_prizes[team_id]:
                    logger.debug(f"Team {team_id} already has prize {prize_type}, skipping")
                    continue

                # Award the prize
                if team_id not in self.awarded_prizes:
                    self.awarded_prizes[team_id] = {}

                self.awarded_prizes[team_id][prize_type] = {
                    "awarded_at": datetime.now().isoformat(),
                    "name": prize["name"],
                    "description": prize["description"],
                    "effects": prize["effects"]
                }

                team_awarded.append(prize)
                logger.info(f"Awarded prize {prize_type} to team {team_id}")

                # Send notification if notification manager is available
                if self.notification_manager is not None:
                    self.notification_manager.emit_prize_awarded(
                        team_id,
                        prize_type,
                        self.awarded_prizes[team_id][prize_type]
                    )

            if team_awarded:
                awarded[team_id] = team_awarded

        # Persist prizes if persistence manager is available
        if awarded and self.persistence_manager is not None:
            game_id = next(iter(eligible_prizes.values()))[0].get("game_id", "unknown")
            self.persistence_manager.save_prizes(game_id, self.awarded_prizes)

        return awarded

    def apply_prize_effects(self, team_id: str, round_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply prize effects to a team's round results.

        Args:
            team_id: Team ID
            round_results: Round calculation results

        Returns:
            Modified round results with prize effects applied
        """
        if team_id not in self.awarded_prizes:
            return round_results

        for prize_type, prize_info in self.awarded_prizes[team_id].items():
            effects = prize_info["effects"]

            # Apply TFP increase (GDP growth prize)
            if "tfp_increase" in effects:
                tfp_bonus = effects["tfp_increase"]
                if "A_next" in round_results:
                    round_results["A_next"] *= (1 + tfp_bonus)
                    logger.debug(f"Applied TFP bonus from {prize_type} prize: {tfp_bonus}. New A_next: {round_results['A_next']}")

            # Apply FDI ratio multiplier (tech leadership prize)
            if "fdi_ratio_multiplier" in effects:
                fdi_multiplier = effects["fdi_ratio_multiplier"]
                if "fdi_ratio" in round_results:
                    round_results["fdi_ratio"] *= fdi_multiplier
                    logger.debug(f"Applied FDI multiplier from {prize_type} prize: {fdi_multiplier}. New fdi_ratio: {round_results['fdi_ratio']}")

            # Apply consumption utility multiplier (sustainable growth prize)
            if "consumption_utility_multiplier" in effects:
                consumption_multiplier = effects["consumption_utility_multiplier"]
                if "C_t" in round_results:
                    round_results["C_t"] *= consumption_multiplier
                    logger.debug(f"Applied consumption multiplier from {prize_type} prize: {consumption_multiplier}. New C_t: {round_results['C_t']}")

            # Apply shock resistance (crisis management prize)
            if "shock_resistance" in effects and "gdp_growth_delta" in round_results:
                shock_resistance = effects["shock_resistance"]
                if round_results["gdp_growth_delta"] < 0:
                    # Reduce negative impact by shock_resistance percentage
                    round_results["gdp_growth_delta"] *= (1 - shock_resistance)
                    logger.debug(f"Applied shock resistance from {prize_type} prize: {shock_resistance}. New gdp_growth_delta: {round_results['gdp_growth_delta']}")

            # Apply terms of trade multiplier (export champion prize)
            if "terms_of_trade_multiplier" in effects:
                trade_multiplier = effects["terms_of_trade_multiplier"]
                if "NX_t" in round_results:
                    round_results["NX_t"] *= trade_multiplier
                    logger.debug(f"Applied trade multiplier from {prize_type} prize: {trade_multiplier}. New NX_t: {round_results['NX_t']}")

        return round_results

    def get_team_prizes(self, team_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all prizes awarded to a team."""
        if team_id not in self.awarded_prizes:
            return {}
        return self.awarded_prizes[team_id]

    def get_all_prizes(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all awarded prizes for all teams."""
        return self.awarded_prizes

    def reset_prizes(self):
        """Reset all awarded prizes."""
        self.awarded_prizes = {}

    def load_prizes(self, game_id: str) -> bool:
        """Load prizes from persistence.

        Args:
            game_id: The ID of the game to load prizes for.

        Returns:
            True if prizes were loaded successfully, False otherwise.
        """
        if self.persistence_manager is None:
            logger.warning("No persistence manager available, cannot load prizes")
            return False

        try:
            prizes = self.persistence_manager.load_prizes(game_id)
            if prizes:
                self.awarded_prizes = prizes
                logger.info(f"Loaded {len(prizes)} team prizes for game {game_id}")

                # Send notification if notification manager is available
                if self.notification_manager is not None:
                    self.notification_manager.emit_prizes_loaded(self.awarded_prizes)

                return True
            else:
                logger.info(f"No prizes found for game {game_id}")
                return False
        except Exception as e:
            logger.error(f"Error loading prizes: {str(e)}")
            return False

    def save_prizes(self, game_id: str) -> bool:
        """Save prizes to persistence.

        Args:
            game_id: The ID of the game to save prizes for.

        Returns:
            True if prizes were saved successfully, False otherwise.
        """
        if self.persistence_manager is None:
            logger.warning("No persistence manager available, cannot save prizes")
            return False

        try:
            success = self.persistence_manager.save_prizes(game_id, self.awarded_prizes)
            if success:
                logger.info(f"Saved prizes for game {game_id}")
            else:
                logger.error(f"Failed to save prizes for game {game_id}")
            return success
        except Exception as e:
            logger.error(f"Error saving prizes: {str(e)}")
            return False

    def _check_gdp_growth_achievement(self, team: Dict[str, Any], current_round: int) -> bool:
        """Check if a team qualifies for the GDP growth achievement prize."""
        # Need at least 3 rounds of history
        if current_round < 3 or "history" not in team or len(team["history"]) < 3:
            return False

        # Check for 8% growth in the last 3 rounds
        last_three_rounds = team["history"][-3:]

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(last_three_rounds)):
            prev_gdp = last_three_rounds[i-1].get("Y", 0)
            curr_gdp = last_three_rounds[i].get("Y", 0)

            if prev_gdp <= 0:
                return False

            growth_rate = (curr_gdp - prev_gdp) / prev_gdp
            growth_rates.append(growth_rate)

        # Check if all growth rates are >= 8%
        return all(rate >= 0.08 for rate in growth_rates)

    def _check_tech_leadership(self, team_id: str, teams: Dict[str, Dict[str, Any]],
                              rankings: Dict[str, List[str]]) -> bool:
        """Check if a team qualifies for the tech leadership prize."""
        # Simple implementation: team with highest TFP (A) gets the prize
        # In a more complex implementation, we could track TFP growth over time

        # Get all non-eliminated teams
        valid_teams = [tid for tid, team in teams.items() if not team.get("eliminated", False)]

        if not valid_teams:
            return False

        # Find team with highest TFP
        highest_tfp_team = max(
            valid_teams,
            key=lambda tid: teams[tid]["current_state"].get("A", 0)
        )

        return team_id == highest_tfp_team

    def _check_sustainable_growth(self, team_id: str, rankings: Dict[str, List[str]]) -> bool:
        """Check if a team qualifies for the sustainable growth prize."""
        # Team must be in top position of balanced economy ranking
        if "balanced_economy" not in rankings or not rankings["balanced_economy"]:
            return False

        return team_id == rankings["balanced_economy"][0]

    def _check_crisis_management(self, team: Dict[str, Any], current_round: int) -> bool:
        """Check if a team qualifies for the crisis management award."""
        # Need at least 3 rounds of history
        if current_round < 3 or "history" not in team or len(team["history"]) < 3:
            return False

        # Check for recovery from negative growth
        history = team["history"]

        # Look for a pattern of negative growth followed by positive growth
        for i in range(1, len(history) - 1):
            prev_gdp = history[i-1].get("Y", 0)
            curr_gdp = history[i].get("Y", 0)
            next_gdp = history[i+1].get("Y", 0)

            if prev_gdp <= 0 or curr_gdp <= 0:
                continue

            # Check for negative growth followed by positive growth
            growth_rate_1 = (curr_gdp - prev_gdp) / prev_gdp
            growth_rate_2 = (next_gdp - curr_gdp) / curr_gdp

            if growth_rate_1 < 0 and growth_rate_2 > 0.05:  # Negative followed by >5% growth
                return True

        return False

    def _check_export_champion(self, team_id: str, rankings: Dict[str, List[str]]) -> bool:
        """Check if a team qualifies for the export champion award."""
        # Team must be in top position of net exports ranking
        if "net_exports" not in rankings or not rankings["net_exports"]:
            return False

        return team_id == rankings["net_exports"][0]
