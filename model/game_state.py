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

# Note: We're keeping the sys.path modification for backward compatibility
# In a proper package structure, this would be handled by proper imports
package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_path not in sys.path:
    sys.path.insert(0, package_path)

# Import the canonical implementation
from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.team_management import TeamManager
from economic_model_py.economic_model.game.events_manager import EventsManager
from economic_model_py.economic_model.game.rankings_manager import RankingsManager
from economic_model_py.economic_model.visualization.visualization_manager import VisualizationManager
# Import for potential future use
from economic_model_py.economic_model.utils.json_utils import convert_numpy_values

# Re-export the classes for backwards compatibility
__all__ = ['GameState', 'TeamManager', 'EventsManager', 'RankingsManager', 'VisualizationManager', 'convert_numpy_values']

# If you need to extend the GameState with additional functionality, you can do so here:
# class ExtendedGameState(GameState):
#     def __init__(self):
#         super().__init__()
#         # Add any additional initialization
#
#     def additional_method(self):
#         # Add any additional methods
#         pass
