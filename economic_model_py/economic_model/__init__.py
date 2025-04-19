"""
Economic Model package for the China Growth Game.

This package contains the core economic model, game state management,
and visualization tools for the China Growth Game.
"""

from economic_model_py.economic_model.core import (
    solow_core,
    solow_model,
    solow_simulation
)

from economic_model_py.economic_model.game import (
    game_state,
    team_management,
    events_manager,
    rankings_manager,
    prize_manager
)

from economic_model_py.economic_model.visualization import (
    visualization_manager
)

from economic_model_py.economic_model.utils import (
    constants,
    replay
)

# For convenience, expose key classes at the package level
from economic_model_py.economic_model.game.game_state import GameState
from economic_model_py.economic_model.game.team_management import TeamManager
from economic_model_py.economic_model.game.events_manager import EventsManager
from economic_model_py.economic_model.game.rankings_manager import RankingsManager
from economic_model_py.economic_model.game.prize_manager import PrizeManager
from economic_model_py.economic_model.visualization.visualization_manager import VisualizationManager
from economic_model_py.economic_model.utils.replay import replay_session
