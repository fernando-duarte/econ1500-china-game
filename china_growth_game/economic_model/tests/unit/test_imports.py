"""
Test imports for the China Growth Game package.
"""

import unittest

class TestImports(unittest.TestCase):
    """Test that all modules can be imported correctly."""

    def test_core_imports(self):
        """Test that core modules can be imported."""
        from china_growth_game.economic_model.core import solow_core
        from china_growth_game.economic_model.core import solow_model
        from china_growth_game.economic_model.core import solow_simulation
        self.assertTrue(True)

    def test_game_imports(self):
        """Test that game modules can be imported."""
        from china_growth_game.economic_model.game import game_state
        from china_growth_game.economic_model.game import team_management
        from china_growth_game.economic_model.game import events_manager
        from china_growth_game.economic_model.game import rankings_manager
        self.assertTrue(True)

    def test_visualization_imports(self):
        """Test that visualization modules can be imported."""
        from china_growth_game.economic_model.visualization import visualization_manager
        self.assertTrue(True)

    def test_utils_imports(self):
        """Test that utils modules can be imported."""
        from china_growth_game.economic_model.utils import constants
        from china_growth_game.economic_model.utils import replay
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
