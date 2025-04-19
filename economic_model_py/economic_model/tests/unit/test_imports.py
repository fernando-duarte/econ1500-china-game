"""
Test imports for the China Growth Game package.
"""

import unittest

class TestImports(unittest.TestCase):
    """Test that all modules can be imported correctly."""

    def test_core_imports(self):
        """Test that core modules can be imported."""
        from economic_model_py.economic_model.core import solow_core
        from economic_model_py.economic_model.core import solow_model
        from economic_model_py.economic_model.core import solow_simulation
        self.assertTrue(True)

    def test_game_imports(self):
        """Test that game modules can be imported."""
        from economic_model_py.economic_model.game import game_state
        from economic_model_py.economic_model.game import team_management
        from economic_model_py.economic_model.game import events_manager
        from economic_model_py.economic_model.game import rankings_manager
        self.assertTrue(True)

    def test_visualization_imports(self):
        """Test that visualization modules can be imported."""
        from economic_model_py.economic_model.visualization import visualization_manager
        self.assertTrue(True)

    def test_utils_imports(self):
        """Test that utils modules can be imported."""
        from economic_model_py.economic_model.utils import constants
        from economic_model_py.economic_model.utils import replay
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
