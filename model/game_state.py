"""
This module provides a wrapper for the canonical GameState implementation
from the china-growth-game/economic-model directory.

This avoids code duplication and ensures a single source of truth for game state.
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the package to Python path if it's not already there
package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_path not in sys.path:
    sys.path.insert(0, package_path)

# Import the canonical implementation
from china_growth_game.economic_model.game.game_state import GameState
from china_growth_game.economic_model.game.team_management import TeamManager
from china_growth_game.economic_model.game.events_manager import EventsManager
from china_growth_game.economic_model.game.rankings_manager import RankingsManager
from china_growth_game.economic_model.visualization.visualization_manager import VisualizationManager

# Re-export the classes for backwards compatibility
__all__ = ['GameState', 'TeamManager', 'EventsManager', 'RankingsManager', 'VisualizationManager']

# If you need to extend the GameState with additional functionality, you can do so here:
# class ExtendedGameState(GameState):
#     def __init__(self):
#         super().__init__()
#         # Add any additional initialization
#
#     def additional_method(self):
#         # Add any additional methods
#         pass
