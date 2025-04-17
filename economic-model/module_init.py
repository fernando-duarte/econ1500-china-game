"""
This file ensures that the economic-model directory is treated as a Python package.
"""

import sys
import os

# Add the current directory to sys.path if it's not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the game_state module
from game_state import GameState

# Make these available for imports
__all__ = ['GameState'] 