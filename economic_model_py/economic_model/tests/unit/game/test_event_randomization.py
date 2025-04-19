import unittest
import random
import math
import statistics
from typing import Dict, List, Any
from economic_model_py.economic_model.game.randomized_events_manager import RandomizedEventsManager, EVENT_CATEGORIES

class TestEventRandomization(unittest.TestCase):
    """Test cases for event randomization."""

    def setUp(self):
        """Set up the test environment."""
        # Use a fixed seed for reproducibility
        self.seed = 42
        self.events_manager = RandomizedEventsManager(seed=self.seed)
        
    def test_init(self):
        """Test the initialization of RandomizedEventsManager."""
        self.assertTrue(self.events_manager.randomization_enabled)
        self.assertEqual(len(self.events_manager.random_events), 0)
        self.assertEqual(len(self.events_manager.event_history), 0)
        
    def test_fixed_events_still_work(self):
        """Test that fixed events from the parent class still work."""
        # WTO event in 2001
        events_2001 = self.events_manager.get_current_events(2001)
        
        # Should have at least the WTO event
        wto_events = [e for e in events_2001 if e["name"] == "China Joins WTO"]
        self.assertEqual(len(wto_events), 1)
        
        # Check that the event is not triggered again
        events_2001_again = self.events_manager.get_current_events(2001)
        wto_events_again = [e for e in events_2001_again if e["name"] == "China Joins WTO"]
        self.assertEqual(len(wto_events_again), 0)
        
    def test_random_events_generation(self):
        """Test that random events are generated."""
        # Run for 10 years
        for year in range(1980, 1990):
            events = self.events_manager.get_current_events(year)
            
            # Check that events were added to history
            year_history = [e for e in self.events_manager.event_history if e["year"] == year]
            self.assertEqual(len(year_history), len(events))
            
    def test_event_probability_distribution(self):
        """Test that event occurrence follows the expected probability distribution."""
        # Run a large number of simulations to get statistically significant results
        num_simulations = 1000
        num_years = 20
        
        # Track event occurrences
        event_counts = {category: 0 for category in EVENT_CATEGORIES}
        total_years = num_simulations * num_years
        
        # Run simulations
        for i in range(num_simulations):
            # Create a new events manager with a different seed for each simulation
            events_manager = RandomizedEventsManager(seed=self.seed + i)
            
            # Run simulation
            history, _ = events_manager.run_simulation(num_years)
            
            # Count events by category
            for entry in history:
                event = entry["event"]
                category = event.get("category")
                if category:
                    event_counts[category] += 1
                    
        # Calculate observed probabilities
        observed_probs = {category: count / total_years for category, count in event_counts.items()}
        
        # Compare with expected probabilities
        for category, config in EVENT_CATEGORIES.items():
            expected_prob = config["probability"]
            observed_prob = observed_probs[category]
            
            # Allow for some statistical variation (within 10% of expected)
            margin = 0.1 * expected_prob
            self.assertAlmostEqual(observed_prob, expected_prob, delta=margin,
                                  msg=f"Category {category}: expected {expected_prob}, observed {observed_prob}")
                                  
    def test_chi_square_goodness_of_fit(self):
        """Test event distribution using chi-square goodness of fit test."""
        # Run a large number of simulations
        num_simulations = 1000
        num_years = 20
        total_years = num_simulations * num_years
        
        # Track event occurrences
        event_counts = {category: 0 for category in EVENT_CATEGORIES}
        
        # Run simulations
        for i in range(num_simulations):
            events_manager = RandomizedEventsManager(seed=self.seed + i)
            history, _ = events_manager.run_simulation(num_years)
            
            # Count events by category
            for entry in history:
                event = entry["event"]
                category = event.get("category")
                if category:
                    event_counts[category] += 1
                    
        # Calculate chi-square statistic
        chi_square = 0
        for category, config in EVENT_CATEGORIES.items():
            expected_count = config["probability"] * total_years
            observed_count = event_counts[category]
            
            # Add to chi-square statistic
            if expected_count > 0:  # Avoid division by zero
                chi_square += ((observed_count - expected_count) ** 2) / expected_count
                
        # Degrees of freedom = number of categories - 1
        df = len(EVENT_CATEGORIES) - 1
        
        # Critical value for chi-square test with df degrees of freedom at 0.05 significance level
        # For df=5, critical value is approximately 11.07
        critical_value = 11.07
        
        # Test should pass if chi-square < critical_value
        self.assertLess(chi_square, critical_value,
                       msg=f"Chi-square test failed: {chi_square} >= {critical_value}")
                       
    def test_event_effect_ranges(self):
        """Test that event effects are within the specified ranges."""
        # Run simulation for 100 years to get a good sample
        history, _ = self.events_manager.run_simulation(100)
        
        # Check each random event
        for entry in history:
            event = entry["event"]
            category = event.get("category")
            
            # Skip fixed events
            if not category:
                continue
                
            # Get category configuration
            config = EVENT_CATEGORIES[category]
            
            # Check each effect
            for effect_name, effect_value in event["effects"].items():
                # Get expected range
                min_val, max_val = config["effects"][effect_name]
                
                # Check that effect is within range
                self.assertGreaterEqual(effect_value, min_val,
                                      msg=f"Effect {effect_name} value {effect_value} < min {min_val}")
                self.assertLessEqual(effect_value, max_val,
                                   msg=f"Effect {effect_name} value {effect_value} > max {max_val}")
                                   
    def test_regional_impact(self):
        """Test that regional impact is correctly applied to events."""
        # Run simulation for 100 years to get a good sample
        history, _ = self.events_manager.run_simulation(100)
        
        # Find natural disaster events (which have regional impact)
        disaster_events = []
        for entry in history:
            event = entry["event"]
            if event.get("category") == "natural_disaster":
                disaster_events.append(event)
                
        # Skip test if no disaster events occurred
        if not disaster_events:
            self.skipTest("No natural disaster events occurred in simulation")
            
        # Check that regional impact is present
        for event in disaster_events:
            self.assertIn("regional_impact", event)
            regional_impact = event["regional_impact"]
            
            # Check specific regions
            self.assertIn("coastal", regional_impact)
            self.assertIn("inland", regional_impact)
            self.assertIn("western", regional_impact)
            
            # Check values
            self.assertGreater(regional_impact["coastal"], 1.0)  # More impact in coastal regions
            self.assertLess(regional_impact["inland"], 1.0)      # Less impact in inland regions
            
    def test_r_and_d_modifier(self):
        """Test that R&D modifier is correctly applied to events."""
        # Run simulation for 100 years to get a good sample
        history, _ = self.events_manager.run_simulation(100)
        
        # Find technological breakthrough events (which have R&D modifier)
        tech_events = []
        for entry in history:
            event = entry["event"]
            if event.get("category") == "technological_breakthrough":
                tech_events.append(event)
                
        # Skip test if no tech events occurred
        if not tech_events:
            self.skipTest("No technological breakthrough events occurred in simulation")
            
        # Check that R&D modifier is present
        for event in tech_events:
            self.assertIn("r_and_d_modifier", event)
            r_and_d_modifier = event["r_and_d_modifier"]
            
            # Check value
            self.assertGreater(r_and_d_modifier, 0.0)
            
    def test_multiple_simulations_different_results(self):
        """Test that different seeds produce different results."""
        # Run two simulations with different seeds
        events_manager1 = RandomizedEventsManager(seed=1)
        events_manager2 = RandomizedEventsManager(seed=2)
        
        history1, _ = events_manager1.run_simulation(20)
        history2, _ = events_manager2.run_simulation(20)
        
        # Count events in each simulation
        count1 = len([e for e in history1 if e["event"].get("category")])
        count2 = len([e for e in history2 if e["event"].get("category")])
        
        # The counts should be different with high probability
        # (there's a small chance they could be the same by coincidence)
        self.assertNotEqual(count1, count2)
        
    def test_same_seed_same_results(self):
        """Test that the same seed produces the same results."""
        # Run two simulations with the same seed
        events_manager1 = RandomizedEventsManager(seed=42)
        events_manager2 = RandomizedEventsManager(seed=42)
        
        history1, _ = events_manager1.run_simulation(20)
        history2, _ = events_manager2.run_simulation(20)
        
        # The histories should be identical
        self.assertEqual(len(history1), len(history2))
        
        # Check each event
        for i in range(len(history1)):
            event1 = history1[i]["event"]
            event2 = history2[i]["event"]
            
            # Check category and year
            self.assertEqual(event1.get("category"), event2.get("category"))
            self.assertEqual(event1.get("year"), event2.get("year"))
            
            # If it's a random event, check effects
            if event1.get("category"):
                for effect_name, effect_value in event1["effects"].items():
                    self.assertEqual(effect_value, event2["effects"][effect_name])
                    
    def test_disable_randomization(self):
        """Test that randomization can be disabled."""
        # Create events manager with randomization disabled
        events_manager = RandomizedEventsManager(seed=42, randomization_enabled=False)
        
        # Run for 10 years
        for year in range(1980, 1990):
            events = events_manager.get_current_events(year)
            
            # Should only have fixed events
            random_events = [e for e in events if e.get("category")]
            self.assertEqual(len(random_events), 0)
            
    def test_statistical_properties(self):
        """Test statistical properties of event generation."""
        # Run a large number of simulations
        num_simulations = 100
        num_years = 100
        
        # Track number of events per year
        events_per_year = []
        
        # Run simulations
        for i in range(num_simulations):
            events_manager = RandomizedEventsManager(seed=self.seed + i)
            
            # Count events per year
            for year in range(1980, 1980 + num_years):
                events = events_manager.get_current_events(year)
                random_events = [e for e in events if e.get("category")]
                events_per_year.append(len(random_events))
                
        # Calculate statistics
        mean_events = statistics.mean(events_per_year)
        stdev_events = statistics.stdev(events_per_year)
        
        # Expected mean: sum of all event probabilities
        expected_mean = sum(config["probability"] for config in EVENT_CATEGORIES.values())
        
        # Check that mean is close to expected
        self.assertAlmostEqual(mean_events, expected_mean, delta=0.1)
        
        # Check that standard deviation is reasonable
        # For a binomial distribution with n=1 and p=expected_mean, stdev = sqrt(p*(1-p))
        expected_stdev = math.sqrt(expected_mean * (1 - expected_mean))
        self.assertAlmostEqual(stdev_events, expected_stdev, delta=0.1)

if __name__ == '__main__':
    unittest.main()
