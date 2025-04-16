import unittest
from enhanced_solow_model import EnhancedSolowModel

class TestEnhancedSolowModel(unittest.TestCase):
    """Test cases for the EnhancedSolowModel class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.model = EnhancedSolowModel()
        
        # Create an initial state based on specifications
        self.initial_state = {
            "year": 1980,
            "round": 0,
            "Y": 306.2,  # GDP
            "K": 800,    # Capital
            "L": 600,    # Labor Force
            "H": 1.0,    # Human Capital
            "A": 1.0,    # Productivity (TFP)
            "NX": 3.6,   # Net Exports
            "C": 306.2 * 0.8,  # Consumption (assuming default savings rate of 20%)
            "initial_Y": 306.2  # Keep track of initial GDP for imports calculation
        }
        
        # Default student decision
        self.default_decision = {
            "savings_rate": 0.2,
            "exchange_rate_policy": "market"
        }
        
        # Empty events list
        self.empty_events = []
        
        # Events with known effects
        self.wto_event = [{
            "year": 2001,
            "name": "China Joins WTO",
            "description": "China joins the World Trade Organization",
            "effects": {
                "exports_multiplier": 1.25,
                "tfp_increase": 0.02
            },
            "triggered": True
        }]

    def test_simulate_round_with_defaults(self):
        """Test simulation of a round with default parameters."""
        # Simulate first round (1980-1985)
        new_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=self.default_decision,
            events=self.empty_events,
            period_index=0
        )
        
        # Verify outputs make sense
        self.assertGreater(new_state["Y"], self.initial_state["Y"], "GDP should increase")
        self.assertGreater(new_state["K"], self.initial_state["K"], "Capital should accumulate")
        self.assertGreater(new_state["A"], self.initial_state["A"], "Productivity should increase")
        
        # Verify consumption is based on savings rate
        expected_consumption = new_state["Y"] * (1 - self.default_decision["savings_rate"])
        self.assertAlmostEqual(new_state["C"], expected_consumption, places=1, 
                          msg="Consumption should be (1-s)*Y")

    def test_exchange_rate_policy_impact(self):
        """Test the impact of different exchange rate policies."""
        # Simulate with undervalued exchange rate
        undervalue_decision = {
            "savings_rate": 0.2,
            "exchange_rate_policy": "undervalue"
        }
        
        undervalue_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=undervalue_decision,
            events=self.empty_events,
            period_index=0
        )
        
        # Simulate with overvalued exchange rate
        overvalue_decision = {
            "savings_rate": 0.2,
            "exchange_rate_policy": "overvalue"
        }
        
        overvalue_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=overvalue_decision,
            events=self.empty_events,
            period_index=0
        )
        
        # Undervalued should have higher exports than overvalued
        self.assertGreater(undervalue_state["exports"], overvalue_state["exports"],
                      "Undervalued exchange rate should increase exports")
        
        # Overvalued should have higher imports than undervalued
        self.assertGreater(overvalue_state["imports"], undervalue_state["imports"],
                      "Overvalued exchange rate should increase imports")
        
        # Undervalued should have better net exports
        self.assertGreater(undervalue_state["NX"], overvalue_state["NX"],
                      "Undervalued exchange rate should improve trade balance")

    def test_savings_rate_impact(self):
        """Test the impact of different savings rates."""
        # Simulate with low savings rate
        low_savings_decision = {
            "savings_rate": 0.1,
            "exchange_rate_policy": "market"
        }
        
        low_savings_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=low_savings_decision,
            events=self.empty_events,
            period_index=0
        )
        
        # Simulate with high savings rate
        high_savings_decision = {
            "savings_rate": 0.5,
            "exchange_rate_policy": "market"
        }
        
        high_savings_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=high_savings_decision,
            events=self.empty_events,
            period_index=0
        )
        
        # Higher savings should lead to more capital accumulation
        self.assertGreater(high_savings_state["K"], low_savings_state["K"],
                      "Higher savings rate should lead to more capital")
        
        # Higher savings should lead to less consumption
        self.assertLess(high_savings_state["C"], low_savings_state["C"],
                    "Higher savings rate should lead to less consumption")

    def test_wto_event_impact(self):
        """Test the impact of the WTO event."""
        # Simulate without WTO event
        normal_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=self.default_decision,
            events=self.empty_events,
            period_index=5  # 2001
        )
        
        # Simulate with WTO event
        wto_state = self.model.simulate_round(
            current_state=self.initial_state,
            decision=self.default_decision,
            events=self.wto_event,
            period_index=5  # 2001
        )
        
        # WTO event should increase exports
        self.assertGreater(wto_state["exports"], normal_state["exports"] * 1.2,
                      "WTO event should significantly increase exports")
        
        # WTO event should increase productivity growth
        self.assertGreater(wto_state["A"], normal_state["A"],
                      "WTO event should increase productivity")

    def test_visualization_data(self):
        """Test generation of visualization data."""
        # Create a simple history with two years
        history = [
            {
                "year": 1980,
                "Y": 100,
                "NX": 10,
                "C": 80
            },
            {
                "year": 1985,
                "Y": 120,
                "NX": 15,
                "C": 90
            }
        ]
        
        # Get visualization data
        viz_data = self.model.get_visualization_data(history)
        
        # Check structure
        self.assertIn('gdp_growth', viz_data, "Visualization should include GDP growth")
        self.assertIn('trade_balance', viz_data, "Visualization should include trade balance")
        self.assertIn('consumption_vs_savings', viz_data, "Visualization should include consumption vs savings")
        
        # Check GDP growth calculation
        expected_growth = ((120 / 100)**(1/5) - 1) * 100  # Annual growth rate
        self.assertAlmostEqual(viz_data['gdp_growth']['data'][1], expected_growth, places=1,
                          msg="GDP growth calculation should be correct")

if __name__ == '__main__':
    unittest.main() 