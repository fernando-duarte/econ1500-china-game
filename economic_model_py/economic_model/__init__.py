"""
Economic Model package for the China Growth Game.

This package contains the core economic model, game state management,
and visualization tools for the China Growth Game.
"""

from china_growth_game.economic_model.core import (
    solow_core,
    solow_model,
    solow_simulation
)

from china_growth_game.economic_model.game import (
    game_state,
    team_management,
    events_manager,
    rankings_manager,
    prize_manager
)

from china_growth_game.economic_model.visualization import (
    visualization_manager
)

from china_growth_game.economic_model.utils import (
    constants,
    replay
)

# For convenience, expose key classes at the package level
from china_growth_game.economic_model.game.game_state import GameState
from china_growth_game.economic_model.game.team_management import TeamManager
from china_growth_game.economic_model.game.events_manager import EventsManager
from china_growth_game.economic_model.game.rankings_manager import RankingsManager
from china_growth_game.economic_model.game.prize_manager import PrizeManager
from china_growth_game.economic_model.visualization.visualization_manager import VisualizationManager
from china_growth_game.economic_model.utils.replay import replay_session
