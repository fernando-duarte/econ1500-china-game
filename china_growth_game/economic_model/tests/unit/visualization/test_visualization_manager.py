import unittest
from china_growth_game.economic_model.visualization.visualization_manager import VisualizationManager

class TestVisualizationManager(unittest.TestCase):
    """Test cases for the VisualizationManager class."""

    def setUp(self):
        """Set up the test environment."""
        self.visualization_manager = VisualizationManager()
        
        # Create mock team data with history
        self.mock_team_data = {
            "team_id": "team1",
            "team_name": "Test Team",
            "current_state": {
                "Year": 2000,
                "GDP": 1200.0,
                "Net Exports": 60.0,
                "Consumption": 900.0,
                "Investment": 300.0
            },
            "history": [
                {
                    "Year": 1980,
                    "GDP": 500.0,
                    "Net Exports": 20.0,
                    "Consumption": 400.0,
                    "Investment": 100.0
                },
                {
                    "Year": 1985,
                    "GDP": 600.0,
                    "Net Exports": 25.0,
                    "Consumption": 480.0,
                    "Investment": 120.0
                },
                {
                    "Year": 1990,
                    "GDP": 800.0,
                    "Net Exports": 35.0,
                    "Consumption": 640.0,
                    "Investment": 160.0
                },
                {
                    "Year": 1995,
                    "GDP": 1000.0,
                    "Net Exports": 45.0,
                    "Consumption": 800.0,
                    "Investment": 200.0
                }
            ]
        }
        
        # Create mock team data with incomplete history
        self.mock_team_incomplete = {
            "team_id": "team2",
            "team_name": "Incomplete Team",
            "current_state": {
                "Year": 1985,
                "GDP": 600.0,
                # Missing Net Exports
                "Consumption": 480.0
                # Missing Investment
            },
            "history": [
                {
                    "Year": 1980,
                    "GDP": 500.0,
                    "Net Exports": 20.0,
                    "Consumption": 400.0,
                    # Missing Investment
                }
            ]
        }
        
        # Create mock team data with no history
        self.mock_team_no_history = {
            "team_id": "team3",
            "team_name": "No History Team",
            "current_state": {
                "Year": 1980,
                "GDP": 500.0,
                "Net Exports": 20.0,
                "Consumption": 400.0,
                "Investment": 100.0
            },
            "history": []
        }
        
    def test_get_team_visualizations(self):
        """Test visualization data generation for a team."""
        vis_data = self.visualization_manager.get_team_visualizations(self.mock_team_data)
        
        # Check that all required visualizations are present
        self.assertIn("gdp_growth_chart", vis_data)
        self.assertIn("trade_balance_chart", vis_data)
        self.assertIn("consumption_savings_pie", vis_data)
        
        # Check GDP growth chart data
        gdp_chart = vis_data["gdp_growth_chart"]
        self.assertIn("years", gdp_chart)
        self.assertIn("gdp_growth_percent", gdp_chart)
        self.assertEqual(len(gdp_chart["years"]), 5)  # 4 history + 1 current
        self.assertEqual(len(gdp_chart["gdp_growth_percent"]), 5)
        self.assertEqual(gdp_chart["years"], [1980, 1985, 1990, 1995, 2000])
        
        # First growth value should be 0 (no previous year)
        self.assertEqual(gdp_chart["gdp_growth_percent"][0], 0.0)
        
        # Check that growth rates are calculated correctly
        # Growth from 1980 to 1985: (600/500)^(1/5) - 1 = 0.037 = 3.7%
        self.assertAlmostEqual(gdp_chart["gdp_growth_percent"][1], 3.7, places=1)
        
        # Check trade balance chart data
        trade_chart = vis_data["trade_balance_chart"]
        self.assertIn("years", trade_chart)
        self.assertIn("net_exports", trade_chart)
        self.assertEqual(len(trade_chart["years"]), 5)
        self.assertEqual(len(trade_chart["net_exports"]), 5)
        self.assertEqual(trade_chart["years"], [1980, 1985, 1990, 1995, 2000])
        self.assertEqual(trade_chart["net_exports"], [20.0, 25.0, 35.0, 45.0, 60.0])
        
        # Check consumption/savings pie chart data
        pie_chart = vis_data["consumption_savings_pie"]
        self.assertIn("consumption", pie_chart)
        self.assertIn("savings", pie_chart)
        self.assertEqual(pie_chart["consumption"], 900.0)
        # Savings = Investment - Net Exports = 300 - 60 = 240
        self.assertEqual(pie_chart["savings"], 240.0)
        
    def test_get_team_visualizations_incomplete(self):
        """Test visualization data generation for a team with incomplete data."""
        vis_data = self.visualization_manager.get_team_visualizations(self.mock_team_incomplete)
        
        # Should return an error message
        self.assertIn("error", vis_data)
        self.assertEqual(vis_data["error"], "Insufficient historical data for visualization")
        
    def test_get_team_visualizations_no_history(self):
        """Test visualization data generation for a team with no history."""
        vis_data = self.visualization_manager.get_team_visualizations(self.mock_team_no_history)
        
        # Check that all required visualizations are present
        self.assertIn("gdp_growth_chart", vis_data)
        self.assertIn("trade_balance_chart", vis_data)
        self.assertIn("consumption_savings_pie", vis_data)
        
        # Check that there's only one data point (current state)
        self.assertEqual(len(vis_data["gdp_growth_chart"]["years"]), 1)
        self.assertEqual(len(vis_data["gdp_growth_chart"]["gdp_growth_percent"]), 1)
        self.assertEqual(len(vis_data["trade_balance_chart"]["years"]), 1)
        self.assertEqual(len(vis_data["trade_balance_chart"]["net_exports"]), 1)
        
        # Growth rate should be 0 for the first point
        self.assertEqual(vis_data["gdp_growth_chart"]["gdp_growth_percent"][0], 0.0)
        
        # Check consumption/savings pie chart data
        pie_chart = vis_data["consumption_savings_pie"]
        self.assertEqual(pie_chart["consumption"], 400.0)
        # Savings = Investment - Net Exports = 100 - 20 = 80
        self.assertEqual(pie_chart["savings"], 80.0)
        
    def test_gdp_growth_calculation(self):
        """Test GDP growth rate calculation."""
        # Create a simple team with consistent growth
        simple_team = {
            "current_state": {
                "Year": 2000,
                "GDP": 1000.0,
                "Net Exports": 50.0,
                "Consumption": 800.0,
                "Investment": 200.0
            },
            "history": [
                {
                    "Year": 1980,
                    "GDP": 100.0,
                    "Net Exports": 5.0,
                    "Consumption": 80.0,
                    "Investment": 20.0
                },
                {
                    "Year": 1990,
                    "GDP": 300.0,
                    "Net Exports": 15.0,
                    "Consumption": 240.0,
                    "Investment": 60.0
                }
            ]
        }
        
        vis_data = self.visualization_manager.get_team_visualizations(simple_team)
        gdp_chart = vis_data["gdp_growth_chart"]
        
        # First growth value should be 0 (no previous year)
        self.assertEqual(gdp_chart["gdp_growth_percent"][0], 0.0)
        
        # Check that growth rates are positive and sensible
        self.assertGreater(gdp_chart["gdp_growth_percent"][1], 0)
        self.assertGreater(gdp_chart["gdp_growth_percent"][2], 0)
        
        # GDP is growing from 100 to 300 to 1000, so growth rates should be significant
        self.assertGreater(gdp_chart["gdp_growth_percent"][1], 5.0)  # At least 5% growth
        self.assertGreater(gdp_chart["gdp_growth_percent"][2], 5.0)  # At least 5% growth

if __name__ == '__main__':
    unittest.main()
